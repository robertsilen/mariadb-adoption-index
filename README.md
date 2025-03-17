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

| KPI                                    | Data Source           | Create Monthly |
|----------------------------------------|-----------------------|----------------|
| mariadb.org downloads                  | curl, historic        | python         |
| dabien popcon                          | curl, historic        | python         |
| docker                                 | curl, save daily      | python         |
| github new PRs external                | python, historic      | -              |
| github new PRs ext. unique user names  | python, historic      | -              |
| github stars                           | curl, save daily      | python         |
| github readme repos                    | python, historic      | python         |
| Zulip total users                      | curl, save daily      | python         |
| Zulip active users 15d                 | curl, save daily      | python         |
| DB-engines                             | python, scrape        | -              |
| Google Trends                          | python, historic      | -              |
| Wikipedia views all langs              | python, historic      | -              |
| Reddit subscribers                     | curl, save daily      | python         |
| Hackernews                             | python, historic      | -              |
| Stackexchange new questions            | python, historic      | -              |
| LinkedIn                               | manual                | -              |
| Youtube                                | python, daily         | python         |
| Fosstadon                              | manual                | -              |
| Instagram                              | python, d, broken     | python         |
| X (Twitter)                            | manual                |                |