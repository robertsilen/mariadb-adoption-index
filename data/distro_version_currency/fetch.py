#!/usr/bin/env python3
"""
distro_version_currency — how current MariaDB is across Linux distributions.

Layer B (Available) of the adoption index: MariaDB is packaged almost
everywhere, so mere presence is not interesting; what matters is whether the
packaged version is *current*. This signal measures that.

Source: Repology (https://repology.org/api/v1/project/mariadb), which tracks the
MariaDB package version in hundreds of distribution repositories and flags each
one as 'newest' (up to date), 'outdated' (behind latest), etc.

Metric (0-100): of the repositories with a clear up-to-date / behind verdict,
the share that ship an up-to-date MariaDB:

    currency = 100 * current / (current + behind)

One snapshot value per month, appended to monthly.csv as:

    month,distro_version_currency

Idempotent: re-running within the same month overwrites that month's row, so a
manual run today and the scheduled end-of-month run won't create duplicates.

Dependency-free (standard library only) so it can be run manually right away:

    python data/distro_version_currency/fetch.py
"""
import csv
import json
import os
from datetime import date
from urllib.request import Request, urlopen

API_URL = "https://repology.org/api/v1/project/mariadb"
# Repology asks for a descriptive User-Agent and blocks the default one.
UA = "mariadb-adoption-index/1.0 (+https://github.com/robertsilen/mariadb-adoption-index)"

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "monthly.csv")
COL = "distro_version_currency"

# Repology per-package statuses. "current" = shipping the latest (or a newer)
# version; "behind" = shipping an older one. Statuses that carry no
# up-to-date/behind judgement (noscheme, incorrect, untrusted, ignored) are
# excluded from the denominator.
CURRENT = {"newest", "unique", "devel", "rolling"}
BEHIND = {"outdated", "legacy"}


def fetch():
    req = Request(API_URL, headers={"User-Agent": UA, "Accept": "application/json"})
    with urlopen(req, timeout=60) as r:
        return json.load(r)


def compute_currency(packages):
    current = sum(1 for p in packages if p.get("status") in CURRENT)
    behind = sum(1 for p in packages if p.get("status") in BEHIND)
    total = current + behind
    if total == 0:
        raise SystemExit("No up-to-date/behind repositories found — "
                         "unexpected Repology response, not writing.")
    return round(100.0 * current / total, 2), current, behind


def upsert_month(month, value):
    """Write value for `month`, replacing any existing row for that month."""
    rows = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="") as f:
            rows = list(csv.reader(f))
    body = [r for r in rows[1:] if r and r[0] != month] if rows else []
    body.append([month, f"{value}"])
    body.sort(key=lambda r: r[0])
    with open(CSV_PATH, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month", COL])
        w.writerows(body)


def main():
    packages = fetch()
    value, current, behind = compute_currency(packages)
    month = date.today().strftime("%Y-%m")
    upsert_month(month, value)
    print(f"{month}: {COL}={value}  "
          f"(current={current}, behind={behind}, repos_seen={len(packages)})")
    print(f"wrote {CSV_PATH}")


if __name__ == "__main__":
    main()
