# 🇨🇴 Colombia Vote Party Bot — Premium Edition

A production-ready Discord bot for tracking vote party progress on the Colombia nation (DiplomaticaMC).

## ✨ Features

### Visual / Embed System
- **6 distinct embed states**: Normal, Building Momentum, Getting Close, Final Push, Celebration, Cooldown
- **Colombia-themed design** with gold, turquoise, and red accent colors
- **Progress bar** with colored emoji blocks
- **Time estimate** and voting speed calculation
- **Per-site contribution** tracking this cycle
- **Celebration embed** when the party completes

### Interactivity
- **5 persistent buttons** that survive bot restarts:
  - ✅ I Voted! (self-report with 1hr cooldown)
  - 🔔 Get Notified / Stop Notifications
  - 📖 How to Vote (ephemeral guide)
  - ⏰ Remind Me Later (DM after 30min)
  - 🏆 Leaderboard
- **Minecraft IGN linking** with `/link` command
- **Anti-spam cooldowns** on all interactions

### Personal & Social Layer
- **Self-reporting vote claims** with streak tracking
- **Personal stats** with `/myvotes`
- **Leaderboards** — cycle and all-time with `/leaderboard`
- **Streak system** — daily voting streaks tracked
- **Per-site contributions** shown in embed

### Stats & History
- **Track completed parties** with duration
- **Average completion time** and fastest party
- **Voting rate** (votes/hour) calculation
- **`/stats` command** with clean embed

### Quality of Life
- **Full Spanish + English** support (`/language`)
- **Clean slash command structure** (`/voteparty` group)
- **Better error handling** and recovery
- **Admin commands** to manage everything
- **Persistent data** via JSON files

## 📁 File Structure

```
.
├── bot.py              # Main bot entry point
├── config.py           # Configuration and constants
├── scraper.py          # Vote site scraper (aiohttp + cloudscraper)
├── data_manager.py     # Data persistence (BotData, PlayerData, StatsData)
├── embed_builder.py    # Premium embed system with 6 states
├── views.py            # Interactive buttons and modals
├── commands.py         # Slash commands (user + admin)
├── i18n.py             # Spanish + English translations
├── requirements.txt    # Python dependencies
├── start.sh            # Startup script for hosting
├── .env                # Environment variables (create from example)
├── bot_data.json       # Auto-generated bot state
├── player_data.json    # Auto-generated player stats
└── bot_stats.json      # Auto-generated historical stats
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
export DISCORD_BOT_TOKEN='your_bot_token_here'
```

### 3. Create Discord Bot
1. Go to https://discord.com/developers/applications
2. Create a new application → Bot tab → Create bot
3. Enable **MESSAGE CONTENT INTENT** and **SERVER MEMBERS INTENT**
4. Invite with permissions: Send Messages, Embed Links, Manage Roles, Use Slash Commands

### 4. Create Required Role
Create a role named **"VP"** in your server. Make sure the bot's role is **above** the VP role.

### 5. Run the Bot
```bash
python bot.py
```

### 6. Setup the Tracker
In Discord:
```
/voteparty setup
```

## 📋 Commands

### User Commands
| Command | Description |
|---------|-------------|
| `/link <ign>` | Link your Minecraft username |
| `/myvotes` | View your personal vote stats |
| `/leaderboard` | View the vote leaderboard |
| `/stats` | View vote party statistics |
| `/language` | Set EN/ES preference |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/voteparty setup` | Post/update tracker embed |
| `/voteparty setremaining <value>` | Set remaining votes |
| `/voteparty setbaseline [value]` | Reset cycle baseline |
| `/voteparty forceupdate` | Force immediate update |
| `/voteparty reset` | Reset all progress |

## 🔧 Configuration

Edit `config.py` to customize:
- `VOTE_GOAL` — Target votes (default: 250)
- `SCRAPE_INTERVAL_SECONDS` — Scrape frequency (default: 15s)
- `PING_THRESHOLD` — When to ping VP role (default: 30)
- `VOTE_CLAIM_COOLDOWN` — Time between vote claims (default: 3600s)
- `VOTE_SITES` — List of vote sites to scrape

## 📝 Dependencies
- `discord.py` >= 2.3.0
- `aiohttp` >= 3.9.0
- `beautifulsoup4` >= 4.12.0
- `cloudscraper` >= 1.2.71
- `python-dotenv` >= 1.0.0

## 📜 License
MIT
