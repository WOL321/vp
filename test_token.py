#!/usr/bin/env python3
"""
Test script to check if DISCORD_BOT_TOKEN is accessible.
Run this on Wispbyte to debug environment variable issues.
"""

import os
import sys

print("=" * 60)
print("DISCORD_BOT_TOKEN DEBUG TEST")
print("=" * 60)
print()

# Check 1: Direct environment variable
print("✓ Check 1: Direct environment variable")
token = os.environ.get("DISCORD_BOT_TOKEN")
if token:
    print(f"  ✓ Found! Token length: {len(token)} characters")
    print(f"  ✓ Token starts with: {token[:10]}...")
else:
    print("  ✗ NOT FOUND in os.environ")
print()

# Check 2: Try loading from .env file
print("✓ Check 2: .env file")
if os.path.exists(".env"):
    print("  ✓ .env file exists")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        token = os.environ.get("DISCORD_BOT_TOKEN")
        if token:
            print(f"  ✓ Loaded from .env! Token length: {len(token)} characters")
        else:
            print("  ✗ .env exists but DISCORD_BOT_TOKEN not found in it")
            print("  ✓ .env file contents:")
            with open(".env", "r") as f:
                for line in f:
                    if line.strip() and not line.startswith("#"):
                        key = line.split("=")[0]
                        print(f"    - {key}")
    except Exception as e:
        print(f"  ✗ Error loading .env: {e}")
else:
    print("  ✗ .env file does NOT exist")
    print("  → You need to create it in the File Manager")
print()

# Check 3: All environment variables
print("✓ Check 3: All environment variables")
discord_vars = [k for k in os.environ.keys() if "DISCORD" in k.upper() or "BOT" in k.upper() or "TOKEN" in k.upper()]
if discord_vars:
    print(f"  ✓ Found {len(discord_vars)} relevant variables:")
    for var in discord_vars:
        print(f"    - {var}")
else:
    print("  ✗ No DISCORD/BOT/TOKEN variables found")
print()

# Check 4: Current directory
print("✓ Check 4: Environment info")
print(f"  Current directory: {os.getcwd()}")
print(f"  Python version: {sys.version}")
print()

# Final verdict
print("=" * 60)
if os.environ.get("DISCORD_BOT_TOKEN"):
    print("✓ SUCCESS: Token is accessible!")
    print("  The bot should start successfully.")
else:
    print("✗ PROBLEM: Token is NOT accessible!")
    print()
    print("  SOLUTION:")
    print("  1. Go to Wispbyte File Manager")
    print("  2. Create a file called '.env' (with the dot)")
    print("  3. Add this line:")
    print("     DISCORD_BOT_TOKEN=your_actual_token_here")
    print("  4. Save and restart the server")
print("=" * 60)
