from typing import Tuple
from datetime import datetime, timezone, timedelta


async def get_today_date() -> Tuple[datetime, datetime]:
    """Get the start and end datetime boundaries for today in UTC."""
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return (start, end)


async def get_month_date() -> Tuple[datetime, datetime]:
    """Get the start and end datetime boundaries for the current month in UTC."""
    now = datetime.now(timezone.utc)
    start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    if now.month == 12:
        end = datetime(now.year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(now.year, now.month + 1, 1, tzinfo=timezone.utc)
    return (start, end)
