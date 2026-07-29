import csv

from database import GarminDatabase, SUMMARY_COLUMNS
from paths import SUMMARY_CSV_PATH


def export_csv() -> int:
    with GarminDatabase() as database:
        rows = database.fetch_summaries()

    with SUMMARY_CSV_PATH.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print("=" * 60)
    print(f"共导出 {len(rows)} 天")
    print(f"已生成 {SUMMARY_CSV_PATH.name}")
    return len(rows)


if __name__ == "__main__":
    export_csv()
