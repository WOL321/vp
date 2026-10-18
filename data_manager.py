"""
Data management module for persistent storage of bot state, player stats, and history.
"""

import json
import os
import logging
from datetime import datetime, timezone
from typing import Optional
from config import VOTE_GOAL, DATA_FILE, STATS_FILE

logger = logging.getLogger("VotePartyBot")


class BotData:
    """Handles persistent storage of core bot state."""

    def __init__(self, filepath: str = DATA_FILE):
        self.filepath = filepath
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load data file: {e}")
        return self._defaults()

    def _defaults(self) -> dict:
        return {
            "message_id": None,
            "channel_id": None,
            "baseline": 0,
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
            "cycle_start_time": None,
        }

    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save data file: {e}")

    # Generic property accessors
    def get(self, key: str, default=None):
        return self.data.get(key, default)

    def set(self, key: str, value):
        self.data[key] = value
        self.save()

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

    @property
    def cycle_start_time(self) -> Optional[float]:
        return self.data.get("cycle_start_time")

    @cycle_start_time.setter
    def cycle_start_time(self, value: Optional[float]):
        self.data["cycle_start_time"] = value


class PlayerData:
    """Handles persistent storage of player vote claims, stats, and leaderboards."""

    def __init__(self, filepath: str = "player_data.json"):
        self.filepath = filepath
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load player data: {e}")
        return self._defaults()

    def _defaults(self) -> dict:
        return {
            "players": {},       # user_id -> player data
            "user_langs": {},    # user_id -> "en" or "es"
            "reminders": {},     # user_id -> reminder timestamp
        }

    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save player data: {e}")

    def get_player(self, user_id: int) -> dict:
        """Get or create player data."""
        uid = str(user_id)
        if uid not in self.data["players"]:
            self.data["players"][uid] = {
                "ign": None,                    # Minecraft username
                "votes_this_cycle": 0,
                "votes_alltime": 0,
                "last_claim_time": None,
                "streak": 0,
                "best_streak": 0,
                "last_vote_date": None,         # YYYY-MM-DD
                "cycle_contributions": {},       # site_name -> votes claimed
            }
        return self.data["players"][uid]

    def claim_vote(self, user_id: int, site_name: Optional[str] = None) -> dict:
        """Record a vote claim. Returns updated player data."""
        player = self.get_player(user_id)
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")

        player["votes_this_cycle"] += 1
        player["votes_alltime"] += 1
        player["last_claim_time"] = now.timestamp()

        # Track streak
        if player["last_vote_date"] != today:
            yesterday = (now.timestamp() - 86400)
            if player["last_vote_date"]:
                last_date = datetime.strptime(player["last_vote_date"], "%Y-%m-%d")
                last_ts = last_date.replace(tzinfo=timezone.utc).timestamp()
                if yesterday - last_ts < 86400:  # Voted yesterday
                    player["streak"] += 1
                else:
                    player["streak"] = 1
            else:
                player["streak"] = 1
            player["last_vote_date"] = today
            player["best_streak"] = max(player["best_streak"], player["streak"])

        # Track per-site contribution
        if site_name:
            if site_name not in player["cycle_contributions"]:
                player["cycle_contributions"][site_name] = 0
            player["cycle_contributions"][site_name] += 1

        self.save()
        return player

    def reset_cycle(self):
        """Reset all players' cycle votes (called when vote party completes)."""
        for uid in self.data["players"]:
            self.data["players"][uid]["votes_this_cycle"] = 0
            self.data["players"][uid]["cycle_contributions"] = {}
        self.save()

    def set_ign(self, user_id: int, ign: str):
        """Set a player's Minecraft username."""
        player = self.get_player(user_id)
        player["ign"] = ign
        self.save()

    def get_ign(self, user_id: int) -> Optional[str]:
        """Get a player's Minecraft username."""
        player = self.get_player(user_id)
        return player.get("ign")

    def get_leaderboard(self, limit: int = 10, cycle_only: bool = True) -> list:
        """Get top voters. Returns list of (user_id, votes) tuples."""
        key = "votes_this_cycle" if cycle_only else "votes_alltime"
        players = []
        for uid, pdata in self.data["players"].items():
            votes = pdata.get(key, 0)
            if votes > 0:
                players.append((int(uid), votes))
        players.sort(key=lambda x: x[1], reverse=True)
        return players[:limit]

    def get_player_rank(self, user_id: int, cycle_only: bool = True) -> tuple:
        """Get player's rank and votes. Returns (rank, votes) or (None, 0)."""
        key = "votes_this_cycle" if cycle_only else "votes_alltime"
        player_votes = self.get_player(user_id).get(key, 0)
        if player_votes == 0:
            return None, 0

        rank = 1
        for uid, pdata in self.data["players"].items():
            if int(uid) != user_id and pdata.get(key, 0) > player_votes:
                rank += 1
        return rank, player_votes

    def set_reminder(self, user_id: int, timestamp: float):
        """Set a reminder for a user."""
        self.data["reminders"][str(user_id)] = timestamp
        self.save()

    def get_reminder(self, user_id: int) -> Optional[float]:
        """Get reminder timestamp for a user."""
        return self.data["reminders"].get(str(user_id))

    def clear_reminder(self, user_id: int):
        """Clear a user's reminder."""
        self.data["reminders"].pop(str(user_id), None)
        self.save()

    def set_lang(self, user_id: int, lang: str):
        """Set user's preferred language."""
        self.data["user_langs"][str(user_id)] = lang
        self.save()

    def get_lang(self, user_id: int) -> str:
        """Get user's preferred language."""
        return self.data["user_langs"].get(str(user_id), "en")

    @property
    def user_langs(self) -> dict:
        return self.data.get("user_langs", {})


class StatsData:
    """Tracks historical stats across vote parties."""

    def __init__(self, filepath: str = STATS_FILE):
        self.filepath = filepath
        self.data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load stats: {e}")
        return self._defaults()

    def _defaults(self) -> dict:
        return {
            "parties_completed": 0,
            "completion_times": [],    # list of seconds to complete
            "total_votes_cast": 0,     # sum of all player claims
            "party_history": [],       # list of {date, duration, top_contributors}
        }

    def save(self):
        try:
            with open(self.filepath, "w") as f:
                json.dump(self.data, f, indent=2, default=str)
        except IOError as e:
            logger.error(f"Failed to save stats: {e}")

    def record_party(self, duration_seconds: float, top_contributors: list):
        """Record a completed vote party."""
        self.data["parties_completed"] += 1
        self.data["completion_times"].append(duration_seconds)

        # Keep only last 50 completion times
        if len(self.data["completion_times"]) > 50:
            self.data["completion_times"] = self.data["completion_times"][-50:]

        self.data["party_history"].append({
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
            "duration": duration_seconds,
            "top_contributors": top_contributors[:5],
        })

        # Keep only last 20 party history entries
        if len(self.data["party_history"]) > 20:
            self.data["party_history"] = self.data["party_history"][-20:]

        self.save()

    def add_votes_cast(self, count: int):
        """Add to total votes cast counter."""
        self.data["total_votes_cast"] += count
        self.save()

    @property
    def parties_completed(self) -> int:
        return self.data.get("parties_completed", 0)

    @property
    def completion_times(self) -> list:
        return self.data.get("completion_times", [])

    @property
    def total_votes_cast(self) -> int:
        return self.data.get("total_votes_cast", 0)

    @property
    def party_history(self) -> list:
        return self.data.get("party_history", [])

    def get_average_time(self) -> Optional[float]:
        """Get average completion time in seconds."""
        times = self.completion_times
        if not times:
            return None
        return sum(times) / len(times)

    def get_fastest_time(self) -> Optional[float]:
        """Get fastest completion time in seconds."""
        times = self.completion_times
        if not times:
            return None
        return min(times)
