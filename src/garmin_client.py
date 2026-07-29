import time
from collections.abc import Callable
from typing import Any, TypeVar

from garminconnect import Garmin

from config import Settings

T = TypeVar("T")


class GarminService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client: Garmin | None = None

    def login(self) -> Garmin:
        last_error: Exception | None = None

        for attempt in range(1, self.settings.login_retries + 1):
            try:
                client = Garmin(
                    self.settings.garmin_email,
                    self.settings.garmin_password,
                )
                client.login()
                self.client = client
                print("✓ Garmin 登录成功")
                try:
                    print(f"用户：{client.get_full_name()}")
                except Exception:
                    pass
                return client
            except Exception as error:
                last_error = error
                if attempt == self.settings.login_retries:
                    break
                wait_seconds = min(60, 5 * attempt)
                print(
                    f"Garmin 登录失败（第 {attempt} 次）：{error}\n"
                    f"{wait_seconds} 秒后重试……"
                )
                time.sleep(wait_seconds)

        raise RuntimeError(f"Garmin 登录失败：{last_error}") from last_error

    def call(self, operation_name: str, operation: Callable[[], T]) -> T:
        last_error: Exception | None = None

        for attempt in range(1, self.settings.request_retries + 1):
            try:
                return operation()
            except Exception as error:
                last_error = error
                if attempt == self.settings.request_retries:
                    break
                wait_seconds = min(60, 3 * attempt)
                print(
                    f"  {operation_name} 失败（第 {attempt} 次）：{error}；"
                    f"{wait_seconds} 秒后重试"
                )
                time.sleep(wait_seconds)

        raise RuntimeError(f"{operation_name} 失败：{last_error}") from last_error

    def download_day(self, day_text: str) -> dict[str, Any]:
        client = self.client or self.login()

        return {
            "date": day_text,
            "stats": self.call("stats", lambda: client.get_stats(day_text)),
            "sleep": self.call("sleep", lambda: client.get_sleep_data(day_text)),
            "body_battery": self.call(
                "body_battery",
                lambda: client.get_body_battery(day_text),
            ),
            "heart_rate": self.call(
                "heart_rate",
                lambda: client.get_heart_rates(day_text),
            ),
            "activities": self.call(
                "activities",
                lambda: client.get_activities_by_date(day_text, day_text),
            ),
        }
