# 🚀 Deploy Your Vote Party Bot

## Option 1: Railway (Recommended - Free & Easy)

Railway is the easiest way to run your bot 24/7 for free.

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2: Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway will automatically detect it's a Python project

### Step 3: Add Environment Variables
In your Railway project dashboard:
1. Go to "Variables" tab
2. Add a new variable:
   - **Name:** `DISCORD_BOT_TOKEN`
   - **Value:** Your bot token from Discord Developer Portal
3. Click "Add"

### Step 4: Done!
Railway will automatically:
- Install dependencies from `requirements.txt`
- Run `bot.py`
- Keep your bot running 24/7
- Restart if it crashes

Check the logs to see your bot come online! 🎉

---

## Option 2: Heroku (Alternative)

### Step 1: Install Heroku CLI
```bash
# macOS
brew install heroku/brew/heroku

# Windows
# Download from https://devcenter.heroku.com/articles/heroku-cli
```

### Step 2: Login and Create App
```bash
heroku login
heroku create colombia-vote-party-bot
```

### Step 3: Set Environment Variable
```bash
heroku config:set DISCORD_BOT_TOKEN=your_token_here
```

### Step 4: Deploy
```bash
git push heroku main
```

### Step 5: Scale Worker
```bash
heroku ps:scale worker=1
```

---

## Option 3: Self-Hosted (VPS)

If you have a VPS (DigitalOcean, AWS, etc.):

### Step 1: Clone and Setup
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Create Environment File
```bash
echo "DISCORD_BOT_TOKEN=your_token_here" > .env
```

### Step 3: Run with Screen/Tmux
```bash
# Using screen
screen -S votebot
python bot.py
# Press Ctrl+A, then D to detach

# Using tmux
tmux new -s votebot
python bot.py
# Press Ctrl+B, then D to detach
```

### Step 4: Or Use Systemd (Better for production)
Create `/etc/systemd/system/votebot.service`:
```ini
[Unit]
Description=Colombia Vote Party Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/your/repo
Environment="DISCORD_BOT_TOKEN=your_token_here"
ExecStart=/path/to/your/repo/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable votebot
sudo systemctl start votebot
sudo systemctl status votebot
```

---

## 🔐 Security Reminders

- **NEVER commit your bot token to GitHub**
- Always use environment variables
- Keep your token secret
- If compromised, reset it immediately in Discord Developer Portal

---

## 📊 Monitoring

### Railway
- Check logs in the Railway dashboard
- Set up email notifications for crashes

### Heroku
```bash
heroku logs --tail
```

### Self-Hosted
```bash
# View logs
journalctl -u votebot -f

# Restart bot
sudo systemctl restart votebot

# Check status
sudo systemctl status votebot
```

---

## 🆘 Troubleshooting

### Bot not starting?
- Check if `DISCORD_BOT_TOKEN` is set correctly
- Verify `requirements.txt` has all dependencies
- Check logs for error messages

### Bot keeps crashing?
- Railway/Heroku will auto-restart
- Check logs for the error
- Common issues: invalid token, missing permissions, network errors

### Commands not showing up?
- Wait up to 1 hour for Discord to sync global commands
- Try kicking and re-inviting the bot
- Check bot has `applications.commands` scope

---

## 🎯 Quick Deploy Checklist

- [ ] Bot token copied from Discord Developer Portal
- [ ] Code pushed to GitHub
- [ ] Railway/Heroku account created
- [ ] Environment variable `DISCORD_BOT_TOKEN` set
- [ ] Bot deployed and running
- [ ] `/voteparty setup` command executed in Discord
- [ ] VP role created in Discord server
- [ ] Bot role positioned above VP role

---

**Your bot is now live! 🇨🇴🎉**
