# MariaDB Adoption Index (beta)

## Monthly Weighted Index (baseline 2024-01)
![Monthly Index](index/mariadb_adoption_index_chart_12m.png)

## Index Weights
![Weights](index/mariadb_adoption_index_weights.png)

## Rolling 12 month values and baseline (2024-01)
![Monthly Values](index/mariadb_adoption_index_table_12m.png)

# Documentation


The MariaDB weighted index is calculated in [create_index.py](index/create_index.py) using prepared monthly values. A monthly index value for each value by using 2024-01 as the baseline. A single weighted summary index value per month is calculated as defined in [create_index_weights.csv](index/create_index_weights.csv).

The source data is fetched either with automation from their original sources (see .github/workflows/) or added manually by the MariaDB Foundation. Raw fetched data is converted to monthly values in _monthly.csv files. 

Cursor and Claude have been used to generate this solution. 

## KPI details

| KPI                                    | Fetch Method          | Key  | Create Monthly    |
|----------------------------------------|-----------------------|------|-------------------|
| mariadb.org downloads                  | curl, historic        |      | raw2monthly.py    |
| Debien popcon                          | curl, historic        |      | raw2monthly.py    |
| Docker official image pulls            | curl, daily           |      | wip               |
| Github new PRs external                | python, historic      | key  | latest2monthly.py |
| Github new PRs ext. unique user names  | python, historic      | key  | latest2monthly.py |
| Github stars                           | curl, daily           |      | daily2monthly.py  |
| Github readme repos                    | curl, daily           |      | daily2monthly.py  |
| Zulip total users                      | curl, daily           | key  | daily2monthly.py  |
| Zulip active users 15d                 | curl, daily           | key  | daily2monthly.py  |
| DB-engines                             | curl scrape, daily    |      | daily2monthly.py  |
| Google trends                          | fetch.py, historic    |      | fetch.py          |
| Wikipedia views all langs              | fetch.py, historic    |      | fetch.py          |
| Reddit subscribers                     | curl, daily           | key  | daily2monthly.py  |
| Hackernews                             | fetch.py, historic    |      | fetch.py          |
| Stackexchange new questions            | fetch.py, historic    |      | fetch.py          |
| LinkedIn                               | manual                | auth | wip               |
| Youtube                                | curl, daily           | key  | daily2monthly.py  |
| Fosstadon                              | manual                |      | wip               |
| Instagram                              | manual                |      | wip               |
| X (Twitter)                            | manual                |      | wip               |

### API-Key docs
* [Github fine-grained personal access tokens](https://github.blog/security/application-security/introducing-fine-grained-personal-access-tokens-for-github/)
* [Zulip API keys](https://zulip.com/api/api-keys)
* [Reddit Developer Token](https://developers.reddit.com/docs/authentication)
* [Youtube Data API](https://developers.google.com/youtube/registering_an_application)
* LinkedIn
* X