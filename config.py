"""
Configuration and constants for Colombia Vote Party Bot
"""

# ─── Core Settings ────────────────────────────────────────────────────────────

VOTE_GOAL = 250
SCRAPE_INTERVAL_SECONDS = 15
PING_THRESHOLD = 30
PING_DELETE_SECONDS = 300
DATA_FILE = "bot_data.json"
STATS_FILE = "bot_stats.json"

# ─── Visual Assets ────────────────────────────────────────────────────────────

BANNER_URL = "https://image.qwenlm.ai/generated-images/bea82c2c-5e60-4930-9930-6d1d9afb7f03/_result.png"
THUMBNAIL_URL = "https://cdn.discordapp.com/emojis/947652669680750613.webp"

# ─── Color Scheme (Colombia-inspired) ─────────────────────────────────────────

# Embed accent colors based on progress
COLOR_GOLD = 0xF1C40F        # Early stage (>50 remaining)
COLOR_TURQUOISE = 0x1ABC9C   # Mid stage (31-50 remaining)
COLOR_RED = 0xE74C3C         # Final push (≤30 remaining)
COLOR_CELEBRATION = 0x2ECC71 # Party complete!
COLOR_COOLDOWN = 0x95A5A6    # Between cycles

# ─── Vote Sites ───────────────────────────────────────────────────────────────

VOTE_SITES = [
    {
        "name": "Minecraft-MP",
        "url": "https://minecraft-mp.com/server-s349345",
        "emoji": "🟡",
        "fallback_patterns": [
            r"Vote\(s\)</strong></td>\s*<td>(\d+)",
            r"Vote\(s\)[^0-9]*(\d+)",
        ],
    },
    {
        "name": "MinecraftServers.org",
        "url": "https://minecraftservers.org/server/679302",
        "emoji": "🔵",
        "fallback_patterns": [
            r">Votes</div>\s*<div[^>]*>(\d+)</div>",
            r"Votes\s*</div>\s*<div[^>]*>\s*(\d+)\s*</div>",
        ],
    },
    {
        "name": "Minecraft-Server-List",
        "url": "https://minecraft-server-list.com/server/513054/vote/",
        "emoji": "🔴",
        "fallback_patterns": [
            r"(\d+) Players have voted for this server in",
            r"<b>(\d+) Votes - All time</b>",
        ],
    },
]

# ─── Cooldowns (in seconds) ───────────────────────────────────────────────────

VOTE_CLAIM_COOLDOWN = 3600  # 1 hour between vote claims
REMINDER_COOLDOWN = 1800    # 30 minutes between reminders
LEADERBOARD_REFRESH = 60    # 1 minute cache for leaderboard

# ─── Milestones ───────────────────────────────────────────────────────────────

MILESTONES = [25, 50, 75, 100, 150, 200, 225, 250]

# ─── Embed States ─────────────────────────────────────────────────────────────

class EmbedState:
    NORMAL = "normal"              # >100 remaining
    MOMENTUM = "momentum"          # 51-100 remaining
    CLOSE = "close"                # 31-50 remaining
    FINAL = "final"                # 1-30 remaining
    CELEBRATION = "celebration"    # 0 remaining (just completed)
    COOLDOWN = "cooldown"          # Between cycles
