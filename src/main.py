import json
from pathlib import Path
from datetime import date

from garminconnect import Garmin
from config import GARMIN_EMAIL, GARMIN_PASSWORD


def login():
    client = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    client.login()

    print("✓ 登录成功")
    print("用户：", client.get_full_name())

    return client


def download_today(client):
    today = date.today().strftime("%Y-%m-%d")

    print(f"\n开始下载 {today} 数据……")

    data = {
        "date": today,
        "stats": client.get_stats(today),
        "sleep": client.get_sleep_data(today),
        "body_battery": client.get_body_battery(today),
        "heart_rate": client.get_heart_rates(today),
        "activities": client.get_activities_by_date(today, today),
    }

    Path("data").mkdir(exist_ok=True)

    filename = Path("data") / f"{today}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ 已保存：{filename}")


def main():
    client = login()
    download_today(client)


if __name__ == "__main__":
    main()