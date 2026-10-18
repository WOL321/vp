#!/bin/bash

# WispByte Startup Script for Colombia Vote Party Bot
# This script installs dependencies and starts the bot

echo "🇨🇴 Starting Colombia Vote Party Bot..."
echo ""

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo ""

# Install Playwright browsers (if playwright is installed)
if python -c "import playwright" 2>/dev/null; then
    echo "🌐 Installing Playwright browsers..."
    playwright install chromium
    echo "✓ Playwright browsers installed"
    echo ""
fi

# Check if token is set in environment
if [ -z "$DISCORD_BOT_TOKEN" ]; then
    echo "⚠️  DISCORD_BOT_TOKEN not found in environment variables"
    
    # Try to load from .env file
    if [ -f .env ]; then
        echo "✓ Found .env file, loading..."
        export $(grep -v '^#' .env | xargs)
        
        if [ -n "$DISCORD_BOT_TOKEN" ]; then
            echo "✓ Token loaded from .env file"
        else
            echo "❌ Error: DISCORD_BOT_TOKEN not found in .env file!"
            echo ""
            echo "Please create a .env file with:"
            echo "  DISCORD_BOT_TOKEN=your_token_here"
            exit 1
        fi
    else
        echo "❌ Error: DISCORD_BOT_TOKEN not set and no .env file found!"
        echo ""
        echo "Please either:"
        echo "  1. Set DISCORD_BOT_TOKEN in WispByte Environment Variables, OR"
        echo "  2. Create a .env file with: DISCORD_BOT_TOKEN=your_token_here"
        exit 1
    fi
else
    echo "✓ DISCORD_BOT_TOKEN found in environment variables"
fi

echo ""
echo "🚀 Starting bot..."
python bot.py
