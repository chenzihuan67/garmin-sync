import os
from dataclasses import dataclass
from datetime import date
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    garmin_email: str
    garmin_password: str
    timezone: str = "Asia/Tokyo"
    default_start_date: date = date(2024, 1, 1)
    refresh_days: int = 3
    request_delay_seconds: float = 1.0
    login_retries: int = 3
    request_retries: int = 3

    @property
    def tzinfo(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)


def _positive_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = int(raw)
    if value < 1:
        raise RuntimeError(f"{name} 必须大于等于 1")
    return value


def _non_negative_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = float(raw)
    if value < 0:
        raise RuntimeError(f"{name} 不能小于 0")
    return value


def load_settings() -> Settings:
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    if not email:
        raise RuntimeError("未找到 GARMIN_EMAIL")
    if not password:
        raise RuntimeError("未找到 GARMIN_PASSWORD")

    start_text = os.getenv("GARMIN_START_DATE", "2024-01-01")

    return Settings(
        garmin_email=email,
        garmin_password=password,
        timezone=os.getenv("GARMIN_TIMEZONE", "Asia/Tokyo"),
        default_start_date=date.fromisoformat(start_text),
        refresh_days=_positive_int("GARMIN_REFRESH_DAYS", 3),
        request_delay_seconds=_non_negative_float("GARMIN_REQUEST_DELAY_SECONDS", 1.0),
        login_retries=_positive_int("GARMIN_LOGIN_RETRIES", 3),
        request_retries=_positive_int("GARMIN_REQUEST_RETRIES", 3),
    )
