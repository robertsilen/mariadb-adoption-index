# Ecosystem Hub entries before daily collection

Daily collection started on 2026-11-06. The earlier values in `monthly.csv` were worked out afterwards from the snapshots below. All counts use the same visibility filters as `fetch.py`. Each value is the count at the end of the month.

The Hub launched on [2026-03-04](https://mariadb.org/the-queen-of-naboo-and-many-systems-mariadb-ecosystem-hub/). March and April are left out because no count from those months has been found.

## Snapshots

| Date | Entries | Source |
|------------|-----|---------------------------------------------------------------|
| 2026-05-13 | 133 | Local export, `adoption-project-repos/ecohub_and_candidates.csv` (not public). All 133 IDs are still in the 14 July snapshot |
| 2026-07-14 | 146 | [Wayback categories.json](https://web.archive.org/web/20260714143637id_/https://ecohub.mariadb.org/categories.json) and its category files |
| 2026-08-10 | 187 | Common Crawl CC-MAIN-2026-34: 185 entries. Its copy has no `solution-stacks` file, so the 2 stacks from the July and September snapshots are added |
| 2026-09-18 | 200 | [Wayback categories.json](https://web.archive.org/web/20260918131054id_/https://ecohub.mariadb.org/categories.json) and its category files |
| 2026-10-07 | 202 | Local copy, `cia/ecohub/raw/` (not public) |
| 2026-11-06 | 219 | `daily.csv`, equal to the Hub home page on that day |

## Month-end values

`dateAdded` means the field on each entry in the current catalog. It only covers entries added from July 2026 on, and not all of them, so it can't be used alone.

| Month | Value | Confidence | How |
|---------|-----|------------|--------------------------------------------------------|
| 2026-05 | 134 | Lower bound | 133 on 13 May, plus the [first Solution Stack on 15 May](https://mariadb.org/introducing-our-first-mariadb-server-solution-stack-a-privacy-first-stack-with-nextcloud-passbolt-and-mariadb/). Up to 10 more may have been added by 31 May |
| 2026-06 | 144 | Upper bound | 146 on 14 July, minus `emma` (dated 1 July) and `sovereign-multi-cloud-db-stack` (dated 14 July) |
| 2026-07 | 181 | Estimate | 187 on 10 August, minus 6 entries dated August. Assumes 27 undated entries, mostly plugins, arrived in July. If they arrived in August, the value is 154 |
| 2026-08 | 192 | Derived | 200 on 18 September, minus 8 entries added in September. Also 187 on 10 August plus 5 dated August |
| 2026-09 | 200 | Derived | 200 on 18 September, with no entries dated 19 to 30 September. The 2 entries added by 7 October are dated October |
| 2026-10 | 217 | Derived | 219 on 6 November, minus 2 dated November. Also 202 on 7 October plus 15 dated October. Matches the 217 in Anna Widenius's table |
| 2026-11 | 219 | Measured | `daily.csv` |

## Notes

- **July:** the evidence for the plugins arriving in July is indirect. lefred's [plugin list](https://lefred.be/my-mariadb-server-plugins/) was published on 24 July, and on 27 July Anna Widenius described the Hub as "about 200" in a chat. The 14 July snapshot has 32 plugins and the 10 August one has 57.
- **`layerbase`:** its `dateAdded` is 2029-09-07, treated here as 2026-09-07. It isn't in the 10 August snapshot and is in the 18 September one.
- **Not used:** a LinkedIn post, seen only in search results, reportedly says 50 products at launch and more than 140 after three months. It couldn't be opened to check.
