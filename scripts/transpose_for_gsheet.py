#!/usr/bin/env python3
"""Transpose the monthly index CSV into the column order used by the GSheet.

Input (default):
  index/mariadb_adoption_index_table_12m.csv   (metrics as rows, months as columns)

Output (default):
  temp/mariadb_adoption_index_table_12m_gsheet_ready.csv   (months as rows, newest first)

The column order matches the "Metrics" sheet of
"MariaDB Community Metrics (mariadb.org).xlsx". That order used to be read out
of the xlsx at runtime, which meant the script only worked on a machine that
happened to have the file. It is pinned below instead, so the script is
reproducible from a clean checkout. Pass --xlsx to re-derive the order from the
spreadsheet after adding or reordering columns there.
"""

from __future__ import annotations

import argparse
import csv
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# ---------------------------------------------------------------------------
# EDIT THIS WHEN THE GSHEET GAINS/REORDERS COLUMNS:
# (metric name in the index CSV, column header in the GSheet), in sheet order.
# ---------------------------------------------------------------------------
GSHEET_COLUMNS: list[tuple[str, str]] = [
    ("MariaDB.org Downloads", "Total mariadb.org downloads"),
    ("Debian Popcon", "debian (no_files, recent, old)"),
    ("Docker Official Image Pulls", "Docker Official Image pulls monthly from robert's git repo"),
    ("Reddit Subscribers (MariaDB)", "Reddit Subscribers (MariaDB)"),
    ("X (Twitter) Foundation Followers", "X (Twitter Followers)"),
    ("X (Twitter) plc Followers", "X (Twitter, plc)"),
    ("Fosstodon Followers Foundation", "Fosstodon"),
    ("DB Engines Score", "DB Engines Score"),
    ("GitHub Stars", "GitHub stars"),
    ("Zulip Total Users", "Zulip Total Users"),
    ("Zulip Users 15-day active", "Zulip Total Users 15-day active"),
    ("LinkedIn Followers Foundation", "LinkedIn Followers"),
    ("LinkedIn Followers PLC", "LinkedIn (plc)"),
    ("Instagram Followers Foundation", "Instagram Followers"),
    ("YouTube Subscribers Foundation", "YouTube Subscribers (Videos)"),
    ("YouTube Subscribers plc", "YouTube (plc 2012)"),
    ("Stackexchange new mariadb questions", "Stackexchange all new mariadb questions"),
    ("Wikipedia Views All Langs", "Wikipedia views (all langs)"),
    ("Github repo README mariadb", "Github repo README mariadb"),
    ("Hackernews", "Hackernews"),
    ("Google Trends", "Google Trends"),
    ("Github New PRs Unique Contributors", "Github server PRs unique contributors rolling 12 months"),
    ("GitHub New PRs External", "Github server external PRs"),
]

# Metrics with no column in the Metrics sheet; appended at the end under their
# index-CSV names so new signals are never silently dropped.
METRICS_SHEET_NAME = "Metrics"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--input-csv", default="index/mariadb_adoption_index_table_12m.csv",
                   help="Source CSV (metrics as rows, months as columns).")
    p.add_argument("--output-csv", default="temp/mariadb_adoption_index_table_12m_gsheet_ready.csv",
                   help="Output CSV path.")
    p.add_argument("--months", type=int, default=0,
                   help="Only emit the N newest months (0 = all).")
    p.add_argument("--xlsx", default=None,
                   help="Re-derive column order from this xlsx instead of the pinned list.")
    return p.parse_args()


def read_source_matrix(input_csv: Path) -> tuple[list[str], dict[str, list[str]]]:
    with input_csv.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if not rows or len(rows[0]) < 2:
        raise ValueError("Input CSV does not look like the expected matrix format.")

    months = [c.strip() for c in rows[0][1:] if c.strip()]
    metrics: dict[str, list[str]] = {}
    for r in rows[1:]:
        if not r or not (r[0] or "").strip():
            continue
        values = r[1:]
        values += [""] * (len(months) - len(values))
        metrics[r[0].strip()] = values[:len(months)]
    return months, metrics


def get_xlsx_headers(xlsx_path: Path, sheet_name: str) -> list[str]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    rel_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    with zipfile.ZipFile(xlsx_path) as zf:
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rel_map = {r.attrib["Id"]: r.attrib["Target"] for r in rels.findall(
            "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")}

        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            ss = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.findall(".//a:t", ns))
                      for si in ss.findall("a:si", ns)]

        for sheet in wb.findall("a:sheets/a:sheet", ns):
            if sheet.attrib.get("name") != sheet_name:
                continue
            ws = ET.fromstring(zf.read("xl/" + rel_map[sheet.attrib[rel_ns]]))
            row1 = ws.find('a:sheetData/a:row[@r="1"]', ns)
            if row1 is None:
                return []
            headers = []
            for cell in row1.findall("a:c", ns):
                v = cell.find("a:v", ns)
                if v is None:
                    headers.append("")
                elif cell.attrib.get("t") == "s":
                    headers.append(shared[int(v.text)])
                else:
                    headers.append(v.text or "")
            return headers
    raise ValueError(f"Sheet '{sheet_name}' not found in {xlsx_path}.")


def main() -> int:
    args = parse_args()
    months, metrics = read_source_matrix(Path(args.input_csv))

    columns = GSHEET_COLUMNS
    if args.xlsx:
        by_header = {h: m for m, h in GSHEET_COLUMNS}
        columns = [(by_header[h], h)
                   for h in get_xlsx_headers(Path(args.xlsx), METRICS_SHEET_NAME)
                   if h in by_header]

    mapped = [(m, h) for m, h in columns if m in metrics]
    unmapped = [m for m in metrics if m not in {m for m, _ in mapped}]

    order = sorted(range(len(months)), key=lambda i: months[i], reverse=True)
    if args.months:
        order = order[:args.months]

    out_path = Path(args.output_csv)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date"] + [h for _, h in mapped] + unmapped)
        for i in order:
            w.writerow([months[i]]
                       + [metrics[m][i] for m, _ in mapped]
                       + [metrics[m][i] for m in unmapped])

    print(f"Wrote {len(order)} rows to {out_path}")
    missing = [m for m, _ in columns if m not in metrics]
    if missing:
        print("GSheet columns with no matching metric in the index CSV:")
        for m in missing:
            print(f"- {m}")
    if unmapped:
        print("Metrics with no GSheet column, appended at the end:")
        for m in unmapped:
            print(f"- {m}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
