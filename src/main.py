"""默认入口：同步 Garmin 数据并更新 SQLite。"""

from sync import sync_history


if __name__ == "__main__":
    raise SystemExit(sync_history())
