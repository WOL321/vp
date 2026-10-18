# ⚡ Quick Start - Get Your Bot Running in 5 Minutes

## Step 1: Get Your Bot Token
1. Go to https://discord.com/developers/applications
2. Select your bot application
3. Go to "Bot" tab
4. Click "Reset Token" (or "View Token")
5. **Copy the token** - you'll need it in Step 4

## Step 2: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

## Step 3: Deploy to Railway
1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Wait for it to deploy

## Step 4: Add Your Token
1. In Railway, click on your project
2. Go to "Variables" tab
3. Click "New Variable"
4. Name: `DISCORD_BOT_TOKEN`
5. Value: (paste your token from Step 1)
6. Click "Add"

## Step 5: Verify Bot is Running
1. Check Railway logs - you should see "Bot is ready!"
2. Go to your Discord server
3. You should see the bot come online

## Step 6: Initialize the Tracker
1. In Discord, go to the channel where you want the tracker
2. Type: `/voteparty setup`
3. The tracker embed will appear! 🎉

## Step 7: Create VP Role
1. Go to Server Settings → Roles
2. Create a role named exactly: **VP**
3. Make sure the bot's role is **above** the VP role

---

## ✅ That's It!

Your bot is now running 24/7 and will:
- Scrape vote counts every 3 minutes
- Update the embed automatically
- Ping the VP role when ≤30 votes remain
- Auto-reset when 250 votes are reached

---

## 🆘 Quick Troubleshooting

**Bot offline?**
- Check Railway logs for errors
- Verify token is correct
- Check bot has proper permissions

**Commands not working?**
- Wait 1 hour for Discord to sync commands
- Try `/voteparty setup` again

**Can't manage roles?**
- Bot role must be above VP role in hierarchy

---

**Need more help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.
