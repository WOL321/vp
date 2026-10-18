"""
Slash commands for the vote party bot.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from config import VOTE_GOAL
from i18n import t
from embed_builder import EmbedBuilder
from views import VoteNotifyView, LinkView

logger = logging.getLogger("VotePartyBot")


class VotePartyCog(commands.Cog):
    """Cog containing all vote party slash commands."""

    def __init__(self, bot):
        self.bot = bot

    # ─── Admin Commands ───────────────────────────────────────────────────────

    voteparty_group = app_commands.Group(
        name="voteparty",
        description="Vote Party management commands (Admin only)",
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
        lang = self.bot.player_data.get_lang(interaction.user.id)

        if not isinstance(channel, discord.TextChannel):
            await interaction.followup.send(
                t("text_channel_only", lang), ephemeral=True
            )
            return

        # Check if we already have a message
        if self.bot.tracker_message:
            try:
                embed = self._build_embed(lang)
                view = VoteNotifyView(bot=self.bot)
                await self.bot.tracker_message.edit(embed=embed, view=view)
                await interaction.followup.send(
                    "✅ Tracker embed updated in place!", ephemeral=True
                )
                return
            except discord.NotFound:
                self.bot.tracker_message = None

        # Create new message
        embed = self._build_embed(lang)
        view = VoteNotifyView(bot=self.bot)

        message = await channel.send(embed=embed, view=view)

        # Save message reference
        self.bot.tracker_message = message
        self.bot.bot_data.message_id = message.id
        self.bot.bot_data.channel_id = channel.id
        self.bot.bot_data.save()

        await interaction.followup.send(
            t("admin_setup", lang, channel=channel.mention),
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
        lang = self.bot.player_data.get_lang(interaction.user.id)

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
                t("admin_setremaining", lang, value=value, progress=progress,
                  VOTE_GOAL=VOTE_GOAL, pct=f"{pct:.1f}", baseline=new_baseline),
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                t("error_generic", lang, error=str(e)), ephemeral=True
            )

    @voteparty_group.command(
        name="setbaseline",
        description="Set the current total vote sum as the new baseline"
    )
    @app_commands.describe(value="Optional: Set baseline to a specific number")
    @app_commands.checks.has_permissions(administrator=True)
    async def setbaseline(self, interaction: discord.Interaction, value: Optional[int] = None):
        """Set the baseline to current total or a specific value."""
        await interaction.response.defer(ephemeral=True)
        lang = self.bot.player_data.get_lang(interaction.user.id)

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

            # Store cycle start data
            self.bot.bot_data.cycle_start_votes = {k: v for k, v in counts.items() if v is not None}
            self.bot.bot_data.cycle_start_time = now.timestamp()
            self.bot.bot_data.vote_history = []

            # Reset player cycle votes
            self.bot.player_data.reset_cycle()

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
                    t("admin_setbaseline", lang, total=total, VOTE_GOAL=VOTE_GOAL),
                    ephemeral=True,
                )
        except Exception as e:
            await interaction.followup.send(
                t("error_generic", lang, error=str(e)), ephemeral=True
            )

    @voteparty_group.command(
        name="forceupdate",
        description="Force an immediate scrape and update"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def forceupdate(self, interaction: discord.Interaction):
        """Force an immediate scrape and update."""
        await interaction.response.defer(ephemeral=True)
        lang = self.bot.player_data.get_lang(interaction.user.id)

        try:
            await self.bot._perform_scrape_and_update()

            await interaction.followup.send(
                t("admin_forceupdate", lang, remaining=self.bot.bot_data.remaining),
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                t("error_generic", lang, error=str(e)), ephemeral=True
            )

    @voteparty_group.command(
        name="reset",
        description="Reset all vote party progress"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def reset(self, interaction: discord.Interaction):
        """Reset all vote party progress."""
        await interaction.response.defer(ephemeral=True)
        lang = self.bot.player_data.get_lang(interaction.user.id)

        try:
            counts, total = await self.bot.scraper.scrape_all()
            now = datetime.now(timezone.utc)

            self.bot.bot_data.baseline = total
            self.bot.bot_data.remaining = VOTE_GOAL
            self.bot.bot_data.site_counts = counts
            self.bot.bot_data.has_ping_sent = False
            self.bot.bot_data.last_updated = now.strftime("%Y-%m-%d %H:%M:%S")
            self.bot.bot_data.last_scrape_time = now.timestamp()
            self.bot.bot_data.cycle_start_votes = {k: v for k, v in counts.items() if v is not None}
            self.bot.bot_data.cycle_start_time = now.timestamp()
            self.bot.bot_data.vote_history = []

            # Reset player cycle votes
            self.bot.player_data.reset_cycle()

            self.bot.bot_data.save()

            await self.bot._update_embed()

            await interaction.followup.send(
                t("admin_reset", lang), ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                t("error_generic", lang, error=str(e)), ephemeral=True
            )

    # ─── User Commands ────────────────────────────────────────────────────────

    @app_commands.command(
        name="link",
        description="Link your Minecraft username to track your votes"
    )
    @app_commands.describe(ign="Your Minecraft in-game name")
    async def link(self, interaction: discord.Interaction, ign: str):
        """Link your Minecraft username."""
        await interaction.response.defer(ephemeral=True)
        lang = self.bot.player_data.get_lang(interaction.user.id)

        # Validate IGN
        import re
        if not re.match(r'^[a-zA-Z0-9_]{3,16}$', ign):
            await interaction.followup.send(
                t("link_invalid", lang), ephemeral=True
            )
            return

        self.bot.player_data.set_ign(interaction.user.id, ign)

        await interaction.followup.send(
            t("link_success", lang, ign=ign), ephemeral=True
        )

    @app_commands.command(
        name="myvotes",
        description="View your personal vote stats"
    )
    async def myvotes(self, interaction: discord.Interaction):
        """View your personal vote stats."""
        await interaction.response.defer(ephemeral=True)
        lang = self.bot.player_data.get_lang(interaction.user.id)

        player = self.bot.player_data.get_player(interaction.user.id)

        if not player.get("ign"):
            embed = discord.Embed(
                title=t("myvotes_title", lang),
                description=t("myvotes_not_linked", lang),
                color=0xF1C40F,
            )
            view = LinkView(bot=self.bot)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            return

        embed = EmbedBuilder.build_myvotes_embed(player, interaction.user.id, lang)
        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="leaderboard",
        description="View the vote leaderboard"
    )
    @app_commands.describe(
        period="Time period for leaderboard",
    )
    @app_commands.choices(period=[
        app_commands.Choice(name="This Cycle", value="cycle"),
        app_commands.Choice(name="All Time", value="alltime"),
    ])
    async def leaderboard(self, interaction: discord.Interaction, period: Optional[app_commands.Choice[str]] = None):
        """View the vote leaderboard."""
        await interaction.response.defer(ephemeral=True)
        lang = self.bot.player_data.get_lang(interaction.user.id)

        cycle_only = period.value == "cycle" if period else True

        leaderboard = self.bot.player_data.get_leaderboard(limit=10, cycle_only=cycle_only)
        user_rank = self.bot.player_data.get_player_rank(interaction.user.id, cycle_only=cycle_only)

        embed = EmbedBuilder.build_leaderboard_embed(
            leaderboard, interaction.user.id, user_rank,
            cycle_only=cycle_only, lang=lang
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="stats",
        description="View vote party statistics"
    )
    async def stats(self, interaction: discord.Interaction):
        """View vote party statistics."""
        await interaction.response.defer(ephemeral=True)
        lang = self.bot.player_data.get_lang(interaction.user.id)

        embed = EmbedBuilder.build_stats_embed(
            self.bot.stats_data,
            self.bot.bot_data.vote_history,
            self.bot.bot_data.remaining,
            lang=lang,
        )

        await interaction.followup.send(embed=embed, ephemeral=True)

    @app_commands.command(
        name="language",
        description="Set your preferred language"
    )
    @app_commands.describe(lang="Your preferred language")
    @app_commands.choices(lang=[
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Español", value="es"),
    ])
    async def language(self, interaction: discord.Interaction, lang: app_commands.Choice[str]):
        """Set your preferred language."""
        self.bot.player_data.set_lang(interaction.user.id, lang.value)

        lang_name = "English" if lang.value == "en" else "Español"
        await interaction.response.send_message(
            f"✅ Language set to **{lang_name}**!", ephemeral=True
        )

    # ─── Error Handler ────────────────────────────────────────────────────────

    @setup.error
    @setremaining.error
    @setbaseline.error
    @forceupdate.error
    @reset.error
    async def voteparty_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        """Handle errors for admin commands."""
        lang = self.bot.player_data.get_lang(interaction.user.id) if self.bot else "en"

        if isinstance(error, app_commands.MissingPermissions):
            msg = t("admin_only", lang)
        else:
            msg = t("error_generic", lang, error=str(error))

        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)

    # ─── Helper ───────────────────────────────────────────────────────────────

    def _build_embed(self, lang: str = "en") -> discord.Embed:
        """Build the tracker embed with current data."""
        return EmbedBuilder.build(
            remaining=self.bot.bot_data.remaining,
            site_counts=self.bot.bot_data.site_counts,
            last_updated=self.bot.bot_data.last_updated,
            last_scrape_time=self.bot.bot_data.last_scrape_time,
            vote_history=self.bot.bot_data.vote_history,
            cycle_start_votes=self.bot.bot_data.cycle_start_votes,
            cycle_start_time=self.bot.bot_data.cycle_start_time,
            last_vote_party_time=self.bot.bot_data.last_vote_party_time,
            lang=lang,
        )
