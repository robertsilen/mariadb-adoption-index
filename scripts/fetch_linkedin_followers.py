#!/usr/bin/env python3
"""
Fetch LinkedIn follower counts for MariaDB PLC and Foundation via Apify
(artificially/linkedin-company-scraper) and append to daily CSVs.
Requires APIFY_API_TOKEN in environment.
"""
import os
import re
import csv
from pathlib import Path

try:
    from apify_client import ApifyClient
except ImportError:
    raise SystemExit("Install apify-client: pip install apify-client")

# Apify actor: no login, returns followerCount from public company pages
ACTOR_ID = "artificially/linkedin-company-scraper"
# LinkedIn company URLs (about page data comes from same place)
COMPANIES = [
    ("mariadb-corporation", "linkedin_followers_plc"),
    ("mariadb-foundation", "linkedin_followers_foundation"),
]


def parse_follower_count(raw: str) -> int | None:
    """Convert '21,000' or '2.3M' style string to int, or None if invalid."""
    if not raw or not isinstance(raw, str):
        return None
    raw = raw.strip().replace(",", "").replace(" ", "")
    if not raw:
        return None
    # Handle "2.3M" etc.
    m = re.match(r"^([\d.]+)\s*([KkMmBb])?$", raw)
    if m:
        num = float(m.group(1))
        suffix = (m.group(2) or "").upper()
        if suffix == "K":
            num *= 1_000
        elif suffix == "M":
            num *= 1_000_000
        elif suffix == "B":
            num *= 1_000_000_000
        return int(num)
    try:
        return int(float(raw))
    except ValueError:
        return None


def main() -> None:
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        raise SystemExit("APIFY_API_TOKEN environment variable is required")

    client = ApifyClient(token)
    company_urls = [f"https://www.linkedin.com/company/{slug}" for slug, _ in COMPANIES]

    run_input = {"companyUrls": company_urls}
    run = client.actor(ACTOR_ID).call(run_input=run_input)
    dataset_id = run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())

    repo_root = Path(__file__).resolve().parent.parent
    date = os.environ.get("DATE")  # e.g. from workflow; default to today
    if not date:
        from datetime import date as date_type
        date = date_type.today().isoformat()

    by_id = {item.get("companyId"): item for item in items}

    for slug, series_name in COMPANIES:
        item = by_id.get(slug)
        if not item:
            print(f"Warning: no result for company {slug}, skipping")
            continue
        raw = item.get("followerCount")
        count = parse_follower_count(str(raw)) if raw is not None else None
        if count is None:
            print(f"Warning: could not parse followerCount for {slug}: {raw!r}")
            continue

        data_dir = repo_root / "data" / series_name
        data_dir.mkdir(parents=True, exist_ok=True)
        daily_path = data_dir / "daily.csv"

        # Ensure header
        if not daily_path.exists():
            daily_path.write_text(f"date,{series_name}\n", encoding="utf-8")

        # Read existing rows to avoid duplicate date
        existing_dates = set()
        rows = []
        with open(daily_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
                existing_dates.add(row["date"])

        if date in existing_dates:
            print(f"Date {date} already in {daily_path}, skipping append")
            continue

        rows.append({"date": date, series_name: str(count)})
        with open(daily_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["date", series_name])
            writer.writeheader()
            writer.writerows(rows)
        print(f"Appended {date},{count} to {daily_path}")


if __name__ == "__main__":
    main()
