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
    COLOR_GOLD, COLOR_BLUE, COLOR_RED
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
        
        # Economy cog
        await self.add_cog(EconomyCog(self))
        
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
    """Welcome message system"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Send welcome message when member joins"""
        # TODO: Implement welcome channel configuration
        welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome")
        
        if welcome_channel:
            embed = discord.Embed(
                title=f"🇨🇴 Welcome to Colombia, {member.display_name}!",
                description=(
                    "Comrade, you have reached our shores. Whether you come to build a home, "
                    "stand alongside our people, or speak on behalf of another nation, there is "
                    "a place for you here.\n\n"
                    "A nation is built by its people—and every great undertaking begins with "
                    "someone willing to lay the first block.\n\n"
                    "Read our rules, meet the community, and request citizenship if you wish "
                    "to call Colombia home. Diplomats, our Foreign Affairs office awaits you.\n\n"
                    "¡Bienvenido a Colombia! 🌴\n"
                    "— Nariño"
                ),
                color=COLOR_GOLD
            )
            
            embed.set_footer(text="Citizenship: /role-request · Support: /ticket · Diplomacy: /diplomacy")
            
            await welcome_channel.send(embed=embed)

class EconomyCog(commands.Cog):
    """Economy system"""
    
    def __init__(self, bot: NariñoBot):
        self.bot = bot
    
    @discord.app_commands.command(name="balance", description="Check your balance")
    async def balance(self, interaction: discord.Interaction):
        """Check balance"""
        balance = data_manager.get("economy", f"balance_{interaction.user.id}", 100)
        
        embed = discord.Embed(
            title="💰 Your Balance",
            description=f"You have **{balance}** Pesos 💰",
            color=COLOR_GOLD
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

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

class RoleRequestView(discord.ui.View):
    """Role request buttons"""
    
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
        """Request citizenship"""
        await interaction.response.send_modal(CitizenshipModal(self.bot))
    
    @discord.ui.button(
        label="🤝 Request Ally Status",
        style=discord.ButtonStyle.secondary,
        custom_id="request_ally",
        row=0
    )
    async def ally_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Request ally status"""
        await interaction.response.send_modal(AllyModal(self.bot))
    
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

class CitizenshipModal(discord.ui.Modal, title="Request Citizenship"):
    """Citizenship request modal"""
    
    ign = discord.ui.TextInput(
        label="Minecraft Username",
        placeholder="Your in-game name",
        required=True
    )
    
    nation = discord.ui.TextInput(
        label="Current Nation",
        placeholder="What nation are you from?",
        required=True
    )
    
    town = discord.ui.TextInput(
        label="Town",
        placeholder="What town do you want to join?",
        required=True
    )
    
    def __init__(self, bot: NariñoBot):
        super().__init__()
        self.bot = bot
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission"""
        # TODO: Send to leadership review channel
        await interaction.response.send_message(
            "✅ Your citizenship request has been submitted! Leadership will review it soon.",
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
