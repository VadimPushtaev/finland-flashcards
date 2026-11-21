"""Plot Chapter 12's before/proposed distributions with a fixed card population."""
from collections import Counter
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator, StrMethodFormatter
import numpy as np

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "homebrew-ch12-scores-before-after.png"
BLUE = "#487BB0"
ORANGE = "#CF6D32"
INK = "#1B2C43"
MUTED = "#596C82"


def main():
    """Use integer-width bins, matched axes within each row, and no filtering."""
    data = json.loads((HERE / "comparison.json").read_text())
    cards = data["card_comparison"]
    x = np.arange(61)
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 11,
        "text.color": INK, "axes.labelcolor": INK,
        "axes.edgecolor": "#BBC8D6", "xtick.color": MUTED, "ytick.color": MUTED,
        "axes.spines.top": False, "axes.spines.right": False,
        "savefig.facecolor": "white",
    })
    fig, axes = plt.subplots(2, 2, figsize=(18, 12), sharex=True, sharey="row")
    fig.subplots_adjust(left=0.065, right=0.975, top=0.79, bottom=0.185,
                        wspace=0.10, hspace=0.38)
    fig.text(0.065, 0.957, "Chapter 12  |  Conservative reassessment proposal",
             fontsize=24, fontweight="bold", va="top")
    fig.text(0.065, 0.917, "Integration, residence and citizenship  •  603 sentences reviewed individually",
             fontsize=14, color=MUTED, va="top")
    fig.text(0.065, 0.883,
             "Relevance = 3 and value = 3: 180 → 36 sentences.  Formula and CORE cutoff stay unchanged.",
             fontsize=12.5, color=INK, va="top")
    fig.text(0.065, 0.85, "BEFORE  ·  Current assessments", fontsize=15, fontweight="bold")
    fig.text(0.545, 0.85, "AFTER  ·  Proposed, not applied", fontsize=15, fontweight="bold")

    for column, label in enumerate(("before", "proposed")):
        sentence_counts = {int(k): v for k, v in data["sentence_histograms"][label].items()}
        assert sum(sentence_counts.values()) == 603
        for row in range(2):
            ax = axes[row, column]
            if row == 0:
                counts = np.array([sentence_counts.get(int(score), 0) for score in x])
                ax.bar(x, counts, width=0.82, color=BLUE, linewidth=0, zorder=3)
                core = data["sentence_tiers"][label]["CORE"]
                subtitle = f"All 603 sentences  ·  {core} at CORE (≥41)"
                ymax = 225
                step = 50
            else:
                original62 = Counter(c[f"{label}_total"] for c in cards if c["originally_in_62_at_56"])
                remaining = Counter(c[f"{label}_total"] for c in cards if not c["originally_in_62_at_56"])
                low = np.array([remaining[int(score)] for score in x])
                high = np.array([original62[int(score)] for score in x])
                assert sum(low) == 41 and sum(high) == 62
                counts = low + high
                ax.bar(x, low, width=0.82, color=BLUE, linewidth=0, zorder=3)
                ax.bar(x, high, bottom=low, width=0.82, color=ORANGE, linewidth=0, zorder=3)
                above = sum(c[f"{label}_total"] >= 50 for c in cards)
                subtitle = f"Same 103 existing cards  ·  {above} at score ≥50"
                ymax = 72
                step = 10
            assert int(sum(counts)) == (603 if row == 0 else 103)
            ax.axvline(40.5, color="#8D9EB2", linestyle=(0, (4, 3)), linewidth=1.2, zorder=2)
            ax.text(41.2, ymax * 0.94, "CORE ≥41", fontsize=9, color=MUTED, va="top")
            for score, count in zip(x, counts):
                if count:
                    ax.text(score, count + ymax * 0.013, str(int(count)), ha="center",
                            va="bottom", fontsize=8 if row == 0 else 9)
            ax.set_title(subtitle, loc="left", fontsize=12, pad=14)
            ax.set_xlim(-0.8, 61)
            ax.set_ylim(0, ymax)
            ax.set_xticks(np.arange(0, 61, 10))
            ax.xaxis.set_minor_locator(MultipleLocator(1))
            ax.yaxis.set_major_locator(MultipleLocator(step))
            ax.yaxis.set_major_formatter(StrMethodFormatter("{x:.0f}"))
            ax.tick_params(axis="x", labelbottom=True, which="major", length=4)
            ax.tick_params(axis="x", which="minor", length=2, color="#CBD5DF")
            ax.tick_params(axis="y", labelleft=True, length=0)
            ax.grid(axis="y", color="#E5EAF0", linewidth=0.8, zorder=0)
            ax.set_axisbelow(True)
            if column == 0:
                ax.set_ylabel("Sentences" if row == 0 else "Existing cards", labelpad=12)
            if row == 1:
                ax.set_xlabel("Weighted primary-sentence score (0–60)", labelpad=10)

    fig.legend(handles=[
        Patch(facecolor=ORANGE, label="Bottom row: the original 62 cards tied at 56"),
        Patch(facecolor=BLUE, label="Bottom row: the other 41 existing cards"),
    ], loc="lower left", bbox_to_anchor=(0.06, 0.105), ncol=2, frameon=False, fontsize=11)
    fig.text(0.065, 0.085,
             "The original 62 now span 11 scores (32–56); four remain at 56. Bars count the same cards before and after.",
             fontsize=11.5, color=INK)
    fig.text(0.065, 0.059,
             "Score = 9 × relevance + 6 × knowledge value + 4 × question suitability + factual specificity. Risk is assessed separately.",
             fontsize=10, color=MUTED)
    fig.text(0.065, 0.038,
             "One bin per integer score; matching scales within each row. Includes every sentence and existing card, including scores below CORE.",
             fontsize=10, color=MUTED)
    fig.text(0.065, 0.017,
             "Proposal dated 2026-11-21. Canonical assessments and decks are unchanged. Relevance judgments are estimates, not measured exam frequencies.",
             fontsize=9, color=MUTED)
    fig.savefig(OUTPUT, dpi=200, metadata={
        "Title": "Chapter 12 conservative reassessment: before and proposed after",
        "Description": "603 sentences and the same 103 existing cards. The original 62 cards scoring 56 are highlighted in orange. Proposal only.",
    })
    plt.close(fig)
    print(f"Saved {OUTPUT} (3600 x 2400 px)")


if __name__ == "__main__":
    main()
