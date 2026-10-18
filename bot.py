"""
Colombia Vote Party Tracker - Discord Bot (Premium Edition)
============================================================
Production-ready Discord bot for tracking vote party progress
on the Colombia nation (DiplomaticaMC).

Features:
- Premium embed design with multiple visual states
- Auto-scraping every 15 seconds from 3 vote sites
- Persistent single-message editing (never spams)
- Automatic cycle detection and reset at 250 votes
- Role-based notification system with persistent buttons
- Self-reporting vote claims with cooldowns and streaks
- Personal stats and leaderboards
- Full Spanish + English support
- Complete admin slash command suite
- Robust error handling and recovery

Author: Colombia Nation Admin Team
License: MIT
"""

import os
import logging
from datetime import datetime, timezone
from typing import Optional

import discord
from discord.ext import commands, tasks

from config import (
    VOTE_GOAL, SCRAPE_INTERVAL_SECONDS, PING_THRESHOLD,
    PING_DELETE_SECONDS, EmbedState
)
from scraper import VoteScraper
from data_manager import BotData, PlayerData, StatsData
from embed_builder import EmbedBuilder
from views import VoteNotifyView
from commands import VotePartyCog
from i18n import t

# ─── Logging Setup ────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("VotePartyBot")


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

        # Data managers
        self.bot_data = BotData()
        self.player_data = PlayerData()
        self.stats_data = StatsData()

        # Scraper
        self.scraper = VoteScraper()

        # Tracker message reference
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
            logger.info(f"✓ Scrape loop started (every {SCRAPE_INTERVAL_SECONDS} sec)")

        # Start reminder checker
        if not self.reminder_loop.is_running():
            self.reminder_loop.start()
            logger.info("✓ Reminder loop started")

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

                    # Re-attach the view
                    view = VoteNotifyView(bot=self)
                    await self.tracker_message.edit(view=view)
            except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
                logger.warning(f"Could not restore tracker message: {e}")
                self.bot_data.message_id = None
                self.bot_data.channel_id = None

    async def close(self):
        """Cleanup on shutdown."""
        self.scrape_loop.cancel()
        self.reminder_loop.cancel()
        await self.scraper.close()
        await super().close()

    # ─── Periodic Tasks ───────────────────────────────────────────────────────

    @tasks.loop(seconds=SCRAPE_INTERVAL_SECONDS)
    async def scrape_loop(self):
        """Periodic task: scrape all sites and update the embed."""
        logger.info("Running scheduled scrape...")
        await self._perform_scrape_and_update()
        await self._cleanup_old_ping()

    @tasks.loop(minutes=1)
    async def reminder_loop(self):
        """Check and send reminders to users."""
        now = datetime.now(timezone.utc).timestamp()

        for user_id_str, reminder_time in list(self.player_data.data.get("reminders", {}).items()):
            user_id = int(user_id_str)
            elapsed = now - reminder_time

            # Send reminder after 30 minutes
            if elapsed >= 1800:  # 30 minutes
                try:
                    user = await self.fetch_user(user_id)
                    remaining = self.bot_data.remaining

                    if remaining > 0:
                        lang = self.player_data.get_lang(user_id)
                        message = t("reminder_message", lang, remaining=remaining)
                        await user.send(message)
                        logger.info(f"✓ Sent reminder to {user_id}")

                    # Clear reminder
                    self.player_data.clear_reminder(user_id)

                except discord.NotFound:
                    self.player_data.clear_reminder(user_id)
                except discord.Forbidden:
                    logger.warning(f"Cannot send DM to {user_id}")
                    self.player_data.clear_reminder(user_id)
                except Exception as e:
                    logger.error(f"Error sending reminder to {user_id}: {e}")
                    self.player_data.clear_reminder(user_id)

    # ─── Core Logic ───────────────────────────────────────────────────────────

    async def _perform_scrape_and_update(self):
        """Scrape all sites, update data, and edit the embed."""
        try:
            counts, total = await self.scraper.scrape_all()
            baseline = self.bot_data.baseline

            remaining = VOTE_GOAL - (total - baseline)

            # Check if vote party is complete
            if remaining <= 0:
                logger.info(f"🎉 Vote party complete! Total: {total}")

                # Record completion
                now = datetime.now(timezone.utc)
                self.bot_data.last_vote_party_time = now.strftime("%Y-%m-%d %H:%M")

                # Calculate duration
                duration = None
                if self.bot_data.cycle_start_time:
                    duration = now.timestamp() - self.bot_data.cycle_start_time

                # Get top contributors
                leaderboard = self.player_data.get_leaderboard(limit=5, cycle_only=True)
                top_contributors = [
                    {"user_id": uid, "votes": votes}
                    for uid, votes in leaderboard
                ]

                # Record stats
                if duration:
                    self.stats_data.record_party(duration, top_contributors)

                # Reset for next cycle
                baseline = total
                remaining = VOTE_GOAL
                self.bot_data.baseline = baseline
                self.bot_data.has_ping_sent = False

                # Store cycle start data
                self.bot_data.cycle_start_votes = {k: v for k, v in counts.items() if v is not None}
                self.bot_data.cycle_start_time = now.timestamp()
                self.bot_data.vote_history = []

                # Reset player cycle votes
                self.player_data.reset_cycle()

                # Clean up ping
                self.bot_data.ping_message_id = None
                self.bot_data.ping_timestamp = None

                logger.info(f"New cycle started. New baseline: {baseline}")

            # Update stored data
            now = datetime.now(timezone.utc)
            self.bot_data.remaining = max(0, remaining)
            self.bot_data.site_counts = counts
            self.bot_data.last_updated = now.strftime("%Y-%m-%d %H:%M:%S")
            self.bot_data.last_scrape_time = now.timestamp()

            # Add to vote history
            self.bot_data.vote_history.append({
                "timestamp": now.timestamp(),
                "total": total,
                "counts": counts
            })
            if len(self.bot_data.vote_history) > 100:
                self.bot_data.vote_history = self.bot_data.vote_history[-100:]

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
                vote_history=self.bot_data.vote_history,
                cycle_start_votes=self.bot_data.cycle_start_votes,
                cycle_start_time=self.bot_data.cycle_start_time,
                last_vote_party_time=self.bot_data.last_vote_party_time,
            )

            view = VoteNotifyView(bot=self)
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
