#!/bin/bash

# WispByte Startup Script for Colombia Vote Party Bot
# This script installs dependencies and starts the bot

echo "🇨🇴 Starting Colombia Vote Party Bot..."

# Install Python dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if token is set
if [ -z "$DISCORD_BOT_TOKEN" ]; then
    echo "❌ Error: DISCORD_BOT_TOKEN environment variable not set!"
    echo "Please set it in your WispByte panel under Environment Variables"
    exit 1
fi

# Start the bot
echo "🚀 Starting bot..."
python bot.py
