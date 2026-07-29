import time
from datetime import date, datetime, timedelta

from config import Settings, load_settings
from database import GarminDatabase
from garmin_client import GarminService
from storage import JsonStorage


def today_in_timezone(settings: Settings) -> date:
    return datetime.now(settings.tzinfo).date()


def determine_start_date(
    settings: Settings,
    storage: JsonStorage,
    database: GarminDatabase,
) -> date:
    candidates = storage.existing_dates()
    database_latest = database.latest_date()
    if database_latest:
        candidates.append(date.fromisoformat(database_latest))

    if not candidates:
        return settings.default_start_date

    latest = max(candidates)
    start = latest - timedelta(days=settings.refresh_days - 1)
    return max(start, settings.default_start_date)


def sync_history() -> int:
    settings = load_settings()
    storage = JsonStorage()

    with GarminDatabase() as database:
        # 首次升级时把已有 JSON 一次性导入 SQLite。
        if database.latest_date() is None:
            imported = database.import_payloads(storage.iter_payloads())
            if imported:
                print(f"已从现有 JSON 导入 SQLite：{imported} 天")

        start_date = determine_start_date(settings, storage, database)
        end_date = today_in_timezone(settings)

        print(f"同步范围：{start_date} ～ {end_date}")
        print(f"时区：{settings.timezone}")
        print(f"最近 {settings.refresh_days} 天会被重新下载")
        print()

        service = GarminService(settings)
        service.login()

        current = start_date
        success_count = 0
        failure_count = 0

        while current <= end_date:
            day_text = current.isoformat()
            print(f"正在同步 {day_text} ...", end=" ", flush=True)

            try:
                payload = service.download_day(day_text)
                storage.save_atomic(payload)
                database.upsert_payload(payload)
                success_count += 1
                print("完成")
            except Exception as error:
                failure_count += 1
                print(f"失败：{error}")

            current += timedelta(days=1)
            if current <= end_date:
                time.sleep(settings.request_delay_seconds)

        print()
        print("=" * 60)
        print(f"同步成功：{success_count} 天")
        print(f"同步失败：{failure_count} 天")

        if failure_count:
            print("部分日期同步失败；下次运行会重新刷新最近几天")
            return 1

        print("Garmin 数据同步完成")
        return 0


if __name__ == "__main__":
    raise SystemExit(sync_history())
