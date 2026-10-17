export const mainBotCode = `"""
Colombia Vote Party Tracker - Discord Bot
==========================================
A production-ready Discord bot for tracking vote party progress
on the Colombia nation (DiplomaticaMC).

Scrapes vote counts from 3 Minecraft server list sites every 3 minutes,
tracks progress toward a 250-vote goal, and notifies members when
the party is close.

Author: Colombia Nation Admin Team
License: MIT
"""

import os
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

# Vote list pages to scrape
VOTE_SITES = [
    {
        "name": "Minecraft-MP",
        "url": "https://minecraft-mp.com/server-s349345",
        "selector": "span.badge.bg-success",  # Adjust if HTML changes
    },
    {
        "name": "MinecraftServers.org",
        "url": "https://minecraftservers.org/server/679302",
        "selector": "div.votes-count span",  # Adjust if HTML changes
    },
    {
        "name": "Minecraft-Server-List",
        "url": "https://minecraft-server-list.com/server/513054/vote/",
        "selector": "span.vote-count",  # Adjust if HTML changes
    },
]

DATA_FILE = "bot_data.json"

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
    """Scrapes vote counts from Minecraft server list websites."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        """Initialize the HTTP session."""
        self.session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; VotePartyBot/1.0)",
                "Accept": "text/html,application/xhtml+xml",
            }
        )

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()

    async def scrape_site(self, site: dict) -> tuple[str, Optional[int]]:
        """
        Scrape a single site for its vote count.
        Returns (site_name, vote_count) or (site_name, None) on failure.
        """
        name = site["name"]
        try:
            async with self.session.get(site["url"], timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status != 200:
                    logger.warning(f"{name}: HTTP {resp.status}")
                    return name, None

                html = await resp.text()
                soup = BeautifulSoup(html, "html.parser")

                # Try the configured selector first
                element = soup.select_one(site["selector"])
                if element:
                    text = element.get_text(strip=True)
                    count = self._extract_number(text)
                    if count is not None:
                        logger.info(f"{name}: Found {count} votes")
                        return name, count

                # Fallback: try common patterns
                count = self._try_fallback_patterns(soup, site["url"])
                if count is not None:
                    logger.info(f"{name}: Found {count} votes (fallback)")
                    return name, count

                logger.warning(f"{name}: Could not find vote count element")
                return name, None

        except asyncio.TimeoutError:
            logger.warning(f"{name}: Request timed out")
            return name, None
        except Exception as e:
            logger.error(f"{name}: Scrape error - {e}")
            return name, None

    def _extract_number(self, text: str) -> Optional[int]:
        """Extract an integer from text, handling various formats."""
        import re
        # Remove commas and whitespace, find first number
        cleaned = re.sub(r"[^\\d]", "", text.replace(",", ""))
        if cleaned:
            return int(cleaned)
        return None

    def _try_fallback_patterns(self, soup: BeautifulSoup, url: str) -> Optional[int]:
        """Try alternative selectors if the primary one fails."""
        # Common patterns for vote counts across different sites
        fallback_selectors = [
            "span.votes",
            "div.votes",
            "span[class*='vote']",
            "div[class*='vote']",
            "span[class*='count']",
            "a[href*='vote']",
        ]

        for selector in fallback_selectors:
            elements = soup.select(selector)
            for el in elements:
                text = el.get_text(strip=True)
                count = self._extract_number(text)
                if count is not None and count > 0:
                    return count
        return None

    async def scrape_all(self) -> tuple[dict[str, Optional[int]], int]:
        """
        Scrape all configured sites and return results.
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

        return counts, total


# ─── Embed Builder ────────────────────────────────────────────────────────────


class EmbedBuilder:
    """Builds the persistent tracker embed."""

    @staticmethod
    def build(
        remaining: int,
        site_counts: dict[str, Optional[int]],
        last_updated: Optional[str],
    ) -> discord.Embed:
        """Build the vote party tracker embed."""
        progress = max(0, VOTE_GOAL - remaining)
        percentage = min(100, max(0, (progress / VOTE_GOAL) * 100))

        # Build progress bar (20 blocks)
        filled = int(percentage / 5)
        empty = 20 - filled
        bar = "█" * filled + "░" * empty

        # Determine color based on progress
        if percentage >= 80:
            color = 0x00FF00  # Green - almost done!
        elif percentage >= 50:
            color = 0xFFAA00  # Orange - halfway
        else:
            color = 0x5865F2  # Discord blurple

        embed = discord.Embed(
            title="🇨🇴 Colombia Vote Party Tracker",
            description=f"**{remaining}** votes remaining to reach **{VOTE_GOAL}**!",
            color=color,
            timestamp=datetime.now(timezone.utc),
        )

        # Progress bar
        embed.add_field(
            name="📊 Progress",
            value=f"\`{bar}\` **{percentage:.1f}%** ({progress}/{VOTE_GOAL})",
            inline=False,
        )

        # Individual site counts
        site_lines = []
        for site in VOTE_SITES:
            name = site["name"]
            count = site_counts.get(name)
            if count is not None:
                site_lines.append(f"• **{name}**: {count} votes")
            else:
                site_lines.append(f"• **{name}**: ⚠️ Unavailable")

        embed.add_field(
            name="🗳️ Vote Sites",
            value="\\n".join(site_lines),
            inline=False,
        )

        # Vote links
        links = "\\n".join([f"• [{site['name']}]({site['url']})" for site in VOTE_SITES])
        embed.add_field(
            name="🔗 Vote Now!",
            value=links,
            inline=False,
        )

        # Last updated
        if last_updated:
            embed.set_footer(text=f"Last updated: {last_updated} UTC")
        else:
            embed.set_footer(text="Waiting for first update...")

        return embed


# ─── Bot Setup ────────────────────────────────────────────────────────────────


class VotePartyBot(commands.Bot):
    """Main bot class with vote party tracking functionality."""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(
            command_prefix="!",  # Only for fallback, we use slash commands
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
        # Sync slash commands globally
        await self.tree.sync()
        logger.info("Slash commands synced.")

    async def on_ready(self):
        """Called when the bot is fully connected."""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")

        # Try to fetch the existing tracker message
        await self._restore_tracker_message()

        # Start the periodic scraping loop
        if not self.scrape_loop.is_running():
            self.scrape_loop.start()

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
                    logger.info(f"Restored tracker message {msg_id} in channel {ch_id}")
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

            # Calculate remaining
            remaining = VOTE_GOAL - (total - baseline)

            # Check if vote party is complete
            if remaining <= 0:
                logger.info(f"Vote party complete! Total: {total}, Baseline: {baseline}")
                # Reset for next cycle
                baseline = total
                remaining = VOTE_GOAL
                self.bot_data.baseline = baseline
                self.bot_data.has_ping_sent = False
                logger.info(f"New cycle started. New baseline: {baseline}")

            self.bot_data.remaining = max(0, remaining)
            self.bot_data.site_counts = counts
            self.bot_data.last_updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
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

            # Build the view with button
            view = VoteNotifyView()

            await self.tracker_message.edit(embed=embed, view=view)
            logger.info("Tracker embed updated successfully")

        except discord.HTTPException as e:
            logger.error(f"Failed to update embed: {e}")

    async def _check_ping(self):
        """Check if we should ping the VP role."""
        remaining = self.bot_data.remaining

        if remaining <= PING_THRESHOLD and not self.bot_data.has_ping_sent:
            if self.tracker_message and self.tracker_message.guild:
                vp_role = discord.utils.get(
                    self.tracker_message.guild.roles, name="VP"
                )
                if vp_role:
                    try:
                        await self.tracker_message.channel.send(
                            f"🚨 **{vp_role.mention}** Only **{remaining}** votes left until the Vote Party! "
                            f"Vote now: https://minecraft-mp.com/server-s349345",
                            allowed_mentions=discord.AllowedMentions(roles=True),
                        )
                        self.bot_data.has_ping_sent = True
                        self.bot_data.save()
                        logger.info(f"VP role pinged! Remaining: {remaining}")
                    except discord.HTTPException as e:
                        logger.error(f"Failed to send ping: {e}")
                else:
                    logger.warning("VP role not found in guild")


# ─── View (Button) ───────────────────────────────────────────────────────────


class VoteNotifyView(discord.ui.View):
    """View containing the notification toggle button."""

    def __init__(self):
        super().__init__(timeout=None)  # Persistent view

    @discord.ui.button(
        label="🔔 Get Notified",
        style=discord.ButtonStyle.primary,
        custom_id="vote_notify_toggle",
    )
    async def notify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle the VP role for the clicking user."""
        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message(
                "❌ This can only be used in a server.", ephemeral=True
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
                    f"✅ You will no longer be notified for vote party updates.",
                    ephemeral=True,
                )
            else:
                await member.add_roles(vp_role)
                await interaction.response.send_message(
                    f"✅ You will now be notified when the vote party is close!",
                    ephemeral=True,
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don't have permission to manage roles. Please ensure my role is above the VP role.",
                ephemeral=True,
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                f"❌ An error occurred: {e}", ephemeral=True
            )


# ─── Slash Commands ───────────────────────────────────────────────────────────


class VotePartyCog(commands.Cog):
    """Cog containing all vote party slash commands."""

    def __init__(self, bot: VotePartyBot):
        self.bot = bot

    @app_commands.command(name="voteparty", description="Vote Party management commands")
    @app_commands.describe(
        action="The action to perform",
        value="Value for setremaining (number of votes remaining)",
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="setup - Post/update tracker", value="setup"),
            app_commands.Choice(name="setremaining - Set remaining votes", value="setremaining"),
            app_commands.Choice(name="setbaseline - Set current sum as baseline", value="setbaseline"),
            app_commands.Choice(name="forceupdate - Force immediate scrape", value="forceupdate"),
        ]
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def voteparty(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        value: Optional[int] = None,
    ):
        """Vote Party management command (Administrator only)."""
        await interaction.response.defer(ephemeral=True)

        if action.value == "setup":
            await self._setup_tracker(interaction)
        elif action.value == "setremaining":
            await self._set_remaining(interaction, value)
        elif action.value == "setbaseline":
            await self._set_baseline(interaction)
        elif action.value == "forceupdate":
            await self._force_update(interaction)

    async def _setup_tracker(self, interaction: discord.Interaction):
        """Post or update the tracker embed in the current channel."""
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

    async def _set_remaining(self, interaction: discord.Interaction, value: Optional[int]):
        """Manually set the remaining votes."""
        if value is None:
            await interaction.followup.send(
                "❌ Please provide a number for the remaining votes.\\n"
                "Usage: /voteparty action:setremaining value:<number>",
                ephemeral=True,
            )
            return

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

        await interaction.followup.send(
            f"✅ Remaining votes set to **{value}**.\\n"
            f"Progress: {VOTE_GOAL - value}/{VOTE_GOAL} ({((VOTE_GOAL - value) / VOTE_GOAL) * 100:.1f}%)",
            ephemeral=True,
        )

    async def _set_baseline(self, interaction: discord.Interaction):
        """Set the current total sum as the new baseline."""
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

            await interaction.followup.send(
                f"✅ New baseline set to **{total}**.\\n"
                f"Vote party reset! {VOTE_GOAL} votes to go.\\n"
                f"Site counts: {', '.join(f'{k}: {v}' for k, v in counts.items())}",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error scraping sites: {e}", ephemeral=True
            )

    async def _force_update(self, interaction: discord.Interaction):
        """Force an immediate scrape and update."""
        await interaction.followup.send("⏳ Scraping all sites...", ephemeral=True)

        try:
            await self.bot._perform_scrape_and_update()
            await interaction.followup.send(
                f"✅ Update complete!\\n"
                f"Remaining: **{self.bot.bot_data.remaining}** votes\\n"
                f"Site counts: {', '.join(f'{k}: {v}' for k, v in self.bot.bot_data.site_counts.items())}",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error during update: {e}", ephemeral=True
            )

    @voteparty.error
    async def voteparty_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        """Handle errors for the voteparty command."""
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
        logger.error("DISCORD_BOT_TOKEN environment variable not set!")
        logger.error("Please set it: export DISCORD_BOT_TOKEN='your_token_here'")
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

export const envExample = `# Discord Bot Token (get from https://discord.com/developers/applications)
DISCORD_BOT_TOKEN=your_bot_token_here
`;

export const setupInstructions = `# Colombia Vote Party Bot - Setup Guide

## Prerequisites
- Python 3.10 or higher
- A Discord account with Administrator permissions on your server
- A Discord Bot Application

## Step 1: Create a Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application" and name it (e.g., "Colombia Vote Party")
3. Go to the "Bot" tab in the left sidebar
4. Click "Add Bot" → "Yes, do it"
5. Under "Privileged Gateway Intents", enable:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
6. Copy the **Bot Token** (keep this secret!)

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
   - ✅ Use Slash Commands
4. Copy the generated URL and open it in your browser
5. Select your server and authorize

## Step 3: Create the VP Role

1. In your Discord server, go to Server Settings → Roles
2. Create a new role named exactly: **VP**
3. Set its color and permissions as desired
4. **Important**: Make sure the bot's role is ABOVE the VP role in the role hierarchy

## Step 4: Install and Run

\`\`\`bash
# Clone or download the bot files
cd colombia-vote-party-bot

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt

# Set your bot token
export DISCORD_BOT_TOKEN='your_token_here'
# On Windows: set DISCORD_BOT_TOKEN=your_token_here

# Run the bot
python bot.py
\`\`\`

## Step 5: Initialize the Tracker

1. In your Discord server, go to the channel where you want the tracker
2. Run: \`/voteparty action:setup\`
3. The tracker embed will appear with the 🔔 Get Notified button

## Commands Reference

| Command | Description | Permission |
|---------|-------------|------------|
| \`/voteparty action:setup\` | Post/update the tracker embed | Administrator |
| \`/voteparty action:setremaining value:<number>\` | Manually set remaining votes | Administrator |
| \`/voteparty action:setbaseline\` | Reset baseline to current total | Administrator |
| \`/voteparty action:forceupdate\` | Force immediate scrape & update | Administrator |

## How It Works

1. **Every 3 minutes**, the bot scrapes vote counts from all 3 sites
2. It **sums the totals** and compares against the baseline
3. **Remaining = 250 - (current_sum - baseline)**
4. When remaining reaches 0, it **automatically resets** for a new cycle
5. When remaining ≤ 30, it **pings the VP role** (once per cycle)
6. Members click **🔔 Get Notified** to toggle the VP role

## Troubleshooting

- **"VP role not found"**: Make sure a role named exactly "VP" exists
- **Site counts show "Unavailable"**: The site may be down or changed their HTML
- **Bot can't manage roles**: Check role hierarchy - bot role must be above VP role
- **Commands not showing**: Wait a few minutes for Discord to sync slash commands

## File Structure

\`\`\`
colombia-vote-party-bot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── bot_data.json       # Auto-generated persistence file
└── README.md           # This file
\`\`\`
`;
