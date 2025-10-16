"""
Voice Message Handler
Transcribes voice messages and interprets them as commands using AI
"""

import os
import tempfile
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import openai


class VoiceCommandHandler:
    """
    Handles voice message transcription and command interpretation.
    Uses OpenAI Whisper for transcription and GPT for command interpretation.
    """

    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the voice handler.

        Args:
            openai_api_key: OpenAI API key (reads from OPENAI_API_KEY env var if not provided)
        """
        load_dotenv()

        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')

        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable.")

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)

        # Available commands that the AI can trigger
        self.available_commands = {
            "status": "Get system status",
            "test": "Run test script",
            "ping": "Test bot connection",
            "time": "Get current time",
            "joke": "Get a joke",
            "hello": "Get greeting",
            "backup": "Run backup",
            "deploy": "Run deployment",
            "showtime": "Show recent Odoo time entries",
            "timeweek": "Show weekly Odoo time summary",
            "timemonth": "Show monthly Odoo time summary",
            "summary": "Show comprehensive time summary with weeks, months, and quarters",
            "invoiced": "Show invoice summary with amounts invoiced and paid",
        }

    async def transcribe_voice(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text using OpenAI Whisper.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Transcribed text
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="en"  # Can be removed for auto-detection
                )
            return transcript.text
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    async def interpret_command(self, transcription: str) -> Dict[str, Any]:
        """
        Use AI to interpret the transcribed text and determine what command to execute.

        Args:
            transcription: The transcribed text from voice message

        Returns:
            Dict with 'command' (str or None) and 'explanation' (str)
        """
        commands_list = "\n".join([f"- {cmd}: {desc}" for cmd, desc in self.available_commands.items()])

        prompt = f"""You are a voice command interpreter for a Telegram bot. The user said:

"{transcription}"

Available commands:
{commands_list}

Determine which command (if any) the user wants to execute. Respond with ONLY the command name (e.g., "status", "test", "ping") or "none" if no command matches.

If the user is asking a question or making a statement that doesn't match a command, respond with "none".

Command:"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a command interpreter. Respond with only the command name or 'none'."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )

            command = response.choices[0].message.content.strip().lower()

            # Validate command
            if command == "none" or command not in self.available_commands:
                return {
                    "command": None,
                    "explanation": f"I heard: '{transcription}'\n\nBut I couldn't match it to a known command."
                }

            return {
                "command": command,
                "explanation": f"I heard: '{transcription}'\n\nExecuting command: /{command}"
            }

        except Exception as e:
            raise Exception(f"Command interpretation failed: {str(e)}")

    async def process_voice_message(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Complete pipeline: transcribe voice and interpret command.

        Args:
            audio_file_path: Path to the audio file

        Returns:
            Dict with 'transcription', 'command', and 'explanation'
        """
        # Step 1: Transcribe
        transcription = await self.transcribe_voice(audio_file_path)

        # Step 2: Interpret
        interpretation = await self.interpret_command(transcription)

        return {
            "transcription": transcription,
            "command": interpretation["command"],
            "explanation": interpretation["explanation"]
        }


async def download_voice_file(telegram_file, bot) -> str:
    """
    Download voice file from Telegram and save to temp location.

    Args:
        telegram_file: The file object from Telegram
        bot: The bot instance

    Returns:
        Path to downloaded file
    """
    # Create temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".ogg")
    temp_path = temp_file.name
    temp_file.close()

    # Download file
    await telegram_file.download_to_drive(temp_path)

    return temp_path
