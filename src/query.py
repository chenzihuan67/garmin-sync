import argparse
import json
from statistics import mean

from database import GarminDatabase


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="查询 Garmin SQLite 数据")
    parser.add_argument("--start", help="开始日期，格式 YYYY-MM-DD")
    parser.add_argument("--end", help="结束日期，格式 YYYY-MM-DD")
    parser.add_argument(
        "--format",
        choices=("json", "summary"),
        default="summary",
        help="输出格式",
    )
    return parser.parse_args()


def average(rows: list[dict], field: str):
    values = [row[field] for row in rows if row.get(field) is not None]
    return round(mean(values), 2) if values else None


def main() -> None:
    args = parse_args()
    with GarminDatabase() as database:
        rows = database.fetch_summaries(args.start, args.end)

    if args.format == "json":
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return

    if not rows:
        print("没有符合条件的数据")
        return

    print(f"日期范围：{rows[0]['date']} ～ {rows[-1]['date']}")
    print(f"天数：{len(rows)}")
    print(f"平均步数：{average(rows, 'steps')}")
    print(f"平均睡眠：{average(rows, 'sleep_hours')} 小时")
    print(f"平均静息心率：{average(rows, 'resting_hr')}")
    print(f"平均压力：{average(rows, 'avg_stress')}")
    print(f"平均睡眠分数：{average(rows, 'sleep_score')}")


if __name__ == "__main__":
    main()
