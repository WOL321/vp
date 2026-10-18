"""
Colombia Vote Party Tracker - Discord Bot
==========================================
Production-ready Discord bot for tracking vote party progress
on the Colombia nation (DiplomaticaMC).

Features:
- Premium embed design with dynamic color coding
- Auto-scraping every 3 minutes from 3 vote sites
- Persistent single-message editing (never spams)
- Automatic cycle detection and reset at 250 votes
- Role-based notification system with persistent button
- Full admin slash command suite
- Robust error handling and fallback selectors

Author: Colombia Nation Admin Team
License: MIT
"""

import os
import re
import json
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks
from bs4 import BeautifulSoup

# Load environment variables from .env file (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, that's okay

# ─── Configuration ────────────────────────────────────────────────────────────

VOTE_GOAL = 250
SCRAPE_INTERVAL_MINUTES = 3
PING_THRESHOLD = 30  # Ping VP role when remaining <= this
DATA_FILE = "bot_data.json"

# Premium embed assets - Colombian flag inspired
BANNER_URL = "https://image.qwenlm.ai/generated-images/bea82c2c-5e60-4930-9930-6d1d9afb7f03/_result.png"
THUMBNAIL_URL = "https://cdn.discordapp.com/emojis/947652669680750613.webp"  # Colombia flag emoji

# Color thresholds for embed accent bar
COLOR_YELLOW = 0xF1C40F  # Remaining > 50 (Early stage)
COLOR_BLUE = 0x3498DB    # Remaining 31-50 (Mid stage)
COLOR_RED = 0xE74C3C     # Remaining <= 30 (Final push)

# ─── Vote Site Definitions ────────────────────────────────────────────────────

VOTE_SITES = [
    {
        "name": "Minecraft-MP",
        "url": "https://minecraft-mp.com/server-s349345",
        "description": "Main vote count from server page",
        "primary_selectors": [
            "table.table-bordered",  # Get the whole table, then parse
        ],
        "fallback_patterns": [
            r"Vote\(s\)</strong></td>\s*<td>(\d+)",
        ],
    },
    {
        "name": "MinecraftServers.org",
        "url": "https://minecraftservers.org/server/679302",
        "description": "Vote count from server listing",
        "primary_selectors": [
            "div.server-info",  # Get the server info div
        ],
        "fallback_patterns": [
            r">Votes</div>\s*<div[^>]*>(\d+)</div>",
        ],
    },
    {
        "name": "Minecraft-Server-List",
        "url": "https://minecraft-server-list.com/server/513054/vote/",
        "description": "Monthly vote count",
        "primary_selectors": [
            "table#votifier_table",
        ],
        "fallback_patterns": [
            r"(\d+) Players have voted for this server in",
            r"<b>(\d+) Votes - All time</b>",
        ],
    },
]

# ─── Logging Setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("VotePartyBot")

# ─── Data Persistence ─────────────────────────────────────────────────────────


class BotData:
    """Handles persistent storage of bot state using a JSON file."""

    def __init__(self, filepath: str = DATA_FILE):
        self.filepath = filepath
        self.data = self._load()

    def _load(self) -> dict:
        """Load data from JSON file, or return defaults."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load data file: {e}")
        return self._defaults()

    def _defaults(self) -> dict:
        """Return default data structure."""
        return {
            "message_id": None,
            "channel_id": None,
            "baseline": 0,
            "last_sum": 0,
            "remaining": VOTE_GOAL,
            "has_ping_sent": False,
            "last_updated": None,
            "site_counts": {},
            "last_scrape_time": None,
        }

    def save(self):
        """Persist current data to JSON file."""
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save data file: {e}")

    # Property accessors
    @property
    def message_id(self) -> Optional[int]:
        return self.data.get("message_id")

    @message_id.setter
    def message_id(self, value: Optional[int]):
        self.data["message_id"] = value

    @property
    def channel_id(self) -> Optional[int]:
        return self.data.get("channel_id")

    @channel_id.setter
    def channel_id(self, value: Optional[int]):
        self.data["channel_id"] = value

    @property
    def baseline(self) -> int:
        return self.data.get("baseline", 0)

    @baseline.setter
    def baseline(self, value: int):
        self.data["baseline"] = value

    @property
    def remaining(self) -> int:
        return self.data.get("remaining", VOTE_GOAL)

    @remaining.setter
    def remaining(self, value: int):
        self.data["remaining"] = value

    @property
    def has_ping_sent(self) -> bool:
        return self.data.get("has_ping_sent", False)

    @has_ping_sent.setter
    def has_ping_sent(self, value: bool):
        self.data["has_ping_sent"] = value

    @property
    def site_counts(self) -> dict:
        return self.data.get("site_counts", {})

    @site_counts.setter
    def site_counts(self, value: dict):
        self.data["site_counts"] = value

    @property
    def last_updated(self) -> Optional[str]:
        return self.data.get("last_updated")

    @last_updated.setter
    def last_updated(self, value: Optional[str]):
        self.data["last_updated"] = value

    @property
    def last_scrape_time(self) -> Optional[float]:
        return self.data.get("last_scrape_time")

    @last_scrape_time.setter
    def last_scrape_time(self, value: Optional[float]):
        self.data["last_scrape_time"] = value


# ─── Web Scraper ──────────────────────────────────────────────────────────────


class VoteScraper:
    """
    Scrapes vote counts from Minecraft server list websites.
    Uses multiple selector strategies and regex fallbacks for robustness.
    """

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        """Initialize the HTTP session with proper headers."""
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
            }
        )

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()

    async def scrape_site(self, site: dict) -> tuple[str, Optional[int]]:
        """
        Scrape a single site for its vote count.
        Tries primary selectors first, then regex fallbacks.
        """
        name = site["name"]
        try:
            async with self.session.get(
                site["url"],
                timeout=aiohttp.ClientTimeout(total=20)
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"{name}: HTTP {resp.status}")
                    return name, None

                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")

                # Site-specific parsing
                if name == "Minecraft-MP":
                    # Find the table row containing "Vote(s)"
                    for row in soup.select("table.table-bordered tr"):
                        if "Vote(s)" in row.get_text():
                            cells = row.find_all("td")
                            if len(cells) >= 2:
                                count = self._extract_number(cells[1].get_text())
                                if count:
                                    logger.info(f"{name}: Found {count} votes")
                                    return name, count
                
                elif name == "MinecraftServers.org":
                    # Find the div containing "Votes" label
                    for row in soup.select("div.server-info div.row"):
                        if "Votes" in row.get_text():
                            cells = row.find_all("div")
                            if len(cells) >= 2:
                                count = self._extract_number(cells[1].get_text())
                                if count:
                                    logger.info(f"{name}: Found {count} votes")
                                    return name, count
                
                elif name == "Minecraft-Server-List":
                    # Look for monthly votes text
                    text = soup.get_text()
                    match = re.search(r"(\d+) Players have voted for this server in", text)
                    if match:
                        count = int(match.group(1))
                        logger.info(f"{name}: Found {count} votes (monthly)")
                        return name, count

                # Fallback: Try regex patterns on full HTML
                for pattern in site["fallback_patterns"]:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if count > 0:
                            logger.info(f"{name}: Found {count} votes (regex)")
                            return name, count

                logger.warning(f"{name}: Could not find vote count")
                return name, None

        except asyncio.TimeoutError:
            logger.warning(f"{name}: Request timed out")
            return name, None
        except Exception as e:
            logger.error(f"{name}: Scrape error - {e}")
            return name, None

    def _extract_number(self, text: str) -> Optional[int]:
        """Extract an integer from text."""
        cleaned = re.sub(r"[^\d]", "", text.replace(",", ""))
        if cleaned:
            return int(cleaned)
        return None

    async def scrape_all(self) -> tuple[dict[str, Optional[int]], int]:
        """
        Scrape all configured sites concurrently.
        Returns (site_counts_dict, total_sum).
        """
        if not self.session:
            await self.start()

        tasks_list = [self.scrape_site(site) for site in VOTE_SITES]
        results = await asyncio.gather(*tasks_list)

        counts = {}
        total = 0
        for name, count in results:
            counts[name] = count
            if count is not None:
                total += count

        logger.info(f"Scrape complete: {counts} | Total: {total}")
        return counts, total


# ─── Embed Builder ────────────────────────────────────────────────────────────


class EmbedBuilder:
    """
    Builds a premium, modern vote party tracker embed with dynamic styling.
    Designed for visual impact and professional appearance.
    
    Color scheme:
    - Yellow: remaining > 50 (Early stage)
    - Blue: remaining 31-50 (Mid stage)
    - Red: remaining <= 30 (Final push)
    """

    @staticmethod
    def get_color(remaining: int) -> int:
        """
        Determine embed accent color based on remaining votes.
        Creates visual urgency as the party approaches completion.
        """
        if remaining <= PING_THRESHOLD:
            return COLOR_RED
        elif remaining <= 50:
            return COLOR_BLUE
        else:
            return COLOR_YELLOW

    @staticmethod
    def get_status_line(remaining: int) -> str:
        """
        Get a dynamic status message based on remaining votes.
        Creates engagement and urgency through progressive messaging.
        """
        if remaining <= 0:
            return "🎉 **Vote Party Complete!**"
        elif remaining <= 30:
            return "🔥 **Final push! Almost there!**"
        elif remaining <= 50:
            return "⚡ **Getting close! Keep voting!**"
        elif remaining <= 100:
            return "💪 **Good progress! Don't stop!**"
        else:
            return "✅ **All good! Let's get started!**"

    @staticmethod
    def build_progress_bar(percentage: float, color: int = COLOR_YELLOW, length: int = 10) -> str:
        """
        Build a visually appealing progress bar using colored emoji squares.
        More vibrant and eye-catching than unicode blocks.
        """
        filled = int(percentage / (100 / length))
        empty = length - filled
        
        # Use colored squares based on the accent color
        if color == COLOR_RED:
            return "🟥" * filled + "⬜" * empty
        elif color == COLOR_BLUE:
            return "🟦" * filled + "⬜" * empty
        else:  # Yellow
            return "🟨" * filled + "⬜" * empty

    @staticmethod
    def format_site_count(name: str, count: Optional[int]) -> str:
        """Format individual site vote count with visual indicator."""
        if count is not None:
            return f"▸ **{name}** — {count} votes"
        else:
            return f"▸ **{name}** — ⚠️ Unavailable"

    @staticmethod
    def build(
        remaining: int,
        site_counts: dict[str, Optional[int]],
        last_updated: Optional[str],
        last_scrape_time: Optional[float] = None,
    ) -> discord.Embed:
        """
        Build a premium vote party tracker embed with modern design.
        Features strong visual hierarchy, clean spacing, and dynamic elements.
        """
        progress = max(0, VOTE_GOAL - remaining)
        percentage = min(100, max(0, (progress / VOTE_GOAL) * 100))
        color = EmbedBuilder.get_color(remaining)

        # Build visual elements
        bar = EmbedBuilder.build_progress_bar(percentage, color)
        status_line = EmbedBuilder.get_status_line(remaining)

        # Create embed with dynamic accent color
        embed = discord.Embed(
            title="🇨🇴 Colombia Vote Party",
            description="",
            color=color,
        )
        
        # Add thumbnail for branding
        embed.set_thumbnail(url=THUMBNAIL_URL)

        # Build premium description with clear sections
        if remaining <= 0:
            embed.description = (
                f"## 🎉 **Vote Party Complete!**\n"
                f"Starting new cycle...\n\n"
                f"{bar} **100.0%**"
            )
        else:
            # Header section with big number
            embed.description = (
                f"# **{remaining}** votes to go\n\n"
                f"{bar} **{percentage:.1f}%**\n"
                f"**{progress}** / {VOTE_GOAL} votes collected\n\n"
            )
            
            # Status message with styled box
            embed.description += f"> {status_line}"

        # Add separator
        embed.description += "\n\n━━━━━━━━━━━━━━━━━━━━"

        # Individual site votes - clean, organized format
        site_lines = []
        for site in VOTE_SITES:
            name = site["name"]
            count = site_counts.get(name)
            if count is not None:
                site_lines.append(f"▸ **{name}** — **{count}** votes")
            else:
                site_lines.append(f"▸ **{name}** — ⚠️ Unavailable")

        # Vote links - numbered
        links = []
        for i, site in enumerate(VOTE_SITES, 1):
            links.append(f"{i}. [Vote on {site['name']}]({site['url']})")

        # Vote counts and links stacked vertically
        embed.add_field(
            name="🗳️ Vote Counts",
            value="\n".join(site_lines) if site_lines else "No data yet",
            inline=False,
        )
        embed.add_field(
            name="🔗 Vote Now",
            value="\n".join(links),
            inline=False,
        )

        # Footer with timestamp
        if last_updated and last_scrape_time:
            try:
                dt = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=timezone.utc)
                
                # Set embed timestamp (Discord shows this as relative time)
                embed.timestamp = dt
                
                # Simple footer text
                embed.set_footer(text=f"⏱️ Updates every {SCRAPE_INTERVAL_MINUTES} minutes")
            except ValueError:
                embed.set_footer(text=f"⏱️ Last updated: {last_updated} UTC")
        elif last_updated:
            embed.set_footer(text=f"⏱️ Last updated: {last_updated} UTC")
        else:
            embed.set_footer(text="⏱️ Waiting for first update...")

        return embed


# ─── View (Persistent Button) ─────────────────────────────────────────────────


class VoteNotifyView(discord.ui.View):
    """Persistent view with the notification toggle button."""

    def __init__(self):
        super().__init__(timeout=None)  # Never expires

    @discord.ui.button(
        label="🔔 Get Notified",
        style=discord.ButtonStyle.primary,
        custom_id="vote_notify_toggle",
    )
    async def notify_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Toggle the VP role for the clicking user."""
        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message(
                "❌ This button only works in a server.", ephemeral=True
            )
            return

        vp_role = discord.utils.get(interaction.guild.roles, name="VP")
        if not vp_role:
            await interaction.response.send_message(
                "❌ The 'VP' role was not found. Please ask an admin to create it.",
                ephemeral=True,
            )
            return

        try:
            if vp_role in member.roles:
                await member.remove_roles(vp_role)
                await interaction.response.send_message(
                    "✅ You will **no longer** be notified for vote party updates.",
                    ephemeral=True,
                )
            else:
                await member.add_roles(vp_role)
                await interaction.response.send_message(
                    "✅ You will now be **notified** when the vote party is close!",
                    ephemeral=True,
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage roles. "
                "Please ensure my role is **above** the VP role.",
                ephemeral=True,
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {e}", ephemeral=True
            )


# ─── Bot Class ────────────────────────────────────────────────────────────────


class VotePartyBot(commands.Bot):
    """Main bot class with vote party tracking functionality."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
        )

        self.bot_data = BotData()
        self.scraper = VoteScraper()
        self.tracker_message: Optional[discord.Message] = None

    async def setup_hook(self):
        """Called when the bot is starting up."""
        await self.scraper.start()
        await self.add_cog(VotePartyCog(self))
        await self.tree.sync()
        logger.info("Slash commands synced globally.")

    async def on_ready(self):
        """Called when the bot is fully connected."""
        logger.info(f"✓ Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"✓ Connected to {len(self.guilds)} guild(s)")

        # Restore tracker message if it exists
        await self._restore_tracker_message()

        # Start the periodic scraping loop
        if not self.scrape_loop.is_running():
            self.scrape_loop.start()
            logger.info(f"✓ Scrape loop started (every {SCRAPE_INTERVAL_MINUTES} min)")

    async def _restore_tracker_message(self):
        """Attempt to restore the persistent tracker message from saved data."""
        msg_id = self.bot_data.message_id
        ch_id = self.bot_data.channel_id

        if msg_id and ch_id:
            try:
                channel = self.get_channel(ch_id)
                if channel is None:
                    channel = await self.fetch_channel(ch_id)

                if isinstance(channel, discord.TextChannel):
                    self.tracker_message = await channel.fetch_message(msg_id)
                    logger.info(f"✓ Restored tracker message {msg_id}")
            except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                logger.warning(f"Could not restore tracker message: {e}")
                self.bot_data.message_id = None
                self.bot_data.channel_id = None

    async def close(self):
        """Cleanup on shutdown."""
        self.scrape_loop.cancel()
        await self.scraper.close()
        await super().close()

    @tasks.loop(minutes=SCRAPE_INTERVAL_MINUTES)
    async def scrape_loop(self):
        """Periodic task: scrape all sites and update the embed."""
        logger.info("Running scheduled scrape...")
        await self._perform_scrape_and_update()

    async def _perform_scrape_and_update(self):
        """Scrape all sites, update data, and edit the embed."""
        try:
            counts, total = await self.scraper.scrape_all()
            baseline = self.bot_data.baseline

            # Calculate remaining votes
            remaining = VOTE_GOAL - (total - baseline)

            # Check if vote party is complete
            if remaining <= 0:
                logger.info(f"🎉 Vote party complete! Total: {total}")
                # Reset for next cycle
                baseline = total
                remaining = VOTE_GOAL
                self.bot_data.baseline = baseline
                self.bot_data.has_ping_sent = False
                logger.info(f"New cycle started. New baseline: {baseline}")

            # Update stored data
            now = datetime.now(timezone.utc)
            self.bot_data.remaining = max(0, remaining)
            self.bot_data.site_counts = counts
            self.bot_data.last_updated = now.strftime("%Y-%m-%d %H:%M:%S")
            self.bot_data.last_scrape_time = now.timestamp()
            self.bot_data.save()

            # Update the embed
            await self._update_embed()

            # Check if we need to ping
            await self._check_ping()

        except Exception as e:
            logger.error(f"Scrape loop error: {e}", exc_info=True)

    async def _update_embed(self):
        """Edit the persistent tracker message with current data."""
        if not self.tracker_message:
            logger.warning("No tracker message to update")
            return

        try:
            embed = EmbedBuilder.build(
                remaining=self.bot_data.remaining,
                site_counts=self.bot_data.site_counts,
                last_updated=self.bot_data.last_updated,
                last_scrape_time=self.bot_data.last_scrape_time,
            )

            view = VoteNotifyView()
            await self.tracker_message.edit(embed=embed, view=view)
            logger.info("Tracker embed updated successfully")

        except discord.HTTPException as e:
            logger.error(f"Failed to update embed: {e}")

    async def _check_ping(self):
        """Check if we should ping the VP role (only once per cycle)."""
        remaining = self.bot_data.remaining

        if remaining <= PING_THRESHOLD and not self.bot_data.has_ping_sent:
            if self.tracker_message and self.tracker_message.guild:
                vp_role = discord.utils.get(
                    self.tracker_message.guild.roles, name="VP"
                )
                if vp_role:
                    try:
                        await self.tracker_message.channel.send(
                            f"🚨 **{vp_role.mention}** Only **{remaining}** votes left "
                            f"until the Vote Party! Vote now!\n"
                            f"🔗 https://minecraft-mp.com/server-s349345",
                            allowed_mentions=discord.AllowedMentions(roles=True),
                        )
                        self.bot_data.has_ping_sent = True
                        self.bot_data.save()
                        logger.info(f"🔔 VP role pinged! Remaining: {remaining}")
                    except discord.HTTPException as e:
                        logger.error(f"Failed to send ping: {e}")
                else:
                    logger.warning("VP role not found in guild")


# ─── Slash Commands ───────────────────────────────────────────────────────────


class VotePartyCog(commands.Cog):
    """Cog containing all vote party slash commands (Administrator only)."""

    def __init__(self, bot: VotePartyBot):
        self.bot = bot

    voteparty_group = app_commands.Group(
        name="voteparty",
        description="Vote Party management commands",
        guild_only=True,
    )

    @voteparty_group.command(
        name="setup",
        description="Post or update the tracker embed in this channel"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction):
        """Post or update the tracker embed in the current channel."""
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.followup.send(
                "❌ This command can only be used in a text channel.", ephemeral=True
            )
            return

        # Check if we already have a message
        if self.bot.tracker_message:
            try:
                embed = EmbedBuilder.build(
                    remaining=self.bot.bot_data.remaining,
                    site_counts=self.bot.bot_data.site_counts,
                    last_updated=self.bot.bot_data.last_updated,
                    last_scrape_time=self.bot.bot_data.last_scrape_time,
                )
                view = VoteNotifyView()
                await self.bot.tracker_message.edit(embed=embed, view=view)
                await interaction.followup.send(
                    "✅ Tracker embed updated in place!", ephemeral=True
                )
                return
            except discord.NotFound:
                self.bot.tracker_message = None

        # Create new message
        embed = EmbedBuilder.build(
            remaining=self.bot.bot_data.remaining,
            site_counts=self.bot.bot_data.site_counts,
            last_updated=self.bot.bot_data.last_updated,
            last_scrape_time=self.bot.bot_data.last_scrape_time,
        )
        view = VoteNotifyView()

        message = await channel.send(embed=embed, view=view)

        # Save message reference
        self.bot.tracker_message = message
        self.bot.bot_data.message_id = message.id
        self.bot.bot_data.channel_id = channel.id
        self.bot.bot_data.save()

        await interaction.followup.send(
            f"✅ Vote Party tracker posted in {channel.mention}!",
            ephemeral=True,
        )

    @voteparty_group.command(
        name="setremaining",
        description="Manually set the number of remaining votes"
    )
    @app_commands.describe(value="Number of remaining votes (0-250)")
    @app_commands.checks.has_permissions(administrator=True)
    async def setremaining(self, interaction: discord.Interaction, value: int):
        """Manually set the remaining votes."""
        await interaction.response.defer(ephemeral=True)

        if value < 0 or value > VOTE_GOAL:
            await interaction.followup.send(
                f"❌ Value must be between 0 and {VOTE_GOAL}.",
                ephemeral=True,
            )
            return

        self.bot.bot_data.remaining = value
        self.bot.bot_data.has_ping_sent = False
        self.bot.bot_data.save()

        await self.bot._update_embed()

        progress = VOTE_GOAL - value
        pct = (progress / VOTE_GOAL) * 100

        await interaction.followup.send(
            f"✅ Remaining votes set to **{value}**.\n"
            f"Progress: {progress}/{VOTE_GOAL} ({pct:.1f}%)",
            ephemeral=True,
        )

    @voteparty_group.command(
        name="setbaseline",
        description="Set the current total vote sum as the new baseline"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setbaseline(self, interaction: discord.Interaction):
        """Set the current total sum as the new baseline."""
        await interaction.response.defer(ephemeral=True)

        try:
            counts, total = await self.bot.scraper.scrape_all()
            now = datetime.now(timezone.utc)
            self.bot.bot_data.baseline = total
            self.bot.bot_data.remaining = VOTE_GOAL
            self.bot.bot_data.site_counts = counts
            self.bot.bot_data.has_ping_sent = False
            self.bot.bot_data.last_updated = now.strftime("%Y-%m-%d %H:%M:%S")
            self.bot.bot_data.last_scrape_time = now.timestamp()
            self.bot.bot_data.save()

            await self.bot._update_embed()

            await interaction.followup.send(
                f"✅ New baseline set to **{total}**.\n"
                f"Vote party reset! {VOTE_GOAL} votes to go.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error scraping sites: {e}", ephemeral=True
            )

    @voteparty_group.command(
        name="forceupdate",
        description="Force an immediate scrape and update"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def forceupdate(self, interaction: discord.Interaction):
        """Force an immediate scrape and update."""
        await interaction.response.defer(ephemeral=True)

        try:
            await self.bot._perform_scrape_and_update()

            await interaction.followup.send(
                f"✅ Update complete!\n"
                f"Remaining: {self.bot.bot_data.remaining} votes",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error during update: {e}", ephemeral=True
            )

    @setup.error
    @setremaining.error
    @setbaseline.error
    @forceupdate.error
    async def voteparty_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        """Handle errors for all voteparty commands."""
        if isinstance(error, app_commands.MissingPermissions):
            msg = "❌ You need **Administrator** permission to use this command."
        else:
            msg = f"❌ An error occurred: {error}"

        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)


# ─── Main Entry Point ─────────────────────────────────────────────────────────


def main():
    """Entry point for the bot."""
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("=" * 60)
        logger.error("DISCORD_BOT_TOKEN environment variable not set!")
        logger.error("Please set it before running:")
        logger.error("  export DISCORD_BOT_TOKEN='your_token_here'")
        logger.error("=" * 60)
        return

    bot = VotePartyBot()
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()
