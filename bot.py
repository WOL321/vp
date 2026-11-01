"""
Nariño Bot - The Ultimate Colombia Nation Bot
Named after Antonio Nariño - Colombian independence leader
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

import discord
from discord.ext import commands, tasks

from config import (
    BOT_NAME, BOT_VERSION, BOT_COLOR,
    VOTE_GOAL, SCRAPE_INTERVAL_SECONDS, PING_THRESHOLD,
    PING_DELETE_SECONDS, MAX_VOTES_PER_CYCLE,
    NATION_MEMBER_ROLE, ALLY_ROLE, VP_ROLE, VERIFIED_ROLE,
    TICKET_CATEGORY_NAME, TICKET_STAFF_ROLE,
    COLOR_GOLD, COLOR_BLUE, COLOR_RED,
    # DiplomaticaMC specific
    STARTING_GOLD, VOTE_REWARD_GOLD, DAILY_REWARD_GOLD, WORK_REWARD_GOLD,
    TOWN_CREATION_COST, NATION_CREATION_COST, TOWN_CLAIM_COST,
    INACTIVITY_WARNING_DAYS, INACTIVITY_DELETION_DAYS
)
from core.i18n import i18n
from core.data_manager import data_manager
from vote.scraper import AdvancedVoteScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("Nariño")

class NariñoBot(commands.Bot):
    """The ultimate Colombia nation bot"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.reactions = True
        
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            activity=discord.Activity(type=discord.ActivityType.watching, name="over Colombia 🇨🇴")
        )
        
        # Core systems
        self.scraper = AdvancedVoteScraper()
        self.vote_history = []
        self.tracker_message = None
        
        # Vote party state
        self.baseline = 0
        self.remaining = VOTE_GOAL
        self.site_counts = {}
        self.last_updated = None
        self.has_ping_sent = False
        self.ping_message_id = None
        self.ping_timestamp = None
        self.cycle_start_votes = {}
        self.cycle_start_time = None
        self.last_vote_party_time = None
        
        # Player data
        self.player_votes = {}  # user_id -> votes_this_cycle
        self.player_cooldowns = {}  # user_id -> last_claim_time
        self.player_streaks = {}  # user_id -> streak_count
        self.player_igns = {}  # user_id -> minecraft_ign
    
    async def setup_hook(self):
        """Called when bot is starting up"""
        await self.scraper.start()
        await self.load_cogs()
        await self.tree.sync()
        logger.info("Slash commands synced globally.")
    
    async def load_cogs(self):
        """Load all cogs"""
        # Vote party cog
        await self.add_cog(VotePartyCog(self))
        
        # Nation features cog
        await self.add_cog(NationCog(self))
        
        # Welcome cog
        await self.add_cog(WelcomeCog(self))
        
        # Economy cog (Gold Standard)
        await self.add_cog(EconomyCog(self))
        
        # Diplomacy cog
        await self.add_cog(DiplomacyCog(self))
        
        # Towny cog (DiplomaticaMC integration)
        await self.add_cog(TownyCog(self))
        
        # SiegeWar cog
        await self.add_cog(SiegeWarCog(self))
        
        # Inactivity cog
        await self.add_cog(InactivityCog(self))
        
        # Fun cog
        await self.add_cog(FunCog(self))
        
        logger.info("All cogs loaded successfully.")
    
    async def on_ready(self):
        """Called when bot is fully connected"""
        logger.info(f"✓ Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"✓ Connected to {len(self.guilds)} guild(s)")
        logger.info(f"✓ {BOT_NAME} v{BOT_VERSION} is ready!")
        
        # Restore vote party state
        await self._restore_vote_state()
        
        # Start periodic tasks
        if not self.scrape_loop.is_running():
            self.scrape_loop.start()
            logger.info(f"✓ Scrape loop started (every {SCRAPE_INTERVAL_SECONDS} sec)")
        
        if not self.reminder_loop.is_running():
            self.reminder_loop.start()
            logger.info("✓ Reminder loop started")
    
    async def _restore_vote_state(self):
        """Restore vote party state from data"""
        self.baseline = data_manager.get("vote_state", "baseline", 0)
        self.remaining = data_manager.get("vote_state", "remaining", VOTE_GOAL)
        self.site_counts = data_manager.get("vote_state", "site_counts", {})
        self.last_updated = data_manager.get("vote_state", "last_updated")
        self.has_ping_sent = data_manager.get("vote_state", "has_ping_sent", False)
        self.cycle_start_votes = data_manager.get("vote_state", "cycle_start_votes", {})
        self.cycle_start_time = data_manager.get("vote_state", "cycle_start_time")
        self.last_vote_party_time = data_manager.get("vote_state", "last_vote_party_time")
        
        # Restore player data
        self.player_votes = data_manager.get("player_data", "votes", {})
        self.player_cooldowns = data_manager.get("player_data", "cooldowns", {})
        self.player_streaks = data_manager.get("player_data", "streaks", {})
        self.player_igns = data_manager.get("player_data", "igns", {})
        
        # Restore tracker message
        msg_id = data_manager.get("vote_state", "message_id")
        ch_id = data_manager.get("vote_state", "channel_id")
        
        if msg_id and ch_id:
            try:
                channel = self.get_channel(ch_id) or await self.fetch_channel(ch_id)
                if channel:
                    self.tracker_message = await channel.fetch_message(msg_id)
                    logger.info(f"✓ Restored tracker message {msg_id}")
            except Exception as e:
                logger.warning(f"Could not restore tracker message: {e}")
    
    async def close(self):
        """Cleanup on shutdown"""
        self.scrape_loop.cancel()
        self.reminder_loop.cancel()
        await self.scraper.close()
        await data_manager.save_all()
        await super().close()
    
    # ─── Periodic Tasks ───────────────────────────────────────────────────────
    
    @tasks.loop(seconds=SCRAPE_INTERVAL_SECONDS)
    async def scrape_loop(self):
        """Periodic vote scraping"""
        logger.info("Running scheduled scrape...")
        await self._perform_scrape_and_update()
        await self._cleanup_old_ping()
    
    @tasks.loop(minutes=1)
    async def reminder_loop(self):
        """Check and send reminders"""
        # TODO: Implement reminder system
        pass
    
    # ─── Vote Party Logic ─────────────────────────────────────────────────────
    
    async def _perform_scrape_and_update(self):
        """Scrape all sites and update the embed"""
        try:
            counts, total = await self.scraper.scrape_all()
            
            # Validate we got data
            successful_sites = sum(1 for v in counts.values() if v is not None)
            total_sites = len(counts)
            
            if successful_sites == 0:
                logger.warning("⚠️ All sites failed - keeping previous data")
                return
            
            if successful_sites < total_sites:
                logger.warning(f"⚠️ Only {successful_sites}/{total_sites} sites returned data")
                for site_name, count in counts.items():
                    if count is None and site_name in self.scraper.last_successful_counts:
                        counts[site_name] = self.scraper.last_successful_counts[site_name]
                
                total = sum(v for v in counts.values() if v is not None)
            
            baseline = self.baseline
            
            # First run - set baseline
            if baseline == 0 and self.last_updated is None:
                logger.info(f"🔧 First run - setting baseline to {total}")
                baseline = total
                self.baseline = baseline
                data_manager.set("vote_state", "baseline", baseline)
            
            remaining = VOTE_GOAL - (total - baseline)
            
            # Sanity check
            if remaining < 0 or remaining > VOTE_GOAL * 2:
                logger.error(f"❌ Invalid remaining value: {remaining}")
                baseline = total
                self.baseline = baseline
                remaining = VOTE_GOAL
                data_manager.set("vote_state", "baseline", baseline)
            
            # Check if vote party is complete
            if remaining <= 0:
                logger.info(f"🎉 Vote party complete! Total: {total}")
                await self._handle_vote_party_complete(total)
            
            # Update state
            now = datetime.now(timezone.utc)
            self.remaining = max(0, remaining)
            self.site_counts = counts
            self.last_updated = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # Add to history
            self.vote_history.append({
                "timestamp": now.timestamp(),
                "total": total,
                "counts": counts
            })
            if len(self.vote_history) > 100:
                self.vote_history = self.vote_history[-100:]
            
            # Save state
            self._save_vote_state()
            
            # Update embed
            await self._update_embed()
            
            # Check ping
            await self._check_ping()
            
        except Exception as e:
            logger.error(f"Scrape loop error: {e}", exc_info=True)
    
    async def _handle_vote_party_complete(self, total: int):
        """Handle vote party completion"""
        now = datetime.now(timezone.utc)
        self.last_vote_party_time = now.strftime("%Y-%m-%d %H:%M")
        
        # Calculate duration
        duration = None
        if self.cycle_start_time:
            duration = now.timestamp() - self.cycle_start_time
        
        # Get top contributors
        top_contributors = sorted(
            self.player_votes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Record stats
        if duration:
            data_manager.append("stats", "completion_times", duration)
            data_manager.increment("stats", "parties_completed")
        
        # Reset for next cycle
        self.baseline = total
        self.remaining = VOTE_GOAL
        self.has_ping_sent = False
        self.cycle_start_votes = {k: v for k, v in self.site_counts.items() if v is not None}
        self.cycle_start_time = now.timestamp()
        self.vote_history = []
        
        # Reset player votes
        self.player_votes = {}
        
        # Clean up ping
        self.ping_message_id = None
        self.ping_timestamp = None
        
        logger.info(f"New cycle started. New baseline: {self.baseline}")
    
    def _save_vote_state(self):
        """Save vote state to data"""
        data_manager.set("vote_state", "baseline", self.baseline)
        data_manager.set("vote_state", "remaining", self.remaining)
        data_manager.set("vote_state", "site_counts", self.site_counts)
        data_manager.set("vote_state", "last_updated", self.last_updated)
        data_manager.set("vote_state", "has_ping_sent", self.has_ping_sent)
        data_manager.set("vote_state", "cycle_start_votes", self.cycle_start_votes)
        data_manager.set("vote_state", "cycle_start_time", self.cycle_start_time)
        data_manager.set("vote_state", "last_vote_party_time", self.last_vote_party_time)
        
        # Save player data
        data_manager.set("player_data", "votes", self.player_votes)
        data_manager.set("player_data", "cooldowns", self.player_cooldowns)
        data_manager.set("player_data", "streaks", self.player_streaks)
        data_manager.set("player_data", "igns", self.player_igns)
    
    async def _update_embed(self):
        """Update the tracker embed"""
        if not self.tracker_message:
            return
        
        try:
            embed = self._build_vote_embed()
            view = VoteNotifyView(self)
            await self.tracker_message.edit(embed=embed, view=view)
            logger.info("Tracker embed updated successfully")
        except Exception as e:
            logger.error(f"Failed to update embed: {e}")
    
    def _build_vote_embed(self) -> discord.Embed:
        """Build the vote party embed"""
        progress = max(0, VOTE_GOAL - self.remaining)
        percentage = min(100, max(0, (progress / VOTE_GOAL) * 100))
        
        # Determine color
        if self.remaining <= 0:
            color = COLOR_GOLD
        elif self.remaining <= PING_THRESHOLD:
            color = COLOR_RED
        elif self.remaining <= 50:
            color = COLOR_BLUE
        else:
            color = COLOR_GOLD
        
        # Build progress bar
        filled = int(percentage / 10)
        bar = "🟨" * filled + "⬜" * (10 - filled)
        
        # Status message
        if self.remaining <= 0:
            status = "🎉 **Vote Party Complete!**"
        elif self.remaining <= 10:
            status = "🔥 **Almost there! Party imminent!**"
        elif self.remaining <= 30:
            status = "⚡ **Getting close! Notify the server!**"
        elif self.remaining <= 100:
            status = "💪 **Good progress! Keep it up!**"
        else:
            status = "🗳️ **Vote party in progress**"
        
        embed = discord.Embed(
            title="🇨🇴 Colombia Vote Party",
            description="",
            color=color
        )
        
        # Build description
        if self.remaining <= 0:
            embed.description = (
                f"🎉 **Vote Party Complete!**\n"
                f"Starting new cycle...\n\n"
                f"{bar} 100.0%\n"
                f"{VOTE_GOAL} / {VOTE_GOAL} votes collected"
            )
        else:
            embed.description = (
                f"**{self.remaining}** votes remaining\n"
                f"{bar} {percentage:.1f}%\n"
                f"{progress} / {VOTE_GOAL} votes collected\n\n"
                f"{status}"
            )
        
        # Add separator
        embed.description += "\n\n━━━━━━━━━━━━━━━━━━━━\n"
        embed.description += "🗳️ **Vote Counts**\n"
        
        # Site votes
        site_emojis = ["🟡", "🔵", "🔴"]
        for i, site in enumerate(VOTE_SITES):
            name = site["name"]
            count = self.site_counts.get(name)
            emoji = site_emojis[i % len(site_emojis)]
            
            if count is not None:
                contribution = None
                if name in self.cycle_start_votes:
                    contribution = count - self.cycle_start_votes[name]
                
                if contribution and contribution > 0:
                    embed.description += f"{emoji} {name} — **{count:,}** (+{contribution})\n"
                else:
                    embed.description += f"{emoji} {name} — **{count:,}**\n"
            else:
                embed.description += f"{emoji} {name} — ⚠️ Unavailable\n"
        
        # Claimed votes
        total_claimed = sum(self.player_votes.values())
        if total_claimed > 0:
            embed.description += f"\n🗳️ **Claimed this cycle:** {total_claimed} votes ({MAX_VOTES_PER_CYCLE} per player)\n"
        
        # Vote links
        embed.description += "🔗 **Vote Now!**\n"
        embed.description += "━━━━━━━━━━━━━━━━\n"
        for i, site in enumerate(VOTE_SITES, 1):
            embed.description += f"{i}. [Vote on {site['name']}]({site['url']})\n"
        
        # Footer
        footer_parts = []
        if self.last_vote_party_time:
            footer_parts.append(f"Last VP: {self.last_vote_party_time}")
        footer_parts.append(f"Updates every {SCRAPE_INTERVAL_SECONDS}s")
        
        embed.set_footer(text=" • ".join(footer_parts))
        
        return embed
    
    async def _check_ping(self):
        """Check if we should ping the VP role"""
        if self.remaining <= PING_THRESHOLD and not self.has_ping_sent:
            if self.tracker_message and self.tracker_message.guild:
                vp_role = discord.utils.get(self.tracker_message.guild.roles, name=VP_ROLE)
                if vp_role:
                    try:
                        ping_msg = await self.tracker_message.channel.send(
                            f"🚨 **{vp_role.mention}** Only **{self.remaining}** votes left until the Vote Party! Vote now!",
                            allowed_mentions=discord.AllowedMentions(roles=True)
                        )
                        self.has_ping_sent = True
                        self.ping_message_id = ping_msg.id
                        self.ping_timestamp = datetime.now(timezone.utc).timestamp()
                        self._save_vote_state()
                        logger.info(f"🔔 VP role pinged! Remaining: {self.remaining}")
                    except Exception as e:
                        logger.error(f"Failed to send ping: {e}")
    
    async def _cleanup_old_ping(self):
        """Delete old ping message"""
        if not self.ping_message_id or not self.ping_timestamp:
            return
        
        now = datetime.now(timezone.utc).timestamp()
        age = now - self.ping_timestamp
        
        if age >= PING_DELETE_SECONDS:
            if self.tracker_message:
                try:
                    channel = self.tracker_message.channel
                    ping_msg = await channel.fetch_message(self.ping_message_id)
                    await ping_msg.delete()
                    logger.info(f"🗑️ Deleted old ping message")
                except Exception:
                    pass
            
            self.ping_message_id = None
            self.ping_timestamp = None
            self._save_vote_state()

# ─── Cogs ─────────────────────────────────────────────────────────────────────

class VotePartyCog(commands.Cog):
    """Vote party commands"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle button interactions"""
        if interaction.type != discord.InteractionType.component:
            return
        
        custom_id = interaction.data.get("custom_id")
        
        if custom_id == "vote_claim_button":
            await self._handle_vote_claim(interaction)
        elif custom_id == "vote_notify_toggle":
            await self._handle_notify_toggle(interaction)
    
    async def _handle_vote_claim(self, interaction: discord.Interaction):
        """Handle vote claim button"""
        user_id = interaction.user.id
        
        # Check if user has linked IGN
        if user_id not in self.bot.player_igns:
            await interaction.response.send_message(
                "🔗 Please link your Minecraft username first using `/link`.",
                ephemeral=True
            )
            return
        
        # Check cooldown
        last_claim = self.bot.player_cooldowns.get(user_id, 0)
        now = datetime.now(timezone.utc).timestamp()
        
        if now - last_claim < 3600:  # 1 hour cooldown
            remaining = int(3600 - (now - last_claim))
            await interaction.response.send_message(
                f"⏳ You can claim another vote in **{remaining // 60}m**.",
                ephemeral=True
            )
            return
        
        # Check cycle limit
        votes_this_cycle = self.bot.player_votes.get(user_id, 0)
        if votes_this_cycle >= MAX_VOTES_PER_CYCLE:
            await interaction.response.send_message(
                f"⚠️ You've already claimed all **{MAX_VOTES_PER_CYCLE}** votes for this cycle!",
                ephemeral=True
            )
            return
        
        # Claim the vote
        self.bot.player_votes[user_id] = votes_this_cycle + 1
        self.bot.player_cooldowns[user_id] = now
        
        # Update streak
        self.bot.player_streaks[user_id] = self.bot.player_streaks.get(user_id, 0) + 1
        
        self.bot._save_vote_state()
        
        # Send confirmation
        total_votes = self.bot.player_votes[user_id]
        streak = self.bot.player_streaks[user_id]
        
        if streak > 1:
            msg = f"✅ **{interaction.user.mention}** voted! 🔥 **{streak} vote streak!**\n*They now have **{total_votes}/{MAX_VOTES_PER_CYCLE}** votes this cycle*"
        else:
            msg = f"✅ **{interaction.user.mention}** voted!\n*They now have **{total_votes}/{MAX_VOTES_PER_CYCLE}** votes this cycle*"
        
        confirm_msg = await interaction.response.send_message(msg)
        
        # Auto-delete after 1 second
        asyncio.create_task(self._delete_after(confirm_msg, 1))
        
        # Update embed
        await self.bot._update_embed()
    
    async def _handle_notify_toggle(self, interaction: discord.Interaction):
        """Handle notification toggle"""
        member = interaction.user
        vp_role = discord.utils.get(interaction.guild.roles, name=VP_ROLE)
        
        if not vp_role:
            await interaction.response.send_message(
                "❌ The 'VP' role was not found.",
                ephemeral=True
            )
            return
        
        try:
            if vp_role in member.roles:
                await member.remove_roles(vp_role)
                await interaction.response.send_message(
                    "✅ You will **no longer** be notified for vote party updates.",
                    ephemeral=True
                )
            else:
                await member.add_roles(vp_role)
                await interaction.response.send_message(
                    "✅ You will now be **notified** when the vote party is close!",
                    ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {e}",
                ephemeral=True
            )
    
    async def _delete_after(self, message, delay: int):
        """Delete message after delay"""
        await asyncio.sleep(delay)
        try:
            await message.delete()
        except:
            pass
    
    @discord.app_commands.command(name="link", description="Link your Minecraft username")
    @discord.app_commands.describe(ign="Your Minecraft in-game name")
    async def link(self, interaction: discord.Interaction, ign: str):
        """Link Minecraft username"""
        import re
        
        if not re.match(r'^[a-zA-Z0-9_]{3,16}$', ign):
            await interaction.response.send_message(
                "❌ Invalid username. Minecraft usernames are 3-16 characters (letters, numbers, underscores).",
                ephemeral=True
            )
            return
        
        self.bot.player_igns[interaction.user.id] = ign
        self.bot._save_vote_state()
        
        await interaction.response.send_message(
            f"✅ Linked your Minecraft username to **{ign}**!",
            ephemeral=True
        )
    
    @discord.app_commands.command(name="myvotes", description="View your vote stats")
    async def myvotes(self, interaction: discord.Interaction):
        """View personal vote stats"""
        user_id = interaction.user.id
        
        ign = self.bot.player_igns.get(user_id)
        if not ign:
            await interaction.response.send_message(
                "🔗 You haven't linked your Minecraft username yet!\nUse `/link` to get started.",
                ephemeral=True
            )
            return
        
        votes_this_cycle = self.bot.player_votes.get(user_id, 0)
        streak = self.bot.player_streaks.get(user_id, 0)
        
        embed = discord.Embed(
            title="🗳️ Your Vote Stats",
            description=f"🎮 **{ign}**\n\n",
            color=COLOR_GOLD
        )
        
        embed.description += f"📊 **This Cycle:** {votes_this_cycle}/{MAX_VOTES_PER_CYCLE}\n"
        embed.description += f"🔥 **Current Streak:** {streak} votes\n"
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.app_commands.command(name="leaderboard", description="View vote leaderboard")
    async def leaderboard(self, interaction: discord.Interaction):
        """View vote leaderboard"""
        sorted_votes = sorted(
            self.bot.player_votes.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title="🏆 Vote Leaderboard - This Cycle",
            description="",
            color=COLOR_GOLD
        )
        
        if not sorted_votes:
            embed.description = "No votes claimed yet. Be the first!"
        else:
            for rank, (user_id, votes) in enumerate(sorted_votes, 1):
                ign = self.bot.player_igns.get(user_id, "Unknown")
                embed.description += f"**#{rank}** {ign} — **{votes}** votes\n"
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class NationCog(commands.Cog):
    """Nation management commands"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
    
    @discord.app_commands.command(name="role-request", description="Request a nation role")
    async def role_request(self, interaction: discord.Interaction):
        """Show role request panel"""
        embed = discord.Embed(
            title="🇨🇴 Colombia Role Requests",
            description=(
                "Choose a role below. Citizenship and Ally requests go to leadership review. "
                "Vote Party Pings can be toggled instantly.\n\n"
                "**Request format:**\n"
                "Minecraft username · Nation · Town · Nation role"
            ),
            color=COLOR_GOLD
        )
        
        view = RoleRequestView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class WelcomeCog(commands.Cog):
    """Advanced welcome system with interactive onboarding"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
        self.welcome_streaks = {}  # Track consecutive welcomes
        self.welcome_games = {}  # Active welcome games
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Advanced welcome with interactive onboarding"""
        welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome")
        
        if not welcome_channel:
            return
        
        # Calculate welcome streak
        guild_id = member.guild.id
        self.welcome_streaks[guild_id] = self.welcome_streaks.get(guild_id, 0) + 1
        streak = self.welcome_streaks[guild_id]
        
        # Create interactive welcome embed
        embed = discord.Embed(
            title=f"🇨🇴 ¡Bienvenido a Colombia, {member.display_name}!",
            description=(
                f"**Welcome Streak:** 🔥 {streak} members\n"
                f"**Member #{member.guild.member_count}**\n\n"
                "Comrade, you have reached our shores. Whether you come to build a home, "
                "stand alongside our people, or speak on behalf of another nation, there is "
                "a place for you here.\n\n"
                "🌟 **Quick Start Guide**\n"
                "1️⃣ Read our rules in #rules\n"
                "2️⃣ Introduce yourself in #introductions\n"
                "3️⃣ Request citizenship below\n"
                "4️⃣ Join the conversation!\n\n"
                "— Nariño 🇨🇴"
            ),
            color=COLOR_GOLD,
            timestamp=discord.utils.utcnow()
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="Welcome to the nation!")
        
        # Create interactive onboarding view
        view = WelcomeOnboardingView(self.bot, member)
        
        welcome_msg = await welcome_channel.send(
            content=f"🎉 {member.mention} just joined Colombia! Welcome!",
            embed=embed,
            view=view
        )
        
        # Start welcome game (optional)
        if streak % 10 == 0:  # Every 10th member
            await self.start_welcome_game(welcome_channel, member, streak)
    
    async def start_welcome_game(self, channel, new_member, streak):
        """Start a welcome celebration game"""
        game_embed = discord.Embed(
            title="🎊 MILESTONE WELCOME! 🎊",
            description=(
                f"**{new_member.display_name}** is member #{streak}!\n\n"
                "🎁 **Special Rewards:**\n"
                "• +500 Pesos bonus\n"
                "• Exclusive 'Milestone Member' role\n"
                "• Featured in #hall-of-fame\n\n"
                "**Quick Challenge:** First person to say '¡Bienvenido!' gets +100 Pesos!"
            ),
            color=0xFFD700
        )
        
        await channel.send(embed=game_embed)
        
        # Award bonus
        data_manager.increment("economy", f"balance_{new_member.id}", 500)
        
        # Give milestone role
        milestone_role = discord.utils.get(new_member.guild.roles, name="Milestone Member")
        if milestone_role:
            await new_member.add_roles(milestone_role)

class EconomyCog(commands.Cog):
    """Advanced economy system - Gold Standard (DiplomaticaMC)"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
    
    @discord.app_commands.command(name="balance", description="Check your gold holdings")
    async def balance(self, interaction: discord.Interaction):
        """Check gold balance"""
        gold = data_manager.get("economy", f"gold_{interaction.user.id}", 0)
        
        # Calculate stacks and ingots
        stacks = gold // 64
        ingots = gold % 64
        
        embed = discord.Embed(
            title="🪙 Your Gold Holdings",
            description=f"You have **{gold}** gold ingots",
            color=COLOR_GOLD,
            timestamp=discord.utils.utcnow()
        )
        
        if stacks > 0:
            embed.add_field(name="📦 Stacks", value=f"{stacks} stacks", inline=True)
        embed.add_field(name="🪙 Ingots", value=f"{ingots} ingots", inline=True)
        
        # Show town/nation info if they have one
        town = data_manager.get("towny", f"town_{interaction.user.id}")
        if town:
            town_balance = data_manager.get("towny", f"town_balance_{town}", 0)
            embed.add_field(name="🏰 Town Treasury", value=f"{town_balance} gold", inline=False)
        
        embed.set_footer(text="Gold is the currency of DiplomaticaMC")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.app_commands.command(name="daily", description="Claim your daily gold reward")
    async def daily(self, interaction: discord.Interaction):
        """Claim daily gold reward"""
        last_claim = data_manager.get("economy", f"daily_{interaction.user.id}", 0)
        now = discord.utils.utcnow().timestamp()
        
        if now - last_claim < 86400:  # 24 hours
            remaining = int(86400 - (now - last_claim))
            hours = remaining // 3600
            minutes = (remaining % 3600) // 60
            
            await interaction.response.send_message(
                f"⏰ You've already claimed your daily reward!\n"
                f"Come back in **{hours}h {minutes}m**.",
                ephemeral=True
            )
            return
        
        # Award daily gold
        data_manager.set("economy", f"daily_{interaction.user.id}", now)
        data_manager.increment("economy", f"gold_{interaction.user.id}", DAILY_REWARD_GOLD)
        
        new_balance = data_manager.get("economy", f"gold_{interaction.user.id}", 0)
        
        embed = discord.Embed(
            title="✅ Daily Reward Claimed!",
            description=f"You received **{DAILY_REWARD_GOLD}** gold ingots! 🪙",
            color=COLOR_GOLD,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="💰 New Balance", value=f"{new_balance} gold", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.app_commands.command(name="work", description="Work to earn gold")
    async def work(self, interaction: discord.Interaction):
        """Work for gold"""
        import random
        
        last_work = data_manager.get("economy", f"work_{interaction.user.id}", 0)
        now = discord.utils.utcnow().timestamp()
        
        if now - last_work < 3600:  # 1 hour cooldown
            remaining = int(3600 - (now - last_work))
            minutes = remaining // 60
            
            await interaction.response.send_message(
                f"⏰ You need to rest! Try again in **{minutes}m**.",
                ephemeral=True
            )
            return
        
        # Random reward between 4-16 gold
        reward = random.randint(4, 16)
        
        data_manager.set("economy", f"work_{interaction.user.id}", now)
        data_manager.increment("economy", f"gold_{interaction.user.id}", reward)
        
        new_balance = data_manager.get("economy", f"gold_{interaction.user.id}", 0)
        
        # Random work messages
        work_messages = [
            "💼 You mined gold in the mountains!",
            "🏗️ You worked on a construction project!",
            "🌾 You harvested and sold crops!",
            "🎣 You went fishing and sold the catch!",
            "⚒️ You crafted and sold items!",
            "🏪 You ran your shop for the day!",
        ]
        
        embed = discord.Embed(
            title="💼 Work Complete!",
            description=f"{random.choice(work_messages)}\n\nYou earned **{reward}** gold ingots! 🪙",
            color=COLOR_GOLD,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="💰 New Balance", value=f"{new_balance} gold", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.app_commands.command(name="pay", description="Pay gold to another player")
    @discord.app_commands.describe(user="Player to pay", amount="Amount of gold to pay")
    async def pay(self, interaction: discord.Interaction, user: discord.Member, amount: int):
        """Pay gold to another player"""
        if amount <= 0:
            await interaction.response.send_message(
                "❌ Amount must be positive!",
                ephemeral=True
            )
            return
        
        sender_balance = data_manager.get("economy", f"gold_{interaction.user.id}", 0)
        
        if sender_balance < amount:
            await interaction.response.send_message(
                f"❌ You don't have enough gold! You have **{sender_balance}** gold.",
                ephemeral=True
            )
            return
        
        # Transfer gold
        data_manager.decrement("economy", f"gold_{interaction.user.id}", amount)
        data_manager.increment("economy", f"gold_{user.id}", amount)
        
        new_sender_balance = data_manager.get("economy", f"gold_{interaction.user.id}", 0)
        new_receiver_balance = data_manager.get("economy", f"gold_{user.id}", 0)
        
        embed = discord.Embed(
            title="✅ Payment Sent!",
            description=f"You paid **{amount}** gold to {user.mention}",
            color=COLOR_GOLD,
            timestamp=discord.utils.utcnow()
        )
        embed.add_field(name="💰 Your Balance", value=f"{new_sender_balance} gold", inline=True)
        embed.add_field(name="💰 Their Balance", value=f"{new_receiver_balance} gold", inline=True)
        
        await interaction.response.send_message(embed=embed)
        
        # Notify receiver
        try:
            await user.send(
                f"💰 You received **{amount}** gold from {interaction.user.mention}!\n"
                f"Your new balance: **{new_receiver_balance}** gold"
            )
        except:
            pass
    
    @discord.app_commands.command(name="top-gold", description="View top gold holders")
    async def top_gold(self, interaction: discord.Interaction):
        """View top gold holders"""
        # Get all players with gold
        players = []
        for key in data_manager.get_all_keys("economy"):
            if key.startswith("gold_"):
                user_id = int(key.replace("gold_", ""))
                gold = data_manager.get("economy", key, 0)
                if gold > 0:
                    players.append((user_id, gold))
        
        # Sort by gold
        players.sort(key=lambda x: x[1], reverse=True)
        top_10 = players[:10]
        
        embed = discord.Embed(
            title="🏆 Top Gold Holders",
            description="The wealthiest players on DiplomaticaMC",
            color=COLOR_GOLD,
            timestamp=discord.utils.utcnow()
        )
        
        if not top_10:
            embed.description = "No players have gold yet!"
        else:
            for i, (user_id, gold) in enumerate(top_10, 1):
                medal = ["🥇", "🥈", "🥉"][i-1] if i <= 3 else f"**#{i}**"
                embed.add_field(
                    name=f"{medal} <@{user_id}>",
                    value=f"{gold:,} gold",
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)

class DiplomacyCog(commands.Cog):
    """Advanced diplomacy system with wars, alliances, and treaties"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
    
    @discord.app_commands.command(name="diplomacy", description="Open diplomatic request")
    async def diplomacy(self, interaction: discord.Interaction):
        """Show diplomacy panel"""
        embed = discord.Embed(
            title="🌐 Foreign Affairs",
            description=(
                "Manage diplomatic relations with other nations.\n\n"
                "**Current Relations:**\n"
                "🟢 **Allies:** 3 nations\n"
                "🟡 **Neutral:** 5 nations\n"
                "🔴 **Enemies:** 1 nation\n\n"
                "Use the buttons below to manage diplomacy."
            ),
            color=COLOR_BLUE
        )
        
        view = DiplomacyView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.app_commands.command(name="declare-war", description="Declare war on another nation")
    @discord.app_commands.checks.has_role(LEADERSHIP_ROLE)
    async def declare_war(self, interaction: discord.Interaction, nation: str, reason: str):
        """Declare war on another nation"""
        # Check if already at war
        wars = data_manager.get("diplomacy", "wars", [])
        for war in wars:
            if war["attacker"] == nation or war["defender"] == nation:
                await interaction.response.send_message(
                    f"❌ Colombia is already at war with {nation}!",
                    ephemeral=True
                )
                return
        
        # Create war
        war = {
            "attacker": "Colombia",
            "defender": nation,
            "reason": reason,
            "declared_by": interaction.user.id,
            "declared_at": discord.utils.utcnow().isoformat(),
            "status": "active",
            "battles": []
        }
        
        wars.append(war)
        data_manager.set("diplomacy", "wars", wars)
        
        # Create war announcement
        war_embed = discord.Embed(
            title="⚔️ WAR DECLARED ⚔️",
            description=(
                f"**Colombia** has declared war on **{nation}**!\n\n"
                f"**Reason:** {reason}\n"
                f"**Declared by:** {interaction.user.mention}\n\n"
                "🔴 **Status:** Active\n"
                "May the best nation win!"
            ),
            color=COLOR_RED,
            timestamp=discord.utils.utcnow()
        )
        
        # Send to announcements
        announcements = discord.utils.get(interaction.guild.text_channels, name="announcements")
        if announcements:
            await announcements.send(embed=war_embed)
        
        await interaction.response.send_message(
            f"⚔️ War declared on **{nation}**! The nation has been notified.",
            ephemeral=True
        )
    
    @discord.app_commands.command(name="propose-alliance", description="Propose alliance with another nation")
    @discord.app_commands.checks.has_role(LEADERSHIP_ROLE)
    async def propose_alliance(self, interaction: discord.Interaction, nation: str, terms: str):
        """Propose alliance"""
        # Create alliance proposal
        proposal = {
            "proposer": "Colombia",
            "target": nation,
            "terms": terms,
            "proposed_by": interaction.user.id,
            "proposed_at": discord.utils.utcnow().isoformat(),
            "status": "pending",
            "votes": {"for": 0, "against": 0}
        }
        
        alliances = data_manager.get("diplomacy", "alliance_proposals", [])
        alliances.append(proposal)
        data_manager.set("diplomacy", "alliance_proposals", alliances)
        
        # Create proposal embed
        proposal_embed = discord.Embed(
            title="🤝 Alliance Proposal",
            description=(
                f"**Colombia** proposes an alliance with **{nation}**\n\n"
                f"**Terms:** {terms}\n"
                f"**Proposed by:** {interaction.user.mention}\n\n"
                "Leadership must vote on this proposal."
            ),
            color=COLOR_GOLD,
            timestamp=discord.utils.utcnow()
        )
        
        view = AllianceVoteView(self.bot, len(alliances) - 1)
        
        # Send to leadership
        leadership = discord.utils.get(interaction.guild.text_channels, name="leadership")
        if leadership:
            await leadership.send(
                content="🤝 **New Alliance Proposal** <@&LEADERSHIP_ROLE_ID>",
                embed=proposal_embed,
                view=view
            )
        
        await interaction.response.send_message(
            f"🤝 Alliance proposal sent to **{nation}**! Leadership will vote on it.",
            ephemeral=True
        )
    
    @discord.app_commands.command(name="peace-treaty", description="Propose peace treaty")
    @discord.app_commands.checks.has_role(LEADERSHIP_ROLE)
    async def peace_treaty(self, interaction: discord.Interaction, nation: str, terms: str):
        """Propose peace treaty"""
        # Find active war
        wars = data_manager.get("diplomacy", "wars", [])
        war_found = False
        
        for war in wars:
            if war["defender"] == nation and war["status"] == "active":
                war_found = True
                break
        
        if not war_found:
            await interaction.response.send_message(
                f"❌ Colombia is not at war with {nation}!",
                ephemeral=True
            )
            return
        
        # Create peace treaty
        treaty = {
            "nation1": "Colombia",
            "nation2": nation,
            "terms": terms,
            "proposed_by": interaction.user.id,
            "proposed_at": discord.utils.utcnow().isoformat(),
            "status": "pending"
        }
        
        treaties = data_manager.get("diplomacy", "treaties", [])
        treaties.append(treaty)
        data_manager.set("diplomacy", "treaties", treaties)
        
        # Create treaty embed
        treaty_embed = discord.Embed(
            title="🕊️ Peace Treaty Proposed",
            description=(
                f"**Colombia** proposes peace with **{nation}**\n\n"
                f"**Terms:** {terms}\n"
                f"**Proposed by:** {interaction.user.mention}\n\n"
                "Both nations must agree to the terms."
            ),
            color=COLOR_BLUE,
            timestamp=discord.utils.utcnow()
        )
        
        # Send to leadership
        leadership = discord.utils.get(interaction.guild.text_channels, name="leadership")
        if leadership:
            await leadership.send(
                content="🕊️ **Peace Treaty Proposed** <@&LEADERSHIP_ROLE_ID>",
                embed=treaty_embed
            )
        
        await interaction.response.send_message(
            f"🕊️ Peace treaty proposed to **{nation}**! Awaiting their response.",
            ephemeral=True
        )
    
    @discord.app_commands.command(name="relations", description="View diplomatic relations")
    async def relations(self, interaction: discord.Interaction):
        """View diplomatic relations"""
        alliances = data_manager.get("diplomacy", "alliances", [])
        wars = data_manager.get("diplomacy", "wars", [])
        neutrals = data_manager.get("diplomacy", "neutrals", [])
        
        embed = discord.Embed(
            title="🌐 Diplomatic Relations",
            description="Current status of Colombia's diplomatic relations",
            color=COLOR_BLUE,
            timestamp=discord.utils.utcnow()
        )
        
        # Allies
        if alliances:
            ally_list = "\n".join([f"🟢 {a['nation']}" for a in alliances])
            embed.add_field(name="🤝 Allies", value=ally_list or "None", inline=True)
        else:
            embed.add_field(name="🤝 Allies", value="None", inline=True)
        
        # Wars
        active_wars = [w for w in wars if w["status"] == "active"]
        if active_wars:
            war_list = "\n".join([f"⚔️ {w['defender']}" for w in active_wars])
            embed.add_field(name="⚔️ At War With", value=war_list, inline=True)
        else:
            embed.add_field(name="⚔️ At War With", value="None", inline=True)
        
        # Neutrals
        if neutrals:
            neutral_list = "\n".join([f"🟡 {n}" for n in neutrals[:10]])
            embed.add_field(name="🟡 Neutral", value=neutral_list or "None", inline=True)
        else:
            embed.add_field(name="🟡 Neutral", value="None", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class DiplomacyView(discord.ui.View):
    """Diplomacy management view"""
    
    def __init__(self, bot: NariñoBot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(
        label="📊 View Relations",
        style=discord.ButtonStyle.primary,
        custom_id="diplomacy_view_relations"
    )
    async def view_relations(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View relations"""
        # This would call the relations command
        await interaction.response.send_message(
            "Use `/relations` to view diplomatic relations!",
            ephemeral=True
        )
    
    @discord.ui.button(
        label="⚔️ Declare War",
        style=discord.ButtonStyle.danger,
        custom_id="diplomacy_declare_war"
    )
    async def declare_war(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Declare war"""
        leadership_role = discord.utils.get(interaction.guild.roles, name=LEADERSHIP_ROLE)
        if leadership_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Only leadership can declare war!",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            "Use `/declare-war <nation> <reason>` to declare war!",
            ephemeral=True
        )
    
    @discord.ui.button(
        label="🤝 Propose Alliance",
        style=discord.ButtonStyle.success,
        custom_id="diplomacy_propose_alliance"
    )
    async def propose_alliance(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Propose alliance"""
        leadership_role = discord.utils.get(interaction.guild.roles, name=LEADERSHIP_ROLE)
        if leadership_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Only leadership can propose alliances!",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            "Use `/propose-alliance <nation> <terms>` to propose an alliance!",
            ephemeral=True
        )

class AllianceVoteView(discord.ui.View):
    """View for voting on alliance proposals"""
    
    def __init__(self, bot: NariñoBot, proposal_index: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.proposal_index = proposal_index
    
    @discord.ui.button(
        label="✅ Vote For",
        style=discord.ButtonStyle.success,
        custom_id="alliance_vote_for"
    )
    async def vote_for(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Vote for alliance"""
        leadership_role = discord.utils.get(interaction.guild.roles, name=LEADERSHIP_ROLE)
        if leadership_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Only leadership can vote!",
                ephemeral=True
            )
            return
        
        # Record vote
        alliances = data_manager.get("diplomacy", "alliance_proposals", [])
        if self.proposal_index < len(alliances):
            proposal = alliances[self.proposal_index]
            voter_id = str(interaction.user.id)
            
            if "voters" not in proposal:
                proposal["voters"] = {}
            
            if voter_id in proposal["voters"]:
                await interaction.response.send_message(
                    "❌ You've already voted!",
                    ephemeral=True
                )
                return
            
            proposal["voters"][voter_id] = "for"
            proposal["votes"]["for"] += 1
            alliances[self.proposal_index] = proposal
            data_manager.set("diplomacy", "alliance_proposals", alliances)
            
            await interaction.response.send_message(
                "✅ Vote recorded! You voted FOR the alliance.",
                ephemeral=True
            )
    
    @discord.ui.button(
        label="❌ Vote Against",
        style=discord.ButtonStyle.danger,
        custom_id="alliance_vote_against"
    )
    async def vote_against(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Vote against alliance"""
        leadership_role = discord.utils.get(interaction.guild.roles, name=LEADERSHIP_ROLE)
        if leadership_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Only leadership can vote!",
                ephemeral=True
            )
            return
        
        # Record vote
        alliances = data_manager.get("diplomacy", "alliance_proposals", [])
        if self.proposal_index < len(alliances):
            proposal = alliances[self.proposal_index]
            voter_id = str(interaction.user.id)
            
            if "voters" not in proposal:
                proposal["voters"] = {}
            
            if voter_id in proposal["voters"]:
                await interaction.response.send_message(
                    "❌ You've already voted!",
                    ephemeral=True
                )
                return
            
            proposal["voters"][voter_id] = "against"
            proposal["votes"]["against"] += 1
            alliances[self.proposal_index] = proposal
            data_manager.set("diplomacy", "alliance_proposals", alliances)
            
            await interaction.response.send_message(
                "❌ Vote recorded! You voted AGAINST the alliance.",
                ephemeral=True
            )

class TownyCog(commands.Cog):
    """Towny integration for DiplomaticaMC"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
    
    @discord.app_commands.command(name="town", description="Manage your town")
    @discord.app_commands.describe(action="Action to perform: info, create, join, leave")
    @discord.app_commands.describe(name="Town name (for create/join)")
    async def town(self, interaction: discord.Interaction, action: str, name: str = None):
        """Manage town"""
        user_id = interaction.user.id
        
        if action == "info":
            # Show town info
            town = data_manager.get("towny", f"town_{user_id}")
            
            if not town:
                await interaction.response.send_message(
                    "❌ You're not in a town!\n"
                    f"Use `/town create <name>` to create one (costs {TOWN_CREATION_COST} gold)\n"
                    f"Or `/town join <name>` to join an existing town",
                    ephemeral=True
                )
                return
            
            town_balance = data_manager.get("towny", f"town_balance_{town}", 0)
            town_members = data_manager.get("towny", f"town_members_{town}", [])
            town_chunks = data_manager.get("towny", f"town_chunks_{town}", 1)
            
            embed = discord.Embed(
                title=f"🏰 {town}",
                description=f"Your town on DiplomaticaMC",
                color=COLOR_GOLD,
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(name="💰 Treasury", value=f"{town_balance} gold", inline=True)
            embed.add_field(name="👥 Members", value=f"{len(town_members)}", inline=True)
            embed.add_field(name="🗺️ Chunks", value=f"{town_chunks}", inline=True)
            
            # Show members
            if town_members:
                member_list = "\n".join([f"<@{m}>" for m in town_members[:10]])
                if len(town_members) > 10:
                    member_list += f"\n... and {len(town_members) - 10} more"
                embed.add_field(name="👥 Town Members", value=member_list, inline=False)
            
            embed.set_footer(text=f"Mayor: <@{town_members[0]}>")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif action == "create":
            if not name:
                await interaction.response.send_message(
                    "❌ Please specify a town name!\n"
                    "Usage: `/town create <name>`",
                    ephemeral=True
                )
                return
            
            # Check if already in a town
            if data_manager.get("towny", f"town_{user_id}"):
                await interaction.response.send_message(
                    "❌ You're already in a town! Use `/town leave` first.",
                    ephemeral=True
                )
                return
            
            # Check gold
            gold = data_manager.get("economy", f"gold_{user_id}", 0)
            if gold < TOWN_CREATION_COST:
                await interaction.response.send_message(
                    f"❌ You need **{TOWN_CREATION_COST}** gold to create a town!\n"
                    f"You have **{gold}** gold.",
                    ephemeral=True
                )
                return
            
            # Create town
            data_manager.decrement("economy", f"gold_{user_id}", TOWN_CREATION_COST)
            data_manager.set("towny", f"town_{user_id}", name)
            data_manager.set("towny", f"town_balance_{name}", 0)
            data_manager.set("towny", f"town_members_{name}", [user_id])
            data_manager.set("towny", f"town_chunks_{name}", 1)
            data_manager.set("towny", f"town_created_{name}", discord.utils.utcnow().isoformat())
            
            new_balance = data_manager.get("economy", f"gold_{user_id}", 0)
            
            embed = discord.Embed(
                title="✅ Town Created!",
                description=f"**{name}** has been founded!\n\nYou are now the mayor!",
                color=COLOR_GOLD,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="💰 Cost", value=f"{TOWN_CREATION_COST} gold", inline=True)
            embed.add_field(name="💰 Remaining Gold", value=f"{new_balance} gold", inline=True)
            embed.add_field(name="🗺️ Starting Chunks", value="1", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
            # Announce in announcements channel
            announcements = discord.utils.get(interaction.guild.text_channels, name="announcements")
            if announcements:
                announce_embed = discord.Embed(
                    title="🏰 New Town Founded!",
                    description=f"**{name}** has been founded by {interaction.user.mention}!\n\nWelcome to the nation!",
                    color=COLOR_GOLD,
                    timestamp=discord.utils.utcnow()
                )
                await announcements.send(embed=announce_embed)
        
        elif action == "join":
            if not name:
                await interaction.response.send_message(
                    "❌ Please specify a town name!\n"
                    "Usage: `/town join <name>`",
                    ephemeral=True
                )
                return
            
            # Check if already in a town
            if data_manager.get("towny", f"town_{user_id}"):
                await interaction.response.send_message(
                    "❌ You're already in a town! Use `/town leave` first.",
                    ephemeral=True
                )
                return
            
            # Check if town exists
            town_members = data_manager.get("towny", f"town_members_{name}")
            if not town_members:
                await interaction.response.send_message(
                    f"❌ Town **{name}** doesn't exist!",
                    ephemeral=True
                )
                return
            
            # Join town
            town_members.append(user_id)
            data_manager.set("towny", f"town_{user_id}", name)
            data_manager.set("towny", f"town_members_{name}", town_members)
            
            embed = discord.Embed(
                title="✅ Joined Town!",
                description=f"You joined **{name}**!",
                color=COLOR_GOLD,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="👥 Total Members", value=f"{len(town_members)}", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif action == "leave":
            town = data_manager.get("towny", f"town_{user_id}")
            
            if not town:
                await interaction.response.send_message(
                    "❌ You're not in a town!",
                    ephemeral=True
                )
                return
            
            # Remove from town
            town_members = data_manager.get("towny", f"town_members_{town}", [])
            if user_id in town_members:
                town_members.remove(user_id)
                data_manager.set("towny", f"town_members_{town}", town_members)
            
            data_manager.delete("towny", f"town_{user_id}")
            
            await interaction.response.send_message(
                f"✅ You left **{town}**.",
                ephemeral=True
            )
    
    @discord.app_commands.command(name="nation", description="Manage your nation")
    @discord.app_commands.describe(action="Action to perform: info, create, join, leave")
    @discord.app_commands.describe(name="Nation name (for create/join)")
    async def nation(self, interaction: discord.Interaction, action: str, name: str = None):
        """Manage nation"""
        user_id = interaction.user.id
        
        if action == "info":
            # Show nation info
            nation = data_manager.get("towny", f"nation_{user_id}")
            
            if not nation:
                await interaction.response.send_message(
                    "❌ You're not in a nation!\n"
                    f"Use `/nation create <name>` to create one (costs {NATION_CREATION_COST} gold)",
                    ephemeral=True
                )
                return
            
            nation_balance = data_manager.get("towny", f"nation_balance_{nation}", 0)
            nation_towns = data_manager.get("towny", f"nation_towns_{nation}", [])
            
            embed = discord.Embed(
                title=f"🌍 {nation}",
                description=f"Your nation on DiplomaticaMC",
                color=COLOR_BLUE,
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(name="💰 Treasury", value=f"{nation_balance} gold", inline=True)
            embed.add_field(name="🏰 Towns", value=f"{len(nation_towns)}", inline=True)
            
            if nation_towns:
                town_list = "\n".join(nation_towns[:10])
                if len(nation_towns) > 10:
                    town_list += f"\n... and {len(nation_towns) - 10} more"
                embed.add_field(name="🏰 Nation Towns", value=town_list, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        elif action == "create":
            if not name:
                await interaction.response.send_message(
                    "❌ Please specify a nation name!\n"
                    "Usage: `/nation create <name>`",
                    ephemeral=True
                )
                return
            
            # Check if already in a nation
            if data_manager.get("towny", f"nation_{user_id}"):
                await interaction.response.send_message(
                    "❌ You're already in a nation!",
                    ephemeral=True
                )
                return
            
            # Check if user has a town
            town = data_manager.get("towny", f"town_{user_id}")
            if not town:
                await interaction.response.send_message(
                    "❌ You must be in a town to create a nation!\n"
                    "Use `/town create <name>` first.",
                    ephemeral=True
                )
                return
            
            # Check gold
            gold = data_manager.get("economy", f"gold_{user_id}", 0)
            if gold < NATION_CREATION_COST:
                await interaction.response.send_message(
                    f"❌ You need **{NATION_CREATION_COST}** gold to create a nation!\n"
                    f"You have **{gold}** gold.",
                    ephemeral=True
                )
                return
            
            # Create nation
            data_manager.decrement("economy", f"gold_{user_id}", NATION_CREATION_COST)
            data_manager.set("towny", f"nation_{user_id}", name)
            data_manager.set("towny", f"nation_balance_{name}", 0)
            data_manager.set("towny", f"nation_towns_{name}", [town])
            data_manager.set("towny", f"nation_created_{name}", discord.utils.utcnow().isoformat())
            
            new_balance = data_manager.get("economy", f"gold_{user_id}", 0)
            
            embed = discord.Embed(
                title="✅ Nation Created!",
                description=f"**{name}** has been founded!\n\nYou are now the nation leader!",
                color=COLOR_BLUE,
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="💰 Cost", value=f"{NATION_CREATION_COST} gold", inline=True)
            embed.add_field(name="💰 Remaining Gold", value=f"{new_balance} gold", inline=True)
            embed.add_field(name="🏰 Starting Town", value=town, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
            # Announce
            announcements = discord.utils.get(interaction.guild.text_channels, name="announcements")
            if announcements:
                announce_embed = discord.Embed(
                    title="🌍 New Nation Founded!",
                    description=f"**{name}** has been founded by {interaction.user.mention}!\n\nA new power rises!",
                    color=COLOR_BLUE,
                    timestamp=discord.utils.utcnow()
                )
                await announcements.send(embed=announce_embed)
        
        elif action == "join":
            if not name:
                await interaction.response.send_message(
                    "❌ Please specify a nation name!",
                    ephemeral=True
                )
                return
            
            # Check if already in a nation
            if data_manager.get("towny", f"nation_{user_id}"):
                await interaction.response.send_message(
                    "❌ You're already in a nation!",
                    ephemeral=True
                )
                return
            
            # Check if user has a town
            town = data_manager.get("towny", f"town_{user_id}")
            if not town:
                await interaction.response.send_message(
                    "❌ You must be in a town to join a nation!",
                    ephemeral=True
                )
                return
            
            # Check if nation exists
            nation_towns = data_manager.get("towny", f"nation_towns_{name}")
            if not nation_towns:
                await interaction.response.send_message(
                    f"❌ Nation **{name}** doesn't exist!",
                    ephemeral=True
                )
                return
            
            # Join nation
            nation_towns.append(town)
            data_manager.set("towny", f"nation_{user_id}", name)
            data_manager.set("towny", f"nation_towns_{name}", nation_towns)
            
            await interaction.response.send_message(
                f"✅ Your town **{town}** joined **{name}**!",
                ephemeral=True
            )
        
        elif action == "leave":
            nation = data_manager.get("towny", f"nation_{user_id}")
            
            if not nation:
                await interaction.response.send_message(
                    "❌ You're not in a nation!",
                    ephemeral=True
                )
                return
            
            # Remove town from nation
            town = data_manager.get("towny", f"town_{user_id}")
            nation_towns = data_manager.get("towny", f"nation_towns_{nation}", [])
            if town in nation_towns:
                nation_towns.remove(town)
                data_manager.set("towny", f"nation_towns_{nation}", nation_towns)
            
            data_manager.delete("towny", f"nation_{user_id}")
            
            await interaction.response.send_message(
                f"✅ Your town left **{nation}**.",
                ephemeral=True
            )
    
    @discord.app_commands.command(name="map", description="View the live map")
    async def map(self, interaction: discord.Interaction):
        """Show live map link"""
        embed = discord.Embed(
            title="🗺️ DiplomaticaMC Live Map",
            description=(
                "Explore the custom Earth map in real-time!\n\n"
                "**Features:**\n"
                "• Real-time player tracking\n"
                "• Town and nation borders\n"
                "• Capital markers\n"
                "• Siege zones\n"
                "• Chunk borders\n"
                "• Mobile responsive\n\n"
                "**[Click here to open the map](https://map.diplomaticamc.com/)**"
            ),
            color=COLOR_BLUE,
            timestamp=discord.utils.utcnow()
        )
        embed.set_image(url="https://diplomaticamc.com/img/map-overview.jpg")
        
        await interaction.response.send_message(embed=embed)
    
    @discord.app_commands.command(name="market", description="View the live market")
    async def market(self, interaction: discord.Interaction):
        """Show live market link"""
        embed = discord.Embed(
            title="📊 DiplomaticaMC Live Market",
            description=(
                "Monitor the global economy in real-time!\n\n"
                "**Features:**\n"
                "• Live price tracking\n"
                "• Trade volume analytics\n"
                "• Stock levels\n"
                "• Price trends\n"
                "• Supply and demand\n\n"
                "**[Click here to open the market](https://market.diplomaticamc.com/)**"
            ),
            color=COLOR_GOLD,
            timestamp=discord.utils.utcnow()
        )
        embed.set_image(url="https://diplomaticamc.com/img/market-overview.jpg")
        
        await interaction.response.send_message(embed=embed)

class SiegeWarCog(commands.Cog):
    """SiegeWar integration for DiplomaticaMC"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
    
    @discord.app_commands.command(name="siege", description="Manage sieges")
    @discord.app_commands.describe(action="Action: status, attack, defend")
    async def siege(self, interaction: discord.Interaction, action: str):
        """Manage sieges"""
        if action == "status":
            # Show active sieges
            sieges = data_manager.get("siegewar", "active_sieges", [])
            
            embed = discord.Embed(
                title="⚔️ Active Sieges",
                description="Current siege battles on DiplomaticaMC",
                color=COLOR_RED,
                timestamp=discord.utils.utcnow()
            )
            
            if not sieges:
                embed.description = "No active sieges at the moment.\n\n**SiegeWar Info:**\n• Weekend-only warfare\n• Non-destructive battles\n• Zero upkeep\n• Zero plundering"
            else:
                for siege in sieges:
                    embed.add_field(
                        name=f"⚔️ {siege['attacker']} → {siege['defender']}",
                        value=(
                            f"**Status:** {siege['status']}\n"
                            f"**Started:** <t:{int(siege['timestamp'])}:R>\n"
                            f"**Battle Points:** {siege.get('points', 0)}"
                        ),
                        inline=False
                    )
            
            embed.set_footer(text="SiegeWar: Opt-in, non-destructive warfare")
            
            await interaction.response.send_message(embed=embed)
        
        elif action == "attack":
            await interaction.response.send_message(
                "⚔️ **SiegeWar Attack**\n\n"
                "To attack a town, use the in-game command:\n"
                "```\n"
                "/sw attack <town_name>\n"
                "```\n\n"
                "**Requirements:**\n"
                "• Must be at war with the nation\n"
                "• Weekend-only (Saturday-Sunday)\n"
                "• Your town must be adjacent to the target\n\n"
                "**SiegeWar Features:**\n"
                "• Non-destructive (no griefing)\n"
                "• Zero upkeep costs\n"
                "• Zero plundering\n"
                "• Strategic weekend battles",
                ephemeral=True
            )
        
        elif action == "defend":
            await interaction.response.send_message(
                "🛡️ **SiegeWar Defense**\n\n"
                "To defend your town, use the in-game command:\n"
                "```\n"
                "/sw defend\n"
                "```\n\n"
                "**Defense Tips:**\n"
                "• Gather your town members\n"
                "• Stock up on gear and potions\n"
                "• Coordinate with allies\n"
                "• Use the terrain to your advantage\n\n"
                "**Remember:** SiegeWar is non-destructive, so your buildings are safe!",
                ephemeral=True
            )
    
    @discord.app_commands.command(name="war-status", description="View current war status")
    async def war_status(self, interaction: discord.Interaction):
        """View war status"""
        wars = data_manager.get("diplomacy", "wars", [])
        active_wars = [w for w in wars if w.get("status") == "active"]
        
        embed = discord.Embed(
            title="⚔️ Current Wars",
            description="Active conflicts on DiplomaticaMC",
            color=COLOR_RED,
            timestamp=discord.utils.utcnow()
        )
        
        if not active_wars:
            embed.description = "🕊️ **Peace!**\n\nNo active wars at the moment.\n\nAll nations are at peace."
        else:
            for war in active_wars:
                embed.add_field(
                    name=f"⚔️ {war['attacker']} vs {war['defender']}",
                    value=(
                        f"**Reason:** {war.get('reason', 'Unknown')}\n"
                        f"**Declared:** <t:{int(war.get('timestamp', 0))}:R>\n"
                        f"**Status:** {war.get('status', 'active')}"
                    ),
                    inline=False
                )
        
        await interaction.response.send_message(embed=embed)

class InactivityCog(commands.Cog):
    """Inactivity tracking for DiplomaticaMC"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
        self.inactivity_check.start()
    
    def cog_unload(self):
        self.inactivity_check.cancel()
    
    @tasks.loop(hours=24)
    async def inactivity_check(self):
        """Check for inactive players daily"""
        now = discord.utils.utcnow().timestamp()
        
        # Get all players
        players = data_manager.get_all_keys("activity")
        
        for player_key in players:
            if player_key.startswith("last_seen_"):
                user_id = int(player_key.replace("last_seen_", ""))
                last_seen = data_manager.get("activity", player_key, now)
                
                days_inactive = (now - last_seen) / 86400
                
                # Warn at 50 days
                if days_inactive >= INACTIVITY_WARNING_DAYS and days_inactive < INACTIVITY_WARNING_DAYS + 1:
                    warned = data_manager.get("activity", f"warned_{user_id}", False)
                    if not warned:
                        try:
                            user = await self.bot.fetch_user(user_id)
                            remaining = int(INACTIVITY_DELETION_DAYS - days_inactive)
                            
                            await user.send(
                                f"⚠️ **Inactivity Warning**\n\n"
                                f"You haven't been active on DiplomaticaMC for **{int(days_inactive)}** days.\n\n"
                                f"**Your Towny data will be deleted in {remaining} days** if you don't log in.\n\n"
                                f"To keep your town/nation, please log in to the server!\n\n"
                                f"IP: `diplomaticamc.com`"
                            )
                            
                            data_manager.set("activity", f"warned_{user_id}", True)
                        except:
                            pass
                
                # Delete at 60 days
                elif days_inactive >= INACTIVITY_DELETION_DAYS:
                    # Delete towny data
                    town = data_manager.get("towny", f"town_{user_id}")
                    if town:
                        # Remove from town
                        town_members = data_manager.get("towny", f"town_members_{town}", [])
                        if user_id in town_members:
                            town_members.remove(user_id)
                            data_manager.set("towny", f"town_members_{town}", town_members)
                        
                        # Delete town if empty
                        if not town_members:
                            data_manager.delete("towny", f"town_{town}")
                            data_manager.delete("towny", f"town_balance_{town}")
                            data_manager.delete("towny", f"town_chunks_{town}")
                    
                    # Remove from nation
                    nation = data_manager.get("towny", f"nation_{user_id}")
                    if nation:
                        data_manager.delete("towny", f"nation_{user_id}")
                    
                    # Clear activity data
                    data_manager.delete("activity", f"last_seen_{user_id}")
                    data_manager.delete("activity", f"warned_{user_id}")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Track activity on message"""
        if message.author.bot:
            return
        
        user_id = message.author.id
        now = discord.utils.utcnow().timestamp()
        
        data_manager.set("activity", f"last_seen_{user_id}", now)
        data_manager.delete("activity", f"warned_{user_id}")  # Reset warning
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Track activity on voice"""
        if before.channel is None and after.channel is not None:
            # Joined voice
            user_id = member.id
            now = discord.utils.utcnow().timestamp()
            
            data_manager.set("activity", f"last_seen_{user_id}", now)
            data_manager.delete("activity", f"warned_{user_id}")

class FunCog(commands.Cog):
    """Fun features"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
    
    @discord.app_commands.command(name="funfact", description="Get a fun fact about Colombia")
    async def funfact(self, interaction: discord.Interaction):
        """Get a fun fact"""
        import random
        from config import FUN_FACTS
        
        lang = i18n.get_user_lang(interaction.user.id)
        facts = FUN_FACTS.get(lang, FUN_FACTS["en"])
        fact = random.choice(facts)
        
        embed = discord.Embed(
            title="🇨🇴 Did You Know?",
            description=fact,
            color=COLOR_GOLD
        )
        
        await interaction.response.send_message(embed=embed)

# ─── Views ────────────────────────────────────────────────────────────────────

class VoteNotifyView(discord.ui.View):
    """Vote party buttons"""
    
    def __init__(self, bot: NariñoBot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(
        label="✅ I Voted!",
        style=discord.ButtonStyle.success,
        custom_id="vote_claim_button",
        row=0
    )
    async def vote_claim_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Vote claim button - handled by cog"""
        pass
    
    @discord.ui.button(
        label="🔔 Get Notified",
        style=discord.ButtonStyle.primary,
        custom_id="vote_notify_toggle",
        row=0
    )
    async def notify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Notify toggle button - handled by cog"""
        pass

class WelcomeOnboardingView(discord.ui.View):
    """Interactive onboarding view for new members"""
    
    def __init__(self, bot: NariñoBot, new_member: discord.Member):
        super().__init__(timeout=86400)  # 24 hours
        self.bot = bot
        self.new_member = new_member
    
    @discord.ui.button(
        label="📜 Read Rules",
        style=discord.ButtonStyle.secondary,
        custom_id="welcome_read_rules",
        row=0
    )
    async def read_rules(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show rules"""
        rules_channel = discord.utils.get(interaction.guild.text_channels, name="rules")
        if rules_channel:
            await interaction.response.send_message(
                f"📜 Check out the rules in {rules_channel.mention}!",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "📜 Please read the server rules!",
                ephemeral=True
            )
    
    @discord.ui.button(
        label="🏠 Request Citizenship",
        style=discord.ButtonStyle.primary,
        custom_id="welcome_request_citizenship",
        row=0
    )
    async def request_citizenship(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Request citizenship"""
        if interaction.user.id != self.new_member.id:
            await interaction.response.send_message(
                "❌ This button is only for the new member!",
                ephemeral=True
            )
            return
        
        await interaction.response.send_modal(CitizenshipModal(self.bot))
    
    @discord.ui.button(
        label="💬 Introduce Yourself",
        style=discord.ButtonStyle.success,
        custom_id="welcome_introduce",
        row=1
    )
    async def introduce(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to introductions"""
        intro_channel = discord.utils.get(interaction.guild.text_channels, name="introductions")
        if intro_channel:
            await interaction.response.send_message(
                f"💬 Introduce yourself in {intro_channel.mention}!\n\n"
                "**Template:**\n"
                "• Name/Age\n"
                "• Where you're from\n"
                "• What brought you here\n"
                "• Your interests",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "💬 Say hello in the chat!",
                ephemeral=True
            )
    
    @discord.ui.button(
        label="🎁 Claim Welcome Gift",
        style=discord.ButtonStyle.secondary,
        custom_id="welcome_claim_gift",
        row=1
    )
    async def claim_gift(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Claim welcome gift"""
        if interaction.user.id != self.new_member.id:
            await interaction.response.send_message(
                "❌ This button is only for the new member!",
                ephemeral=True
            )
            return
        
        # Check if already claimed
        if data_manager.get("welcome_gifts", str(interaction.user.id)):
            await interaction.response.send_message(
                "❌ You've already claimed your welcome gift!",
                ephemeral=True
            )
            return
        
        # Award gift
        data_manager.set("welcome_gifts", str(interaction.user.id), True)
        data_manager.increment("economy", f"balance_{interaction.user.id}", 100)
        
        # Give verified role
        verified_role = discord.utils.get(interaction.guild.roles, name=VERIFIED_ROLE)
        if verified_role and verified_role not in interaction.user.roles:
            await interaction.user.add_roles(verified_role)
        
        await interaction.response.send_message(
            "🎁 **Welcome Gift Claimed!**\n\n"
            "• +100 Pesos 💰\n"
            "• ✅ Verified role\n"
            "• 🎉 Welcome to Colombia!\n\n"
            "Start exploring and have fun!",
            ephemeral=True
        )

class RoleRequestView(discord.ui.View):
    """Advanced role request system with multi-step verification"""
    
    def __init__(self, bot: NariñoBot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(
        label="🏠 Request Citizenship",
        style=discord.ButtonStyle.primary,
        custom_id="request_citizenship",
        row=0
    )
    async def citizenship_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Request citizenship with full verification"""
        # Check if already has citizenship
        nation_role = discord.utils.get(interaction.guild.roles, name=NATION_MEMBER_ROLE)
        if nation_role and nation_role in interaction.user.roles:
            await interaction.response.send_message(
                "✅ You're already a citizen of Colombia!",
                ephemeral=True
            )
            return
        
        # Check if pending request exists
        pending = data_manager.get("role_requests", f"citizenship_{interaction.user.id}")
        if pending and pending.get("status") == "pending":
            await interaction.response.send_message(
                "⏳ You already have a pending citizenship request!\n"
                "Please wait for leadership to review it.",
                ephemeral=True
            )
            return
        
        await interaction.response.send_modal(CitizenshipModal(self.bot))
    
    @discord.ui.button(
        label="🤝 Request Ally Status",
        style=discord.ButtonStyle.secondary,
        custom_id="request_ally",
        row=0
    )
    async def ally_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Request ally status"""
        ally_role = discord.utils.get(interaction.guild.roles, name=ALLY_ROLE)
        if ally_role and ally_role in interaction.user.roles:
            await interaction.response.send_message(
                "✅ You already have Ally status!",
                ephemeral=True
            )
            return
        
        await interaction.response.send_modal(AllyModal(self.bot))
    
    @discord.ui.button(
        label="🌐 Foreign Diplomat",
        style=discord.ButtonStyle.secondary,
        custom_id="request_diplomat",
        row=0
    )
    async def diplomat_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Request diplomat status"""
        await interaction.response.send_modal(DiplomatModal(self.bot))
    
    @discord.ui.button(
        label="🔔 Toggle Vote Party Pings",
        style=discord.ButtonStyle.success,
        custom_id="toggle_vp_pings",
        row=1
    )
    async def vp_pings_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle VP pings"""
        member = interaction.user
        vp_role = discord.utils.get(interaction.guild.roles, name=VP_ROLE)
        
        if not vp_role:
            await interaction.response.send_message(
                "❌ The 'VP' role was not found.",
                ephemeral=True
            )
            return
        
        try:
            if vp_role in member.roles:
                await member.remove_roles(vp_role)
                await interaction.response.send_message(
                    "✅ You will **no longer** be notified for vote party updates.",
                    ephemeral=True
                )
            else:
                await member.add_roles(vp_role)
                await interaction.response.send_message(
                    "✅ You will now be **notified** when the vote party is close!",
                    ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {e}",
                ephemeral=True
            )

class CitizenshipModal(discord.ui.Modal, title="🏠 Citizenship Application"):
    """Advanced citizenship application with verification"""
    
    ign = discord.ui.TextInput(
        label="Minecraft Username (IGN)",
        placeholder="Your exact in-game name",
        min_length=3,
        max_length=16,
        required=True
    )
    
    nation = discord.ui.TextInput(
        label="Current Nation",
        placeholder="What nation are you from? (or 'None')",
        required=True
    )
    
    town = discord.ui.TextInput(
        label="Desired Town",
        placeholder="Which town do you want to join?",
        required=True
    )
    
    role = discord.ui.TextInput(
        label="Desired Role",
        placeholder="What role do you want? (Citizen, Merchant, etc.)",
        required=True
    )
    
    experience = discord.ui.TextInput(
        label="Why should we accept you?",
        placeholder="Tell us about yourself and why you want to join Colombia...",
        style=discord.TextStyle.paragraph,
        min_length=50,
        max_length=1000,
        required=True
    )
    
    def __init__(self, bot: NariñoBot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle citizenship application"""
        # Create application
        application = {
            "user_id": interaction.user.id,
            "username": str(interaction.user),
            "ign": self.ign.value,
            "nation": self.nation.value,
            "town": self.town.value,
            "role": self.role.value,
            "experience": self.experience.value,
            "status": "pending",
            "timestamp": discord.utils.utcnow().isoformat(),
            "reviewers": []
        }
        
        # Save application
        data_manager.set("role_requests", f"citizenship_{interaction.user.id}", application)
        
        # Create review embed
        review_embed = discord.Embed(
            title="🏠 New Citizenship Application",
            description=f"**Applicant:** {interaction.user.mention}\n**Status:** ⏳ Pending Review",
            color=COLOR_GOLD,
            timestamp=discord.utils.utcnow()
        )
        
        review_embed.add_field(name="🎮 Minecraft IGN", value=self.ign.value, inline=True)
        review_embed.add_field(name="🌍 Current Nation", value=self.nation.value, inline=True)
        review_embed.add_field(name="🏘️ Desired Town", value=self.town.value, inline=True)
        review_embed.add_field(name="👔 Desired Role", value=self.role.value, inline=True)
        review_embed.add_field(name="📝 Experience", value=self.experience.value[:1000], inline=False)
        
        # Create review buttons
        review_view = ApplicationReviewView(self.bot, interaction.user.id, "citizenship")
        
        # Send to leadership channel
        leadership_channel = discord.utils.get(interaction.guild.text_channels, name="leadership")
        if leadership_channel:
            await leadership_channel.send(
                content="🚨 **New Citizenship Application** <@&LEADERSHIP_ROLE_ID>",
                embed=review_embed,
                view=review_view
            )
        
        await interaction.response.send_message(
            "✅ **Application Submitted!**\n\n"
            "Your citizenship application has been sent to leadership for review.\n"
            "You'll be notified once a decision is made.\n\n"
            "**Application Details:**\n"
            f"• IGN: {self.ign.value}\n"
            f"• Town: {self.town.value}\n"
            f"• Role: {self.role.value}\n\n"
            "Good luck, comrade! 🇨🇴",
            ephemeral=True
        )

class DiplomatModal(discord.ui.Modal, title="🌐 Diplomat Application"):
    """Foreign diplomat application"""
    
    nation = discord.ui.TextInput(
        label="Your Nation",
        placeholder="What nation do you represent?",
        required=True
    )
    
    position = discord.ui.TextInput(
        label="Your Position",
        placeholder="e.g., Ambassador, Foreign Minister",
        required=True
    )
    
    purpose = discord.ui.TextInput(
        label="Purpose of Visit",
        placeholder="Why are you here? (Trade, Alliance, etc.)",
        style=discord.TextStyle.paragraph,
        min_length=50,
        max_length=1000,
        required=True
    )
    
    def __init__(self, bot: NariñoBot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle diplomat application"""
        application = {
            "user_id": interaction.user.id,
            "username": str(interaction.user),
            "nation": self.nation.value,
            "position": self.position.value,
            "purpose": self.purpose.value,
            "status": "pending",
            "timestamp": discord.utils.utcnow().isoformat()
        }
        
        data_manager.set("role_requests", f"diplomat_{interaction.user.id}", application)
        
        # Create review embed
        review_embed = discord.Embed(
            title="🌐 New Diplomat Application",
            description=f"**Diplomat:** {interaction.user.mention}\n**Nation:** {self.nation.value}",
            color=COLOR_BLUE,
            timestamp=discord.utils.utcnow()
        )
        
        review_embed.add_field(name="👔 Position", value=self.position.value, inline=True)
        review_embed.add_field(name="📋 Purpose", value=self.purpose.value[:500], inline=False)
        
        # Send to foreign affairs channel
        fa_channel = discord.utils.get(interaction.guild.text_channels, name="foreign-affairs")
        if fa_channel:
            review_view = ApplicationReviewView(self.bot, interaction.user.id, "diplomat")
            await fa_channel.send(
                content="🌐 **New Diplomat Application**",
                embed=review_embed,
                view=review_view
            )
        
        await interaction.response.send_message(
            "✅ **Diplomat Application Submitted!**\n\n"
            "Your application has been sent to Foreign Affairs.\n"
            "They will contact you soon.\n\n"
            f"• Nation: {self.nation.value}\n"
            f"• Position: {self.position.value}\n\n"
            "¡Bienvenido diplomático! 🌐",
            ephemeral=True
        )

class ApplicationReviewView(discord.ui.View):
    """View for reviewing applications"""
    
    def __init__(self, bot: NariñoBot, applicant_id: int, app_type: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.applicant_id = applicant_id
        self.app_type = app_type
    
    @discord.ui.button(
        label="✅ Approve",
        style=discord.ButtonStyle.success,
        custom_id="approve_application"
    )
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Approve application"""
        # Check permissions
        leadership_role = discord.utils.get(interaction.guild.roles, name=LEADERSHIP_ROLE)
        if leadership_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Only leadership can approve applications!",
                ephemeral=True
            )
            return
        
        # Get application
        app_key = f"{self.app_type}_{self.applicant_id}"
        application = data_manager.get("role_requests", app_key)
        
        if not application:
            await interaction.response.send_message(
                "❌ Application not found!",
                ephemeral=True
            )
            return
        
        # Update status
        application["status"] = "approved"
        application["reviewed_by"] = interaction.user.id
        application["reviewed_at"] = discord.utils.utcnow().isoformat()
        data_manager.set("role_requests", app_key, application)
        
        # Assign role
        applicant = interaction.guild.get_member(self.applicant_id)
        if applicant:
            if self.app_type == "citizenship":
                role = discord.utils.get(interaction.guild.roles, name=NATION_MEMBER_ROLE)
            elif self.app_type == "diplomat":
                role = discord.utils.get(interaction.guild.roles, name="Diplomat")
            else:
                role = discord.utils.get(interaction.guild.roles, name=ALLY_ROLE)
            
            if role:
                await applicant.add_roles(role)
                
                # Notify applicant
                try:
                    await applicant.send(
                        f"🎉 **Application Approved!**\n\n"
                        f"Your {self.app_type} application has been approved!\n"
                        f"You now have the **{role.name}** role.\n\n"
                        f"Welcome to Colombia! 🇨🇴"
                    )
                except:
                    pass
        
        # Update embed
        interaction.message.embeds[0].color = discord.Color.green()
        interaction.message.embeds[0].description = (
            f"**Applicant:** <@{self.applicant_id}>\n"
            f"**Status:** ✅ Approved by {interaction.user.mention}"
        )
        
        await interaction.message.edit(embed=interaction.message.embeds[0], view=None)
        await interaction.response.send_message(
            f"✅ Application approved! {applicant.mention if applicant else 'Applicant'} has been notified.",
            ephemeral=True
        )
    
    @discord.ui.button(
        label="❌ Deny",
        style=discord.ButtonStyle.danger,
        custom_id="deny_application"
    )
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Deny application"""
        # Check permissions
        leadership_role = discord.utils.get(interaction.guild.roles, name=LEADERSHIP_ROLE)
        if leadership_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Only leadership can deny applications!",
                ephemeral=True
            )
            return
        
        # Get application
        app_key = f"{self.app_type}_{self.applicant_id}"
        application = data_manager.get("role_requests", app_key)
        
        if not application:
            await interaction.response.send_message(
                "❌ Application not found!",
                ephemeral=True
            )
            return
        
        # Update status
        application["status"] = "denied"
        application["reviewed_by"] = interaction.user.id
        application["reviewed_at"] = discord.utils.utcnow().isoformat()
        data_manager.set("role_requests", app_key, application)
        
        # Notify applicant
        applicant = interaction.guild.get_member(self.applicant_id)
        if applicant:
            try:
                await applicant.send(
                    f"❌ **Application Denied**\n\n"
                    f"Your {self.app_type} application has been denied.\n"
                    f"You may reapply in 7 days.\n\n"
                    f"If you have questions, please contact staff."
                )
            except:
                pass
        
        # Update embed
        interaction.message.embeds[0].color = discord.Color.red()
        interaction.message.embeds[0].description = (
            f"**Applicant:** <@{self.applicant_id}>\n"
            f"**Status:** ❌ Denied by {interaction.user.mention}"
        )
        
        await interaction.message.edit(embed=interaction.message.embeds[0], view=None)
        await interaction.response.send_message(
            "❌ Application denied. Applicant has been notified.",
            ephemeral=True
        )

class AllyModal(discord.ui.Modal, title="Request Ally Status"):
    """Ally request modal"""
    
    nation = discord.ui.TextInput(
        label="Your Nation",
        placeholder="What nation do you represent?",
        required=True
    )
    
    leader = discord.ui.TextInput(
        label="Nation Leader",
        placeholder="Who is your nation's leader?",
        required=True
    )
    
    def __init__(self, bot: NariñoBot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission"""
        # TODO: Send to leadership review channel
        await interaction.response.send_message(
            "✅ Your ally request has been submitted! Leadership will review it soon.",
            ephemeral=True
        )

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    """Main entry point"""
    token = os.environ.get("DISCORD_BOT_TOKEN")
    
    if not token:
        logger.error("=" * 60)
        logger.error("DISCORD_BOT_TOKEN environment variable not set!")
        logger.error("Please set it before running:")
        logger.error("  export DISCORD_BOT_TOKEN='your_token_here'")
        logger.error("=" * 60)
        return
    
    bot = NariñoBot()
    bot.run(token, log_handler=None)

if __name__ == "__main__":
    main()
