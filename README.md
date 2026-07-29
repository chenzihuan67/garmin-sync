# Garmin Sync V2

Garmin Connect 数据同步项目。原始数据保存在 `data/*.json`，结构化摘要同时写入 `database/garmin.db`，并导出 `summary.csv`。

## 常用命令

```cmd
python src\sync.py
python src\export_csv.py
python src\query.py --start 2026-07-01 --end 2026-07-31
```

## 数据层

- `data/YYYY-MM-DD.json`：完整原始数据备份
- `database/garmin.db`：供程序和未来 AI/MCP 查询
- `summary.csv`：方便 Excel 查看

## 可选环境变量

- `GARMIN_TIMEZONE`，默认 `Asia/Tokyo`
- `GARMIN_START_DATE`，默认 `2024-01-01`
- `GARMIN_REFRESH_DAYS`，默认 `3`
- `GARMIN_REQUEST_DELAY_SECONDS`，默认 `1`
- `GARMIN_LOGIN_RETRIES`，默认 `3`
- `GARMIN_REQUEST_RETRIES`，默认 `3`
