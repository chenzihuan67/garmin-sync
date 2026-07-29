import json
from pathlib import Path

import pandas as pd

rows = []

for file in sorted(Path("data").glob("*.json")):

    with open(file, "r", encoding="utf-8") as f:
        d = json.load(f)

    stats = d.get("stats", {})
    sleep = d.get("sleep", {})
    heart = d.get("heart_rate", {})
    body = d.get("body_battery", [])

    daily_sleep = sleep.get("dailySleepDTO", {})
    sleep_scores = daily_sleep.get("sleepScores", {})

    body_charged = None
    if body:
        body_charged = body[0].get("charged")

    row = {

        # 日期
        "date": d.get("date"),

        # 活动
        "steps": stats.get("totalSteps"),
        "distance_km": (stats.get("totalDistanceMeters") or 0) / 1000,
        "calories": stats.get("totalKilocalories"),

        # 心率
        "resting_hr": heart.get("restingHeartRate"),
        "min_hr": heart.get("minHeartRate"),
        "max_hr": heart.get("maxHeartRate"),

        # 压力
        "avg_stress": stats.get("averageStressLevel"),
        "max_stress": stats.get("maxStressLevel"),

        # Body Battery
        "bb_charged": body_charged,
        "bb_high": stats.get("bodyBatteryHighestValue"),
        "bb_low": stats.get("bodyBatteryLowestValue"),
        "bb_wakeup": stats.get("bodyBatteryAtWakeTime"),

        # 睡眠
        "sleep_hours":
            (daily_sleep.get("sleepTimeSeconds") or 0) / 3600,

        "nap_hours":
            (daily_sleep.get("napTimeSeconds") or 0) / 3600,

        "deep_hours":
            (daily_sleep.get("deepSleepSeconds") or 0) / 3600,

        "light_hours":
            (daily_sleep.get("lightSleepSeconds") or 0) / 3600,

        "rem_hours":
            (daily_sleep.get("remSleepSeconds") or 0) / 3600,

        "awake_hours":
            (daily_sleep.get("awakeSleepSeconds") or 0) / 3600,

        "sleep_score":
            sleep_scores.get("overall", {}).get("value"),

        "sleep_avg_hr":
            daily_sleep.get("avgHeartRate"),

        # 呼吸
        "respiration":
            stats.get("avgWakingRespirationValue"),
    }

    rows.append(row)

df = pd.DataFrame(rows)

df = df.sort_values("date")

df.to_csv(
    "summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print(df)

print()
print("=" * 60)
print(f"共导出 {len(df)} 天")
print("已生成 summary.csv")