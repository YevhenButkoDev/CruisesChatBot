from datetime import datetime, date, timedelta
from typing import Tuple, Optional


def validate_and_correct_date_range(date_from: Optional[str], date_to: Optional[str]) -> Tuple[date, date, bool]:
    """
    Validate and correct a date range with fallback to defaults.

    Rules:
    - If either date is missing, defaults are used
    - If date_from >= date_to, defaults are used
    - Both dates must be after today
    - Default: today to today + 2 years

    :param date_from: Start date in ISO format 'YYYY-MM-DD' or None
    :param date_to: End date in ISO format 'YYYY-MM-DD' or None
    :return: Tuple (corrected_date_from, corrected_date_to, is_valid)
    """
    today = date.today()
    default_from = today
    default_to = today + timedelta(days=365 * 2)

    # Parse dates safely
    from_dt = _parse_date_safe(date_from)
    to_dt = _parse_date_safe(date_to)

    # Validation logic
    if not from_dt or not to_dt:
        return default_from, default_to, False

    if from_dt >= to_dt:
        return default_from, default_to, False

    if from_dt <= today or to_dt <= today:
        return default_from, default_to, False

    return from_dt, to_dt, True


def _parse_date_safe(date_str: Optional[str]) -> Optional[date]:
    """Safely parse date string to date object."""
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None
