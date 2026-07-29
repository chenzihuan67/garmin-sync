"""兼容旧命令：实际同步逻辑已迁移到 sync.py。"""

from sync import sync_history


if __name__ == "__main__":
    raise SystemExit(sync_history())
