# 🚀 Quick Deployment Guide

## Step 1: Push to GitHub

```bash
git add .
git commit -m "🇨🇴 Nariño Bot - Ultimate Colombia Nation Bot"
git push
```

## Step 2: Wispbyte Setup

1. Go to your Wispbyte panel
2. Select your bot server
3. Make sure startup command is: `python bot.py`
4. Set environment variable:
   - Name: `DISCORD_BOT_TOKEN`
   - Value: Your bot token from Discord Developer Portal

5. Restart the server

## Step 3: Verify Bot is Online

In Discord, you should see:
```
✓ Logged in as Nariño#XXXX
✓ Connected to X guild(s)
✓ Nariño v1.0.0 is ready!
```

## Step 4: Initial Setup

### Create Required Roles
Make sure these roles exist in your server:
- `Nation Member`
- `Ally`
- `VP`
- `Verified`
- `Staff`
- `Leadership`

**Important:** Bot role must be ABOVE these roles in hierarchy!

### Setup Vote Tracker
In the channel where you want the vote tracker:
```
/voteparty setup
```

### Test Commands
```
/link YourMinecraftName    # Link your IGN
/myvotes                   # Check your votes
/leaderboard               # View leaderboard
/balance                   # Check economy
/funfact                   # Get a fun fact
/role-request              # Show role panel
```

## Step 5: Test Everything

### Vote Party
1. Click "✅ I Voted!" button
2. Verify confirmation appears and auto-deletes in 1 second
3. Check embed updates
4. Verify vote count increases

### Role Requests
1. Click "🏠 Request Citizenship"
2. Fill out the modal
3. Verify submission message

### Welcome Messages
1. Have a friend join the server
2. Verify welcome message appears in #welcome channel

### Economy
1. Run `/balance` - should show 100 Pesos
2. Run `/daily` - should give daily reward
3. Run `/work` - should earn money

## Step 6: Monitor

Run daily:
```
/voteparty scraperstats
```

Check:
- ✅ All 3 sites show >90% success rate
- ✅ No consecutive failures
- ✅ Baseline looks correct

## Troubleshooting

### Bot not responding
- Check if bot is online
- Verify DISCORD_BOT_TOKEN is set
- Check bot has proper permissions

### "⚠️ Unavailable" for sites
- Run `/voteparty scraperstats`
- Check if sites are actually down
- Review logs on Wispbyte

### Roles not working
- Verify roles exist with exact names
- Check bot role is above them in hierarchy
- Verify bot has "Manage Roles" permission

### Vote counts wrong
- Run `/voteparty fixbaseline`
- Manually check vote counts on sites
- Calculate correct total

## Success Indicators

✅ Bot is online and responding  
✅ Vote tracker shows all 3 sites  
✅ Vote claiming works (3 per cycle)  
✅ Welcome messages appear  
✅ Role requests work  
✅ Economy commands work  
✅ Bilingual support works  
✅ No errors in logs  

## Next Steps

1. Announce the bot to your server
2. Gather feedback from members
3. Monitor for a few days
4. Plan Phase 2 features (tickets, diplomacy, etc.)

---

**🎉 You're ready to go!**

¡Bienvenido a Colombia! 🇨🇴 🌴
