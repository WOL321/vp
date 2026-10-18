"""
Enhanced embed builder with multiple visual states and Colombia-themed design.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import discord

from config import (
    VOTE_GOAL, SCRAPE_INTERVAL_SECONDS, PING_THRESHOLD,
    COLOR_GOLD, COLOR_TURQUOISE, COLOR_RED, COLOR_CELEBRATION, COLOR_COOLDOWN,
    THUMBNAIL_URL, VOTE_SITES, EmbedState, MILESTONES
)
from i18n import t

logger = logging.getLogger("VotePartyBot")


class EmbedBuilder:
    """
    Builds premium vote party tracker embeds with multiple visual states.
    """

    @staticmethod
    def get_state(remaining: int) -> str:
        """Determine the current embed state based on remaining votes."""
        if remaining <= 0:
            return EmbedState.CELEBRATION
        elif remaining <= 30:
            return EmbedState.FINAL
        elif remaining <= 50:
            return EmbedState.CLOSE
        elif remaining <= 100:
            return EmbedState.MOMENTUM
        else:
            return EmbedState.NORMAL

    @staticmethod
    def get_color(remaining: int) -> int:
        """Get embed accent color based on remaining votes."""
        if remaining <= 0:
            return COLOR_CELEBRATION
        elif remaining <= PING_THRESHOLD:
            return COLOR_RED
        elif remaining <= 50:
            return COLOR_TURQUOISE
        else:
            return COLOR_GOLD

    @staticmethod
    def get_status_line(remaining: int, lang: str = "en") -> str:
        """Get a dynamic status message based on remaining votes."""
        if remaining <= 0:
            return t("status_complete", lang)
        elif remaining <= 10:
            return t("status_imminent", lang)
        elif remaining <= 30:
            return t("status_close", lang)
        elif remaining <= 100:
            return t("status_progress", lang)
        else:
            return t("status_started", lang)

    @staticmethod
    def build_progress_bar(percentage: float, color: int = COLOR_GOLD, length: int = 10) -> str:
        """Build a visually appealing progress bar."""
        filled = int(percentage / (100 / length))
        empty = length - filled

        if color == COLOR_RED:
            bar = "🟥" * filled + "⬜" * empty
        elif color == COLOR_TURQUOISE:
            bar = "🟩" * filled + "⬜" * empty
        else:
            bar = "🟨" * filled + "⬜" * empty

        return bar

    @staticmethod
    def get_milestones_reached(progress: int) -> list:
        """Get list of milestones that have been reached."""
        return [m for m in MILESTONES if m <= progress]

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
    def get_voting_rate(vote_history: list) -> Optional[float]:
        """Calculate current voting rate in votes per hour."""
        if len(vote_history) < 2:
            return None

        recent = vote_history[-10:]
        if len(recent) < 2:
            return None

        first_time = recent[0]["timestamp"]
        first_votes = recent[0]["total"]
        last_time = recent[-1]["timestamp"]
        last_votes = recent[-1]["total"]

        time_diff_hours = (last_time - first_time) / 3600
        vote_diff = last_votes - first_votes

        if time_diff_hours <= 0 or vote_diff <= 0:
            return None

        return vote_diff / time_diff_hours

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    @staticmethod
    def build(
        remaining: int,
        site_counts: dict[str, Optional[int]],
        last_updated: Optional[str],
        last_scrape_time: Optional[float] = None,
        vote_history: Optional[list] = None,
        cycle_start_votes: Optional[dict] = None,
        cycle_start_time: Optional[float] = None,
        last_vote_party_time: Optional[str] = None,
        lang: str = "en",
    ) -> discord.Embed:
        """
        Build a premium vote party tracker embed with state-based design.
        """
        progress = max(0, VOTE_GOAL - remaining)
        percentage = min(100, max(0, (progress / VOTE_GOAL) * 100))
        color = EmbedBuilder.get_color(remaining)
        state = EmbedBuilder.get_state(remaining)

        bar = EmbedBuilder.build_progress_bar(percentage, color)
        status_line = EmbedBuilder.get_status_line(remaining, lang)

        # Calculate voting rate and estimate
        voting_rate = EmbedBuilder.get_voting_rate(vote_history or [])
        est_completion = EmbedBuilder.estimate_completion(vote_history or [], remaining)

        # Calculate cycle duration
        cycle_duration = None
        if cycle_start_time:
            cycle_duration = datetime.now(timezone.utc).timestamp() - cycle_start_time

        # Create embed
        embed = discord.Embed(
            title=t("embed_title", lang),
            description="",
            color=color,
        )

        embed.set_thumbnail(url=THUMBNAIL_URL)

        # Build description based on state
        if state == EmbedState.CELEBRATION:
            embed.description = EmbedBuilder._build_celebration_desc(
                cycle_duration, voting_rate, lang
            )
        else:
            embed.description = EmbedBuilder._build_normal_desc(
                remaining, progress, percentage, bar, status_line,
                est_completion, voting_rate, lang
            )

        # Add separator and vote counts
        embed.description += "\n\n━━━━━━━━━━━━━━━━━━━━\n"
        embed.description += t("vote_counts", lang) + "\n"

        # Individual site votes with per-site contribution
        for i, site in enumerate(VOTE_SITES):
            name = site["name"]
            count = site_counts.get(name)
            emoji = site["emoji"]

            # Calculate contribution this cycle
            contribution = None
            if cycle_start_votes and name in cycle_start_votes and count is not None:
                contribution = count - cycle_start_votes[name]

            if count is not None:
                if contribution and contribution > 0:
                    embed.description += f"{emoji} {name} — **{count:,}** (+{contribution})\n"
                else:
                    embed.description += f"{emoji} {name} — **{count:,}**\n"
            else:
                embed.description += f"{emoji} {name} — {t('unavailable', lang)}\n"

        # Vote Now section
        embed.description += t("vote_now", lang) + "\n"
        embed.description += "━━━━━━━━━━━━━━━━\n"
        for i, site in enumerate(VOTE_SITES, 1):
            embed.description += f"{i}. [{t('vote_on', lang, name=site['name'])}]({site['url']})\n"

        # Footer
        footer_parts = []
        if last_vote_party_time:
            footer_parts.append(t("last_vp", lang, time=last_vote_party_time))

        if last_updated and last_scrape_time:
            try:
                dt = datetime.strptime(last_updated, "%Y-%m-%d %H:%M:%S")
                dt = dt.replace(tzinfo=timezone.utc)
                embed.timestamp = dt
            except ValueError:
                pass

        footer_parts.append(t("updates_every", lang, seconds=SCRAPE_INTERVAL_SECONDS))

        if footer_parts:
            embed.set_footer(text=" • ".join(footer_parts))
        else:
            embed.set_footer(text=t("waiting_first", lang))

        return embed

    @staticmethod
    def _build_normal_desc(
        remaining: int, progress: int, percentage: float,
        bar: str, status_line: str, est_completion: Optional[str],
        voting_rate: Optional[float], lang: str
    ) -> str:
        """Build description for normal/momentum/close/final states."""
        desc = (
            f"{t('votes_remaining', lang, remaining=remaining)}\n"
            f"{bar} {percentage:.1f}%\n"
            f"{t('votes_collected', lang, progress=progress, VOTE_GOAL=VOTE_GOAL)}\n\n"
            f"{status_line}"
        )

        # Add estimate if available
        if est_completion:
            desc += f"\n🕐 {t('stats_est_completion', lang)}: **{est_completion}**"

        # Add voting rate if available
        if voting_rate and voting_rate > 0:
            desc += f"\n📈 {t('stats_votes_per_hour', lang, rate=f'{voting_rate:.1f}')}"

        return desc

    @staticmethod
    def _build_celebration_desc(
        cycle_duration: Optional[float], voting_rate: Optional[float], lang: str
    ) -> str:
        """Build description for celebration state."""
        desc = t("celebration_desc", lang, goal=VOTE_GOAL) + "\n\n"

        if cycle_duration:
            duration_str = EmbedBuilder.format_duration(cycle_duration)
            desc += t("celebration_stats", lang, time=duration_str, speed=f"{voting_rate:.1f}" if voting_rate else "?")

        desc += "\n\n" + t("celebration_new_cycle", lang)

        return desc

    @staticmethod
    def build_leaderboard_embed(
        leaderboard: list, user_id: int, user_rank: tuple,
        cycle_only: bool = True, lang: str = "en"
    ) -> 'discord.Embed':
        """Build a leaderboard embed."""
        title = t("lb_title", lang)
        subtitle = t("lb_cycle", lang) if cycle_only else t("lb_alltime", lang)

        embed = discord.Embed(
            title=f"{title} — {subtitle}",
            description="",
            color=COLOR_GOLD,
        )

        if not leaderboard:
            embed.description = t("lb_no_data", lang)
        else:
            for rank, (uid, votes) in enumerate(leaderboard, 1):
                # Try to get mention, fallback to ID
                embed.description += t("lb_entry", lang, rank=rank, mention=f"<@{uid}>", votes=votes) + "\n"

            # Add user's rank if they're not in top 10
            if user_rank[0] and user_rank[0] > 10:
                embed.description += f"\n{t('lb_your_rank', lang, rank=user_rank[0], votes=user_rank[1])}"

        embed.set_thumbnail(url="🏆")

        return embed

    @staticmethod
    def build_stats_embed(stats_data, vote_history: list, remaining: int, lang: str = "en") -> 'discord.Embed':
        """Build a stats embed showing historical data."""
        embed = discord.Embed(
            title=t("stats_title", lang),
            description="",
            color=COLOR_TURQUOISE,
        )

        # Parties completed
        embed.description += f"🎉 **{t('stats_parties', lang)}:** {stats_data.parties_completed}\n"

        # Average time
        avg_time = stats_data.get_average_time()
        if avg_time:
            embed.description += f"⏱️ **{t('stats_avg_time', lang)}:** {EmbedBuilder.format_duration(avg_time)}\n"

        # Fastest party
        fastest = stats_data.get_fastest_time()
        if fastest:
            embed.description += f"⚡ **{t('stats_fastest', lang)}:** {EmbedBuilder.format_duration(fastest)}\n"

        # Total votes cast
        embed.description += f"🗳️ **{t('stats_total_votes', lang)}:** {stats_data.total_votes_cast:,}\n"

        # Current voting rate
        voting_rate = EmbedBuilder.get_voting_rate(vote_history)
        if voting_rate:
            embed.description += f"📈 **{t('stats_current_rate', lang)}:** {t('stats_votes_per_hour', lang, rate=f'{voting_rate:.1f}')}\n"

        # Estimate completion
        est = EmbedBuilder.estimate_completion(vote_history, remaining)
        if est:
            embed.description += f"🕐 **{t('stats_est_completion', lang)}:** {est}\n"

        return embed

    @staticmethod
    def build_myvotes_embed(player_data: dict, user_id: int, lang: str = "en") -> 'discord.Embed':
        """Build a personal vote stats embed."""
        embed = discord.Embed(
            title=t("myvotes_title", lang),
            description="",
            color=COLOR_GOLD,
        )

        ign = player_data.get("ign")
        if ign:
            embed.description = f"🎮 **{ign}**\n\n"

        # This cycle
        embed.description += f"📊 **{t('myvotes_this_cycle', lang)}:** {player_data.get('votes_this_cycle', 0)}\n"

        # All time
        embed.description += f"⭐ **{t('myvotes_alltime', lang)}:** {player_data.get('votes_alltime', 0)}\n"

        # Streak
        streak = player_data.get("streak", 0)
        if streak > 0:
            embed.description += f"🔥 **{t('myvotes_streak', lang)}:** {t('myvotes_days', lang, days=streak)}\n"

        # Best streak
        best_streak = player_data.get("best_streak", 0)
        if best_streak > 0:
            embed.description += f"⭐ **{t('myvotes_best_streak', lang)}:** {t('myvotes_days', lang, days=best_streak)}\n"

        # Per-site contributions
        contributions = player_data.get("cycle_contributions", {})
        if contributions:
            embed.description += "\n🗳️ **Site Contributions:**\n"
            for site_name, count in contributions.items():
                # Find emoji for site
                emoji = "⚪"
                for site in VOTE_SITES:
                    if site["name"] == site_name:
                        emoji = site["emoji"]
                        break
                embed.description += f"{emoji} {site_name}: {count}\n"

        return embed
