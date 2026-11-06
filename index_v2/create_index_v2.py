#!/usr/bin/env python3
"""
MariaDB Adoption Index v2 — layered.

Unlike v1 (index/create_index.py), which blends every signal into ONE number,
v2 groups the same signals into the adoption-strategy layers and computes a
separate sub-index per layer:

    Running        — is MariaDB actually deployed and used?
    Available      — can people easily get/pick it? (currently a GAP: no signals)
    Chosen         — is it deliberately chosen? (from the survey; not yet wired)
    Visible        — mindshare / how much it is talked about
    Participation  — contribution to the project

Reads the SAME data/<path>/monthly.csv files as v1 (no data duplication),
driven by index_v2/index_v2_config.csv (columns: label,path,weight,layer).

Each signal is indexed to baseline 2023-12 = 100. Within a layer we take a
weighted average of the indexed signals. A composite (weighted across all
signals, same as v1) is drawn for reference.

Outputs into index_v2/:
    index_v2_layers.png      small-multiples, one panel per layer + composite
    index_v2_layers.csv      month x layer table (+ composite)
    index_v2_signals.csv     month x signal, indexed to baseline (audit trail)
"""
import os
import datetime
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
CONFIG = os.path.join(HERE, "index_v2_config.csv")
BASELINE = "2023-12"
MONTHS_SHOWN = 12  # last N months plus the baseline

# Layer display order follows the strategy doc's funnel (Running → Available →
# Chosen → Visible, "usage → mindshare → perception"); Participation is the
# fifth, cross-cutting theme. Lettered A–E so they can be referenced by label.
LAYER_ORDER = ["Running", "Available", "Chosen", "Visible", "Participation"]
# The four funnel layers are lettered A–D and shown on the top row.
# Participation (cross-cutting) and Composite (the blend) sit on their own
# row below, without letters.
FUNNEL = ["Running", "Available", "Chosen", "Visible"]
LETTER = {"Running": "A", "Available": "B", "Chosen": "C", "Visible": "D"}
PANEL_SUBTITLE = {
    "Running":       "Is MariaDB actually deployed & used?\ndownloads · Docker pulls · Debian popcon",
    "Available":     "Can people easily get & pick it?\ncloud catalogs · distros · frameworks (no signals yet)",
    "Chosen":        "Is it deliberately chosen?\nfrom the survey (not wired in yet)",
    "Visible":       "Mindshare — how much it's talked about\nDB-Engines · Trends · Wikipedia · socials · HN · Stack Exchange",
    "Participation": "Contribution to the project\npull requests · contributors · Zulip",
    "Composite":     "Combined index — weighted blend of ALL signals above\n(same method as v1; shown for reference)",
}


def load_config():
    cfg = pd.read_csv(CONFIG)
    cfg["weight"] = pd.to_numeric(cfg["weight"], errors="coerce").fillna(0)
    return cfg


def load_signal(path):
    """Return a Series indexed by 'month' with the signal's raw value."""
    fp = os.path.join(DATA, path, "monthly.csv")
    if not os.path.exists(fp):
        print(f"  ! missing {fp} — skipping")
        return None
    df = pd.read_csv(fp)
    # monthly.csv is always two columns: month, <signal_name>
    val_col = [c for c in df.columns if c != "month"][0]
    s = df.set_index("month")[val_col].sort_index()
    s = pd.to_numeric(s, errors="coerce")
    s = s[~s.index.duplicated(keep="last")]
    return s


def index_to_baseline(s):
    """Rebase a series so BASELINE == 100. Returns None if no usable baseline."""
    if s is None or BASELINE not in s.index:
        return None
    base = s.loc[BASELINE]
    if pd.isna(base) or base == 0:
        return None
    return s / base * 100.0


def weighted_layer_index(indexed, weights):
    """
    indexed: DataFrame (month x signal) already rebased to 100 at baseline.
    weights: dict signal->weight, only for the signals in this layer.
    Weighted average across available signals per month (ignoring NaN, so a
    signal that doesn't reach back to a given month doesn't drag it to zero).
    """
    cols = [c for c in indexed.columns if c in weights and weights[c] > 0]
    if not cols:
        return None
    sub = indexed[cols]
    w = pd.Series({c: weights[c] for c in cols})
    # per-month weighted mean over non-NaN entries
    mask = sub.notna()
    wsum = (mask * w).sum(axis=1)
    num = (sub.fillna(0) * w).sum(axis=1)
    out = num / wsum.replace(0, pd.NA)
    return out


def main():
    cfg = load_config()

    # 1. Load + index every signal.
    indexed = {}
    weights = {}
    layer_of = {}
    skipped = []
    for _, row in cfg.iterrows():
        path, w, layer = row["path"], float(row["weight"]), row["layer"]
        idx = index_to_baseline(load_signal(path))
        if idx is None:
            skipped.append(path)
            continue
        indexed[path] = idx
        weights[path] = w
        layer_of[path] = layer

    if skipped:
        print("Skipped (no baseline / missing):", ", ".join(skipped))

    idx_df = pd.DataFrame(indexed).sort_index()

    # 2. Per-layer sub-index + composite.
    layer_series = {}
    for layer in LAYER_ORDER:
        paths = [p for p in indexed if layer_of.get(p) == layer]
        if not paths:
            layer_series[layer] = None
            continue
        layer_series[layer] = weighted_layer_index(idx_df, {p: weights[p] for p in paths})

    composite = weighted_layer_index(idx_df, weights)  # all signals, v1-style

    # 3. Trim to baseline + last MONTHS_SHOWN months.
    #    Drop the current calendar month: it is only a few days in and most
    #    signals report monthly, so it is an incomplete, misleading data point.
    current_month = datetime.date.today().strftime("%Y-%m")
    all_months = [m for m in sorted(idx_df.index) if m < current_month]
    recent = all_months[-MONTHS_SHOWN:]
    keep = sorted(set(recent) | {BASELINE})

    def trim(s):
        if s is None:
            return None
        return pd.to_numeric(s.reindex(keep), errors="coerce")

    layer_series = {k: trim(v) for k, v in layer_series.items()}
    composite = trim(composite)

    # 4. Table CSV.
    table = pd.DataFrame({"month": keep}).set_index("month")
    for layer in LAYER_ORDER:
        if layer_series[layer] is not None:
            pre = f"{LETTER[layer]}. " if layer in LETTER else ""
            table[f"{pre}{layer}"] = layer_series[layer]
    table["Composite"] = composite
    out_csv = os.path.join(HERE, "index_v2_layers.csv")
    table.round(1).to_csv(out_csv)
    print("wrote", out_csv)

    idx_df.reindex(keep).round(1).to_csv(os.path.join(HERE, "index_v2_signals.csv"))
    print("wrote", os.path.join(HERE, "index_v2_signals.csv"))

    # 5. Small-multiples chart: one panel per layer + a composite panel.
    # Layout: top row = the four funnel layers (A–D); bottom row = Participation
    # + Composite (no letters), left-aligned with two empty cells after them.
    ncol = 4
    slots = FUNNEL + [None, None, None, None]           # row 0
    slots[4] = "Participation"                           # row 1, col 0
    slots[5] = "Composite"                               # row 1, col 1
    fig, axes = plt.subplots(2, ncol, figsize=(19, 10), sharex=True)
    axes = axes.ravel()
    x = list(range(len(keep)))
    xlabels = [m if (i == 0 or i == len(keep) - 1) else "" for i, m in enumerate(keep)]

    def panel_header(ax, name, value=None):
        """Bold label (+ current value) with a plain-language subtitle beneath."""
        letter = LETTER.get(name)
        tag = f"{letter}  ·  {name}" if letter else name
        head = tag if value is None else f"{tag}   ·   {value:.0f}"
        color = "#C0392B" if name == "Composite" else "#1F4E79"
        ax.set_title(head, fontsize=15, fontweight="bold", color=color, pad=30)
        ax.annotate(PANEL_SUBTITLE.get(name, ""),
                    xy=(0.5, 1.02), xycoords="axes fraction",
                    ha="center", va="bottom", fontsize=8.5, color="#666666",
                    linespacing=1.3)

    for ax, name in zip(axes, slots):
        if name is None:
            ax.axis("off")
            continue
        s = composite if name == "Composite" else layer_series[name]
        ax.axhline(100, color="#bbbbbb", lw=1, ls="--", zorder=1)
        if s is None or s.dropna().empty:
            ax.text(0.5, 0.45, "no signals yet", ha="center", va="center",
                    transform=ax.transAxes, color="#aaaaaa", fontsize=13, style="italic")
            panel_header(ax, name)
            ax.set_xticks([])
            ax.set_yticks([])
            continue
        y = s.reindex(keep).values
        color = "#C0392B" if name == "Composite" else "#1F4E79"
        ax.plot(x, y, marker="o", ms=4, lw=2.2, color=color, zorder=3)
        panel_header(ax, name, s.dropna().iloc[-1])
        ax.set_xticks(x)
        ax.set_xticklabels(xlabels, rotation=0, fontsize=8)
        ax.grid(axis="y", color="#eeeeee", zorder=0)

    fig.suptitle("MariaDB Adoption Index v2 — by strategy layer (baseline 2023-12 = 100)",
                 fontsize=17, fontweight="bold", y=0.998)
    fig.text(0.5, 0.955,
             "Each panel is a separate sub-index. Read each trend on its own — "
             "the layers are not on a comparable scale (flow vs. stock signals).",
             ha="center", fontsize=9.5, color="#666666")
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    out_png = os.path.join(HERE, "index_v2_layers.png")
    fig.savefig(out_png, dpi=130)
    print("wrote", out_png)

    # 6. Console summary.
    print("\nLatest ({}):".format(keep[-1]))
    for name in LAYER_ORDER + ["Composite"]:
        s = composite if name == "Composite" else layer_series[name]
        label = f"{LETTER[name]}. {name}" if name in LETTER else name
        if s is None or s.dropna().empty:
            print(f"  {label:<18} —   (no signals)")
        else:
            print(f"  {label:<18} {s.dropna().iloc[-1]:6.1f}")


if __name__ == "__main__":
    main()
