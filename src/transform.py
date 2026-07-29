from typing import Any


def _hours(seconds: Any) -> float:
    return float(seconds or 0) / 3600


def extract_daily_summary(payload: dict[str, Any]) -> dict[str, Any]:
    stats = payload.get("stats") or {}
    sleep = payload.get("sleep") or {}
    heart = payload.get("heart_rate") or {}
    body = payload.get("body_battery") or []

    daily_sleep = sleep.get("dailySleepDTO") or {}
    sleep_scores = daily_sleep.get("sleepScores") or {}

    body_charged = None
    if isinstance(body, list) and body:
        first = body[0] or {}
        if isinstance(first, dict):
            body_charged = first.get("charged")

    activities = payload.get("activities") or []
    activity_count = len(activities) if isinstance(activities, list) else 0

    return {
        "date": payload.get("date"),
        "steps": stats.get("totalSteps"),
        "distance_km": float(stats.get("totalDistanceMeters") or 0) / 1000,
        "calories": stats.get("totalKilocalories"),
        "resting_hr": heart.get("restingHeartRate"),
        "min_hr": heart.get("minHeartRate"),
        "max_hr": heart.get("maxHeartRate"),
        "avg_stress": stats.get("averageStressLevel"),
        "max_stress": stats.get("maxStressLevel"),
        "bb_charged": body_charged,
        "bb_high": stats.get("bodyBatteryHighestValue"),
        "bb_low": stats.get("bodyBatteryLowestValue"),
        "bb_wakeup": stats.get("bodyBatteryAtWakeTime"),
        "sleep_hours": _hours(daily_sleep.get("sleepTimeSeconds")),
        "nap_hours": _hours(daily_sleep.get("napTimeSeconds")),
        "deep_hours": _hours(daily_sleep.get("deepSleepSeconds")),
        "light_hours": _hours(daily_sleep.get("lightSleepSeconds")),
        "rem_hours": _hours(daily_sleep.get("remSleepSeconds")),
        "awake_hours": _hours(daily_sleep.get("awakeSleepSeconds")),
        "sleep_score": (sleep_scores.get("overall") or {}).get("value"),
        "sleep_avg_hr": daily_sleep.get("avgHeartRate"),
        "respiration": stats.get("avgWakingRespirationValue"),
        "activity_count": activity_count,
    }
