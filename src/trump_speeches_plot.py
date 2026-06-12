import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from datetime import datetime

# ── Data ──────────────────────────────────────────────────────────────────────
speeches = [
    {
        "date": datetime(2026, 3, 2),
        "title": "Operation Epic Fury\nLaunch Statement",
        "location": "White House, Washington DC",
        "channel": "All Major Networks",
        "topic": "Announced US military operation\nagainst Iran's nuclear programme.\nObjectives: destroy ballistic missiles,\nannihilate navy, cut proxy support.",
        "month": "March",
    },
    {
        "date": datetime(2026, 3, 3),
        "title": "Bilateral Meeting\nRemarks",
        "location": "White House, Washington DC",
        "channel": "White House / C-SPAN",
        "topic": "Diplomatic meeting remarks\nfollowing Operation Epic Fury launch.",
        "month": "March",
    },
    {
        "date": datetime(2026, 3, 9),
        "title": "Operation Epic Fury\nPress Conference",
        "location": "White House, Washington DC",
        "channel": "All Major Networks / C-SPAN",
        "topic": "Progress update on military\nstrike campaign against Iran.\nHighlighted early successes.",
        "month": "March",
    },
    {
        "date": datetime(2026, 3, 11),
        "title": "White House Remarks",
        "location": "White House, Washington DC",
        "channel": "White House Live / C-SPAN",
        "topic": "General presidential remarks\non domestic and foreign policy.",
        "month": "March",
    },
    {
        "date": datetime(2026, 3, 17),
        "title": "St. Patrick's Day\nRemarks",
        "location": "White House, Washington DC",
        "channel": "White House Live",
        "topic": "Welcomed Irish Taoiseach Micheál\nMartin for traditional Shamrock\nceremony and bilateral talks.",
        "month": "March",
    },
    {
        "date": datetime(2026, 4, 1),
        "title": "Primetime Address:\nOperation Epic Fury",
        "location": "Cross Hall, White House, DC",
        "channel": "ABC · NBC · CBS · CNN\nFox News · NewsNation · PBS · C-SPAN",
        "topic": "Declared Iran's military 'in ruins'.\nOperation 'nearing completion'.\nOffered 2–3 week deal-or-bomb\nultimatum. ~20-minute address.",
        "month": "April",
    },
    {
        "date": datetime(2026, 4, 6),
        "title": "White House\nPress Conference",
        "location": "White House, Washington DC",
        "channel": "All Major Networks / C-SPAN",
        "topic": "Q&A on Iran ceasefire timeline,\neconomic tariffs, domestic agenda.",
        "month": "April",
    },
    {
        "date": datetime(2026, 4, 15),
        "title": "TPUSA 'Build the\nRed Wall' Rally",
        "location": "Phoenix, Arizona",
        "channel": "Fox News / NewsNation / OAN",
        "topic": "Energised conservative base\nahead of midterm cycle.\nCelebrated Operation Epic Fury\nand economic gains.",
        "month": "April",
    },
    {
        "date": datetime(2026, 4, 15),
        "title": "Tax Day Roundtable",
        "location": "Las Vegas, Nevada",
        "channel": "White House Live / Fox News",
        "topic": "Discussed tax relief measures,\ntariff revenues, and economic\noutperformance under second term.",
        "month": "April",
    },
    {
        "date": datetime(2026, 4, 21),
        "title": "'America Reads\nthe Bible' Event",
        "location": "White House / Social Media",
        "channel": "Social Media (Truth Social\n& YouTube)",
        "topic": "Read a passage from the\nKing James Bible as part of\na nationally-promoted event.",
        "month": "April",
    },
    {
        "date": datetime(2026, 4, 23),
        "title": "White House Remarks",
        "location": "White House, Washington DC",
        "channel": "White House Live / C-SPAN",
        "topic": "Presidential remarks on ongoing\nIran ceasefire negotiations and\ndomestic policy updates.",
        "month": "April",
    },
    {
        "date": datetime(2026, 4, 25),
        "title": "White House Remarks",
        "location": "White House, Washington DC",
        "channel": "White House Live / C-SPAN",
        "topic": "Remarks following ceasefire\nannouncement with Iran.\nOperation Epic Fury declared\na success.",
        "month": "April",
    },
    {
        "date": datetime(2026, 4, 26),
        "title": "60 Minutes Interview",
        "location": "White House, Washington DC",
        "channel": "CBS (60 Minutes)",
        "topic": "Sat-down interview with Norah\nO'Donnell. Discussed Iran war\noutcome, economy, and second-\nterm agenda.",
        "month": "April",
    },
    {
        "date": datetime(2026, 5, 6),
        "title": "White House Remarks",
        "location": "White House, Washington DC",
        "channel": "White House Live / C-SPAN",
        "topic": "Remarks on post-Iran foreign\npolicy and domestic priorities.",
        "month": "May",
    },
    {
        "date": datetime(2026, 5, 8),
        "title": "White House Remarks",
        "location": "White House, Washington DC",
        "channel": "White House Live / C-SPAN",
        "topic": "General policy remarks;\ndiscussed trade deals and\npost-conflict reconstruction.",
        "month": "May",
    },
    {
        "date": datetime(2026, 5, 10),
        "title": "Military Mother's\nDay Event",
        "location": "White House, Washington DC",
        "channel": "Fox News / CNN / White\nHouse Live",
        "topic": "Joint appearance with Melania\nTrump. Honoured Gold Star and\nAngel Moms. Patriotic address\nahead of Mother's Day.",
        "month": "May",
    },
    {
        "date": datetime(2026, 5, 12),
        "title": "Nationwide Address\non 2026 Agenda",
        "location": "White House, Washington DC",
        "channel": "ABC · NBC · CBS · CNN\nFox News · PBS · C-SPAN",
        "topic": "Touted achievements: Iran deal,\neconomic growth, border security.\nOutlined legislative priorities\nfor rest of 2026.",
        "month": "May",
    },
    {
        "date": datetime(2026, 5, 14),
        "title": "The Villages Event\n(Seniors Address)",
        "location": "The Villages Charter School,\nFlorida",
        "channel": "Fox News / NewsNation",
        "topic": "Spoke on Social Security,\nMedicare protections, and\ncost-of-living relief for\nseniors.",
        "month": "May",
    },
]

# ── Colour palette by month ────────────────────────────────────────────────────
MONTH_COLORS = {"March": "#2176AE", "April": "#C1292E", "May": "#57A773"}
CARD_BG      = {"March": "#E8F4FD", "April": "#FDECEA", "May": "#EAF7EF"}

# ── Figure layout ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(28, 46), facecolor="#0D1117")
ax  = fig.add_subplot(111)
ax.set_facecolor("#0D1117")
ax.set_xlim(0, 10)
ax.set_ylim(-1, len(speeches) + 2)
ax.axis("off")

# ── Title ─────────────────────────────────────────────────────────────────────
fig.text(
    0.5, 0.985,
    "PRESIDENT TRUMP  ·  SPEECHES & ADDRESSES",
    ha="center", va="top", fontsize=28, fontweight="bold",
    color="white", fontfamily="DejaVu Sans",
)
fig.text(
    0.5, 0.978,
    "March – May 2026  |  Location · Broadcast Channel · Key Events",
    ha="center", va="top", fontsize=15, color="#8B949E",
)

# ── Legend ────────────────────────────────────────────────────────────────────
legend_patches = [
    mpatches.Patch(color=MONTH_COLORS["March"], label="March 2026"),
    mpatches.Patch(color=MONTH_COLORS["April"],  label="April 2026"),
    mpatches.Patch(color=MONTH_COLORS["May"],    label="May 2026"),
]
ax.legend(
    handles=legend_patches, loc="upper right",
    fontsize=11, framealpha=0.15, labelcolor="white",
    edgecolor="#30363D", facecolor="#161B22",
    bbox_to_anchor=(0.99, 0.99),
)

# ── Timeline spine ────────────────────────────────────────────────────────────
spine_x = 1.55
ax.plot([spine_x, spine_x], [-0.5, len(speeches) - 0.5],
        color="#30363D", lw=2, zorder=1)

# ── Draw each card ────────────────────────────────────────────────────────────
for i, sp in enumerate(speeches):
    y     = len(speeches) - 1 - i   # top-to-bottom order
    color = MONTH_COLORS[sp["month"]]
    cbg   = CARD_BG[sp["month"]]

    # Dot on spine
    ax.scatter([spine_x], [y], s=120, color=color, zorder=3, linewidths=1.5,
               edgecolors="white")

    # Horizontal connector
    ax.plot([spine_x, 1.75], [y, y], color=color, lw=1.5, zorder=2)

    # ── Card background ──
    card = FancyBboxPatch(
        (1.80, y - 0.45), 7.8, 0.9,
        boxstyle="round,pad=0.04", linewidth=1.2,
        edgecolor=color, facecolor="#161B22", zorder=4,
    )
    ax.add_patch(card)

    # Date label (left of spine)
    ax.text(
        spine_x - 0.08, y,
        sp["date"].strftime("%b %d"),
        ha="right", va="center", fontsize=9.5, fontweight="bold",
        color=color, zorder=5,
    )

    # ── Title ──
    ax.text(
        1.95, y + 0.14,
        sp["title"],
        ha="left", va="center", fontsize=10.5, fontweight="bold",
        color="white", zorder=5, linespacing=1.25,
    )

    # ── Location icon + text ──
    ax.text(
        4.60, y + 0.18,
        "◎  " + sp["location"],   # ◎
        ha="left", va="center", fontsize=8.5,
        color="#79C0FF", zorder=5, linespacing=1.2,
    )

    # ── Channel icon + text ──
    ax.text(
        4.60, y - 0.18,
        "▶  " + sp["channel"],    # ▶
        ha="left", va="center", fontsize=8,
        color="#F0883E", zorder=5, linespacing=1.2,
    )

    # ── Topic / what happened ──
    ax.text(
        1.95, y - 0.12,
        sp["topic"],
        ha="left", va="center", fontsize=7.8,
        color="#8B949E", zorder=5, linespacing=1.25,
    )

# ── Month separators ──────────────────────────────────────────────────────────
month_boundaries = {"March": 4.5, "April": 9.5}
for label, ypos in month_boundaries.items():
    ax.axhline(ypos, xmin=0.02, xmax=0.98, color="#21262D", lw=1, ls="--", zorder=0)

# ── Footer ────────────────────────────────────────────────────────────────────
fig.text(
    0.5, 0.004,
    "Sources: whitehouse.gov · C-SPAN · CNBC · PBS NewsHour · Al Jazeera · Fox News · CBS · Rev.com",
    ha="center", fontsize=8.5, color="#484F58",
)

plt.tight_layout(rect=[0, 0.005, 1, 0.975])
out = r"C:\Users\Riyan\Downloads\trump_speeches_march_may_2026.png"
plt.savefig(out, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: {out}")
