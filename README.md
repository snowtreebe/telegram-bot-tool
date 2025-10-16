# Telegram Bot Tool

A powerful Python Telegram bot with voice recognition, AI command interpretation, and Odoo time tracking integration. Perfect for personal automation, notifications, and voice-controlled workflows.

## ✨ Features

### Core Features
- 🤖 **Interactive Command Bot** - Responds to text commands via Telegram
- 🎤 **Voice Command Recognition** - Speak commands naturally using OpenAI Whisper
- 🧠 **AI Command Interpretation** - GPT-4 understands natural language
- 📊 **Odoo Time Tracking Integration** - Query your time entries via Telegram
- 🔔 **Notification System** - Send automated messages from scripts/cron jobs
- 🔄 **Sync & Async Support** - Works with any Python workflow

### Bot Commands

#### Built-in Commands
- `/start` - Get welcome message and command list
- `/help` - Show all available commands
- `/ping` - Test bot connectivity
- `/status` - Get system information
- `/time` - Get current time
- `/hello` - Get a greeting
- `/joke` - Get a random programming joke

#### Odoo Time Tracking Commands
- `/showtime` - Show recent time entries (last 5)
- `/timeweek` - Weekly time summary by project
- `/timemonth` - Monthly time summary by project
- `/summary` - Comprehensive summary with weeks, months, quarters (MD tables)

#### Custom Commands
- `/test` - Run your custom test script
- `/backup` - Trigger backup workflow (customizable)
- `/deploy` - Trigger deployment (customizable)

#### Voice Commands
Send a voice message saying any command naturally:
- "Ping" → executes `/ping`
- "What's the status?" → executes `/status`
- "Show me a time summary" → executes `/summary`
- "Tell me a joke" → executes `/joke`

## 🚀 Quick Start

### 1. Create a Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Save the **bot token**

### 2. Get Your Chat ID

1. Start a chat with your new bot
2. Send any message
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find `"chat":{"id":` in the response - that's your **chat ID**

### 3. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required for bot functionality
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# Optional: For voice commands
OPENAI_API_KEY=sk-proj-your_key_here

# Optional: For Odoo integration (if you have odoo-logger configured)
# These are read from /Users/quentin/Projects/odoo-logger/.env automatically
```

### 5. Run the Bot

```bash
# Activate virtual environment
source venv/bin/activate

# Start the command bot
python src/scripts/run_command_bot.py
```

You should see:
```
==================================================
🤖 Starting Telegram Command Bot
==================================================
✓ Voice commands enabled
✓ Voice message handler registered

💡 Tip: Send /start to your bot to see available commands
🎤 You can also send voice messages to execute commands!
==================================================

🤖 Bot is starting...
```

## 📁 Project Structure

```
telegram_tool/
├── src/
│   ├── utils/                      # Core utilities
│   │   ├── telegram_bot.py         # Basic notification sender
│   │   ├── telegram_listener.py    # Command bot framework
│   │   ├── voice_handler.py        # Voice transcription & AI interpretation
│   │   └── odoo_time_wrapper.py    # Odoo time tracking integration
│   └── scripts/                    # Executable scripts
│       ├── run_command_bot.py      # Main bot runner (start here!)
│       ├── my_test_script.py       # Example test script
│       └── example_notification.py # Simple notification example
├── docs/                           # Detailed documentation
│   ├── COMMAND_BOT.md             # Command bot guide
│   └── VOICE_COMMANDS.md          # Voice commands guide
├── .env                           # Your credentials (not in git)
├── .env.example                   # Configuration template
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 💡 Usage Examples

### Send Simple Notification

```python
from src.utils import TelegramNotifier

notifier = TelegramNotifier()
notifier.send_sync("✅ Backup completed!")
```

### Use in Cron Job

```bash
# Send daily report at 9 AM
0 9 * * * cd /path/to/telegram_tool && /path/to/venv/bin/python -c "from src.utils import TelegramNotifier; TelegramNotifier().send_sync('📊 Daily report ready!')"
```

### Custom Command Handler

Edit `src/scripts/run_command_bot.py`:

```python
async def my_custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Custom command: /mycommand"""
    await update.message.reply_text("🎉 My custom action!")
    # Your logic here...

# Register it
bot.add_command("mycommand", my_custom_command)

# Add to voice recognition
COMMAND_MAP = {
    # ... existing commands ...
    "mycommand": my_custom_command,
}
```

### Query Odoo Time Tracking

```python
from src.utils.odoo_time_wrapper import get_recent_time_entries, get_time_summary_tables

# Get last 5 entries
entries = get_recent_time_entries(limit=5)
print(entries)

# Get comprehensive summary with MD tables
summary = get_time_summary_tables()
print(summary)
```

## 🎤 Voice Commands Setup

Voice commands use OpenAI's Whisper (transcription) and GPT-4 (interpretation).

**Cost estimate:** ~$0.11 per 100 voice commands (~$1.10 per 1000 commands)

1. Get OpenAI API key from https://platform.openai.com/api-keys
2. Add to `.env`:
   ```env
   OPENAI_API_KEY=sk-proj-your_key_here
   ```
3. Restart the bot
4. Send a voice message: "Ping" or "Show me my time entries"

See [docs/VOICE_COMMANDS.md](docs/VOICE_COMMANDS.md) for details.

## 📊 Odoo Integration

The bot integrates with [odoo-logger](https://github.com/youruser/odoo-logger) to query time tracking data.

**Requirements:**
- Working `odoo-logger` installation at `/Users/quentin/Projects/odoo-logger`
- Configured `.env` file in odoo-logger directory with Odoo credentials

**Available commands:**
- `/showtime` - Recent entries
- `/timeweek` - Weekly summary
- `/timemonth` - Monthly summary
- `/summary` - Comprehensive tables (weeks, months, quarters)

## 🔧 Customization

### Add New Commands

1. Edit `src/scripts/run_command_bot.py`
2. Create command handler function
3. Register with `bot.add_command()`
4. Add to `COMMAND_MAP` for voice support
5. Update `voice_handler.py` available_commands

### Integrate with Your Scripts

```python
from src.utils import TelegramNotifier

def my_automation():
    notifier = TelegramNotifier()

    try:
        # Your logic here
        result = do_something()
        notifier.send_sync(f"✅ Success: {result}")
    except Exception as e:
        notifier.send_sync(f"❌ Error: {e}")
```

## 📚 Documentation

- [Command Bot Guide](docs/COMMAND_BOT.md) - Detailed command bot documentation
- [Voice Commands Guide](docs/VOICE_COMMANDS.md) - Voice setup and usage

## 🐛 Troubleshooting

**"Bot token not provided"**
- Check your `.env` file exists and contains `TELEGRAM_BOT_TOKEN`

**"Voice commands are not configured"**
- Add `OPENAI_API_KEY` to `.env` and restart bot

**"Could not connect to Odoo"**
- Verify odoo-logger is installed at `/Users/quentin/Projects/odoo-logger`
- Check odoo-logger's `.env` file has valid Odoo credentials

**Bot not responding**
- Make sure you've sent `/start` to your bot first
- Check bot is running: `ps aux | grep run_command_bot`
- Restart: Kill process and run `python src/scripts/run_command_bot.py`

## 🔐 Security

- `.env` is in `.gitignore` - never commit credentials
- Bot token and API keys are sensitive - keep them private
- Consider adding user ID restrictions in production
- Set OpenAI spending limits in dashboard

## 📝 License

MIT

## 🙋 Support

For issues or questions:
1. Check [docs/](docs/) folder
2. Review error messages in bot output
3. Check Telegram bot status
4. Verify all credentials in `.env`

---

**Built with:**
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API
- [OpenAI API](https://platform.openai.com/) - Whisper & GPT-4
- [odoo-logger](https://github.com/youruser/odoo-logger) - Time tracking integration
