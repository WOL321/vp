"""
Colombia Vote Party Tracker - Discord Bot
=========================================
Production-ready Discord bot for tracking vote party progress
on the Colombia nation (DiplomaticaMC).

Features:
- Clean embed design with dynamic color coding
- Auto-scraping every 15 seconds from 3 vote sites
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
import cloudscraper
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
SCRAPE_INTERVAL_SECONDS = 15
PING_THRESHOLD = 30  # Ping VP role when remaining <= this
PING_DELETE_SECONDS = 300  # Delete ping message after 5 minutes (300 seconds)
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
        "fallback_patterns": [
            r"Vote\(s\)</strong></td>\s*<td>(\d+)",
            r"Vote\(s\)[^0-9]*(\d+)",
        ],
    },
    {
        "name": "MinecraftServers.org",
        "url": "https://minecraftservers.org/server/679302",
        "fallback_patterns": [
            r">Votes</div>\s*<div[^>]*>(\d+)</div>",
            r"Votes\s*</div>\s*<div[^>]*>\s*(\d+)\s*</div>",
        ],
    },
    {
        "name": "Minecraft-Server-List",
        "url": "https://minecraft-server-list.com/server/513054/vote/",
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
            "ping_message_id": None,
            "ping_timestamp": None,
            "last_vote_party_time": None,
            "vote_history": [],
            "cycle_start_votes": {},
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

    @property
    def ping_message_id(self) -> Optional[int]:
        return self.data.get("ping_message_id")

    @ping_message_id.setter
    def ping_message_id(self, value: Optional[int]):
        self.data["ping_message_id"] = value

    @property
    def ping_timestamp(self) -> Optional[float]:
        return self.data.get("ping_timestamp")

    @ping_timestamp.setter
    def ping_timestamp(self, value: Optional[float]):
        self.data["ping_timestamp"] = value

    @property
    def last_vote_party_time(self) -> Optional[str]:
        return self.data.get("last_vote_party_time")

    @last_vote_party_time.setter
    def last_vote_party_time(self, value: Optional[str]):
        self.data["last_vote_party_time"] = value

    @property
    def vote_history(self) -> list:
        return self.data.get("vote_history", [])

    @vote_history.setter
    def vote_history(self, value: list):
        self.data["vote_history"] = value

    @property
    def cycle_start_votes(self) -> dict:
        return self.data.get("cycle_start_votes", {})

    @cycle_start_votes.setter
    def cycle_start_votes(self, value: dict):
        self.data["cycle_start_votes"] = value


# ─── Web Scraper ──────────────────────────────────────────────────────────────


class VoteScraper:
    """
    Scrapes vote counts from Minecraft server list websites.
    Uses multiple selector strategies and regex fallbacks for robustness.
    Includes caching to prevent data loss when scrapes fail.
    """

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_successful_counts: dict[str, int] = {}

    async def start(self):
        """Initialize the HTTP session with proper headers."""
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
        )

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()

    def _validate_vote_count(self, name: str, count: int) -> bool:
        """Validate that a vote count is reasonable."""
        if count < 0:
            logger.warning(f"{name}: Invalid vote count {count} (negative)")
            return False
        if count > 1000000:
            logger.warning(f"{name}: Suspicious vote count {count} (too large)")
            return False
        return True

    async def scrape_site(self, site: dict) -> tuple[str, Optional[int]]:
        """
        Scrape a single site for its vote count.
        Uses regex on raw HTML for maximum reliability.
        Uses cloudscraper for sites with Cloudflare protection.
        Caches successful results to prevent data loss on failures.
        """
        name = site["name"]
        url = site["url"]

        # Minecraft-Server-List uses Cloudflare, so we need cloudscraper
        if name == "Minecraft-Server-List":
            try:
                scraper = cloudscraper.create_scraper()
                response = scraper.get(url, timeout=20)

                if response.status_code != 200:
                    logger.warning(f"{name}: HTTP {response.status_code}")
                    if name in self.last_successful_counts:
                        logger.info(f"{name}: Using cached value {self.last_successful_counts[name]}")
                        return name, self.last_successful_counts[name]
                    return name, None

                html = response.text
                logger.info(f"{name}: Got {len(html)} bytes of HTML (via cloudscraper)")

                for pattern in site["fallback_patterns"]:
                    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                    if match:
                        count = int(match.group(1))
                        if self._validate_vote_count(name, count):
                            logger.info(f"{name}: Found {count} votes (pattern: {pattern[:30]}...)")
                            self.last_successful_counts[name] = count
                            return name, count

                logger.warning(f"{name}: Could not find vote count. HTML snippet: {html[:500]}")
                if name in self.last_successful_counts:
                    logger.info(f"{name}: Using cached value {self.last_successful_counts[name]}")
                    return name, self.last_successful_counts[name]
                return name, None

            except Exception as e:
                logger.error(f"{name}: Cloudscraper error - {e}")
                if name in self.last_successful_counts:
                    logger.info(f"{name}: Using cached value {self.last_successful_counts[name]}")
                    return name, self.last_successful_counts[name]
                return name, None

        # For other sites, use regular aiohttp
        try:
            async with self.session.get(
                url,
                timeout=aiohttp.ClientTimeout(total=20)
            ) as resp:
                if resp.status != 200:
                    logger.warning(f"{name}: HTTP {resp.status}")
                    if name in self.last_successful_counts:
                        logger.info(f"{name}: Using cached value {self.last_successful_counts[name]}")
                        return name, self.last_successful_counts[name]
                    return name, None

                html = await resp.text()
                logger.info(f"{name}: Got {len(html)} bytes of HTML")

                for pattern in site["fallback_patterns"]:
                    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                    if match:
                        count = int(match.group(1))
                        if self._validate_vote_count(name, count):
                            logger.info(f"{name}: Found {count} votes (pattern: {pattern[:30]}...)")
                            self.last_successful_counts[name] = count
                            return name, count

                logger.warning(f"{name}: Could not find vote count. HTML snippet: {html[:500]}")
                if name in self.last_successful_counts:
                    logger.info(f"{name}: Using cached value {self.last_successful_counts[name]}")
                    return name, self.last_successful_counts[name]
                return name, None

        except asyncio.TimeoutError:
            logger.warning(f"{name}: Request timed out")
            if name in self.last_successful_counts:
                logger.info(f"{name}: Using cached value {self.last_successful_counts[name]}")
                return name, self.last_successful_counts[name]
            return name, None
        except Exception as e:
            logger.error(f"{name}: Scrape error - {e}")
            if name in self.last_successful_counts:
                logger.info(f"{name}: Using cached value {self.last_successful_counts[name]}")
                return name, self.last_successful_counts[name]
            return name, None

    async def scrape_all(self) -> tuple[dict[str, Optional[int]], int]:
        """
        Scrape all configured sites sequentially with small delays.
        Returns (site_counts_dict, total_sum).
        """
        if not self.session:
            await self.start()

        counts = {}
        total = 0

        for i, site in enumerate(VOTE_SITES):
            name, count = await self.scrape_site(site)
            counts[name] = count
            if count is not None:
                total += count

            if i < len(VOTE_SITES) - 1:
                await asyncio.sleep(1)

        logger.info(f"Scrape complete: {counts} | Total: {total}")
        return counts, total


# ─── Embed Builder ────────────────────────────────────────────────────────────


class EmbedBuilder:
    """
    Builds a clean vote party tracker embed with dynamic styling.

    Color scheme:
    - Yellow: remaining > 50 (Early stage)
    - Blue: remaining 31-50 (Mid stage)
    - Red: remaining <= 30 (Final push)
    """

    @staticmethod
    def get_color(remaining: int) -> int:
        """Determine embed accent color based on remaining votes."""
        if remaining <= PING_THRESHOLD:
            return COLOR_RED
        elif remaining <= 50:
            return COLOR_BLUE
        else:
            return COLOR_YELLOW

    @staticmethod
    def get_status_line(remaining: int) -> str:
        """Get a dynamic status message based on remaining votes."""
        if remaining <= 0:
            return "🎉 **Vote Party Complete!**"
        elif remaining <= 10:
            return "🔥 **Almost there! Party imminent!**"
        elif remaining <= 30:
            return "⚡ **Getting close! Notify the server!**"
        elif remaining <= 100:
            return "💪 **Good progress! Keep it up!**"
        else:
            return "🗳️ **Vote party in progress**"

    @staticmethod
    def build_progress_bar(percentage: float, color: int = COLOR_YELLOW, length: int = 10) -> str:
        """Build a visually appealing progress bar."""
        filled = int(percentage / (100 / length))
        empty = length - filled

        if color == COLOR_RED:
            bar = "🟥" * filled + "⬜" * empty
        elif color == COLOR_BLUE:
            bar = "🟦" * filled + "⬜" * empty
        else:
            bar = "🟨" * filled + "⬜" * empty

        return bar

    @staticmethod
    def estimate_completion(vote_history: list, remaining: int) -> Optional[str]:
        """Estimate time to completion based on voting rate."""
        if len(vote_history) < 2:
            return None

        recent = vote_history[-10:]
        if len(recent) < 2:
            return None

        first_time = recent[0]["timestamp"]
        first_votes = recent[0]["total"]
        last_time = recent[-1]["timestamp"]
        last_votes = recent[-1]["total"]

        time_diff = last_time - first_time
        vote_diff = last_votes - first_votes

        if time_diff <= 0 or vote_diff <= 0:
            return None

        votes_per_second = vote_diff / time_diff
        seconds_to_complete = remaining / votes_per_second

        if seconds_to_complete < 60:
            return f"~{int(seconds_to_complete)}s"
        elif seconds_to_complete < 3600:
            return f"~{int(seconds_to_complete / 60)}m"
        else:
            return f"~{seconds_to_complete / 3600:.1f}h"

    @staticmethod
    def build(
        remaining: int,
        site_counts: dict[str, Optional[int]],
        last_updated: Optional[str],
        last_scrape_time: Optional[float] = None,
        vote_history: Optional[list] = None,
        cycle_start_votes: Optional[dict] = None,
        last_vote_party_time: Optional[str] = None,
    ) -> discord.Embed:
        """
        Build a clean vote party tracker embed.
        """
        progress = max(0, VOTE_GOAL - remaining)
        percentage = min(100, max(0, (progress / VOTE_GOAL) * 100))
        color = EmbedBuilder.get_color(remaining)

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

        # Build clean description format
        if remaining <= 0:
            embed.description = (
                f"🎉 **Vote Party Complete!**\n"
                f"Starting new cycle...\n\n"
                f"{bar} 100.0%\n"
                f"{VOTE_GOAL} / {VOTE_GOAL} votes collected"
            )
        else:
            embed.description = (
                f"**{remaining}** votes remaining\n"
                f"{bar} {percentage:.1f}%\n"
                f"{progress} / {VOTE_GOAL} votes collected\n\n"
                f"{status_line}"
            )

        # Add separator and vote counts section
        embed.description += "\n\n━━━━━━━━━━━━━━━━━━━━\n"
        embed.description += "🗳️ **Vote Counts**\n"

        # Individual site votes with color-coded emojis
        # 🟡 = Minecraft-MP, 🔵 = MinecraftServers.org, 🔴 = Minecraft-Server-List
        site_emojis = ["🟡", "🔵", "🔴"]
        for i, site in enumerate(VOTE_SITES):
            name = site["name"]
            count = site_counts.get(name)
            emoji = site_emojis[i % len(site_emojis)]
            if count is not None:
                embed.description += f"{emoji} {name} — **{count:,}**\n"
            else:
                embed.description += f"{emoji} {name} — ⚠️ Unavailable\n"

        # Vote Now section with links
        embed.description += "🔗 **Vote Now!**\n"
        embed.description += "━━━━━━━━━━━━━━━━\n"
        for i, site in enumerate(VOTE_SITES, 1):
            embed.description += f"{i}. [Vote on {site['name']}]({site['url']})\n"

        # Footer with last VP time and update info
        footer_parts = []
        if last_vote_party_time:
            footer_parts.append(f"Last VP: {last_vote_party_time}")

        if last_updated and last_scrape_time:
            try:
                dt = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=timezone.utc)
                embed.timestamp = dt
            except ValueError:
                pass

        footer_parts.append(f"Updates every {SCRAPE_INTERVAL_SECONDS}s")

        if footer_parts:
            embed.set_footer(text=" • ".join(footer_parts))
        else:
            embed.set_footer(text=f"⏱️ Updates every {SCRAPE_INTERVAL_SECONDS} seconds")

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

        await self._restore_tracker_message()

        if not self.scrape_loop.is_running():
            self.scrape_loop.start()
            logger.info(f"✓ Scrape loop started (every {SCRAPE_INTERVAL_SECONDS} sec)")

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

    @tasks.loop(seconds=SCRAPE_INTERVAL_SECONDS)
    async def scrape_loop(self):
        """Periodic task: scrape all sites and update the embed."""
        logger.info("Running scheduled scrape...")
        await self._perform_scrape_and_update()
        await self._cleanup_old_ping()

    async def _perform_scrape_and_update(self):
        """Scrape all sites, update data, and edit the embed."""
        try:
            counts, total = await self.scraper.scrape_all()
            baseline = self.bot_data.baseline

            remaining = VOTE_GOAL - (total - baseline)

            if remaining <= 0:
                logger.info(f"🎉 Vote party complete! Total: {total}")
                now = datetime.now(timezone.utc)
                self.bot_data.last_vote_party_time = now.strftime("%Y-%m-%d %H:%M")

                baseline = total
                remaining = VOTE_GOAL
                self.bot_data.baseline = baseline
                self.bot_data.has_ping_sent = False

                self.bot_data.cycle_start_votes = {k: v for k, v in counts.items() if v is not None}
                self.bot_data.vote_history = []

                self.bot_data.ping_message_id = None
                self.bot_data.ping_timestamp = None
                logger.info(f"New cycle started. New baseline: {baseline}")

            now = datetime.now(timezone.utc)
            self.bot_data.remaining = max(0, remaining)
            self.bot_data.site_counts = counts
            self.bot_data.last_updated = now.strftime("%Y-%m-%d %H:%M:%S")
            self.bot_data.last_scrape_time = now.timestamp()

            self.bot_data.vote_history.append({
                "timestamp": now.timestamp(),
                "total": total,
                "counts": counts
            })
            if len(self.bot_data.vote_history) > 100:
                self.bot_data.vote_history = self.bot_data.vote_history[-100:]

            self.bot_data.save()

            await self._update_embed()
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
                vote_history=self.bot_data.vote_history,
                cycle_start_votes=self.bot_data.cycle_start_votes,
                last_vote_party_time=self.bot_data.last_vote_party_time,
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
                        ping_msg = await self.tracker_message.channel.send(
                            f"🚨 **{vp_role.mention}** Only **{remaining}** votes left "
                            f"until the Vote Party! Vote now!\n"
                            f"🔗 https://minecraft-mp.com/server-s349345",
                            allowed_mentions=discord.AllowedMentions(roles=True),
                        )
                        self.bot_data.has_ping_sent = True
                        self.bot_data.ping_message_id = ping_msg.id
                        self.bot_data.ping_timestamp = datetime.now(timezone.utc).timestamp()
                        self.bot_data.save()
                        logger.info(f"🔔 VP role pinged! Remaining: {remaining}")
                    except discord.HTTPException as e:
                        logger.error(f"Failed to send ping: {e}")
                else:
                    logger.warning("VP role not found in guild")

    async def _cleanup_old_ping(self):
        """Delete old ping message if it's been more than PING_DELETE_SECONDS."""
        if not self.bot_data.ping_message_id or not self.bot_data.ping_timestamp:
            return

        now = datetime.now(timezone.utc).timestamp()
        age = now - self.bot_data.ping_timestamp

        if age >= PING_DELETE_SECONDS:
            if self.tracker_message:
                try:
                    channel = self.tracker_message.channel
                    ping_msg = await channel.fetch_message(self.bot_data.ping_message_id)
                    await ping_msg.delete()
                    logger.info(f"🗑️ Deleted old ping message (age: {age:.0f}s)")
                except discord.NotFound:
                    logger.info("Ping message already deleted")
                except discord.HTTPException as e:
                    logger.error(f"Failed to delete ping message: {e}")

            self.bot_data.ping_message_id = None
            self.bot_data.ping_timestamp = None
            self.bot_data.save()


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

        if self.bot.tracker_message:
            try:
                embed = EmbedBuilder.build(
                    remaining=self.bot.bot_data.remaining,
                    site_counts=self.bot.bot_data.site_counts,
                    last_updated=self.bot.bot_data.last_updated,
                    last_scrape_time=self.bot.bot_data.last_scrape_time,
                    vote_history=self.bot.bot_data.vote_history,
                    cycle_start_votes=self.bot.bot_data.cycle_start_votes,
                    last_vote_party_time=self.bot.bot_data.last_vote_party_time,
                )
                view = VoteNotifyView()
                await self.bot.tracker_message.edit(embed=embed, view=view)
                await interaction.followup.send(
                    "✅ Tracker embed updated in place!", ephemeral=True
                )
                return
            except discord.NotFound:
                self.bot.tracker_message = None

        embed = EmbedBuilder.build(
            remaining=self.bot.bot_data.remaining,
            site_counts=self.bot.bot_data.site_counts,
            last_updated=self.bot.bot_data.last_updated,
            last_scrape_time=self.bot.bot_data.last_scrape_time,
            vote_history=self.bot.bot_data.vote_history,
            cycle_start_votes=self.bot.bot_data.cycle_start_votes,
            last_vote_party_time=self.bot.bot_data.last_vote_party_time,
        )
        view = VoteNotifyView()

        message = await channel.send(embed=embed, view=view)

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
        """Manually set the remaining votes and adjust baseline to persist."""
        await interaction.response.defer(ephemeral=True)

        if value < 0 or value > VOTE_GOAL:
            await interaction.followup.send(
                f"❌ Value must be between 0 and {VOTE_GOAL}.",
                ephemeral=True,
            )
            return

        try:
            counts, current_total = await self.bot.scraper.scrape_all()

            progress = VOTE_GOAL - value
            new_baseline = current_total - progress

            self.bot.bot_data.baseline = new_baseline
            self.bot.bot_data.remaining = value
            self.bot.bot_data.site_counts = counts
            self.bot.bot_data.has_ping_sent = False

            now = datetime.now(timezone.utc)
            self.bot.bot_data.last_updated = now.strftime("%Y-%m-%d %H:%M:%S")
            self.bot.bot_data.last_scrape_time = now.timestamp()
            self.bot.bot_data.save()

            await self.bot._update_embed()

            pct = (progress / VOTE_GOAL) * 100

            await interaction.followup.send(
                f"✅ Remaining votes set to **{value}**.\n"
                f"Progress: {progress}/{VOTE_GOAL} ({pct:.1f}%)\n"
                f"Baseline adjusted to **{new_baseline}** to persist.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error: {e}", ephemeral=True
            )

    @voteparty_group.command(
        name="setbaseline",
        description="Set the current total vote sum as the new baseline"
    )
    @app_commands.describe(value="Optional: Set baseline to a specific number instead of current total")
    @app_commands.checks.has_permissions(administrator=True)
    async def setbaseline(self, interaction: discord.Interaction, value: Optional[int] = None):
        """Set the baseline to current total or a specific value."""
        await interaction.response.defer(ephemeral=True)

        try:
            counts, total = await self.bot.scraper.scrape_all()
            now = datetime.now(timezone.utc)

            new_baseline = value if value is not None else total

            self.bot.bot_data.baseline = new_baseline
            self.bot.bot_data.remaining = VOTE_GOAL
            self.bot.bot_data.site_counts = counts
            self.bot.bot_data.has_ping_sent = False
            self.bot.bot_data.last_updated = now.strftime("%Y-%m-%d %H:%M:%S")
            self.bot.bot_data.last_scrape_time = now.timestamp()

            self.bot.bot_data.cycle_start_votes = {k: v for k, v in counts.items() if v is not None}
            self.bot.bot_data.vote_history = []

            self.bot.bot_data.save()

            await self.bot._update_embed()

            if value is not None:
                await interaction.followup.send(
                    f"✅ Baseline manually set to **{new_baseline}**.\n"
                    f"Vote party reset! {VOTE_GOAL} votes to go.",
                    ephemeral=True,
                )
            else:
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
