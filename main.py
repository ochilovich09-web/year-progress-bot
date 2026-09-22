import os
import json
import urllib.request
from datetime import datetime, timezone, timedelta, date

def get_random_quote():
    """Fetches a random inspirational quote from a free API."""
    url = "https://dummyjson.com/quotes/random"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            return f'"{data["quote"]}" — {data["author"]}'
    except Exception:
        # Fallback quote in case the API call times out or fails
        return '"The best way to predict the future is to create it." — Abraham Lincoln'

def generate_progress_message():
    # Set explicitly to GMT+5 (Asia/Tashkent)
    tashkent_tz = timezone(timedelta(hours=5))
    now = datetime.now(tashkent_tz)
    today = now.date()
    current_year = now.year
    
    # 1. Year Progress Calculation
    year_start = datetime(current_year, 1, 1, tzinfo=tashkent_tz)
    year_end = datetime(current_year + 1, 1, 1, tzinfo=tashkent_tz)
    
    total_seconds = (year_end - year_start).total_seconds()
    elapsed_seconds = (now - year_start).total_seconds()
    percentage = (elapsed_seconds / total_seconds) * 100
    
    # 20-character progress bar
    bar_length = 20
    filled_blocks = int(round((percentage / 100) * bar_length))
    bar = "▓" * filled_blocks + "░" * (bar_length - filled_blocks)
    
    # 2. Countdown to 31 December
    dec_31 = date(current_year, 12, 31)
    days_until_dec_31 = (dec_31 - today).days
    
    # 3. Countdown to 25 May
    may_25 = date(current_year, 5, 25)
    if today > may_25:
        may_25 = date(current_year + 1, 5, 25)
    days_until_may_25 = (may_25 - today).days

    # Fetch a random quote
    quote = get_random_quote()

    # Build Message Lines
    lines = [
        f"{bar} {int(round(percentage))}%",
        f"{days_until_dec_31} days until 31 December",
        f"{days_until_may_25} days until 25 May"
    ]

    # Special Date Triggers
    if today.month == 12 and today.day == 31:
        lines.append("\n🎉 Happy New Year's Eve! Happy New Year! 🥳✨")
    elif today.month == 5 and today.day == 25:
        lines.append("\n✨ Happy 25th of May! Wishing you a great holiday! 🌟")

    # Add Quote at the bottom
    lines.append(f"\n{quote}")

    return "\n".join(lines)

def send_telegram_message(bot_token, channel_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        "chat_id": channel_id,
        "text": text
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    with urllib.request.urlopen(req) as response:
        return response.read()

if __name__ == "__main__":
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    channel_id = os.environ.get("TELEGRAM_CHANNEL_ID")
    
    if not bot_token or not channel_id:
        raise ValueError("Environment variables TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID are required.")
        
    message = generate_progress_message()
    send_telegram_message(bot_token, channel_id, message)
    print("Message successfully posted to Telegram!")
        
    message = generate_progress_message()
    send_telegram_message(bot_token, channel_id, message)
    print("Message successfully posted to Telegram!")
