from garminconnect import Garmin
from datetime import date
from pprint import pprint

email = input("Garmin 邮箱: ")
password = input("Garmin 密码: ")

client = Garmin(email, password)
client.login()

today = date.today().strftime("%Y-%m-%d")

print("=" * 60)
print("今天：", today)

apis = [
    ("get_stats", lambda: client.get_stats(today)),
    ("get_sleep_data", lambda: client.get_sleep_data(today)),
    ("get_body_battery", lambda: client.get_body_battery(today)),
    ("get_heart_rates", lambda: client.get_heart_rates(today)),
    ("get_activities_by_date", lambda: client.get_activities_by_date(today, today)),
]

for name, func in apis:
    print(f"\n{'='*20} {name} {'='*20}")
    try:
        result = func()
        pprint(result)
    except Exception as e:
        print(f"❌ {name} 失败：{e}")