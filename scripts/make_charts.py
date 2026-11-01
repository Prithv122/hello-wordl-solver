"""Charts for the README / guide (needs matplotlib).  python scripts/make_charts.py"""
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "charts")
LETTERS = "abcdefghijklmnopqrstuvwxyz"
SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#6b6b68", "#e6e5e1"
BLUE = ["#fcfcfb", "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
CMAP = LinearSegmentedColormap.from_list("seq_blue", BLUE)
BAR = "#2a78d6"

plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": GRID,
                     "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
                     "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "bold"})


def load(L):
    p = os.path.join(ROOT, "output", "analysis", f"len_{L:02d}.json")
    return json.load(open(p)) if os.path.exists(p) else None


def positional(lengths):
    fig, axes = plt.subplots(2, 4, figsize=(13, 8.6), constrained_layout=True)
    vmax = 0.0
    data = {}
    for L in lengths:
        r = load(L)
        if r:
            data[L] = np.array(r["letters"]["positional_matrix"]).T  # (26, L)
            vmax = max(vmax, data[L].max())
    for ax, L in zip(axes.ravel(), lengths):
        if L not in data:
            ax.axis("off"); continue
        m = data[L]
        im = ax.imshow(m, cmap=CMAP, vmin=0, vmax=vmax, aspect="auto")
        ax.set_title(f"{L} letters")
        ax.set_yticks(range(26), [c.upper() for c in LETTERS], fontsize=7)
        ax.set_xticks(range(L), [str(i + 1) for i in range(L)], fontsize=7)
        for sp in ax.spines.values():
            sp.set_visible(False)
        # label only the top letter of each position (selective direct labels)
        for j in range(L):
            i = int(m[:, j].argmax())
            ax.text(j, i, f"{m[i, j] * 100:.0f}", ha="center", va="center", fontsize=6.5,
                    color="white" if m[i, j] > vmax * 0.55 else INK)
    cb = fig.colorbar(im, ax=axes, shrink=0.5, label="P(letter at this position)")
    cb.outline.set_visible(False)
    fig.suptitle("Where letters sit: probability of each letter at each position (weighted by answer likelihood)",
                 fontsize=11, fontweight="bold", color=INK)
    fig.savefig(os.path.join(OUT, "letter_positions.png"), dpi=130)
    plt.close(fig)


def presence(lengths):
    cols, mats = [], []
    for L in lengths:
        r = load(L)
        if r:
            cols.append(L)
            pr = r["letters"]["presence"]
            mats.append([pr[c] for c in LETTERS])
    m = np.array(mats).T
    order = np.argsort(-m.mean(1))
    m = m[order]
    fig, ax = plt.subplots(figsize=(6.2, 8.4), constrained_layout=True)
    im = ax.imshow(m, cmap=CMAP, vmin=0, vmax=1, aspect="auto")
    ax.set_yticks(range(26), [LETTERS[i].upper() for i in order])
    ax.set_xticks(range(len(cols)), [str(c) for c in cols])
    ax.set_xlabel("word length")
    for sp in ax.spines.values():
        sp.set_visible(False)
    for i in range(26):
        for j in range(len(cols)):
            ax.text(j, i, f"{m[i, j] * 100:.0f}", ha="center", va="center", fontsize=6.5,
                    color="white" if m[i, j] > 0.55 else INK)
    ax.set_title("P(letter appears in the answer), %", loc="left")
    cb = fig.colorbar(im, ax=ax, shrink=0.4)
    cb.outline.set_visible(False)
    fig.savefig(os.path.join(OUT, "letter_presence.png"), dpi=130)
    plt.close(fig)


def benchmark(lengths):
    b = json.load(open(os.path.join(ROOT, "output", "benchmark.json")))
    fig, axes = plt.subplots(2, 4, figsize=(13, 5.6), sharey=True, constrained_layout=True)
    for ax, L in zip(axes.ravel(), lengths):
        r = b.get(str(L), {}).get("common_answers")
        if not r:
            ax.axis("off"); continue
        dist = {int(k): v for k, v in r["distribution"].items()}
        n = r["games"]
        xs = list(range(1, 7))
        ys = [dist.get(x, 0) / n * 100 for x in xs]
        fail = sum(v for k, v in dist.items() if k > 6) / n * 100
        labels = [str(x) for x in xs] + ["fail"]
        ax.bar(range(7), ys + [fail], color=[BAR] * 6 + ["#8a8a86"], width=0.72, edgecolor=SURFACE, linewidth=2)
        for i, y in enumerate(ys + [fail]):
            if y >= 1 or (i == 6 and y > 0):
                ax.text(i, y + 1.5, f"{y:.0f}%" if y >= 1 else f"{y:.1f}%", ha="center", fontsize=7.5, color=INK)
        ax.set_xticks(range(7), labels)
        ax.set_title(f"{L} letters · avg {r['avg_guesses']:.2f} · win {r['win_rate'] * 100:.1f}%")
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        for sp in ("top", "right", "left"):
            ax.spines[sp].set_visible(False)
        ax.set_xlabel("guesses needed")
    axes[0, 0].set_ylabel("% of games")
    axes[1, 0].set_ylabel("% of games")
    fig.suptitle("Solver performance on held-out real Hello Wordl answers (6 tries)", fontsize=11,
                 fontweight="bold")
    fig.savefig(os.path.join(OUT, "benchmark.png"), dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    lengths = [int(x) for x in sys.argv[1:]] or list(range(4, 12))
    positional(lengths)
    presence(lengths)
    benchmark(lengths)
    print("charts ->", OUT)
