# 🔒 Security Guide

## What Needs to Be Secret?

### ✅ MUST BE SECRET (Never commit to code)
- **Discord Bot Token** - This is your bot's password
- **API Keys** - Any third-party service keys
- **Database passwords** - If you add a database later
- **Private keys** - SSL certificates, etc.

### ❌ SAFE TO COMMIT (Public information)
- Channel IDs
- Server/Guild IDs  
- Role IDs
- User IDs
- Vote site URLs
- Configuration values (vote goal, thresholds, etc.)

## How to Set Up Secrets

### Option 1: GitHub Secrets (Recommended for GitHub Actions)

1. **Get your bot token:**
   - Go to https://discord.com/developers/applications
   - Select your bot
   - Go to "Bot" tab
   - Click "Reset Token" or "View Token"
   - Copy the token

2. **Add to GitHub:**
   - Go to your repo on GitHub
   - Click **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `DISCORD_BOT_TOKEN`
   - Value: paste your token
   - Click **Add secret**

3. **Use in workflow:**
   ```yaml
   env:
     DISCORD_BOT_TOKEN: ${{ secrets.DISCORD_BOT_TOKEN }}
   ```

### Option 2: Environment Variables (For Railway, Heroku, etc.)

Most hosting platforms let you set environment variables in their dashboard:

**Railway:**
- Go to your project
- Click "Variables" tab
- Add `DISCORD_BOT_TOKEN` = your token

**Heroku:**
- Go to your app
- Settings → Config Vars
- Add `DISCORD_BOT_TOKEN` = your token

**DigitalOcean/VPS:**
```bash
# Add to ~/.bashrc or ~/.profile
export DISCORD_BOT_TOKEN="your_token_here"

# Or create a systemd service file with Environment=
```

### Option 3: Local Development (.env file)

1. **Copy the template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env:**
   ```bash
   DISCORD_BOT_TOKEN=your_actual_token_here
   ```

3. **The bot will automatically load it** (thanks to python-dotenv)

4. **Never commit .env!** (It's already in .gitignore)

## How the Bot Loads the Token

The bot checks for the token in this order:

1. **Environment variable** (from GitHub Secrets, hosting platform, etc.)
2. **.env file** (for local development)
3. **Error** if neither is found

```python
token = os.environ.get("DISCORD_BOT_TOKEN")
if not token:
    logger.error("DISCORD_BOT_TOKEN not found!")
    return
```

## Common Mistakes to Avoid

### ❌ DON'T DO THIS:
```python
# BAD: Hardcoded token
TOKEN = "MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.G12345.abcdef123456"
bot.run(TOKEN)
```

```python
# BAD: Token in config file that gets committed
config = {
    "token": "your_token_here"
}
```

### ✅ DO THIS:
```python
# GOOD: Environment variable
token = os.environ.get("DISCORD_BOT_TOKEN")
bot.run(token)
```

## What If My Token Gets Leaked?

If you accidentally commit your token or it gets exposed:

1. **Immediately go to Discord Developer Portal**
2. **Click "Reset Token"**
3. **Update your secrets** with the new token
4. **Check your git history** - the old token is still there!

To remove it from git history:
```bash
# Use BFG Repo-Cleaner or git filter-branch
# Then force push (be careful!)
git push --force
```

## Testing Your Setup

### Local Test:
```bash
# Create .env file
echo "DISCORD_BOT_TOKEN=your_token" > .env

# Run the bot
python bot.py

# You should see: "Logged in as BotName#1234"
```

### GitHub Actions Test:
```bash
# Push to main branch
git push origin main

# Check Actions tab - should see deployment running
# Check logs for: "Logged in as BotName#1234"
```

## Security Checklist

- [ ] Bot token is in GitHub Secrets (not in code)
- [ ] `.env` file is in `.gitignore`
- [ ] `.env.example` is committed (as a template)
- [ ] No tokens in git history
- [ ] Using environment variables in deployment
- [ ] Token is strong (Discord generates secure tokens)
- [ ] Bot has minimal required permissions
- [ ] Regular security audits (check who has access)

## Additional Security Tips

### 1. Limit Bot Permissions
Only request the permissions your bot actually needs:
- Send Messages
- Embed Links
- Read Message History
- Manage Roles (for VP role)
- Use Slash Commands

### 2. Use a Separate Bot Account
Never use your personal Discord account token for bots.

### 3. Regular Token Rotation
Consider resetting your token periodically (every 3-6 months).

### 4. Monitor Bot Activity
Check Discord Developer Portal for unusual activity.

### 5. Keep Dependencies Updated
```bash
pip install --upgrade -r requirements.txt
```

## Need Help?

If you're unsure about security:
1. Never share your token with anyone
2. Use GitHub Secrets for all sensitive data
3. When in doubt, reset the token
4. Ask in Discord's developer community

---

**Remember:** Your bot token is like a password. Treat it with the same level of security! 🔐
