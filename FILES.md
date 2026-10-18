# 📦 Project Files Overview

## Core Bot Files
- **`bot.py`** - Main bot code (Python)
- **`requirements.txt`** - Python dependencies
- **`.env.example`** - Environment variable template
- **`railway.json`** - Railway deployment config
- **`Procfile`** - Process configuration for deployment

## Documentation
- **`README.md`** - Project overview and quick deploy guide
- **`QUICKSTART.md`** - 5-minute setup guide (start here!)
- **`DEPLOYMENT.md`** - Detailed deployment options (Railway, Heroku, VPS)
- **`SECURITY.md`** - Security best practices and token management
- **`PROJECT_SUMMARY.md`** - Complete project overview

## Website
- **`src/App.tsx`** - Documentation website with live embed preview
- **`src/data/botCode.ts`** - Bot code displayed on website
- **`index.html`** - Website entry point

## Configuration
- **`.gitignore`** - Git ignore rules
- **`bot_data.json`** - Auto-generated persistence file (created at runtime)

---

## 🚀 Deployment Files Created

### 1. `railway.json`
Configures Railway deployment:
```json
{
  "deploy": {
    "startCommand": "python bot.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### 2. `Procfile`
Tells Railway/Heroku how to run the bot:
```
worker: python bot.py
```

### 3. `QUICKSTART.md`
Step-by-step guide to deploy in 5 minutes using Railway (free tier).

### 4. `DEPLOYMENT.md`
Comprehensive deployment guide with multiple options:
- Railway (recommended)
- Heroku
- Self-hosted VPS

---

## 🎯 Next Steps

1. **Read `QUICKSTART.md`** - Get your bot running in 5 minutes
2. **Push to GitHub** - `git push origin main`
3. **Deploy to Railway** - Free, runs 24/7
4. **Add token** - Set `DISCORD_BOT_TOKEN` in Railway
5. **Initialize** - Run `/voteparty setup` in Discord

---

## 📊 What You Get

✅ Premium Discord embed with dynamic colors  
✅ Auto-scraping every 3 minutes  
✅ Persistent single-message editing  
✅ Role-based notifications  
✅ Admin slash commands  
✅ Live-updating timestamps  
✅ 24/7 uptime on Railway  
✅ Complete documentation  

---

**Ready to deploy? Start with `QUICKSTART.md`!** 🚀
