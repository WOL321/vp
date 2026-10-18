# 🇨🇴 Colombia Vote Party Bot

A production-ready Discord bot for tracking vote party progress on the Colombia nation (DiplomaticaMC). Features a premium embed design with dynamic color coding, automatic scraping, and intelligent notifications.

## 🚀 Quick Deploy

Get your bot running in 5 minutes:

1. **Push to GitHub** → `git push origin main`
2. **Deploy to Railway** → [railway.app](https://railway.app) (free, runs 24/7)
3. **Add token** → Set `DISCORD_BOT_TOKEN` in Railway Variables
4. **Initialize** → Run `/voteparty setup` in Discord

📖 **See [QUICKSTART.md](QUICKSTART.md) for detailed steps**

---

## ✨ Features

### 🎨 Premium Embed Design
- **Colombian Indigenous Aesthetic**: Inspired by Muisca gold work, jade, and earth tones
- **Dynamic Color Coding**: Gold (>50 votes), Turquoise (31-50), Blood Red (≤30)
- **Visual Progress Bar**: Clean Unicode-based progress visualization
- **Status Messages**: Dynamic messages that change with progress
- **Professional Layout**: Strong visual hierarchy with clean spacing
- **Dark Theme**: Modern, polished appearance with cultural authenticity

### 🤖 Core Functionality
- **Auto-Scraping**: Scrapes vote counts every 3 minutes from 3 sites
- **Smart Cycle Detection**: Automatically resets when 250 votes reached
- **Persistent Message**: Single embed that updates in-place (never spams)
- **Role Notifications**: 🔔 button toggles VP role for notifications
- **One-Time Ping**: Alerts VP role when ≤30 votes remain (once per cycle)

### 🛠️ Admin Commands
- `/voteparty setup` - Post/update tracker embed
- `/voteparty setremaining <number>` - Manually set remaining votes
- `/voteparty setbaseline` - Reset baseline to current total
- `/voteparty forceupdate` - Force immediate scrape and update

## 📊 Vote Sites

The bot scrapes from these three sites:
1. **Minecraft-MP**: https://minecraft-mp.com/server-s349345
2. **MinecraftServers.org**: https://minecraftservers.org/server/679302
3. **Minecraft-Server-List**: https://minecraft-server-list.com/server/513054/vote/

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Discord account with Administrator permissions
- Discord Bot Application

### Installation

```bash
# Clone or download the bot
cd colombia-vote-party-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your bot token
export DISCORD_BOT_TOKEN='your_token_here'
# Windows: set DISCORD_BOT_TOKEN=your_token_here

# Run the bot
python bot.py
```

### Discord Setup

1. **Create Bot Application**
   - Go to https://discord.com/developers/applications
   - Click "New Application" → name it
   - Go to "Bot" tab → "Add Bot"
   - Enable: Server Members Intent, Message Content Intent
   - Copy the Bot Token

2. **Invite Bot to Server**
   - OAuth2 → URL Generator
   - Scopes: `bot`, `applications.commands`
   - Permissions: Send Messages, Embed Links, Manage Messages, Manage Roles, Read Message History
   - Copy URL → open in browser → select server

3. **Create VP Role**
   - Server Settings → Roles → Create Role
   - Name it exactly: **VP**
   - Ensure bot's role is ABOVE VP in hierarchy

4. **Initialize Tracker**
   - Go to desired channel
   - Run: `/voteparty setup`
   - Tracker embed appears with 🔔 button

## 🎯 How It Works

1. **Every 3 minutes**, the bot scrapes all 3 vote sites
2. **Sums the totals** and compares against baseline
3. **Calculates remaining**: `250 - (current_sum - baseline)`
4. **When remaining ≤ 0**: Automatically resets for new cycle
5. **When remaining ≤ 30**: Pings VP role (once per cycle)
6. **Members click 🔔**: Toggle VP role for notifications

## 🎨 Embed Design

The embed features:
- Large, bold remaining votes text
- Visual progress bar with percentage
- Individual site vote counts
- Clickable vote links
- Dynamic status messages
- Color-coded accent bar
- Professional spacing and hierarchy

### Color States (Colombian Indigenous Palette)
- **Gold** (#D4AF37): >50 votes remaining - "All good! Let's get started!" (Muisca gold work)
- **Turquoise** (#40E0D0): 31-50 votes remaining - "Getting close! Keep voting!" (Indigenous jewelry)
- **Blood Red** (#8B0000): ≤30 votes remaining - "Final push! Almost there!" (Ceremonial significance)

## 🔧 Technical Details

### Architecture
- **Modular Design**: Separate classes for scraping, embed building, data persistence
- **Error Handling**: Robust fallback selectors and graceful degradation
- **Persistence**: JSON-based storage for bot state
- **Async/Await**: Fully asynchronous with aiohttp

### Dependencies
```
discord.py>=2.4.0
aiohttp>=3.9.0
beautifulsoup4>=4.12.0
```

### File Structure
```
colombia-vote-party-bot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── bot_data.json       # Auto-generated persistence file
└── README.md           # This file
```

## 🐛 Troubleshooting

### "VP role not found"
- Create a role named exactly "VP" (case-sensitive)

### Site counts show "Unavailable"
- Site may be down or HTML structure changed
- Bot will retry on next scrape cycle

### Bot can't manage roles
- Check role hierarchy - bot role must be above VP role

### Commands not showing
- Wait up to 1 hour for Discord to sync slash commands globally
- Or wait a few minutes for guild-specific sync

### Embed not updating
- Ensure bot has "Manage Messages" permission
- Check bot is online and scrape loop is running

## 📝 Configuration

Edit these constants in `bot.py`:

```python
VOTE_GOAL = 250                    # Vote party goal
SCRAPE_INTERVAL_MINUTES = 3        # Scraping frequency
PING_THRESHOLD = 30                # Ping when remaining ≤ this
```

## 🔒 Security Notes

- Never commit your bot token to version control
- Use environment variables for sensitive data
- Keep dependencies updated
- Monitor bot logs for errors

## 📄 License

MIT License - Feel free to modify and use for your own servers!

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional vote sites
- Enhanced embed animations
- Statistics tracking
- Multi-server support

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review bot logs for error messages
3. Ensure all permissions are correctly set
4. Verify VP role exists and hierarchy is correct

---

**Built for the Colombia nation on DiplomaticaMC** 🇨🇴
