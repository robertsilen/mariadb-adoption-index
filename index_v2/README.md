# Adoption Index v2 — layered

An alternative view of the same signals as `index/` (v1). Where v1 blends
everything into **one** number, v2 groups the signals into the adoption-strategy
layers and reports a **separate sub-index per layer**, so you can see *which kind*
of adoption is moving.

Layers (from `MariaDB_Adoption_Strategy_2026-2027`). Order follows the
strategy's own funnel — **Running → Available → Chosen → Visible** (A–D,
"usage → mindshare → perception"), shown on the top row of the chart.
**Participation** (cross-cutting) and **Composite** sit on their own row
below, without letters; Composite is not a layer but the weighted blend of
all signals.

| # | Layer | Question it answers | Status |
|---|---|---|---|
| **A** | **Running** | Is MariaDB actually deployed and used? | downloads, Docker pulls, Debian popcon |
| **B** | **Available** | Can people easily get / pick it? | **gap — no signals yet** |
| **C** | **Chosen** | Is it *deliberately* chosen? | **gap — comes from the survey** |
| **D** | **Visible** | Mindshare — how much it's talked about | DB-Engines, Trends, Wikipedia, socials, HN, SE, stars |
| — | **Participation** | Contribution to the project | PRs, unique/returning contributors, Zulip |
| — | **Composite** | Combined single number (v1-style) | weighted blend of all of the above |

## Design
- Reads the **same** `data/<signal>/monthly.csv` as v1 — no data is duplicated.
- Driven by [`index_v2_config.csv`](index_v2_config.csv): `label,path,weight,layer`.
- Each signal is indexed to **baseline `2023-12` = 100**; within a layer we take a
  weighted average of the indexed signals (NaN-aware, so a signal that doesn't
  reach back to a month doesn't pull it to zero).
- The current (incomplete) calendar month is dropped.

## Run
```bash
python3 index_v2/create_index_v2.py
```
Outputs into `index_v2/`: `index_v2_layers.png` (small multiples),
`index_v2_layers.csv` (month × layer), `index_v2_signals.csv` (indexed audit trail).

## Known limitation / next steps
- **Flow vs stock.** *Running* and *Participation* are dominated by monthly-**flow**
  counts (downloads/month, new PRs/month) which grow far above 100, while *Visible*
  is mostly **stock** counts (followers, scores) that move slowly. The layers are
  therefore **not on a comparable scale** — read each panel on its own trend, not
  against the others. (v1 hides this by blending them; v2 makes it visible.)
- **Fill the two gaps:**
  - *Available* — add signals like cloud-catalog presence, distro version currency,
    framework/ORM support, ecohub listings.
  - *Chosen* — wire in the survey's "deliberate choice" signal (e.g. an annual
    `data/survey_deliberate_choice/monthly.csv`).
