import json
import sqlite3
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from paths import DATABASE_PATH
from transform import extract_daily_summary

SUMMARY_COLUMNS = [
    "date",
    "steps",
    "distance_km",
    "calories",
    "resting_hr",
    "min_hr",
    "max_hr",
    "avg_stress",
    "max_stress",
    "bb_charged",
    "bb_high",
    "bb_low",
    "bb_wakeup",
    "sleep_hours",
    "nap_hours",
    "deep_hours",
    "light_hours",
    "rem_hours",
    "awake_hours",
    "sleep_score",
    "sleep_avg_hr",
    "respiration",
    "activity_count",
]


class GarminDatabase:
    def __init__(self, path: Path = DATABASE_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.initialize()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()

    def close(self) -> None:
        self.connection.close()

    def initialize(self) -> None:
        self.connection.executescript(
            """
            PRAGMA journal_mode = DELETE;
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS raw_daily (
                date TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS daily_summary (
                date TEXT PRIMARY KEY,
                steps INTEGER,
                distance_km REAL,
                calories INTEGER,
                resting_hr INTEGER,
                min_hr INTEGER,
                max_hr INTEGER,
                avg_stress INTEGER,
                max_stress INTEGER,
                bb_charged INTEGER,
                bb_high INTEGER,
                bb_low INTEGER,
                bb_wakeup INTEGER,
                sleep_hours REAL,
                nap_hours REAL,
                deep_hours REAL,
                light_hours REAL,
                rem_hours REAL,
                awake_hours REAL,
                sleep_score INTEGER,
                sleep_avg_hr INTEGER,
                respiration REAL,
                activity_count INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_daily_summary_date
            ON daily_summary(date);
            """
        )
        self.connection.commit()

    def upsert_payload(self, payload: dict[str, Any]) -> None:
        summary = extract_daily_summary(payload)
        day_text = str(summary["date"])

        self.connection.execute(
            """
            INSERT INTO raw_daily(date, payload_json, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(date) DO UPDATE SET
                payload_json = excluded.payload_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (day_text, json.dumps(payload, ensure_ascii=False)),
        )

        placeholders = ", ".join("?" for _ in SUMMARY_COLUMNS)
        assignments = ", ".join(
            f"{column}=excluded.{column}"
            for column in SUMMARY_COLUMNS
            if column != "date"
        )
        values = [summary[column] for column in SUMMARY_COLUMNS]

        self.connection.execute(
            f"""
            INSERT INTO daily_summary ({', '.join(SUMMARY_COLUMNS)})
            VALUES ({placeholders})
            ON CONFLICT(date) DO UPDATE SET
                {assignments},
                updated_at = CURRENT_TIMESTAMP
            """,
            values,
        )
        self.connection.commit()

    def import_payloads(self, payloads: Iterable[dict[str, Any]]) -> int:
        count = 0
        for payload in payloads:
            self.upsert_payload(payload)
            count += 1
        return count

    def latest_date(self) -> str | None:
        row = self.connection.execute(
            "SELECT MAX(date) AS latest_date FROM daily_summary"
        ).fetchone()
        return row["latest_date"] if row else None

    def fetch_summaries(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        parameters: list[str] = []

        if start_date:
            conditions.append("date >= ?")
            parameters.append(start_date)
        if end_date:
            conditions.append("date <= ?")
            parameters.append(end_date)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = self.connection.execute(
            f"SELECT {', '.join(SUMMARY_COLUMNS)} "
            f"FROM daily_summary {where} ORDER BY date",
            parameters,
        ).fetchall()
        return [dict(row) for row in rows]
