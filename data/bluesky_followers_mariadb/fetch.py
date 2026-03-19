#!/usr/bin/env python3
import csv
import json
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime, timezone
from pathlib import Path

API_BASES = [
    "https://public.api.bsky.app/xrpc",
    "https://api.bsky.app/xrpc",
    "https://bsky.social/xrpc",
]
ACTOR = "mariadb.bsky.social"
SERIES = "bluesky_followers_mariadb"


def fetch_followers_count(actor: str) -> int:
    query = urllib.parse.urlencode({"actor": actor})
    last_error = None
    data = None
    for base in API_BASES:
        url = f"{base}/app.bsky.actor.getProfile?{query}"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "mariadb-adoption-index/1.0",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                break
        except (HTTPError, URLError) as e:
            last_error = e
            continue
    if data is None:
        raise RuntimeError(f"All Bluesky endpoints failed: {last_error}")
    count = data.get("followersCount")
    if count is None:
        raise RuntimeError("followersCount missing from Bluesky profile response")
    return int(count)


def append_daily_row(day_str: str, value: int) -> Path:
    repo_root = Path(__file__).resolve().parents[2]
    out_dir = repo_root / "data" / SERIES
    out_dir.mkdir(parents=True, exist_ok=True)
    daily_csv = out_dir / "daily.csv"

    if not daily_csv.exists():
        daily_csv.write_text(f"date,{SERIES}\n", encoding="utf-8")

    rows = []
    seen_dates = set()
    with open(daily_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
            seen_dates.add(row.get("date"))

    if day_str in seen_dates:
        print(f"Date {day_str} already exists in {daily_csv}, skipping")
        return daily_csv

    rows.append({"date": day_str, SERIES: str(value)})
    with open(daily_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", SERIES])
        writer.writeheader()
        writer.writerows(rows)

    return daily_csv


def main() -> None:
    day_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    followers = fetch_followers_count(ACTOR)
    out = append_daily_row(day_str, followers)
    print(f"Saved {day_str},{followers} to {out}")


if __name__ == "__main__":
    main()
