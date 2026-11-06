# Turns the weekly page checks in raw.json into one number a month for each database: the providers
# whose broad page or own page for that database mentions it, leaving out those with a reason in that
# database's not_counted_because column of providers.csv. A page about another database is ignored, since
# it can mention this one without the provider offering it. Each page keeps its last readable result,
# so a page that fails to load doesn't lower the number. Run from the root of the repository.

import csv
import json

FOLDER = "data/managed_mariadb_providers"
OUTPUT_FILES = {
    "mariadb": "monthly.csv",
    "mysql": "monthly_mysql.csv",
    "postgresql": "monthly_postgresql.csv",
}

with open(f"{FOLDER}/raw.json") as f:
    raw = json.load(f)
with open(f"{FOLDER}/providers.csv", newline="") as f:
    providers = list(csv.DictReader(f))

for database, filename in OUTPUT_FILES.items():
    counted = [row["provider"] for row in providers if not row[f"{database}_not_counted_because"]]

    mentions = {}
    monthly = {}
    for date in sorted(raw):
        for provider, pages in raw[date].items():
            for name, page in pages.items():
                if name in ("broad_page", f"{database}_page") and page[database] is not None:
                    mentions[(provider, name)] = page[database]
        monthly[date[:7]] = len({provider for (provider, _), count in mentions.items() if count > 0 and provider in counted})

    with open(f"{FOLDER}/{filename}", "w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["month", f"managed_{database}_providers"])
        for month in sorted(monthly, reverse=True):
            writer.writerow([month, monthly[month]])
