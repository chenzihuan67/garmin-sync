import json
from pathlib import Path
from datetime import date

from garminconnect import Garmin

email = input("Garmin 邮箱: ")
password = input("Garmin 密码: ")

client = Garmin(email, password)
client.login()

today = date.today().strftime("%Y-%m-%d")

print(f"下载 {today} 数据...")

output = {
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
    json.dump(output, f, ensure_ascii=False, indent=2)

print()
print("================================")
print("保存成功：")
print(filename)
print("================================")