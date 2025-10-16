#!/usr/bin/env python3
"""
Helper script to get your Telegram chat ID
"""

import requests
import sys

BOT_TOKEN = "8389037883:AAEiN0omdIxPt_cZSRPQLVp7eUmD6NP7FUc"

def get_chat_id():
    """Fetch and display chat ID from Telegram API"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

    print("Fetching updates from Telegram API...")
    print(f"URL: {url}\n")

    try:
        response = requests.get(url)
        data = response.json()

        if not data.get("ok"):
            print("❌ API request failed")
            print(f"Response: {data}")
            return

        results = data.get("result", [])

        if not results:
            print("❌ No messages found!")
            print("\nPlease:")
            print("1. Open Telegram")
            print("2. Search for @qdoguz_bot")
            print("3. Click 'Start' or send any message")
            print("4. Run this script again")
            return

        print(f"✅ Found {len(results)} message(s)!\n")

        # Get the most recent chat ID
        latest_message = results[-1]
        chat_id = latest_message.get("message", {}).get("chat", {}).get("id")

        if chat_id:
            print(f"🎉 Your Chat ID: {chat_id}")
            print(f"\nAdd this to your .env file:")
            print(f"TELEGRAM_CHAT_ID={chat_id}")
        else:
            print("❌ Could not find chat ID in response")
            print(f"\nFull response:\n{data}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    get_chat_id()
