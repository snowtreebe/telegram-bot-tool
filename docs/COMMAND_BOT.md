# Telegram Command Bot

Your bot can now **receive and respond to commands**! Send commands to your bot and it will execute actions and reply.

## Quick Start

### 1. Start the bot listener

```bash
source venv/bin/activate
python src/scripts/run_command_bot.py
```

The bot will start listening for commands. Keep this running in a terminal.

### 2. Send commands to your bot in Telegram

Open Telegram and send commands to your bot:

- `/start` - Show welcome message and available commands
- `/help` - Get help
- `/ping` - Test if bot is alive
- `/status` - Get system status (CPU, memory, disk, uptime)
- `/hello` - Get a friendly greeting
- `/time` - Get current date/time
- `/joke` - Get a random programming joke
- `/backup` - Trigger backup (example - customize this!)
- `/deploy` - Trigger deployment (example - customize this!)

### 3. Send regular messages

Any non-command message will be echoed back to you.

---

## Built-in Commands

### `/start`
Shows welcome message with all available commands.

### `/help`
Shows help information about bot commands.

### `/ping`
Simple test to verify bot is responding.
**Response:** "🏓 Pong! Bot is alive and responding."

### `/status`
Get detailed system information:
- Platform and OS version
- CPU usage percentage
- Memory usage (used/total)
- Disk usage (used/total)
- System uptime

**Example response:**
```
📊 System Status

💻 Platform: Darwin 24.4.0
🔧 CPU Usage: 23%
💾 Memory: 45% used (8GB / 16GB)
💿 Disk: 67% used (250GB / 500GB)
⏱ Uptime: 5 days, 12 hours

✅ All systems operational
```

---

## Custom Commands

You can easily add your own commands! Edit `src/scripts/run_command_bot.py`:

### Example: Add a `/weather` command

```python
async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get weather information"""
    # Your weather API logic here
    await update.message.reply_text("☀️ Today: Sunny, 72°F")

# Register it
bot.add_command("weather", weather_command)
```

### Example: Run a shell command

```python
async def restart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Restart a service"""
    await update.message.reply_text("🔄 Restarting service...")

    import subprocess
    result = subprocess.run(["systemctl", "restart", "myservice"],
                          capture_output=True, text=True)

    if result.returncode == 0:
        await update.message.reply_text("✅ Service restarted successfully!")
    else:
        await update.message.reply_text(f"❌ Error: {result.stderr}")

bot.add_command("restart", restart_command)
```

### Example: Get file contents

```python
async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get last 10 lines of log file"""
    try:
        with open('/var/log/myapp.log', 'r') as f:
            lines = f.readlines()[-10:]
            log_text = ''.join(lines)
        await update.message.reply_text(f"📋 Recent logs:\n```\n{log_text}\n```",
                                       parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error reading logs: {e}")

bot.add_command("logs", logs_command)
```

### Example: Command with arguments

```python
async def say_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo back user's message - Usage: /say hello world"""
    if context.args:
        message = ' '.join(context.args)
        await update.message.reply_text(f"You said: {message}")
    else:
        await update.message.reply_text("Usage: /say <message>")

bot.add_command("say", say_command)
```

---

## Running as a Service

To keep the bot running 24/7, you can run it as a background service:

### Option 1: Using screen (simple)

```bash
screen -S telegram-bot
source venv/bin/activate
python src/scripts/run_command_bot.py

# Press Ctrl+A then D to detach
# Reattach with: screen -r telegram-bot
```

### Option 2: Using systemd (recommended for Linux)

Create `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Command Bot
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/telegram_tool
ExecStart=/path/to/telegram_tool/venv/bin/python src/scripts/run_command_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

### Option 3: Using nohup (simple background)

```bash
source venv/bin/activate
nohup python src/scripts/run_command_bot.py > bot.log 2>&1 &
echo $! > bot.pid

# Stop with: kill $(cat bot.pid)
```

---

## Security Considerations

### 1. Restrict who can use commands

Add user ID verification:

```python
ALLOWED_USERS = [8218327856]  # Your chat ID

async def restricted_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Unauthorized")
        return

    # Your command logic here
    await update.message.reply_text("✅ Authorized action completed")
```

### 2. Be careful with shell commands

Always validate input and use subprocess safely:

```python
import subprocess
import shlex

async def safe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Bad: subprocess.run(f"ls {user_input}", shell=True)  # Dangerous!
    # Good:
    result = subprocess.run(["ls", "/safe/path"],
                          capture_output=True, text=True)
```

### 3. Keep your token secure

- Never commit `.env` to git (it's in `.gitignore`)
- Don't share your bot token
- Regenerate token if exposed (use BotFather `/revoke`)

---

## Troubleshooting

### Bot doesn't respond
- Make sure `run_command_bot.py` is running
- Check terminal for errors
- Verify `.env` has correct `TELEGRAM_BOT_TOKEN`

### Commands not working
- Make sure you're using `/` before command (e.g., `/status` not `status`)
- Check terminal output for registration messages

### Bot stops after a while
- Check for errors in logs
- Use systemd or screen to keep it running
- Add error handling to your commands

---

## Use Cases

**Server Monitoring:**
- `/status` - Check server health
- `/logs` - View recent logs
- `/disk` - Check disk space alerts

**DevOps:**
- `/deploy` - Trigger deployments
- `/restart` - Restart services
- `/build` - Run build pipelines

**Home Automation:**
- `/lights on` - Control smart devices
- `/temperature` - Get sensor readings
- `/camera` - Get security cam snapshot

**Personal Assistant:**
- `/remind` - Set reminders
- `/todo` - Manage tasks
- `/weather` - Get weather updates

---

## Next Steps

1. **Customize commands** in `src/scripts/run_command_bot.py`
2. **Add your own logic** for backup, deploy, etc.
3. **Run as a service** for 24/7 operation
4. **Add security** with user ID restrictions
5. **Integrate with your systems** (databases, APIs, scripts)

Happy automating! 🤖
