"""
Nariño Bot Configuration
Named after Antonio Nariño - Colombian independence leader
"""

import os
from typing import Dict, List

# ─── Core Settings ────────────────────────────────────────────────────────────

BOT_NAME = "Nariño"
BOT_VERSION = "1.0.0"
BOT_COLOR = 0xF1C40F  # Colombian yellow

# ─── Vote Party Settings ──────────────────────────────────────────────────────

VOTE_GOAL = 250
SCRAPE_INTERVAL_SECONDS = 15
PING_THRESHOLD = 30
PING_DELETE_SECONDS = 300
MAX_VOTES_PER_CYCLE = 3

# ─── Economy Settings (DiplomaticaMC Gold Standard) ───────────────────────────

# DiplomaticaMC uses GOLD as currency (ingots and blocks)
# This tracks gold holdings, not virtual currency
STARTING_GOLD = 0  # Players start with 0 gold
VOTE_REWARD_GOLD = 64  # 64 gold ingots (1 stack) for voting
DAILY_REWARD_GOLD = 16  # 16 gold ingots daily
WORK_REWARD_GOLD = 8  # 8 gold ingots for work
CURRENCY_NAME = "Gold"
CURRENCY_EMOJI = "🪙"

# Towny Costs (DiplomaticaMC specific)
TOWN_CREATION_COST = 64  # 64 gold ingots to create a town
NATION_CREATION_COST = 1024  # 1024 gold ingots to create a nation
TOWN_CLAIM_COST = 16  # 16 gold per chunk claim

# Inactivity Settings
INACTIVITY_WARNING_DAYS = 50  # Warn at 50 days
INACTIVITY_DELETION_DAYS = 60  # Delete Towny data at 60 days

# ─── Activity Settings ────────────────────────────────────────────────────────

INACTIVE_DAYS = 30
MESSAGE_COOLDOWN = 60  # seconds between XP gains
VOICE_COOLDOWN = 60

# ─── Moderation Settings ──────────────────────────────────────────────────────

MAX_WARNINGS = 3
WARNING_EXPIRE_DAYS = 30
AUTOMOD_ENABLED = True

# ─── Ticket Settings ──────────────────────────────────────────────────────────

TICKET_CATEGORY_NAME = "🎫 Support Tickets"
TICKET_STAFF_ROLE = "Staff"

# ─── Role Settings ────────────────────────────────────────────────────────────

NATION_MEMBER_ROLE = "Nation Member"
ALLY_ROLE = "Ally"
VP_ROLE = "VP"
VERIFIED_ROLE = "Verified"
STAFF_ROLE = "Staff"
LEADERSHIP_ROLE = "Leadership"

# ─── Vote Sites ───────────────────────────────────────────────────────────────

VOTE_SITES = [
    {
        "name": "Minecraft-MP",
        "url": "https://minecraft-mp.com/server-s349345",
        "emoji": "🟡",
        "fallback_patterns": [
            r"Vote\(s\)</strong></td>\s*<td[^>]*>\s*(\d+)\s*</td>",
            r"Vote\(s\)[^0-9]{0,50}(\d+)",
        ],
    },
    {
        "name": "MinecraftServers.org",
        "url": "https://minecraftservers.org/server/679302",
        "emoji": "🔵",
        "fallback_patterns": [
            r">Votes</div>\s*<div[^>]*>\s*(\d+)\s*</div>",
            r"Votes\s*</div>\s*<div[^>]*>\s*(\d+)\s*</div>",
        ],
    },
    {
        "name": "Minecraft-Server-List",
        "url": "https://minecraft-server-list.com/server/513054/vote/",
        "emoji": "🔴",
        "fallback_patterns": [
            r"(\d+)\s+Players have voted for this server in",
            r"<b>(\d+)\s+Votes\s*-\s*All time</b>",
        ],
    },
]

# ─── Cooldowns ────────────────────────────────────────────────────────────────

VOTE_CLAIM_COOLDOWN = 3600  # 1 hour
REMINDER_COOLDOWN = 1800    # 30 minutes
DAILY_REWARD_COOLDOWN = 86400  # 24 hours
WORK_COOLDOWN = 3600  # 1 hour

# ─── File Paths ───────────────────────────────────────────────────────────────

DATA_DIR = "data"
BOT_DATA_FILE = f"{DATA_DIR}/bot_data.json"
PLAYER_DATA_FILE = f"{DATA_DIR}/player_data.json"
STATS_FILE = f"{DATA_DIR}/stats.json"
ECONOMY_FILE = f"{DATA_DIR}/economy.json"
TICKETS_FILE = f"{DATA_DIR}/tickets.json"
DIPLOMACY_FILE = f"{DATA_DIR}/diplomacy.json"
TOWNS_FILE = f"{DATA_DIR}/towns.json"
EVENTS_FILE = f"{DATA_DIR}/events.json"
MODLOG_FILE = f"{DATA_DIR}/modlog.json"

# ─── Embed States ─────────────────────────────────────────────────────────────

class EmbedState:
    NORMAL = "normal"
    MOMENTUM = "momentum"
    CLOSE = "close"
    FINAL = "final"
    CELEBRATION = "celebration"
    COOLDOWN = "cooldown"

# ─── Colors ───────────────────────────────────────────────────────────────────

COLOR_GOLD = 0xF1C40F
COLOR_BLUE = 0x003893  # Colombian blue
COLOR_RED = 0xCE1126   # Colombian red
COLOR_TURQUOISE = 0x1ABC9C
COLOR_CELEBRATION = 0x2ECC71
COLOR_COOLDOWN = 0x95A5A6

# ─── Milestones ───────────────────────────────────────────────────────────────

MILESTONES = [25, 50, 75, 100, 150, 200, 225, 250]

# ─── Fun Facts (Colombia) ────────────────────────────────────────────────────

FUN_FACTS = {
    "en": [
        "Colombia is the only South American country with coastlines on both the Pacific Ocean and the Caribbean Sea!",
        "Colombia produces 12% of the world's coffee!",
        "Bogotá, the capital, is higher than most European mountains at 2,640 meters!",
        "Colombia has more bird species than any other country - over 1,900!",
        "The emerald industry in Colombia produces 60% of the world's emeralds!",
        "Colombia is named after Christopher Columbus (Cristóbal Colón in Spanish)!",
        "The Amazon rainforest covers 35% of Colombia's territory!",
        "Colombia has over 50 national natural parks!",
        "Shakira and J Balvin are from Colombia!",
        "Colombia is the world's leading producer of emeralds!",
    ],
    "es": [
        "¡Colombia es el único país sudamericano con costas en el Océano Pacífico y el Mar Caribe!",
        "¡Colombia produce el 12% del café del mundo!",
        "¡Bogotá, la capital, está más alta que la mayoría de las montañas europeas a 2,640 metros!",
        "¡Colombia tiene más especies de aves que cualquier otro país - más de 1,900!",
        "¡La industria esmeraldina de Colombia produce el 60% de las esmeraldas del mundo!",
        "¡Colombia lleva el nombre de Cristóbal Colón!",
        "¡La selva amazónica cubre el 35% del territorio colombiano!",
        "¡Colombia tiene más de 50 parques naturales nacionales!",
        "¡Shakira y J Balvin son de Colombia!",
        "¡Colombia es el principal productor mundial de esmeraldas!",
    ]
}

# ─── Trivia Questions ─────────────────────────────────────────────────────────

TRIVIA_QUESTIONS = {
    "en": [
        {"q": "What is the capital of Colombia?", "a": "Bogotá"},
        {"q": "What river is the longest in Colombia?", "a": "Magdalena"},
        {"q": "What precious stone is Colombia famous for?", "a": "Emerald"},
        {"q": "Who is known as 'The Liberator' of Colombia?", "a": "Simón Bolívar"},
        {"q": "What is Colombia's national bird?", "a": "Andean Condor"},
        {"q": "What ocean borders Colombia to the west?", "a": "Pacific"},
        {"q": "What sea borders Colombia to the north?", "a": "Caribbean"},
        {"q": "What famous Colombian singer is known as the 'Queen of Latin Music'?", "a": "Shakira"},
    ],
    "es": [
        {"q": "¿Cuál es la capital de Colombia?", "a": "Bogotá"},
        {"q": "¿Qué río es el más largo de Colombia?", "a": "Magdalena"},
        {"q": "¿Qué piedra preciosa es famosa en Colombia?", "a": "Esmeralda"},
        {"q": "¿Quién es conocido como 'El Libertador' de Colombia?", "a": "Simón Bolívar"},
        {"q": "¿Cuál es el ave nacional de Colombia?", "a": "Cóndor Andino"},
        {"q": "¿Qué océano bordea Colombia al oeste?", "a": "Pacífico"},
        {"q": "¿Qué mar bordea Colombia al norte?", "a": "Caribe"},
        {"q": "¿Qué famosa cantante colombiana es conocida como la 'Reina de la Música Latina'?", "a": "Shakira"},
    ]
}
