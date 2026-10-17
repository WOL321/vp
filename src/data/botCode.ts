export const mainBotCode = `"""
Colombia Vote Party Tracker - Discord Bot
==========================================
Production-ready Discord bot for tracking vote party progress
on the Colombia nation (DiplomaticaMC).

Scrapes vote counts from 3 Minecraft server list sites every 3 minutes,
tracks progress toward a 250-vote goal, and notifies members when
the party is close.

Features:
- Auto-scraping with fallback selectors
- Dynamic color-coded embed (green/yellow/red)
- Persistent single-message editing
- Automatic cycle detection and reset
- Role-based notification system
- Full admin slash command suite

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

# ─── Configuration ────────────────────────────────────────────────────────────

VOTE_GOAL = 250
SCRAPE_INTERVAL_MINUTES = 3
PING_THRESHOLD = 30  # Ping VP role when remaining <= this
DATA_FILE = "bot_data.json"

# Color thresholds for embed accent bar
COLOR_YELLOW = 0xF1C40F  # Remaining > 50 (Yellow)
COLOR_BLUE = 0x3498DB    # Remaining 31-50 (Blue)
COLOR_RED = 0xE74C3C     # Remaining <= 30 (Red)

# ─── Vote Site Definitions ────────────────────────────────────────────────────
# Each site has primary and fallback selectors for robust scraping

VOTE_SITES = [
    {
        "name": "Minecraft-MP",
        "url": "https://minecraft-mp.com/server-s349345",
        "description": "Main vote count from server page",
        "primary_selectors": [
            # Look for the "Vote(s)" badge/counter
            "span.badge.bg-success",
            "div.card-body span.badge",
            "span.votes",
            "div.votes span",
        ],
        "fallback_patterns": [
            r"(\\d+)\\s*vote",  # "X votes" or "X vote"
            r"Votes?:\\s*(\\d+)",
        ],
    },
    {
        "name": "MinecraftServers.org",
        "url": "https://minecraftservers.org/server/679302",
        "description": "Vote count from server listing",
        "primary_selectors": [
            # Look for the "Votes" number
            "div.votes-count span",
            "span.votes",
            "div.server-info .votes",
            "span[class*='vote']",
        ],
        "fallback_patterns": [
            r"(\d+)\s*votes?",
            r"Votes?:\s*(\d+)",
        ],
    },
    {
        "name": "Minecraft-Server-List",
        "url": "https://minecraft-server-list.com/server/513054/vote/",
        "description": "Monthly/all-time vote count",
        "primary_selectors": [
            # Look for monthly or all-time votes
            "span.vote-count",
            "div.vote-stats span",
            "span[class*='monthly']",
            "div.monthly-votes span",
        ],
        "fallback_patterns": [
            r"(\d+)\s*votes?\s*(this\s*month|monthly)",
            r"Monthly:\s*(\d+)",
            r"(\d+)\s*votes?",
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
        }

    def save(self):
        """Persist current data to JSON file."""
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save data file: {e}")

    # Property accessors for clean API
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
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
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
        Returns (site_name, vote_count) or (site_name, None) on failure.
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

                # Strategy 1: Try primary CSS selectors
                for selector in site["primary_selectors"]:
                    element = soup.select_one(selector)
                    if element:
                        text = element.get_text(strip=True)
                        count = self._extract_number(text)
                        if count is not None and count > 0:
                            logger.info(f"{name}: Found {count} votes (selector: {selector})")
                            return name, count

                # Strategy 2: Try regex patterns on full HTML
                for pattern in site["fallback_patterns"]:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        count = int(match.group(1))
                        if count > 0:
                            logger.info(f"{name}: Found {count} votes (regex: {pattern})")
                            return name, count

                # Strategy 3: Try extracting from all span/div elements
                count = self._brute_force_extract(soup)
                if count is not None:
                    logger.info(f"{name}: Found {count} votes (brute force)")
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
        """Extract an integer from text, handling various formats."""
        # Remove commas and whitespace, find first number sequence
        cleaned = re.sub(r"[^\\d]", "", text.replace(",", ""))
        if cleaned:
            return int(cleaned)
        return None

    def _brute_force_extract(self, soup: BeautifulSoup) -> Optional[int]:
        """Last resort: search all elements for vote-related numbers."""
        vote_keywords = ["vote", "votes", "votos"]

        for element in soup.find_all(["span", "div", "p", "strong", "b"]):
            text = element.get_text(strip=True).lower()
            if any(keyword in text for keyword in vote_keywords):
                # Try to extract number from this element
                numbers = re.findall(r"\\d+", text)
                for num_str in numbers:
                    num = int(num_str)
                    # Filter out obviously wrong numbers (like years)
                    if 10 < num < 100000:
                        return num
        return None

    async def scrape_all(self) -> tuple[dict[str, Optional[int]], int]:
        """
        Scrape all configured sites concurrently.
        Returns (site_counts_dict, total_sum).
        Only counts sites that returned valid data.
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
    Builds the premium vote party tracker embed with dynamic styling.
    Color changes based on remaining votes:
    - Green: remaining > 50
    - Yellow: remaining <= 50
    - Red: remaining <= 30
    """

    @staticmethod
    def get_color(remaining: int) -> int:
        """
        Determine embed color based on remaining votes.
        - Yellow: remaining > 50
        - Blue: remaining 31-50
        - Red: remaining <= 30
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
        Changes to create urgency as the party approaches completion.
        """
        if remaining <= 0:
            return "🎉 Vote Party Complete!"
        elif remaining <= 30:
            return "🔥 Final push! Almost there!"
        elif remaining <= 50:
            return "⚡ Getting close! Keep voting!"
        elif remaining <= 100:
            return "💪 Good progress! Don't stop!"
        else:
            return "✅ All good! Let's get started!"

    @staticmethod
    def build_progress_bar(percentage: float, length: int = 20) -> str:
        """Build a visual progress bar with filled and empty blocks."""
        filled = int(percentage / (100 / length))
        empty = length - filled
        return "▰" * filled + "▱" * empty

    @staticmethod
    def build(
        remaining: int,
        site_counts: dict[str, Optional[int]],
        last_updated: Optional[str],
    ) -> discord.Embed:
        """Build the premium vote party tracker embed."""
        progress = max(0, VOTE_GOAL - remaining)
        percentage = min(100, max(0, (progress / VOTE_GOAL) * 100))
        color = EmbedBuilder.get_color(remaining)

        # Build progress bar
        bar = EmbedBuilder.build_progress_bar(percentage)

        # Get dynamic status line
        status_line = EmbedBuilder.get_status_line(remaining)

        # Create embed with dynamic color
        embed = discord.Embed(
            title="🇨🇴 Colombia Vote Party Tracker",
            color=color,
            timestamp=datetime.now(timezone.utc),
        )

        # Main description - big clear text with status
        if remaining <= 0:
            embed.description = (
                f"## 🎉 **Vote Party Complete!**\\n"
                f"Starting new cycle...\\n"
                f"\\n"
                f"\`{bar}\` **100.0%**"
            )
        else:
            embed.description = (
                f"## **{remaining}** votes remaining to reach **{VOTE_GOAL}!**\\n"
                f"\\n"
                f"\`{bar}\` **{percentage:.1f}%**\\n"
                f"**{progress}** / {VOTE_GOAL} votes collected\\n"
                f"\\n"
                f"**{status_line}**"
            )

        # Individual site counts - clean formatting
        site_lines = []
        for site in VOTE_SITES:
            name = site["name"]
            count = site_counts.get(name)
            if count is not None:
                site_lines.append(f"\\u2022 **{name}** \\u2014 {count} votes")
            else:
                site_lines.append(f"\\u2022 **{name}** \\u2014 ⚠️ Unavailable")

        embed.add_field(
            name="🗳️ Vote Counts",
            value="\\n".join(site_lines) if site_lines else "No data yet",
            inline=False,
        )

        # Vote links - clickable
        links = []
        for site in VOTE_SITES:
            links.append(f"\\u2022 [Vote on {site['name']}]({site['url']})")

        embed.add_field(
            name="🔗 Vote Now",
            value="\\n".join(links),
            inline=False,
        )

        # Footer with last updated time
        if last_updated:
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
                "Please ensure my role is **above** the VP role in the hierarchy.",
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
            command_prefix="!",  # Fallback only, we use slash commands
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
                logger.info(
                    f"🎉 Vote party complete! Total: {total}, Baseline: {baseline}"
                )
                # Reset for next cycle
                baseline = total
                remaining = VOTE_GOAL
                self.bot_data.baseline = baseline
                self.bot_data.has_ping_sent = False
                logger.info(f"New cycle started. New baseline: {baseline}")

            # Update stored data
            self.bot_data.remaining = max(0, remaining)
            self.bot_data.site_counts = counts
            self.bot_data.last_updated = datetime.now(timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
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
                            f"until the Vote Party! Vote now to help us reach the goal!\\n"
                            f"\\n"
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
                # Update existing message
                embed = EmbedBuilder.build(
                    remaining=self.bot.bot_data.remaining,
                    site_counts=self.bot.bot_data.site_counts,
                    last_updated=self.bot.bot_data.last_updated,
                )
                view = VoteNotifyView()
                await self.bot.tracker_message.edit(embed=embed, view=view)
                await interaction.followup.send(
                    "✅ Tracker embed updated in place!", ephemeral=True
                )
                return
            except discord.NotFound:
                # Message was deleted, create new one
                self.bot.tracker_message = None

        # Create new message
        embed = EmbedBuilder.build(
            remaining=self.bot.bot_data.remaining,
            site_counts=self.bot.bot_data.site_counts,
            last_updated=self.bot.bot_data.last_updated,
        )
        view = VoteNotifyView()

        message = await channel.send(embed=embed, view=view)

        # Save message reference
        self.bot.tracker_message = message
        self.bot.bot_data.message_id = message.id
        self.bot.bot_data.channel_id = channel.id
        self.bot.bot_data.save()

        await interaction.followup.send(
            f"✅ Vote Party tracker posted in {channel.mention}!\\n"
            f"Message ID: {message.id}",
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
        self.bot.bot_data.has_ping_sent = False  # Reset ping status
        self.bot.bot_data.save()

        await self.bot._update_embed()

        progress = VOTE_GOAL - value
        pct = (progress / VOTE_GOAL) * 100

        await interaction.followup.send(
            f"✅ Remaining votes set to **{value}**.\\n"
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
            self.bot.bot_data.baseline = total
            self.bot.bot_data.remaining = VOTE_GOAL
            self.bot.bot_data.site_counts = counts
            self.bot.bot_data.has_ping_sent = False
            self.bot.bot_data.last_updated = datetime.now(timezone.utc).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.bot.bot_data.save()

            await self.bot._update_embed()

            site_summary = ", ".join(
                f"{k}: {v if v is not None else 'N/A'}"
                for k, v in counts.items()
            )

            await interaction.followup.send(
                f"✅ New baseline set to **{total}**.\\n"
                f"Vote party reset! {VOTE_GOAL} votes to go.\\n\\n"
                f"**Site counts:**\\n{site_summary}",
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

            site_summary = ", ".join(
                f"{k}: {v if v is not None else 'N/A'}"
                for k, v in self.bot.bot_data.site_counts.items()
            )

            await interaction.followup.send(
                f"✅ Update complete!\\n\\n"
                f"**Remaining:** {self.bot.bot_data.remaining} votes\\n"
                f"**Site counts:**\\n{site_summary}",
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
    bot.run(token, log_handler=None)  # We handle logging ourselves


if __name__ == "__main__":
    main()
`;

export const requirementsTxt = `discord.py>=2.3.0
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
`;

export const envExample = `# Discord Bot Token
# Get from: https://discord.com/developers/applications
DISCORD_BOT_TOKEN=your_bot_token_here
`;

export const setupInstructions = `# Colombia Vote Party Bot - Setup Guide

## Prerequisites
- Python 3.10 or higher
- A Discord account with Administrator permissions
- A Discord Bot Application

## Step 1: Create a Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application" → name it (e.g., "Colombia Vote Party")
3. Go to "Bot" tab → Click "Add Bot" → "Yes, do it"
4. Under "Privileged Gateway Intents", enable:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. Copy the **Bot Token** (keep this secret!)

## Step 2: Invite the Bot to Your Server

1. Go to "OAuth2" → "URL Generator"
2. Select scopes:
   - ✅ bot
   - ✅ applications.commands
3. Select Bot Permissions:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Manage Messages
   - ✅ Manage Roles
   - ✅ Read Message History
   - ✅ Use External Emojis
4. Copy the generated URL → open in browser → select your server

## Step 3: Create the VP Role

1. Server Settings → Roles → Create Role
2. Name it exactly: **VP**
3. **Important**: Bot's role must be ABOVE VP in hierarchy

## Step 4: Install and Run

\`\`\`bash
# Clone or download the bot files
cd colombia-vote-party-bot

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Set your bot token
export DISCORD_BOT_TOKEN='your_token_here'
# Windows: set DISCORD_BOT_TOKEN=your_token_here

# Run the bot
python bot.py
\`\`\`

## Step 5: Initialize the Tracker

1. Go to the channel where you want the tracker
2. Run: \`/voteparty setup\`
3. The tracker embed will appear with the 🔔 button

## Commands

| Command | Description |
|---------|-------------|
| \`/voteparty setup\` | Post/update tracker embed |
| \`/voteparty setremaining <number>\` | Set remaining votes |
| \`/voteparty setbaseline\` | Reset baseline to current total |
| \`/voteparty forceupdate\` | Force immediate scrape |

## How It Works

1. Every 3 minutes, scrapes all 3 vote sites
2. Sums the totals and compares to baseline
3. Remaining = 250 - (current_sum - baseline)
4. When remaining ≤ 0, auto-resets for new cycle
5. When remaining ≤ 30, pings VP role (once per cycle)
6. Members toggle VP role with 🔔 button

## Troubleshooting

- **"VP role not found"**: Create role named exactly "VP"
- **Site counts unavailable**: Site may be down or HTML changed
- **Can't manage roles**: Bot role must be above VP role
- **Commands not showing**: Wait for Discord to sync (up to 1 hour)
`;
