import hashlib
import datetime

FINE_PER_DAY = 1.0
DEFAULT_LOAN_DAYS = 14


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def validate_string(value: str) -> bool:
    return isinstance(value, str) and len(value.strip()) > 0


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def calculate_due_date(days: int = DEFAULT_LOAN_DAYS) -> datetime.date:
    return datetime.date.today() + datetime.timedelta(days=days)


def calculate_fine(due_date: datetime.date, return_date: datetime.date) -> float:
    if return_date <= due_date:
        return 0.0
    overdue_days = (return_date - due_date).days
    return round(overdue_days * FINE_PER_DAY, 2)
