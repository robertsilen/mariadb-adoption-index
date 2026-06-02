"""
Compute "returning external contributors" — a stickiness/retention metric for
MariaDB/server external GitHub contributors.

For each month M, the metric counts unique external contributors who:
  - Submitted >=1 PR labeled "External Contribution" in the current 12-month
    window [M-11, M], AND
  - Also submitted >=1 such PR in the prior 12-month window [M-23, M-12].

Reuses the raw PR data already fetched by
data/github_new_prs_external/fetch.py so no extra API calls are needed.

Output files (one row per month, sorted descending):
  monthly-extended.csv - full breakdown for review and analysis
  monthly.csv          - slim index input: month + github_returning_contributors only

monthly-extended.csv columns:
  month                          - YYYY-MM
  github_returning_contributors  - main metric (count returning)
  contributors_current_12m       - unique contributors in [M-11, M]
  contributors_prior_12m         - unique contributors in [M-23, M-12]
  new_contributors_12m           - current minus returning
  retention_rate_pct             - returning / prior * 100
  prior_window_months            - size of prior window (12 once fully ramped up)

PR data is fetched from 2020-01-01; prior_window_months reaches 12 from
2022-05 onwards.
"""

import pandas as pd

SRC = 'data/github_new_prs_external/since-2023-01-01.csv'
RAW_OUT = 'data/github_returning_contributors/monthly-extended.csv'
MONTHLY_OUT = 'data/github_returning_contributors/monthly.csv'

src = pd.read_csv(SRC).fillna('')
src['month'] = pd.to_datetime(src['created_date']).dt.to_period('M')

df = src[src['labels'].str.contains("External Contribution", na=False)].copy()

data_min = df['month'].min()
data_max = df['month'].max()
print(f"External-contribution PRs: {len(df)} rows, covering {data_min} - {data_max}")

months = pd.period_range(start=data_min, end=data_max, freq='M')

rows = []
for M in months:
    current_start = M - 11
    prior_end = M - 12

    if prior_end < data_min:
        continue

    prior_start = max(prior_end - 11, data_min)

    current_users = set(
        df[(df['month'] >= current_start) & (df['month'] <= M)]['creator_username']
    )
    prior_users = set(
        df[(df['month'] >= prior_start) & (df['month'] <= prior_end)]['creator_username']
    )

    returning = current_users & prior_users
    new_contribs = current_users - prior_users
    prior_window_months = (prior_end - prior_start).n + 1
    retention_pct = (
        round(len(returning) / len(prior_users) * 100, 1) if prior_users else 0.0
    )

    rows.append({
        'month': str(M),
        'github_returning_contributors': len(returning),
        'contributors_current_12m': len(current_users),
        'contributors_prior_12m': len(prior_users),
        'new_contributors_12m': len(new_contribs),
        'retention_rate_pct': retention_pct,
        'prior_window_months': prior_window_months,
    })

results = pd.DataFrame(rows).sort_values('month', ascending=False)
results.to_csv(RAW_OUT, index=False)
results[['month', 'github_returning_contributors']].to_csv(MONTHLY_OUT, index=False)
print(results.to_string(index=False))
print(f"\nSaved to {RAW_OUT}")
print(f"Saved to {MONTHLY_OUT}")
