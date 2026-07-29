import os
from dotenv import load_dotenv

load_dotenv()

GARMIN_EMAIL = os.getenv("GARMIN_EMAIL")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")

if not GARMIN_EMAIL:
    raise RuntimeError("未找到 GARMIN_EMAIL")

if not GARMIN_PASSWORD:
    raise RuntimeError("未找到 GARMIN_PASSWORD")