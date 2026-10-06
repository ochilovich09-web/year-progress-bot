import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import date


BAR_LENGTH = 21


# =========================
# Quote
# =========================

def get_random_quote():
    """Fetch a random inspirational quote."""

    url = "https://dummyjson.com/quotes/random"

    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "YearProgressBot/1.0"}
        )

        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))

        return f'"{data["quote"]}" — {data["author"]}'

    except Exception:
        return '"The only way to do great work is to love what you do." — Steve Jobs'


# =========================
# Year calculations
# =========================

def is_leap(year):
    return year % 4 == 0 and (
        year % 100 != 0 or year % 400 == 0
    )


def get_percent(day_of_year, total_days):
    """Return whole-day percentage, rounded down."""

    return day_of_year * 100 // total_days


def get_year_progress(today):
    total_days = 366 if is_leap(today.year) else 365

    day_of_year = today.timetuple().tm_yday

    percentage = get_percent(
        day_of_year,
        total_days
    )

    yesterday_percentage = get_percent(
        day_of_year - 1,
        total_days
    )

    percentage_changed = (
        percentage != yesterday_percentage
    )

    return percentage, percentage_changed


# =========================
# Message
# =========================

def generate_progress_message(today, percentage):

    current_year = today.year

    total_days = (
        366
        if is_leap(current_year)
        else 365
    )

    day_of_year = today.timetuple().tm_yday

    # -------------------------
    # Progress bar
    # -------------------------

    filled_blocks = (
        BAR_LENGTH * percentage // 100
    )

    empty_blocks = (
        BAR_LENGTH - filled_blocks
    )

    bar = (
        "▓" * filled_blocks
        + "░" * empty_blocks
    )

    # -------------------------
    # Days until December 31
    # -------------------------

    dec_31 = date(
        current_year,
        12,
        31
    )

    days_until_dec_31 = (
        dec_31 - today
    ).days

    # -------------------------
    # Days until May 25
    # -------------------------

    may_25 = date(
        current_year,
        5,
        25
    )

    if today > may_25:
        may_25 = date(
            current_year + 1,
            5,
            25
        )

    days_until_may_25 = (
        may_25 - today
    ).days

    # -------------------------
    # Quote
    # -------------------------

    quote = get_random_quote()

    # -------------------------
    # Final message
    # -------------------------

    message = f"""<code>{bar}</code> <b>{percentage}%</b>

📆 Day {day_of_year} of {total_days}

⏳ <b>{days_until_dec_31}</b> days until December 31
🎯 <b>{days_until_may_25}</b> days until May 25

💭 <i>{quote}</i>"""

    return message


# =========================
# Telegram
# =========================

def send_telegram_message(message):
    """Send the generated message to the Telegram channel."""

    token = os.environ.get(
        "TELEGRAM_BOT_TOKEN"
    )

    channel_id = os.environ.get(
        "TELEGRAM_CHANNEL_ID"
    )

    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing from GitHub Secrets."
        )

    if not channel_id:
        raise RuntimeError(
            "TELEGRAM_CHANNEL_ID is missing from GitHub Secrets."
        )

    url = (
        f"https://api.telegram.org/"
        f"bot{token}/sendMessage"
    )

    data = urllib.parse.urlencode({
        "chat_id": channel_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type":
                "application/x-www-form-urlencoded"
        },
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

        if not result.get("ok"):
            raise RuntimeError(
                f"Telegram API error: {result}"
            )

        print(
            "✅ Telegram message sent successfully."
        )

    except urllib.error.HTTPError as error:

        error_body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        raise RuntimeError(
            f"Telegram HTTP error "
            f"{error.code}: {error_body}"
        ) from error

    except urllib.error.URLError as error:

        raise RuntimeError(
            f"Could not connect to Telegram: "
            f"{error.reason}"
        ) from error


# =========================
# Main
# =========================

def main():

    # GitHub Actions runner uses UTC.
    # The date calculation below is intentionally
    # adjusted to Tashkent (UTC+5).

    from datetime import (
        datetime,
        timedelta,
        timezone
    )

    tashkent_timezone = timezone(
        timedelta(hours=5)
    )

    today = datetime.now(
        tashkent_timezone
    ).date()

    print(
        f"📅 Date: {today}"
    )

    percentage, percentage_changed = (
        get_year_progress(today)
    )

    print(
        f"📊 Year progress: "
        f"{percentage}%"
    )

    print(
        f"📈 Percentage changed today: "
        f"{percentage_changed}"
    )

    message = generate_progress_message(
        today,
        percentage
    )

    print("\n--- Message ---")
    print(message)
    print("----------------\n")

    # FORCE_POST=1 makes GitHub Actions
    # send the message every time the workflow runs.

    force_post = (
        os.environ.get(
            "FORCE_POST",
            "0"
        ) == "1"
    )

    if percentage_changed or force_post:

        send_telegram_message(
            message
        )

    else:

        print(
            "ℹ️ Percentage did not change. "
            "No post needed."
        )


if __name__ == "__main__":
    main()

