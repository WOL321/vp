"""
Persistent views and interactive buttons for the vote party bot.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
import discord
from discord import ui
from config import MAX_VOTES_PER_CYCLE, REMINDER_COOLDOWN, VOTE_SITES
from i18n import t, get_user_lang

logger = logging.getLogger("VotePartyBot")


def format_cooldown(seconds: float) -> str:
    """Format cooldown seconds to human-readable string."""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


class VoteNotifyView(discord.ui.View):
    """
    Persistent view with multiple interactive buttons.
    Survives bot restarts via custom_ids.
    """

    def __init__(self, bot=None):
        super().__init__(timeout=None)
        self.bot = bot

    async def _delete_message_after(self, message, delay: int):
        """Delete a message after a specified delay."""
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except discord.HTTPException:
            pass  # Message already deleted or no permission

    @ui.button(
        label="✅ I Voted!",
        style=discord.ButtonStyle.success,
        custom_id="vote_claim_button",
        row=0,
    )
    async def vote_claim_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Handle 'I Voted' button - claim a vote with cooldown."""
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                t("error_server_only", "en"), ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=False)

        user_id = interaction.user.id
        lang = self.bot.player_data.get_lang(user_id) if self.bot else "en"
        player_data = self.bot.player_data if self.bot else None

        if not player_data:
            await interaction.followup.send(t("error_generic", lang, error="Bot not ready"), ephemeral=True)
            return

        # Check if user has linked their IGN
        ign = player_data.get_ign(user_id)
        if not ign:
            await interaction.followup.send(t("vote_first_link", lang), ephemeral=True)
            return

        # Check if they've reached the cycle limit
        player = player_data.get_player(user_id)
        votes_this_cycle = player.get("votes_this_cycle", 0)

        if votes_this_cycle >= MAX_VOTES_PER_CYCLE:
            await interaction.followup.send(
                f"⚠️ You've already claimed all **{MAX_VOTES_PER_CYCLE}** votes for this cycle!\n"
                f"*Wait for the next vote party to claim more.*",
                ephemeral=True
            )
            return

        # Claim the vote
        updated_player = player_data.claim_vote(user_id)
        total_votes = updated_player["votes_this_cycle"]
        remaining_claims = MAX_VOTES_PER_CYCLE - total_votes
        streak = updated_player.get("streak", 0)

        # Update stats
        if self.bot:
            self.bot.stats_data.add_votes_cast(1)

        # Send public confirmation message
        if streak > 1:
            confirm_msg = f"✅ **{interaction.user.mention}** voted! 🔥 **{streak} day streak!**\n*They now have **{total_votes}/{MAX_VOTES_PER_CYCLE}** votes this cycle*"
        else:
            confirm_msg = f"✅ **{interaction.user.mention}** voted!\n*They now have **{total_votes}/{MAX_VOTES_PER_CYCLE}** votes this cycle*"
        
        if remaining_claims > 0:
            confirm_msg += f"\n💡 *{remaining_claims} vote{'s' if remaining_claims > 1 else ''} remaining*"
        
        # Send message and schedule auto-delete after 30 seconds
        confirm_message = await interaction.followup.send(confirm_msg)
        asyncio.create_task(self._delete_message_after(confirm_message, 30))

        # Update the tracker embed to show the new claimed vote count
        if self.bot and self.bot.tracker_message:
            try:
                from embed_builder import EmbedBuilder
                embed = EmbedBuilder.build(
                    remaining=self.bot.bot_data.remaining,
                    site_counts=self.bot.bot_data.site_counts,
                    last_updated=self.bot.bot_data.last_updated,
                    last_scrape_time=self.bot.bot_data.last_scrape_time,
                    vote_history=self.bot.bot_data.vote_history,
                    cycle_start_votes=self.bot.bot_data.cycle_start_votes,
                    cycle_start_time=self.bot.bot_data.cycle_start_time,
                    last_vote_party_time=self.bot.bot_data.last_vote_party_time,
                    claimed_votes=total_votes,
                    last_voter=interaction.user.display_name,
                )
                await self.bot.tracker_message.edit(embed=embed)
            except Exception as e:
                logger.error(f"Failed to update embed after vote claim: {e}")

    @ui.button(
        label="🔔 Get Notified",
        style=discord.ButtonStyle.primary,
        custom_id="vote_notify_toggle",
        row=0,
    )
    async def notify_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Toggle VP role for notification."""
        member = interaction.user
        if not isinstance(member, discord.Member):
            await interaction.response.send_message(
                t("error_server_only", "en"), ephemeral=True
            )
            return

        lang = self.bot.player_data.get_lang(member.id) if self.bot else "en"

        vp_role = discord.utils.get(interaction.guild.roles, name="VP")
        if not vp_role:
            await interaction.response.send_message(
                t("role_not_found", lang), ephemeral=True
            )
            return

        try:
            if vp_role in member.roles:
                await member.remove_roles(vp_role)
                # Update button label
                button.label = t("btn_notify", lang)
                await interaction.response.send_message(
                    t("notify_off", lang), ephemeral=True
                )
            else:
                await member.add_roles(vp_role)
                button.label = t("btn_stop_notify", lang)
                await interaction.response.send_message(
                    t("notify_on", lang), ephemeral=True
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                t("permission_error", lang), ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.response.send_message(
                t("error_generic", lang, error=str(e)), ephemeral=True
            )

    @ui.button(
        label="📖 How to Vote",
        style=discord.ButtonStyle.secondary,
        custom_id="vote_how_to_button",
        row=1,
    )
    async def how_to_vote_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Show how to vote guide."""
        lang = self.bot.player_data.get_lang(interaction.user.id) if self.bot else "en"

        embed = discord.Embed(
            title=t("how_to_title", lang),
            description=t("how_to_desc", lang),
            color=0x3498DB,
        )

        embed.add_field(name="\u200b", value=t("how_to_step1", lang), inline=False)
        embed.add_field(name="\u200b", value=t("how_to_step2", lang), inline=False)
        embed.add_field(name="\u200b", value=t("how_to_step3", lang), inline=False)
        embed.add_field(name="\u200b", value=t("how_to_step4", lang), inline=False)
        embed.add_field(name="\u200b", value=t("how_to_tip", lang), inline=False)

        # Add vote links
        vote_links = ""
        for i, site in enumerate(VOTE_SITES, 1):
            vote_links += f"{i}. [{site['name']}]({site['url']})\n"
        embed.add_field(name="🔗 Vote Links", value=vote_links, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ui.button(
        label="⏰ Remind Me",
        style=discord.ButtonStyle.secondary,
        custom_id="vote_remind_button",
        row=1,
    )
    async def remind_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Set a reminder to vote later."""
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                t("error_server_only", "en"), ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        lang = self.bot.player_data.get_lang(user_id) if self.bot else "en"

        if not self.bot:
            await interaction.followup.send(t("error_generic", lang, error="Bot not ready"), ephemeral=True)
            return

        # Check reminder cooldown
        existing_reminder = self.bot.player_data.get_reminder(user_id)
        if existing_reminder:
            elapsed = datetime.now(timezone.utc).timestamp() - existing_reminder
            remaining_cooldown = REMINDER_COOLDOWN - elapsed
            if remaining_cooldown > 0:
                time_str = format_cooldown(remaining_cooldown)
                await interaction.followup.send(
                    t("reminder_cooldown", lang, time=time_str), ephemeral=True
                )
                return

        # Set reminder
        reminder_time = datetime.now(timezone.utc).timestamp()
        self.bot.player_data.set_reminder(user_id, reminder_time)

        await interaction.followup.send(
            t("reminder_set", lang), ephemeral=True
        )

    @ui.button(
        label="🏆 Leaderboard",
        style=discord.ButtonStyle.secondary,
        custom_id="vote_leaderboard_button",
        row=2,
    )
    async def leaderboard_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Show the vote leaderboard."""
        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                t("error_server_only", "en"), ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        lang = self.bot.player_data.get_lang(user_id) if self.bot else "en"

        if not self.bot:
            await interaction.followup.send(t("error_generic", lang, error="Bot not ready"), ephemeral=True)
            return

        # Get leaderboard
        leaderboard = self.bot.player_data.get_leaderboard(limit=10, cycle_only=True)
        user_rank = self.bot.player_data.get_player_rank(user_id, cycle_only=True)

        from embed_builder import EmbedBuilder
        embed = EmbedBuilder.build_leaderboard_embed(
            leaderboard, user_id, user_rank, cycle_only=True, lang=lang
        )

        await interaction.followup.send(embed=embed, ephemeral=True)


class LinkModal(discord.ui.Modal, title="Link Your Minecraft Username"):
    """Modal for linking Minecraft IGN."""

    ign = ui.TextInput(
        label="Minecraft Username (IGN)",
        placeholder="e.g. Notch",
        min_length=3,
        max_length=16,
        required=True,
    )

    def __init__(self, bot=None):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        lang = self.bot.player_data.get_lang(interaction.user.id) if self.bot else "en"

        # Validate IGN
        ign = self.ign.value.strip()
        import re
        if not re.match(r'^[a-zA-Z0-9_]{3,16}$', ign):
            await interaction.response.send_message(
                t("link_invalid", lang), ephemeral=True
            )
            return

        # Save IGN
        if self.bot:
            self.bot.player_data.set_ign(interaction.user.id, ign)

        await interaction.response.send_message(
            t("link_success", lang, ign=ign), ephemeral=True
        )


class LinkView(discord.ui.View):
    """View with a button to open the link modal."""

    def __init__(self, bot=None):
        super().__init__(timeout=300)
        self.bot = bot

    @ui.button(
        label="🔗 Link Minecraft Username",
        style=discord.ButtonStyle.primary,
    )
    async def link_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Open the link modal."""
        modal = LinkModal(bot=self.bot)
        await interaction.response.send_modal(modal)
