# 🚀 WispByte Deployment Guide

## Quick Setup (5 minutes)

### Step 1: Upload Files to WispByte

1. Log into your WispByte panel
2. Select your server
3. Go to **File Manager**
4. Upload all bot files:
   - `bot.py`
   - `requirements.txt`
   - `.env.example` (optional)

**OR** use Git integration:
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .
```

### Step 2: Set Environment Variable

1. In WispByte panel, go to **Startup** or **Environment** tab
2. Add environment variable:
   - **Variable:** `DISCORD_BOT_TOKEN`
   - **Value:** Your bot token from Discord Developer Portal
3. Save changes

### Step 3: Configure Startup

In WispByte panel, set:
- **Startup Command:** `bash start.sh`
- **Python Version:** 3.10 or higher

### Step 4: Start the Server

1. Click **Start** in WispByte panel
2. Watch the console for:
   ```
   🇨🇴 Starting Colombia Vote Party Bot...
   📦 Installing dependencies...
   🚀 Starting bot...
   ✓ Logged in as BotName#1234
   ✓ Connected to X guilds
   ```

### Step 5: Initialize in Discord

1. Go to your Discord server
2. Run: `/voteparty setup`
3. Create a role named **VP** (case-sensitive)
4. Make sure bot role is **above** VP role in hierarchy

## ✅ That's It!

Your bot is now running 24/7 on WispByte!

---

## 🔧 Troubleshooting

### Bot won't start?
- Check console for errors
- Verify `DISCORD_BOT_TOKEN` is set correctly
- Make sure Python 3.10+ is installed

### Commands not showing?
- Wait up to 1 hour for Discord to sync
- Try re-inviting the bot

### Can't manage roles?
- Bot role must be **above** VP role in server settings

---

## 📊 Monitoring

- **Console:** Check WispByte console for real-time logs
- **Restart:** Use WispByte panel to restart if needed
- **Auto-restart:** WispByte should auto-restart on crash

---

## 🆘 Need Help?

1. Check WispByte console for error messages
2. Verify all environment variables are set
3. Make sure all files are uploaded correctly
4. Check bot has proper Discord permissions

---

**Your bot is live! 🇨🇴🎉**
