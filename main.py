import json
import os
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

TASHKENT_TZ = timezone(timedelta(hours=5))  # GMT+5 (Asia/Tashkent)
BAR_LENGTH = 20


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
    return '"The only way to do great work is to love what you do." — Steve Jobs'


def is_leap(year):
  return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def get_percent(day_of_year, total_days):
  """Whole-day percent, floored (e.g. day 73 of 365 -> 20)."""
  return day_of_year * 100 // total_days


def get_year_progress(today):
  total_days = 366 if is_leap(today.year) else 365
  doy = today.timetuple().tm_yday
  percent_now = get_percent(doy, total_days)
  percent_yesterday = get_percent(doy - 1, total_days)
  return percent_now, percent_now != percent_yesterday


def generate_progress_message(today, percentage):
  current_year = today.year

  # Progress bar
  filled_blocks = BAR_LENGTH * percentage // 100
  bar = "▓" * filled_blocks + "░" * (BAR_LENGTH - filled_blocks)

  # Countdown to 31 December
    # Countdown to 31 December
  dec_31 = date(current_year, 12, 31)
  days_until_dec_31 = (dec_31 - today).days

  # Countdown to 25 May
  may_25 = date(current_year, 5, 25)
  if today > may_25:
    may_25 = date(current_year + 1, 5, 25)
  days_until_may_25 = (may_25 - today).days
