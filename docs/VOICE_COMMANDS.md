# Voice Commands

Send voice messages to your Telegram bot and it will transcribe them using AI, understand what you want, and execute the command!

## Setup

### 1. Get an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key

### 2. Add to .env file

Edit your `.env` file and add:

```bash
OPENAI_API_KEY=sk-proj-your_api_key_here
```

### 3. Restart the bot

```bash
# Kill the current bot
kill $(ps aux | grep run_command_bot | grep -v grep | awk '{print $2}')

# Start with voice support
source venv/bin/activate
python src/scripts/run_command_bot.py
```

You should see:
```
✓ Voice commands enabled
✓ Voice message handler registered
🎤 You can also send voice messages to execute commands!
```

## How It Works

1. **You speak** a voice message in Telegram
2. **Bot transcribes** using OpenAI Whisper (speech-to-text)
3. **AI interprets** what command you want using GPT-4
4. **Bot executes** the matching command
5. **Bot responds** with the result

## Example Voice Commands

### System Status
**Say:** "What's the system status?" or "Check status" or "How's the server?"
**Executes:** `/status` command

### Run Test
**Say:** "Run the test script" or "Execute test" or "Test it"
**Executes:** `/test` command

### Ping
**Say:** "Ping" or "Are you alive?" or "Test connection"
**Executes:** `/ping` command

### Get Time
**Say:** "What time is it?" or "Tell me the time" or "Current time"
**Executes:** `/time` command

### Tell Joke
**Say:** "Tell me a joke" or "Make me laugh" or "Got any jokes?"
**Executes:** `/joke` command

### Backup
**Say:** "Run backup" or "Start backup" or "Backup now"
**Executes:** `/backup` command

### Deploy
**Say:** "Deploy" or "Start deployment" or "Deploy now"
**Executes:** `/deploy` command

## Response Flow

When you send a voice message, you'll see:

```
🎤 Processing voice message...

I heard: 'run the test script'

Executing command: /test

[Then the actual command output]
```

## Supported Languages

Currently configured for English, but Whisper supports 50+ languages. To change:

Edit `src/utils/voice_handler.py`:

```python
transcript = self.client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="es"  # Spanish, or remove for auto-detect
)
```

## Cost Considerations

### Whisper API Pricing
- $0.006 per minute of audio
- A 10-second voice message costs ~$0.001

### GPT-4 API Pricing
- ~$0.0001 per command interpretation
- Uses gpt-4o-mini for efficiency

### Example Monthly Costs
- 100 voice commands/month: ~$0.10 + $0.01 = **$0.11**
- 1000 voice commands/month: ~$1.00 + $0.10 = **$1.10**

Very affordable for personal use!

## Customization

### Add New Voice Commands

Edit `run_command_bot.py` and add to `COMMAND_MAP`:

```python
COMMAND_MAP = {
    "status": status_command,
    "test": test_command,
    "mycommand": my_custom_command,  # Add your command here
}
```

Then update `voice_handler.py` to recognize it:

```python
self.available_commands = {
    "status": "Get system status",
    "test": "Run test script",
    "mycommand": "Description of my command",  # Add here
}
```

### Adjust AI Interpretation

The AI uses GPT-4 to understand natural language. You can adjust the prompt in `voice_handler.py`:

```python
prompt = f"""You are a voice command interpreter...

Available commands:
{commands_list}

Determine which command the user wants...
"""
```

## Troubleshooting

### "Voice commands are not configured"
- Make sure `OPENAI_API_KEY` is in your `.env` file
- Restart the bot

### "Transcription failed"
- Check your OpenAI API key is valid
- Ensure you have API credits
- Voice message might be too quiet

### "Command interpretation failed"
- OpenAI API might be down
- Check your internet connection
- API key might have insufficient quota

### Voice message not recognized
- Speak clearly
- Keep messages under 30 seconds
- Use simple command phrases like "run test" or "check status"

## Security

### API Key Safety
- Never commit your `.env` file to git
- Rotate API keys periodically
- Use API key restrictions (OpenAI dashboard)

### Command Authorization
Voice commands use the same security as text commands. To add user restrictions:

```python
ALLOWED_USERS = [8218327856]  # Your chat ID

async def voice_message_handler(update, context):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ Unauthorized")
        return
    # ... rest of handler
```

## Advanced Usage

### Custom Transcription Models

Whisper has different models:
- `whisper-1` - Standard model (recommended)

### Custom AI Models

Change the GPT model in `voice_handler.py`:

```python
response = self.client.chat.completions.create(
    model="gpt-4",  # More accurate but more expensive
    # model="gpt-4o-mini",  # Default - fast and cheap
    # model="gpt-3.5-turbo",  # Even cheaper
    ...
)
```

### Multi-step Commands

You can build commands that take parameters from voice:

```python
async def interpret_command(self, transcription: str) -> Dict[str, Any]:
    # Extract command AND parameters
    prompt = f"""Extract command and any parameters from: "{transcription}"

    Example: "backup the database to S3" → command: backup, params: location=s3

    Return JSON: {{"command": "...", "params": {{...}}}}
    """
```

## Examples in Other Languages

### Spanish
**Say:** "Muéstrame el estado del sistema"
**Bot understands:** status command

### French
**Say:** "Lance le script de test"
**Bot understands:** test command

Just set `language=None` in Whisper call for auto-detection!

---

Happy voice commanding! 🎤🤖
