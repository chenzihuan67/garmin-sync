from datetime import date, datetime, timedelta
from pathlib import Path
import json
import time

from garminconnect import Garmin

from config import GARMIN_EMAIL, GARMIN_PASSWORD


DATA_DIR = Path("data")
DEFAULT_START_DATE = date(2024, 1, 1)

# 每次重新下载最近几天，防止当天数据不完整
REFRESH_DAYS = 3

# 请求之间稍微停顿，降低 Garmin 429 限流概率
REQUEST_DELAY_SECONDS = 1


def login() -> Garmin:
    """登录 Garmin Connect。"""
    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    client.login()

    print("✓ Garmin 登录成功")

    try:
        print(f"用户：{client.get_full_name()}")
    except Exception:
        pass

    return client


def get_existing_dates() -> list[date]:
    """读取 data 文件夹中已有的日期文件。"""
    existing_dates = []

    for file in DATA_DIR.glob("*.json"):
        try:
            file_date = datetime.strptime(file.stem, "%Y-%m-%d").date()
            existing_dates.append(file_date)
        except ValueError:
            # 忽略文件名不符合 YYYY-MM-DD 格式的 JSON
            continue

    return sorted(existing_dates)


def determine_start_date() -> date:
    """
    确定本次同步起点。

    没有历史文件：
        从 DEFAULT_START_DATE 开始。

    已有历史文件：
        从最新日期往前 REFRESH_DAYS - 1 天开始，
        以便刷新最近几天的数据。
    """
    existing_dates = get_existing_dates()

    if not existing_dates:
        return DEFAULT_START_DATE

    latest_date = existing_dates[-1]

    start_date = latest_date - timedelta(days=REFRESH_DAYS - 1)

    return max(start_date, DEFAULT_START_DATE)


def download_day(client: Garmin, day: date) -> bool:
    """下载并覆盖指定日期的数据。"""
    day_text = day.isoformat()
    filename = DATA_DIR / f"{day_text}.json"

    print(f"正在同步 {day_text} ...", end=" ")

    try:
        data = {
            "date": day_text,
            "stats": client.get_stats(day_text),
            "sleep": client.get_sleep_data(day_text),
            "body_battery": client.get_body_battery(day_text),
            "heart_rate": client.get_heart_rates(day_text),
            "activities": client.get_activities_by_date(
                day_text,
                day_text,
            ),
        }

        # 先写临时文件，成功后再替换正式文件，
        # 防止运行中断导致原 JSON 损坏。
        temporary_file = filename.with_suffix(".json.tmp")

        with open(temporary_file, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
            )

        temporary_file.replace(filename)

        print("完成")
        return True

    except Exception as error:
        print(f"失败：{error}")
        return False


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)

    start_date = determine_start_date()
    end_date = date.today()

    print(f"同步范围：{start_date} ～ {end_date}")
    print(f"最近 {REFRESH_DAYS} 天会被重新下载")
    print()

    client = login()

    current_date = start_date
    success_count = 0
    failure_count = 0

    while current_date <= end_date:
        success = download_day(client, current_date)

        if success:
            success_count += 1
        else:
            failure_count += 1

        current_date += timedelta(days=1)

        if current_date <= end_date:
            time.sleep(REQUEST_DELAY_SECONDS)

    print()
    print("=" * 60)
    print(f"同步成功：{success_count} 天")
    print(f"同步失败：{failure_count} 天")

    if failure_count == 0:
        print("Garmin 数据同步完成")
    else:
        print("部分日期同步失败，下次运行时会再次尝试")


if __name__ == "__main__":
    main()