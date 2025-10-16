#!/usr/bin/env python3
"""
Run your Telegram command bot
This script starts a bot that listens for commands and responds
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.utils.telegram_listener import (
    TelegramCommandBot,
    start_command,
    help_command,
    ping_command,
    status_command,
    echo_handler
)
from src.utils.voice_handler import VoiceCommandHandler, download_voice_file
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
import os


# ============================================
# CUSTOM COMMAND HANDLERS
# Add your own commands here!
# ============================================

async def hello_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /hello"""
    await update.message.reply_text("👋 Hello! How can I help you today?")


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /time - Get current time"""
    from datetime import datetime
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"🕐 Current time: {current_time}")


async def joke_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /joke - Get a random joke"""
    import random
    jokes = [
        "Why don't programmers like nature? It has too many bugs! 🐛",
        "Why do programmers prefer dark mode? Because light attracts bugs! 💡",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💻",
        "Why did the developer go broke? Because he used up all his cache! 💰",
    ]
    await update.message.reply_text(random.choice(jokes))


async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /backup - Trigger backup (example)"""
    await update.message.reply_text("🔄 Starting backup process...")

    # Your backup logic here
    # For example:
    # os.system("./backup.sh")
    # or call a Python function

    await update.message.reply_text("✅ Backup completed successfully!")


async def deploy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /deploy - Trigger deployment (example)"""
    await update.message.reply_text("🚀 Deployment started...")

    # Your deployment logic here
    # For example:
    # os.system("git pull && npm install && npm run build")

    await update.message.reply_text("✅ Deployment completed!")


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /test - Run your test script"""
    await update.message.reply_text("🧪 Running test script...")

    try:
        # Import and run your test script
        from src.scripts.my_test_script import run_test
        result = run_test()
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"❌ Test failed: {str(e)}")


async def showtime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /showtime - Show recent Odoo time entries"""
    await update.message.reply_text("⏳ Fetching recent time entries from Odoo...")

    try:
        from src.utils.odoo_time_wrapper import get_recent_time_entries
        result = get_recent_time_entries(limit=5)
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def timeweek_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /timeweek - Show weekly time summary"""
    await update.message.reply_text("⏳ Fetching weekly summary from Odoo...")

    try:
        from src.utils.odoo_time_wrapper import get_weekly_summary
        result = get_weekly_summary()
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def timemonth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /timemonth - Show monthly time summary"""
    await update.message.reply_text("⏳ Fetching monthly summary from Odoo...")

    try:
        from src.utils.odoo_time_wrapper import get_monthly_summary
        result = get_monthly_summary()
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def summary_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /summary - Show comprehensive time summary with MD tables"""
    await update.message.reply_text("⏳ Generating comprehensive time summary from Odoo...")

    try:
        from src.utils.odoo_time_wrapper import get_time_summary_tables
        result = get_time_summary_tables()
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def invoiced_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /invoiced - Show invoice summary with amounts invoiced and paid"""
    await update.message.reply_text("💰 Fetching invoice summary from Odoo...")

    try:
        from src.utils.odoo_time_wrapper import get_invoice_summary
        result = get_invoice_summary()
        await update.message.reply_text(result, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


# ============================================
# VOICE MESSAGE HANDLER
# ============================================

# Initialize voice handler (will be set up in main)
voice_handler = None

# Map of command names to their handler functions
COMMAND_MAP = {
    "status": status_command,
    "test": test_command,
    "ping": ping_command,
    "time": time_command,
    "joke": joke_command,
    "hello": hello_command,
    "backup": backup_command,
    "deploy": deploy_command,
    "showtime": showtime_command,
    "timeweek": timeweek_command,
    "timemonth": timemonth_command,
    "summary": summary_command,
    "invoiced": invoiced_command,
}


async def voice_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages: transcribe and execute commands"""
    global voice_handler

    if not voice_handler:
        await update.message.reply_text(
            "❌ Voice commands are not configured.\n\n"
            "To enable voice commands:\n"
            "1. Add OPENAI_API_KEY to your .env file\n"
            "2. Restart the bot"
        )
        return

    # Step 1: Downloading
    status_msg = await update.message.reply_text("🎤 Received voice message, downloading...")

    try:
        # Download voice file
        voice_file = await update.message.voice.get_file()
        audio_path = await download_voice_file(voice_file, context.bot)

        # Step 2: Transcribing
        await status_msg.edit_text("📝 Transcribing audio...")

        # Process voice message
        result = await voice_handler.process_voice_message(audio_path)

        # Clean up temp file
        os.remove(audio_path)

        # Send transcription result
        await update.message.reply_text(result["explanation"])

        # Execute command if one was recognized
        if result["command"]:
            command_func = COMMAND_MAP.get(result["command"])
            if command_func:
                await command_func(update, context)
            else:
                await update.message.reply_text(f"⚠️ Command '{result['command']}' is not yet implemented.")

    except Exception as e:
        await update.message.reply_text(f"❌ Error processing voice message: {str(e)}")


# ============================================
# MAIN BOT SETUP
# ============================================

def main():
    """Initialize and run the bot with all commands"""
    global voice_handler

    try:
        print("=" * 50)
        print("🤖 Starting Telegram Command Bot")
        print("=" * 50)

        # Initialize bot
        bot = TelegramCommandBot()

        # Initialize voice handler if OpenAI API key is available
        try:
            voice_handler = VoiceCommandHandler()
            print("✓ Voice commands enabled")
        except ValueError:
            print("⚠️  Voice commands disabled (no OPENAI_API_KEY)")
            voice_handler = None

        # Register built-in commands
        bot.add_command("start", start_command)
        bot.add_command("help", help_command)
        bot.add_command("ping", ping_command)
        bot.add_command("status", status_command)

        # Register your custom commands
        bot.add_command("hello", hello_command)
        bot.add_command("time", time_command)
        bot.add_command("joke", joke_command)
        bot.add_command("backup", backup_command)
        bot.add_command("deploy", deploy_command)
        bot.add_command("test", test_command)

        # Register Odoo time commands
        bot.add_command("showtime", showtime_command)
        bot.add_command("timeweek", timeweek_command)
        bot.add_command("timemonth", timemonth_command)
        bot.add_command("summary", summary_command)
        bot.add_command("invoiced", invoiced_command)

        # Register voice message handler
        if voice_handler:
            bot.app.add_handler(MessageHandler(filters.VOICE, voice_message_handler))
            print("✓ Voice message handler registered")

        # Handle regular messages (non-commands)
        bot.add_message_handler(echo_handler)

        print("\n💡 Tip: Send /start to your bot to see available commands")
        if voice_handler:
            print("🎤 You can also send voice messages to execute commands!")
        print("=" * 50)

        # Start the bot (this blocks)
        bot.run()

    except ValueError as e:
        print(f"\n❌ Configuration error: {e}")
        print("\nMake sure your .env file contains:")
        print("  TELEGRAM_BOT_TOKEN=your_bot_token")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
