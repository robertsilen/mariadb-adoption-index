#!/usr/bin/env python3
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from urllib.error import HTTPError, URLError
from datetime import datetime, timedelta, timezone
from pathlib import Path

API_BASES = [
    "https://public.api.bsky.app/xrpc",
    "https://api.bsky.app/xrpc",
    "https://bsky.social/xrpc",
]
QUERY = "mariadb"
SERIES = "bluesky_mentions_mariadb"


def _request_json(url: str, headers: dict | None = None) -> dict:
    req_headers = {
        "User-Agent": "mariadb-adoption-index/1.0",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_auth_headers() -> dict:
    handle = os.environ.get("BLUESKY_HANDLE")
    app_password = os.environ.get("BLUESKY_APP_PASSWORD")
    if not handle or not app_password:
        return {}

    body = json.dumps({"identifier": handle, "password": app_password}).encode("utf-8")
    for base in API_BASES:
        url = f"{base}/com.atproto.server.createSession"
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "User-Agent": "mariadb-adoption-index/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                token = data.get("accessJwt")
                if token:
                    return {"Authorization": f"Bearer {token}"}
        except Exception:
            continue
    return {}


def fetch_page(params: dict, auth_headers: dict) -> dict:
    endpoint = "app.bsky.feed.searchPosts"
    query = urllib.parse.urlencode(params)
    last_error = None
    for base in API_BASES:
        url = f"{base}/{endpoint}?{query}"
        try:
            return _request_json(url, headers=auth_headers)
        except (HTTPError, URLError) as e:
            last_error = e
            continue
    raise RuntimeError(f"All Bluesky endpoints failed: {last_error}")


def count_mentions_for_day(day_str: str) -> int:
    day = datetime.strptime(day_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    next_day = day + timedelta(days=1)
    since = day.isoformat().replace("+00:00", "Z")
    until = next_day.isoformat().replace("+00:00", "Z")

    total = 0
    cursor = None
    max_pages = 100
    auth_headers = _get_auth_headers()

    for _ in range(max_pages):
        params = {
            "q": QUERY,
            "limit": 100,
            "sort": "latest",
            "since": since,
            "until": until,
        }
        if cursor:
            params["cursor"] = cursor

        data = fetch_page(params, auth_headers)
        posts = data.get("posts", [])

        # Count only posts that actually contain the token to avoid broad match drift.
        for post in posts:
            record = post.get("record", {})
            text = (record.get("text") or "").lower()
            if "mariadb" in text:
                total += 1

        cursor = data.get("cursor")
        if not cursor or not posts:
            break

        # Be polite with API rate/latency.
        time.sleep(0.2)

    return total


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
    try:
        mentions = count_mentions_for_day(day_str)
    except Exception as e:
        raise SystemExit(
            "Failed to fetch Bluesky mentions. "
            "If you see 403 errors, set BLUESKY_HANDLE and BLUESKY_APP_PASSWORD "
            f"for authenticated requests. Original error: {e}"
        )
    out = append_daily_row(day_str, mentions)
    print(f"Saved {day_str},{mentions} to {out}")


if __name__ == "__main__":
    main()
