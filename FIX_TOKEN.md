# 🔧 Fix: Bot Token Not Found

## Problem
The bot is crashing with "DISCORD_BOT_TOKEN environment variable not set!" even though you've set it.

## Why This Happens
The `.env` file is in `.gitignore`, so it doesn't get pushed to GitHub. When Wispbyte pulls the code, the `.env` file doesn't exist on the server.

## Solution

### Option 1: Create .env File on Wispbyte (Recommended)

1. **Go to Wispbyte File Manager**
   - Click on your server
   - Go to "Files" tab

2. **Create .env file**
   - Click "New File"
   - Name it exactly: `.env` (with the dot at the beginning)
   - Add this content:
     ```
     DISCORD_BOT_TOKEN=your_actual_bot_token_here
     ```
   - Replace `your_actual_bot_token_here` with your real token from Discord Developer Portal
   - Click "Save"

3. **Restart the server**
   - Go back to your server dashboard
   - Click "Restart"

### Option 2: Set Environment Variable in Wispbyte

1. **Go to Wispbyte Environment Variables**
   - Click on your server
   - Go to "Settings" or "Environment" tab
   - Find "Environment Variables" section

2. **Add the variable**
   - Variable name: `DISCORD_BOT_TOKEN`
   - Value: Your actual bot token (no quotes)
   - Click "Save"

3. **Stop and Start (not just restart)**
   - Click "Stop" and wait for it to fully stop
   - Then click "Start"
   - (Environment variables only load on fresh start)

## Test the Fix

Run this command in the Wispbyte console:
```bash
python test_token.py
```

This will show you exactly what's happening with the token.

## Where to Find Your Bot Token

1. Go to https://discord.com/developers/applications
2. Click on your application
3. Go to "Bot" tab
4. Under "Token", click "Reset Token" (or "Copy" if you haven't reset it)
5. Copy the token (it looks like: `MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.Gabcde.XYZ123abc456DEF789ghi`)

## Important Notes

- **Never share your bot token publicly**
- **Don't commit .env to GitHub** (it's already in .gitignore)
- The token is case-sensitive
- No spaces or quotes around the token in .env file

## Still Not Working?

Check the Wispbyte console logs after restart. You should see:
```
✓ DISCORD_BOT_TOKEN found in environment variables
✓ Bot token found, starting bot...
```

If you still see the error, run `python test_token.py` and share the output.
