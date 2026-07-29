import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from paths import DATA_DIR


class JsonStorage:
    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def path_for(self, day: date | str) -> Path:
        day_text = day.isoformat() if isinstance(day, date) else day
        return self.data_dir / f"{day_text}.json"

    def existing_dates(self) -> list[date]:
        dates: list[date] = []
        for file in self.data_dir.glob("*.json"):
            try:
                dates.append(datetime.strptime(file.stem, "%Y-%m-%d").date())
            except ValueError:
                continue
        return sorted(dates)

    def save_atomic(self, payload: dict[str, Any]) -> Path:
        day_text = str(payload["date"])
        target = self.path_for(day_text)
        temporary = target.with_suffix(".json.tmp")

        with temporary.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)

        temporary.replace(target)
        return target

    def load(self, file: Path) -> dict[str, Any]:
        with file.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def iter_payloads(self):
        for file in sorted(self.data_dir.glob("*.json")):
            yield self.load(file)
