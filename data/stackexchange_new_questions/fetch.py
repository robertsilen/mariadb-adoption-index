import os
import requests
import pandas as pd
import time
from collections import defaultdict
from datetime import datetime, UTC

SITES_API = "https://api.stackexchange.com/2.3/sites"
QUESTIONS_API = "https://api.stackexchange.com/2.3/questions"
STACKEXCHANGE_KEY = os.getenv("STACKEXCHANGE_KEY")


def request_json(url, params, max_retries=5):
    """Request JSON from Stack Exchange API with retries and backoff handling."""
    if STACKEXCHANGE_KEY:
        params = {**params, "key": STACKEXCHANGE_KEY}

    last_error = None
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=30)
        except Exception as e:
            last_error = e
            time.sleep(2 * (attempt + 1))
            continue

        if resp.status_code == 200:
            try:
                data = resp.json()
            except ValueError as e:
                last_error = e
                time.sleep(2 * (attempt + 1))
                continue
            # Respect server-requested backoff
            if "backoff" in data:
                time.sleep(int(data["backoff"]) + 1)
            # Proactive tiny delay to be polite
            time.sleep(0.25)
            return data

        # Rate limited: wait and retry, try to parse backoff if provided
        if resp.status_code == 429:
            try:
                data = resp.json()
                backoff = int(data.get("backoff", 0))
            except Exception:
                backoff = 0
            wait_seconds = max(backoff, 5 * (attempt + 1))
            time.sleep(wait_seconds)
            continue

        # Other transient errors
        last_error = RuntimeError(f"HTTP {resp.status_code}: {resp.text[:200]}")
        time.sleep(2 * (attempt + 1))

    if last_error:
        raise RuntimeError(f"Failed to fetch after retries: {last_error}")
    raise RuntimeError("Failed to fetch after retries with unknown error")


def check_api_key_and_connectivity():
    """Print confirmation about API key presence and basic API connectivity/quota."""
    if STACKEXCHANGE_KEY:
        print("STACKEXCHANGE_KEY found in environment.")
    else:
        print("STACKEXCHANGE_KEY not set. Proceeding with lower quota.")

    try:
        # Minimal call to verify access and show quota
        data = request_json(SITES_API, {"pagesize": 1})
        quota_remaining = data.get("quota_remaining")
        if quota_remaining is not None:
            print(f"Stack Exchange API reachable. Quota remaining: {quota_remaining}")
        else:
            print("Stack Exchange API reachable.")
    except Exception as e:
        print(f"Unable to reach Stack Exchange API: {e}")


def fetch_all_platforms():
    """Return list of Stack Exchange platform identifiers (api_site_parameter) for main sites only."""
    platforms = []
    page = 1
    while True:
        params = {
            "page": page,
            "pagesize": 100,
        }
        data = request_json(SITES_API, params)

        for site in data.get("items", []):
            # Only include main sites, exclude meta sites
            if site.get("site_type") == "main_site":
                api_param = site.get("api_site_parameter")
                if api_param:
                    platforms.append(api_param)

        if not data.get("has_more"):
            break
        page += 1

    # Ensure deterministic order
    platforms = sorted(set(platforms))
    return platforms


def get_mariadb_questions_by_month(platform):
    """Return dict mapping yyyy-mm -> count for questions tagged 'mariadb' on given platform."""
    monthly_counts = defaultdict(int)

    params = {
        "site": platform,
        "tagged": "mariadb",
        "pagesize": 100,
        "order": "desc",
        "sort": "creation",
    }

    page = 1
    while True:
        params["page"] = page
        try:
            data = request_json(QUESTIONS_API, params)
        except RuntimeError:
            # If a site errors (e.g., tag not supported or persistent rate limit), stop for this platform
            break

        for item in data.get("items", []):
            created_ts = item.get("creation_date")
            if created_ts is None:
                continue
            month = datetime.fromtimestamp(created_ts, UTC).strftime("%Y-%m")
            monthly_counts[month] += 1

        if not data.get("has_more"):
            break
        page += 1

    return dict(monthly_counts)


def main():
    check_api_key_and_connectivity()
    platforms = fetch_all_platforms()
    print("Count of platforms found:", len(platforms))

    # Aggregate raw counts per platform/month
    raw_rows = []
    for platform in platforms:
        try:
            counts = get_mariadb_questions_by_month(platform)
            print(platform, len(counts))
        except Exception:
            counts = {}
        for month, count in counts.items():
            raw_rows.append({
                "month": month,
                "platform": platform,
                "monthly_counts": int(count),
            })

    # Build raw.csv: month, platform, monthly_counts (yyyy-mm)
    if raw_rows:
        raw_df = pd.DataFrame(raw_rows)
        raw_df = raw_df.sort_values(["month", "platform"]).reset_index(drop=True)
    else:
        raw_df = pd.DataFrame(columns=["month", "platform", "monthly_counts"])

    raw_df.to_csv("data/stackexchange_new_questions/raw.csv", index=False)

    # Group by month across all platforms and save to monthly.csv
    if not raw_df.empty:
        monthly_df = (
            raw_df.groupby("month", as_index=False)["monthly_counts"].sum()
            .rename(columns={"monthly_counts": "stackexchange_new_questions"})
            .sort_values("month")
            .reset_index(drop=True)
        )
    else:
        monthly_df = pd.DataFrame(columns=["month", "stackexchange_new_questions"])

    monthly_df.to_csv("data/stackexchange_new_questions/monthly.csv", index=False)


if __name__ == "__main__":
    main()


