#!/usr/bin/env python3
"""
Example script showing how to use the Telegram notifier
in various scenarios like cron jobs or monitoring scripts.
"""

from src.utils.telegram_bot import TelegramNotifier


def example_simple_notification():
    """Send a simple notification."""
    notifier = TelegramNotifier()
    notifier.send_sync("🔔 Simple notification from your script!")


def example_status_report():
    """Send a formatted status report."""
    notifier = TelegramNotifier()

    status_report = """
📊 *System Status Report*

✅ Service: Running
💾 Disk Space: 45% used
🔄 Last Backup: 2 hours ago
📈 Uptime: 15 days

_Generated automatically_
"""

    notifier.send_sync(status_report, parse_mode="Markdown")


def example_error_notification():
    """Send an error notification."""
    notifier = TelegramNotifier()

    error_message = """
❌ *Error Alert*

Service: API Server
Error: Connection timeout
Time: 2025-10-15 14:30:00
Severity: High

Action required: Check server logs
"""

    notifier.send_sync(error_message, parse_mode="Markdown")


def example_with_error_handling():
    """Example with proper error handling."""
    try:
        notifier = TelegramNotifier()

        if notifier.test_connection_sync():
            success = notifier.send_sync("✅ Process completed successfully!")
            if success:
                print("Notification sent!")
            else:
                print("Failed to send notification")
    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    print("=== Example 1: Simple Notification ===")
    example_simple_notification()

    print("\n=== Example 2: Status Report ===")
    example_status_report()

    print("\n=== Example 3: Error Notification ===")
    example_error_notification()

    print("\n=== Example 4: With Error Handling ===")
    example_with_error_handling()
