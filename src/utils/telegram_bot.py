"""
Telegram Bot Connection Script
Provides functionality to send notifications and messages to Telegram
"""

import os
import asyncio
from typing import Optional
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError


class TelegramNotifier:
    """
    A class to handle Telegram bot connections and message sending.
    Ideal for sending notifications from cron jobs or other automated processes.
    """

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize the Telegram bot connection.

        Args:
            bot_token: Telegram bot token (if not provided, reads from TELEGRAM_BOT_TOKEN env var)
            chat_id: Chat ID to send messages to (if not provided, reads from TELEGRAM_CHAT_ID env var)
        """
        load_dotenv()

        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')

        if not self.bot_token:
            raise ValueError("Bot token not provided. Set TELEGRAM_BOT_TOKEN environment variable or pass bot_token parameter.")

        if not self.chat_id:
            raise ValueError("Chat ID not provided. Set TELEGRAM_CHAT_ID environment variable or pass chat_id parameter.")

        self.bot = Bot(token=self.bot_token)

    async def send_message(self, message: str, parse_mode: Optional[str] = None) -> bool:
        """
        Send a message to the configured chat.

        Args:
            message: The message text to send
            parse_mode: Optional parse mode ('Markdown', 'MarkdownV2', or 'HTML')

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            print(f"✓ Message sent successfully to chat {self.chat_id}")
            return True
        except TelegramError as e:
            print(f"✗ Failed to send message: {e}")
            return False

    async def test_connection(self) -> bool:
        """
        Test the bot connection by fetching bot information.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            bot_info = await self.bot.get_me()
            print(f"✓ Connected to Telegram bot: @{bot_info.username}")
            print(f"  Bot ID: {bot_info.id}")
            print(f"  Bot Name: {bot_info.first_name}")
            return True
        except TelegramError as e:
            print(f"✗ Connection failed: {e}")
            return False

    def send_sync(self, message: str, parse_mode: Optional[str] = None) -> bool:
        """
        Synchronous wrapper for send_message.
        Useful for calling from non-async code.

        Args:
            message: The message text to send
            parse_mode: Optional parse mode ('Markdown', 'MarkdownV2', or 'HTML')

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        return asyncio.run(self.send_message(message, parse_mode))

    def test_connection_sync(self) -> bool:
        """
        Synchronous wrapper for test_connection.
        Useful for calling from non-async code.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        return asyncio.run(self.test_connection())


async def main():
    """Example usage of the TelegramNotifier class."""
    try:
        # Initialize the notifier
        notifier = TelegramNotifier()

        # Test the connection
        print("\n=== Testing Connection ===")
        if await notifier.test_connection():
            # Send a test message
            print("\n=== Sending Test Message ===")
            await notifier.send_message("🤖 Telegram bot connection successful!")
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nPlease create a .env file with:")
        print("  TELEGRAM_BOT_TOKEN=your_bot_token")
        print("  TELEGRAM_CHAT_ID=your_chat_id")


if __name__ == "__main__":
    asyncio.run(main())
