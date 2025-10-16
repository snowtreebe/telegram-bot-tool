#!/usr/bin/env python3
"""
A simple test script that can be triggered by Telegram command
"""

import random
from datetime import datetime


def run_test():
    """
    Your custom test logic goes here!
    This function is called when you send /test to your bot.
    """
    # Example: Generate random number
    lucky_number = random.randint(1, 100)

    # Example: Get current time
    current_time = datetime.now().strftime("%H:%M:%S")

    # Example: Do some calculation
    result = 42 * 2

    # Return a message to send back to Telegram
    return f"""
🧪 Test Script Executed!

🎲 Lucky Number: {lucky_number}
⏰ Execution Time: {current_time}
🔢 Calculation Result: 42 × 2 = {result}

✅ Script completed successfully!
"""


if __name__ == "__main__":
    # Can also run standalone for testing
    print(run_test())
