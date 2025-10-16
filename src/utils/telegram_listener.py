"""
Telegram Bot Command Listener
Listens for commands sent to your bot and executes actions
"""

import os
import asyncio
from typing import Optional, Callable, Dict
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


class TelegramCommandBot:
    """
    A bot that listens for commands and messages from Telegram.
    You send commands to your bot, and it responds or triggers actions.
    """

    def __init__(self, bot_token: Optional[str] = None):
        """
        Initialize the command bot.

        Args:
            bot_token: Telegram bot token (reads from TELEGRAM_BOT_TOKEN env var if not provided)
        """
        load_dotenv()

        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')

        if not self.bot_token:
            raise ValueError("Bot token not provided. Set TELEGRAM_BOT_TOKEN environment variable.")

        self.app = Application.builder().token(self.bot_token).build()
        self.commands: Dict[str, Callable] = {}

    def add_command(self, command: str, handler: Callable):
        """
        Register a command handler.

        Args:
            command: Command name (without the /)
            handler: Async function to handle the command
                     Should accept (update: Update, context: ContextTypes.DEFAULT_TYPE)

        Example:
            async def hello_handler(update, context):
                await update.message.reply_text("Hello!")

            bot.add_command("hello", hello_handler)
        """
        self.commands[command] = handler
        self.app.add_handler(CommandHandler(command, handler))
        print(f"✓ Registered command: /{command}")

    def add_message_handler(self, handler: Callable):
        """
        Register a handler for regular text messages (non-commands).

        Args:
            handler: Async function to handle messages
                     Should accept (update: Update, context: ContextTypes.DEFAULT_TYPE)
        """
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler))
        print(f"✓ Registered message handler")

    def run(self):
        """
        Start the bot and begin listening for commands.
        This is a blocking call that runs indefinitely until stopped.
        """
        print("\n🤖 Bot is starting...")
        print(f"📡 Listening for commands...")
        if self.commands:
            print(f"📝 Registered commands: {', '.join(['/' + cmd for cmd in self.commands.keys()])}")
        print("\nPress Ctrl+C to stop\n")

        # Run the bot with polling
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


# Built-in command handlers for common use cases
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Default /start command handler"""
    await update.message.reply_text(
        "👋 Hello! I'm your personal notification bot.\n\n"
        "Available commands:\n"
        "/start - Show this message\n"
        "/help - Get help\n"
        "/ping - Test if bot is alive\n"
        "/status - Get system status\n\n"
        "Send me any message and I'll echo it back!"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Default /help command handler"""
    await update.message.reply_text(
        "🤖 Bot Commands:\n\n"
        "/start - Show welcome message\n"
        "/help - Show this help\n"
        "/ping - Test bot response\n"
        "/status - Get system status\n\n"
        "You can customize these commands in your script!"
    )


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Default /ping command handler"""
    await update.message.reply_text("🏓 Pong! Bot is alive and responding.")


async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo back any non-command message"""
    user_message = update.message.text
    await update.message.reply_text(f"You said: {user_message}")


# Example: System status command
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get basic system status"""
    import platform
    import psutil
    from datetime import datetime

    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time

        status_message = f"""
📊 *System Status*

💻 Platform: {platform.system()} {platform.release()}
🔧 CPU Usage: {cpu_percent}%
💾 Memory: {memory.percent}% used ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)
💿 Disk: {disk.percent}% used ({disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB)
⏱ Uptime: {uptime.days} days, {uptime.seconds // 3600} hours

✅ All systems operational
"""
        await update.message.reply_text(status_message, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error getting status: {str(e)}")


if __name__ == "__main__":
    """
    Example: Run a bot with default commands
    """
    try:
        bot = TelegramCommandBot()

        # Register default commands
        bot.add_command("start", start_command)
        bot.add_command("help", help_command)
        bot.add_command("ping", ping_command)
        bot.add_command("status", status_command)

        # Register message handler for non-commands
        bot.add_message_handler(echo_handler)

        # Start listening
        bot.run()

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\nMake sure your .env file contains TELEGRAM_BOT_TOKEN")
    except Exception as e:
        print(f"❌ Error: {e}")
