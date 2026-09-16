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

Side data (not part of the index) from the same API response, written to
monthly_total_distros.csv as:

    month,total_distros,total_repos

where total_repos is the number of distinct Repology repositories carrying a
MariaDB package (Debian 12, Debian 13 and Debian unstable count as three), and
total_distros collapses those to distinct distributions / package ecosystems
(Debian counts once). See distro_of() for the collapsing rule.

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
TOTALS_CSV_PATH = os.path.join(HERE, "monthly_total_distros.csv")
TOTALS_COLS = ["total_distros", "total_repos"]

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


def distro_of(repo):
    """Collapse a Repology repository name to its distribution / ecosystem.

    Repology names repositories '<distro>[_<release or channel>...]', e.g.
    debian_12, debian_unstable, ubuntu_24_04, fedora_rawhide, alpine_edge,
    opensuse_leap_15_6, opensuse_tumbleweed, nix_unstable, or just homebrew.
    The leading token is the distribution, so that is what we keep.
    """
    return repo.split("_", 1)[0]


def compute_totals(packages):
    repos = {p["repo"] for p in packages if p.get("repo")}
    distros = {distro_of(r) for r in repos}
    return len(distros), len(repos)


def upsert_month(path, columns, month, values):
    """Write `values` for `month` to `path`, replacing any existing row for that month."""
    rows = []
    if os.path.exists(path):
        with open(path, newline="") as f:
            rows = list(csv.reader(f))
    body = [r for r in rows[1:] if r and r[0] != month] if rows else []
    body.append([month] + [f"{v}" for v in values])
    body.sort(key=lambda r: r[0])
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["month"] + columns)
        w.writerows(body)


def main():
    packages = fetch()
    value, current, behind = compute_currency(packages)
    total_distros, total_repos = compute_totals(packages)
    month = date.today().strftime("%Y-%m")
    upsert_month(CSV_PATH, [COL], month, [value])
    upsert_month(TOTALS_CSV_PATH, TOTALS_COLS, month, [total_distros, total_repos])
    print(f"{month}: {COL}={value}  "
          f"(current={current}, behind={behind}, packages_seen={len(packages)})")
    print(f"wrote {CSV_PATH}")
    print(f"{month}: total_distros={total_distros} total_repos={total_repos}")
    print(f"wrote {TOTALS_CSV_PATH}")


if __name__ == "__main__":
    main()
