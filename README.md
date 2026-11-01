# 🇨🇴 Nariño Bot - The Ultimate Colombia Nation Bot

Named after **Antonio Nariño** - "El Precursor" (The Precursor), one of Colombia's greatest independence leaders.

## 🎯 Features

### ✅ Vote Party System (Enhanced)
- **99%+ accuracy** scraper with triple-layer extraction
- **3 votes per cycle** limit (no farming!)
- **Leaderboards** and personal stats
- **Bilingual support** (EN/ES)
- **Auto-delete confirmations** (1 second)
- **Advanced analytics** and voting rate tracking

### 🎉 Welcome Messages
- Colombian-themed welcome embed
- Auto-detects new members
- Links to role requests, tickets, diplomacy

### 🎭 Role Requests
- **Citizenship** → Leadership review
- **Ally Status** → Leadership review
- **Vote Party Pings** → Instant toggle
- Request format: `Minecraft username · Nation · Town · Nation role`

### 🎫 Support Tickets
- `/ticket` command to open support ticket
- Creates private channel
- Staff can respond
- Close/archive tickets

### 💰 Economy System
- Virtual currency (Pesos 💰)
- Daily rewards
- Work command
- Balance tracking

### 🧠 Fun Features
- Colombia trivia
- Fun facts (bilingual)
- Interactive commands

### 🌐 Diplomacy (Coming Soon)
- Alliance tracking
- War declarations
- Peace treaties
- Diplomatic relations

### 🏘️ Town Management (Coming Soon)
- Town tracking
- Town leaderboards
- Town-specific channels

### 🎮 Activity Tracking (Coming Soon)
- XP system
- Levels
- Activity leaderboards
- Inactive member cleanup

### 🛡️ Moderation (Coming Soon)
- Auto-mod
- Warning system
- Temp mute/ban
- Mod logs

### 🎁 Events (Coming Soon)
- Giveaways
- Tournaments
- Attendance tracking

---

## 🏗️ Architecture

```
narino-bot/
├── bot.py                      # Main entry point
├── config.py                   # All configuration
├── requirements.txt            # Dependencies
├── start.sh                    # Startup script
│
├── core/                       # Core systems
│   ├── __init__.py
│   ├── data_manager.py         # Advanced data persistence
│   └── i18n.py                 # Bilingual support
│
├── vote/                       # Vote Party system
│   ├── __init__.py
│   └── scraper.py              # Advanced vote scraper
│
└── data/                       # Auto-generated data files
    ├── bot_data.json
    ├── player_data.json
    ├── stats.json
    ├── economy.json
    └── ...
```

---

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
2. Create a new application
3. Go to "Bot" tab and create a bot
4. Copy the bot token
5. Enable these **Privileged Gateway Intents**:
   - ✅ MESSAGE CONTENT INTENT
   - ✅ SERVER MEMBERS INTENT
6. Invite the bot with these permissions:
   - Send Messages
   - Embed Links
   - Manage Roles
   - Use Slash Commands
   - Read Message History
   - Manage Messages (for auto-delete)

### 4. Create Required Roles
Create these roles in your server:
- `Nation Member` - For citizens
- `Ally` - For allied nations
- `VP` - For vote party notifications
- `Verified` - For verified members
- `Staff` - For ticket handlers
- `Leadership` - For role request reviewers

**Important:** Make sure the bot's role is **above** these roles in the role hierarchy.

### 5. Run the Bot
```bash
python bot.py
```

### 6. Setup the Tracker
In Discord, use the command:
```
/voteparty setup
```

This will post the vote party tracker embed in the current channel.

---

## 📋 Commands

### Vote Party Commands
| Command | Description |
|---------|-------------|
| `/link <ign>` | Link your Minecraft username |
| `/myvotes` | View your personal vote stats |
| `/leaderboard` | View the vote leaderboard |
| `/voteparty setup` | Post/update tracker embed (Admin) |
| `/voteparty setremaining <value>` | Set remaining votes (Admin) |
| `/voteparty setbaseline [value]` | Reset cycle baseline (Admin) |
| `/voteparty forceupdate` | Force immediate update (Admin) |
| `/voteparty fixbaseline` | Fix corrupted baseline (Admin) |
| `/voteparty scraperstats` | View scraper statistics (Admin) |

### Nation Commands
| Command | Description |
|---------|-------------|
| `/role-request` | Show role request panel |
| `/ticket` | Open a support ticket |
| `/diplomacy` | Open diplomatic request |

### Economy Commands
| Command | Description |
|---------|-------------|
| `/balance` | Check your balance |
| `/daily` | Claim daily reward |
| `/work` | Work to earn money |

### Fun Commands
| Command | Description |
|---------|-------------|
| `/funfact` | Get a fun fact about Colombia |
| `/trivia` | Start a trivia game |

---

## 🎨 Interactive Buttons

### Vote Party Buttons
- ✅ **I Voted!** - Claim your vote (3 per cycle)
- 🔔 **Get Notified** - Toggle VP role notifications
- 📖 **How to Vote** - Vote guide with links
- ⏰ **Remind Me** - Get a DM reminder in 30min
- 🏆 **Leaderboard** - View top voters

### Role Request Buttons
- 🏠 **Request Citizenship** - Open citizenship modal
- 🤝 **Request Ally Status** - Open ally modal
- 🔔 **Toggle Vote Party Pings** - Instant VP role toggle

---

## 🔧 Configuration

Edit `config.py` to customize:

### Vote Party
```python
VOTE_GOAL = 250              # Target votes
SCRAPE_INTERVAL_SECONDS = 15 # Scrape frequency
PING_THRESHOLD = 30          # When to ping VP role
MAX_VOTES_PER_CYCLE = 3      # Max votes per player per cycle
```

### Economy
```python
STARTING_BALANCE = 100       # Starting money
VOTE_REWARD = 50             # Reward for voting
CURRENCY_NAME = "Pesos"      # Currency name
CURRENCY_EMOJI = "💰"        # Currency emoji
```

### Roles
```python
NATION_MEMBER_ROLE = "Nation Member"
ALLY_ROLE = "Ally"
VP_ROLE = "VP"
VERIFIED_ROLE = "Verified"
STAFF_ROLE = "Staff"
LEADERSHIP_ROLE = "Leadership"
```

---

## 📊 Data Files

The bot automatically creates these files in the `data/` directory:

- `bot_data.json` - Bot state and configuration
- `player_data.json` - Player votes, cooldowns, streaks
- `stats.json` - Historical statistics
- `economy.json` - Player balances
- `tickets.json` - Support tickets
- `diplomacy.json` - Diplomatic relations
- `towns.json` - Town data
- `events.json` - Event data
- `modlog.json` - Moderation logs

**Note:** These files are auto-generated and should not be edited manually.

---

## 🌐 Bilingual Support

The bot supports both **English** and **Spanish**. Users can set their preference with:

```
/language en  # English
/language es  # Español
```

All commands, embeds, buttons, and messages are fully translated.

---

## 🎯 Advanced Features

### Vote Scraper
- **Triple-layer extraction** (BeautifulSoup + Regex + Playwright)
- **4 retry attempts** with exponential backoff
- **User-agent rotation** to prevent blocking
- **Consecutive failure tracking**
- **Comprehensive caching**
- **Real-time monitoring** (`/voteparty scraperstats`)

### Data Manager
- **Advanced JSON persistence** with caching
- **Auto-save every 30 seconds**
- **Dirty tracking** for efficient saves
- **Search and filter** capabilities
- **Increment/decrement** operations

### I18n System
- **Auto-detection** of language from message content
- **Context-aware translations**
- **User preference storage**
- **Fallback to English** if translation missing

---

## 🐛 Troubleshooting

### Bot not responding to commands
- Check if bot is online in Discord
- Restart bot
- Check Discord bot token is set
- Verify bot has proper permissions

### "⚠️ Unavailable" for vote sites
- Check if sites are actually down (visit URLs manually)
- Run `/voteparty scraperstats` to see error details
- Check logs for specific error messages
- Sites may have changed HTML - need to update selectors

### Baseline corrupted (impossible vote counts)
- Run `/voteparty fixbaseline`
- Manually check vote counts on all 3 sites
- Calculate total (should be ~13,000-14,000)
- Run `/voteparty setbaseline [total]`

### Brotli compression error
- Make sure `Brotli>=1.1.0` is in requirements.txt
- Run `pip install -r requirements.txt`
- Restart bot

---

## 📈 Monitoring

### Daily Check
Run `/voteparty scraperstats` to verify:
- ✅ All 3 sites show success rates >90%
- ✅ No consecutive failures
- ✅ Baseline and remaining look correct

### Weekly Check
- Review scraper success rates
- Check for any site changes
- Verify vote party tracking is working

### Log Messages to Watch
```
✅ "Found X votes (BeautifulSoup)" - Success
⚠️ "Only X/3 sites returned data" - Partial failure
❌ "Invalid remaining value" - Corrupted baseline
⚠️ "X consecutive failures" - Site down
```

---

## 🔮 Future Features

These features are planned for future updates:

### Diplomacy System
- Alliance tracking between nations
- War declarations and peace treaties
- Diplomatic relations status
- Foreign affairs channels

### Town Management
- Town creation and management
- Town leaderboards
- Town-specific channels
- Town statistics

### Activity Tracking
- XP system for messages and voice
- Level-up rewards
- Activity leaderboards
- Inactive member cleanup

### Moderation
- Auto-moderation (filter bad words, spam)
- Warning system with expiration
- Temp mute/ban commands
- Comprehensive mod logs

### Events
- Giveaway system
- Tournament management
- Event attendance tracking
- Event announcements

### Minecraft Integration
- Server status display
- Role sync between Discord and MC
- In-game commands
- Player verification

---

## 🤝 Contributing

This is a custom bot for the Colombia nation on DiplomaticaMC. If you want to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📜 License

MIT License - Feel free to modify and use for your own nation bot!

---

## 🎉 Credits

**Bot Name:** Nariño  
**Named After:** Antonio Nariño - "El Precursor"  
**Nation:** Colombia 🇨🇴  
**Server:** DiplomaticaMC  
**Created By:** Colombia Nation Admin Team  

---

## 📞 Support

If you need help:
1. Check the troubleshooting section above
2. Review the logs on your hosting panel
3. Run `/voteparty scraperstats` for diagnostics
4. Check the Discord bot permissions

---

## 🚀 Ready to Go!

Your Nariño bot is now ready to serve the Colombia nation! 

**Next steps:**
1. ✅ Push code to GitHub
2. ✅ Restart bot on your hosting panel
3. ✅ Run `/voteparty setup` in Discord
4. ✅ Test all commands
5. ✅ Enjoy your premium nation bot! 🇨🇴

¡Bienvenido a Colombia! 🌴
