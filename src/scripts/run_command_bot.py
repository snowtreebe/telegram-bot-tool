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
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, ConversationHandler, filters
import os
from datetime import date as dt_date


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
# TIME LOGGING CONVERSATION HANDLER
# ============================================

# Conversation states
SEARCHING_PROJECT, SELECTING_PROJECT, SEARCHING_TASK, SELECTING_TASK, ENTERING_HOURS, ENTERING_DESCRIPTION = range(6)


async def logtime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the time logging conversation"""
    await update.message.reply_text("⏱️ Loading projects...")

    try:
        from src.utils.odoo_time_wrapper import get_projects_list

        projects = get_projects_list()

        if not projects:
            await update.message.reply_text("❌ No projects found or could not connect to Odoo.")
            return ConversationHandler.END

        # Store all projects in context
        context.user_data['all_projects'] = projects

        await update.message.reply_text(
            "📁 *Search for a project*\n\n"
            f"Type part of the project name to search.\n"
            f"(You have {len(projects)} projects available)\n\n"
            "Send /cancel to abort.",
            parse_mode="Markdown"
        )

        return SEARCHING_PROJECT

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        return ConversationHandler.END


async def search_projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle project search text"""
    search_term = update.message.text.strip().lower()

    if not search_term:
        await update.message.reply_text("❌ Please enter a search term.")
        return SEARCHING_PROJECT

    all_projects = context.user_data.get('all_projects', [])

    # Filter projects by search term
    matching_projects = [
        p for p in all_projects
        if search_term in p['name'].lower()
    ]

    if not matching_projects:
        await update.message.reply_text(
            f"❌ No projects found matching '{search_term}'\n\n"
            "Try a different search term or /cancel to abort."
        )
        return SEARCHING_PROJECT

    if len(matching_projects) > 20:
        await update.message.reply_text(
            f"🔍 Found {len(matching_projects)} projects matching '{search_term}'\n\n"
            "Please be more specific to narrow down the results."
        )
        return SEARCHING_PROJECT

    # Show matching projects as buttons
    keyboard = []
    for i in range(0, len(matching_projects), 2):
        row = []
        for project in matching_projects[i:i+2]:
            row.append(InlineKeyboardButton(
                project['name'][:30],
                callback_data=f"proj_{project['id']}"
            ))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Search again", callback_data="search_again")])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"📁 *Found {len(matching_projects)} project(s):*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    return SELECTING_PROJECT


async def project_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle project selection and show tasks"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Time logging cancelled.")
        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "search_again":
        await query.edit_message_text("📁 Search for a project:")
        await query.message.reply_text(
            "Type part of the project name to search.\n"
            "Send /cancel to abort."
        )
        return SEARCHING_PROJECT

    # Extract project ID
    project_id = int(query.data.split("_")[1])
    context.user_data['project_id'] = project_id

    # Get project name (from button text)
    project_name = query.message.reply_markup.inline_keyboard[0][0].text
    for row in query.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == query.data:
                project_name = button.text
                break

    context.user_data['project_name'] = project_name

    await query.edit_message_text(f"📁 Project selected: *{project_name}*\n⏳ Loading tasks...", parse_mode="Markdown")

    try:
        from src.utils.odoo_time_wrapper import get_tasks_list

        tasks = get_tasks_list(project_id)

        if not tasks:
            await query.message.reply_text("❌ No tasks found for this project.")
            return ConversationHandler.END

        # Store tasks for search
        context.user_data['all_tasks'] = tasks

        await query.message.reply_text(
            f"📋 *Search for a task in '{project_name}'*\n\n"
            f"Type part of the task name to search.\n"
            f"(You have {len(tasks)} tasks in this project)\n\n"
            "Send /cancel to abort.",
            parse_mode="Markdown"
        )

        return SEARCHING_TASK

    except Exception as e:
        await query.message.reply_text(f"❌ Error: {str(e)}")
        return ConversationHandler.END


async def search_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle task search text"""
    search_term = update.message.text.strip().lower()

    if not search_term:
        await update.message.reply_text("❌ Please enter a search term.")
        return SEARCHING_TASK

    all_tasks = context.user_data.get('all_tasks', [])

    # Filter tasks by search term
    matching_tasks = [
        t for t in all_tasks
        if search_term in t['name'].lower()
    ]

    if not matching_tasks:
        await update.message.reply_text(
            f"❌ No tasks found matching '{search_term}'\n\n"
            "Try a different search term or /cancel to abort."
        )
        return SEARCHING_TASK

    if len(matching_tasks) > 20:
        await update.message.reply_text(
            f"🔍 Found {len(matching_tasks)} tasks matching '{search_term}'\n\n"
            "Please be more specific to narrow down the results."
        )
        return SEARCHING_TASK

    # Show matching tasks as buttons
    keyboard = []
    for i in range(0, len(matching_tasks), 2):
        row = []
        for task in matching_tasks[i:i+2]:
            row.append(InlineKeyboardButton(
                task['name'][:30],
                callback_data=f"task_{task['id']}"
            ))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("🔙 Search again", callback_data="search_again_task")])
    keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"📋 *Found {len(matching_tasks)} task(s):*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    return SELECTING_TASK


async def task_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle task selection and ask for hours"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Time logging cancelled.")
        context.user_data.clear()
        return ConversationHandler.END

    if query.data == "search_again_task":
        project_name = context.user_data.get('project_name', 'this project')
        await query.edit_message_text("📋 Search for a task:")
        await query.message.reply_text(
            f"Type part of the task name in '{project_name}' to search.\n"
            "Send /cancel to abort."
        )
        return SEARCHING_TASK

    # Extract task ID
    task_id = int(query.data.split("_")[1])
    context.user_data['task_id'] = task_id

    # Get task name
    task_name = query.message.reply_markup.inline_keyboard[0][0].text
    for row in query.message.reply_markup.inline_keyboard:
        for button in row:
            if button.callback_data == query.data:
                task_name = button.text
                break

    context.user_data['task_name'] = task_name

    await query.edit_message_text(
        f"✅ Task selected: *{task_name}*\n\n"
        f"⏱️ *How many hours did you work?*\n"
        f"(Enter a number like: 2.5)",
        parse_mode="Markdown"
    )

    return ENTERING_HOURS


async def hours_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle hours input and ask for description"""
    try:
        hours = float(update.message.text)
        if hours <= 0 or hours > 24:
            await update.message.reply_text("❌ Please enter a valid number of hours (0-24)")
            return ENTERING_HOURS

        context.user_data['hours'] = hours

        await update.message.reply_text(
            f"✅ Hours: *{hours}h*\n\n"
            f"📝 *What did you work on?*\n"
            f"(Enter a description)",
            parse_mode="Markdown"
        )

        return ENTERING_DESCRIPTION

    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number (e.g., 2.5)")
        return ENTERING_HOURS


async def description_entered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle description and create time entry"""
    description = update.message.text.strip()

    if not description:
        await update.message.reply_text("❌ Description cannot be empty. Please try again.")
        return ENTERING_DESCRIPTION

    context.user_data['description'] = description

    # Log the time
    await update.message.reply_text("⏳ Logging time to Odoo...")

    try:
        from src.utils.odoo_time_wrapper import log_time_entry

        result = log_time_entry(
            project_id=context.user_data['project_id'],
            task_id=context.user_data['task_id'],
            description=description,
            hours=context.user_data['hours'],
            log_date=dt_date.today().isoformat()
        )

        # Show summary
        summary = (
            f"{result}\n\n"
            f"📁 Project: {context.user_data['project_name']}\n"
            f"📋 Task: {context.user_data['task_name']}\n"
            f"⏱️ Hours: {context.user_data['hours']}h\n"
            f"📝 Description: {description}"
        )

        await update.message.reply_text(summary)

        # Clear user data
        context.user_data.clear()

        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        context.user_data.clear()
        return ConversationHandler.END


async def cancel_logging(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the time logging conversation"""
    await update.message.reply_text("❌ Time logging cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


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

        # Register time logging conversation handler
        from telegram.ext import CommandHandler
        logtime_handler = ConversationHandler(
            entry_points=[CommandHandler("logtime", logtime_command)],
            states={
                SEARCHING_PROJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_projects)],
                SELECTING_PROJECT: [CallbackQueryHandler(project_selected)],
                SEARCHING_TASK: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_tasks)],
                SELECTING_TASK: [CallbackQueryHandler(task_selected)],
                ENTERING_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, hours_entered)],
                ENTERING_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description_entered)],
            },
            fallbacks=[CommandHandler("cancel", cancel_logging)],
            per_message=False,
            per_chat=True,
            per_user=True,
        )
        bot.app.add_handler(logtime_handler)
        print("✓ Time logging conversation handler registered")

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
