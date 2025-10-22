from datetime import datetime, date, timedelta

def validate_and_correct_date_range(date_from: str | None, date_to: str | None) -> tuple[date, date, bool]:
    """
    Validates and corrects a date range.

    Rules:
    - If either date is missing, default is used.
    - If date_from >= date_to, defaults are used.
    - Both dates must be after today.
    - Default date_from = today, date_to = today + 2 years.

    :param date_from: Start date in ISO format 'YYYY-MM-DD' or None.
    :param date_to: End date in ISO format 'YYYY-MM-DD' or None.
    :return: Tuple (corrected_date_from, corrected_date_to) as datetime.date objects.
    """
    today = date.today()
    default_from = today
    default_to = today + timedelta(days=365 * 2)

    # Parse safely
    try:
        from_dt = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
    except ValueError:
        from_dt = None

    try:
        to_dt = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None
    except ValueError:
        to_dt = None

    # Validation logic
    if not from_dt or not to_dt:
        return default_from, default_to, False

    if from_dt >= to_dt:
        return default_from, default_to, False

    if from_dt <= today or to_dt <= today:
        return default_from, default_to, False

    return from_dt, to_dt, True