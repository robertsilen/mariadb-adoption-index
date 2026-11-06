# Metrics by group (v2)

Which signals feed each layer, named by their `data/<folder>/` path in this repo.
Source of truth: [`index_v2_config.csv`](index_v2_config.csv) (`label,path,weight,layer`).
Weights in parentheses.

## A · Running — is MariaDB actually deployed & used?
- `mariadborg_downloads` (20)
- `debian_popcon` (10)
- `docker_official_image_pulls` (10)

## B · Available — can people easily get & pick it?
- `distro_version_currency` — *data folder + monthly workflow built; not yet
  added to `index_v2_config.csv` (needs a first-month baseline fallback in the
  aggregator before it can be indexed).*

*Still the thinnest layer. Three more planned — see "Potential new sources".*

## C · Chosen — is it deliberately chosen?
*No signals yet — comes from the survey. See "Potential new sources" below.*

## D · Visible — mindshare / how much it's talked about
- `db_engines_score` (10)
- `google_trends` (5)
- `wikipedia_views_all_langs` (5)
- `github_stars` (3)
- `github_repo_readme` (3)
- `reddit_subscribers` (3)
- `hackernews` (3)
- `stackexchange_new_questions` (3)
- `linkedin_followers_foundation` (2)
- `linkedin_followers_plc` (2)
- `youtube_subscribers_foundation` (2)
- `youtube_subscribers_plc` (2)
- `fosstodon_followers_foundation` (1)
- `instagram_followers_foundation` (1)
- `x_followers_foundation` (1)
- `x_followers_plc` (1)

## Participation — contribution to the project
- `github_new_prs_external` (5)
- `github_returning_contributors` (3)
- `github_new_prs_unique_contributors` (2)
- `zulip_total_users` (2)
- `zulip_users_active_15d` (1)

## Composite
Not a layer — the weighted blend of **all** of the above (same method as v1).

---

# Potential new sources to add

## Already in `data/` but not yet tagged in v2
These folders exist in the repo but are **not** in `index_v2_config.csv`. Decide a layer + weight, or drop:

- `brew_installs_30d` → **A · Running** (macOS installs — fills the Running layer)
- `bluesky_followers_mariadb` → **D · Visible**
- `bluesky_mentions_mariadb` → **D · Visible**
- `instagram_followers_plc` → **D · Visible** (Foundation one is already in; add plc for parity)
- `bing_search_mariadb_database` → **D · Visible** (search interest)
- `google_search_mariadb_database` → **D · Visible** (search interest)

## B · Available — new signals to build (highest priority: the thin layer)
- ✅ **Distro version currency** — `data/distro_version_currency/` built (Repology API, monthly).
- **Cloud catalog presence** — is MariaDB on the menu in AWS / Azure / GCP / DigitalOcean / etc. managed-DB catalogs (count of clouds offering it). Manual checklist, ~quarterly.
- **Framework / ORM support** — is MariaDB a first-class option (not just "MySQL-compatible") in Laravel, Django, Rails, Spring, Prisma, etc. Manual scoring.
- **EcoHub listings** — number of providers / solution stacks / integrations listed on ecohub.mariadb.org.

## C · Chosen — from the survey
- **Deliberate-choice signal** — share of survey respondents who *chose* MariaDB on purpose (vs inherited it). Wire the annual survey number in as e.g. `data/survey_deliberate_choice/monthly.csv` (annual point, carried forward).
- Optional companions from the survey: **NPS** (users), **new-vs-migrated** share.

## Other candidates worth considering
- **Job postings** mentioning MariaDB (Indeed / LinkedIn Jobs) → **D · Visible** (named demand).
- **Stack Overflow tag** activity (separate from Stack Exchange DBA) → **D · Visible**.
- **Packagist / npm / PyPI** driver download counts (mariadb connectors) → **A · Running**.
- **GitHub dependents** ("used by") for mariadb connector repos → **A · Running** / Participation.
