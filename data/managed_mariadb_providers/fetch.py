# Checks whether the pages of managed database providers mention MariaDB, MySQL and PostgreSQL.
# Reads the pages from providers.csv and saves the counts under today's date in raw.json.
# latest_run.csv has the same results for the latest run only, one row per page, for reading.
# Run from the root of the repository. A second run on the same day replaces that day's results.
#
# "mariadb", "mysql" and "postgresql" are numbers of mentions, or null when the page could not be read.
# A page that is gone (404 or 410) counts as 0 mentions. A page that blocks us (403), fails, or names no
# database at all, for example because it needs JavaScript, is null, so raw2monthly.py doesn't record a false drop.
#
# Mentions don't prove that a provider offers a database, so changes are printed for a person to check.

import csv
import datetime
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

FOLDER = "data/managed_mariadb_providers"
USER_AGENT = "mariadb-adoption-index/0.1"
PAGE_COLUMNS = ["broad_page", "mariadb_page", "mysql_page", "postgresql_page"]
DATABASES = ["mariadb", "mysql", "postgresql"]

def read_page(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    result = {"url": url, "status": None, "title": None, "mariadb": None, "mysql": None, "postgresql": None}
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result["status"] = response.status
            body = response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        result["status"] = e.code
        if e.code in (404, 410):
            result.update(mariadb=0, mysql=0, postgresql=0)
        return result
    except Exception as e:
        result["status"] = type(e).__name__
        return result

    title = re.search(r"<title[^>]*>(.*?)</title>", body, re.S | re.I)
    if title:
        result["title"] = re.sub(r"\s+", " ", html.unescape(title.group(1))).strip()

    text = re.sub(r"<(script|style)\b.*?</\1>", " ", body, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    mariadb = len(re.findall(r"maria\s?db", text, re.I))
    mysql = len(re.findall(r"\bmysql\b", text, re.I))
    postgresql = len(re.findall(r"postgres", text, re.I))
    if mariadb + mysql + postgresql > 0:
        result.update(mariadb=mariadb, mysql=mysql, postgresql=postgresql)
    return result

def check_provider(row):
    pages = {name: read_page(row[name]) for name in PAGE_COLUMNS if row[name]}
    return row["provider"], pages

def print_changes(previous, current):
    for provider, pages in current.items():
        for name, page in pages.items():
            before = previous.get(provider, {}).get(name, {})
            if page["mariadb"] is None:
                # Many hosting home pages name no database, which isn't worth a line every week.
                if page["status"] != 200 or before.get("mariadb") is not None:
                    print(f"NOT READ  {provider} {name}: {page['status']} {page['url']}")
                continue
            # A page about one database often mentions others, so only its own name is watched.
            databases = DATABASES if name == "broad_page" else [name.removesuffix("_page")]
            for database in databases:
                if (before.get(database) or 0) > 0 and page[database] == 0:
                    print(f"LOST      {provider} {name} {database}: {before[database]} -> 0 {page['url']}")
                elif before.get(database) == 0 and page[database] > 0:
                    print(f"NEW       {provider} {name} {database}: 0 -> {page[database]} {page['url']}")

def write_latest_run(today, rows, current):
    with open(f"{FOLDER}/latest_run.csv", "w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["date", "provider", "page", "title", "mariadb", "mysql", "postgresql", "status", "not_counted_for", "url"])
        for row in rows:
            not_counted_for = ", ".join(db for db in DATABASES if row[f"{db}_not_counted_because"])
            for name, page in current[row["provider"]].items():
                writer.writerow([today, row["provider"], name.removesuffix("_page"), page["title"], page["mariadb"],
                                 page["mysql"], page["postgresql"], page["status"], not_counted_for, page["url"]])

if __name__ == "__main__":
    today = datetime.date.today().isoformat()
    with open(f"{FOLDER}/providers.csv", newline="") as f:
        rows = list(csv.DictReader(f))

    with ThreadPoolExecutor(8) as pool:
        current = dict(pool.map(check_provider, rows))

    readable = [page for pages in current.values() for page in pages.values() if page["mariadb"] is not None]
    if not readable:
        print("Error: no page could be read, raw.json not changed", file=sys.stderr)
        sys.exit(1)

    raw = {}
    if os.path.exists(f"{FOLDER}/raw.json"):
        with open(f"{FOLDER}/raw.json") as f:
            raw = json.load(f)

    earlier = [date for date in raw if date < today]
    print_changes(raw[max(earlier)] if earlier else {}, current)

    raw[today] = current
    with open(f"{FOLDER}/raw.json", "w") as f:
        json.dump(raw, f, indent=1, sort_keys=True)
        f.write("\n")
    write_latest_run(today, rows, current)

    total = sum(len(pages) for pages in current.values())
    print(f"{today}: read {len(readable)} of {total} pages for {len(current)} providers")
