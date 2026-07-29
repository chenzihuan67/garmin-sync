from database import GarminDatabase
from storage import JsonStorage


def main() -> None:
    storage = JsonStorage()
    with GarminDatabase() as database:
        count = database.import_payloads(storage.iter_payloads())
    print(f"SQLite 重建完成：导入 {count} 天")


if __name__ == "__main__":
    main()
