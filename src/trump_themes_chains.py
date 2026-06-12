"""
Trump Coast Guard Speech - Directional Word-Implication Chains
With INTERSECTING words (bridge words belong to 2+ themes).
"""
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

# Theme colors
COLORS = {
    "BORDER":     "#ef4444",
    "IRAN":       "#f59e0b",
    "ECONOMY":    "#10b981",
    "MILITARY":   "#3b82f6",
    "GRIEVANCE":  "#a855f7",
    "TECH":       "#06b6d4",
    "FOREIGN":    "#f97316",
    "GEOGRAPHY":  "#ec4899",
}

# Each word entry: (word, note, [list of themes it belongs to])
# First theme listed = "home" theme. Extra themes = bridges.
themes = [
    ("BORDER / IMMIGRATION", "BORDER", [
        ("Fentanyl",       "rare trigger",           ["BORDER"]),
        ("Drug",           "drug crisis",            ["BORDER"]),
        ("Illegal Alien",  "actor label",            ["BORDER", "GRIEVANCE"]),
        ("Venezuela",      "source + regime",        ["BORDER", "FOREIGN"]),
        ("Cuba",           "source + regime",        ["BORDER", "FOREIGN"]),
        ("Border",         "umbrella",               ["BORDER"]),
    ]),
    ("IRAN / MIDDLE EAST", "IRAN", [
        ("Hormuz",         "specific trigger",       ["IRAN", "FOREIGN"]),
        ("Iran",           "country focus",          ["IRAN", "FOREIGN"]),
        ("Nuclear",        "the threat / deal",      ["IRAN"]),
        ("Eight War",      "'I stopped wars'",       ["IRAN", "GRIEVANCE"]),
    ]),
    ("ECONOMY / BRAGGING", "ECONOMY", [
        ("250",            "America's 250th b'day",  ["ECONOMY"]),
        ("Hottest",        "'hottest economy'",      ["ECONOMY", "GRIEVANCE"]),
        ("Trillion",       "tariffs / AI invest $",  ["ECONOMY", "TECH"]),
        ("Stock Market",   "scoreboard",             ["ECONOMY", "GRIEVANCE"]),
        ("First Term",     "comparison anchor",      ["ECONOMY", "GRIEVANCE"]),
    ]),
    ("MILITARY / COAST GUARD", "MILITARY", [
        ("Long Blue Line", "USCG motto",             ["MILITARY"]),
        ("Recruit",        "'recruiting back'",      ["MILITARY"]),
        ("DEI / Woke",     "prior weakness",         ["MILITARY", "GRIEVANCE"]),
        ("Transgender",    "culture jab",            ["MILITARY", "GRIEVANCE"]),
        ("Space Force",    "'I created it'",         ["MILITARY"]),
        ("Natl Security",  "broad wrapper",          ["MILITARY", "FOREIGN"]),
    ]),
    ("GRIEVANCE / RIVALS", "GRIEVANCE", [
        ("Sleepy Joe",     "personal attack",        ["GRIEVANCE"]),
        ("Fake News",      "media attack",           ["GRIEVANCE"]),
        ("Democrat",       "party attack",           ["GRIEVANCE"]),
        ("Election",       "'rigged / won big'",     ["GRIEVANCE"]),
    ]),
    ("TECH / FUTURE", "TECH", [
        ("AI",             "China competition",      ["TECH"]),
        ("Crypto/Bitcoin", "'crypto capital'",       ["TECH", "ECONOMY"]),
        ("America First",  "umbrella slogan",        ["TECH", "GRIEVANCE"]),
    ]),
    ("FOREIGN POLICY", "FOREIGN", [
        ("Russia",         "Ukraine deal",           ["FOREIGN"]),
        ("Gulf of America","renaming flex",          ["FOREIGN", "GEOGRAPHY"]),
    ]),
    ("GEOGRAPHY / FLEX", "GEOGRAPHY", [
        ("Texas",          "border / energy",        ["GEOGRAPHY", "BORDER"]),
        ("Puerto Rico",    "wildcard",               ["GEOGRAPHY"]),
    ]),
]

fig, ax = plt.subplots(figsize=(22, 15), facecolor="#0a0a0a")
ax.set_facecolor("#0a0a0a")
ax.set_xlim(0, 22)
ax.set_ylim(0, 15)
ax.axis("off")

# Title
ax.text(11, 14.5, "TRUMP @ COAST GUARD ACADEMY — RHETORICAL CHAINS WITH BRIDGE WORDS",
        ha="center", va="center", fontsize=21, color="white", fontweight="bold")
ax.text(11, 14.05,
        "Top word in each card = rare TRIGGER.  Arrow ⇒ 'if said, the next is near-certain.'  "
        "Pills with TWO colors = bridge words shared across themes.",
        ha="center", va="center", fontsize=11, color="#9ca3af", style="italic")

cols = 4
rows = 2
col_w = 5.4
row_h = 6.3
x_pad = 0.25
y_top = 13.3

# Track word positions for cross-theme bridges
word_positions = {}  # word -> list of (x, y, themes)

for idx, (title, home_key, chain) in enumerate(themes):
    color = COLORS[home_key]
    r = idx // cols
    c = idx % cols
    x0 = c * col_w + x_pad
    y_box_top = y_top - r * row_h
    box_w = col_w - 2 * x_pad
    box_h = row_h - 0.6

    # Card background
    card = FancyBboxPatch(
        (x0, y_box_top - box_h), box_w, box_h,
        boxstyle="round,pad=0.05,rounding_size=0.15",
        linewidth=1.5, edgecolor=color, facecolor="#171717"
    )
    ax.add_patch(card)

    # Title bar
    title_bar = FancyBboxPatch(
        (x0, y_box_top - 0.55), box_w, 0.55,
        boxstyle="round,pad=0.02,rounding_size=0.1",
        linewidth=0, facecolor=color, alpha=0.85
    )
    ax.add_patch(title_bar)
    ax.text(x0 + box_w / 2, y_box_top - 0.28, title,
            ha="center", va="center", fontsize=11.5, color="white", fontweight="bold")

    n = len(chain)
    word_area_top = y_box_top - 0.85
    word_area_bottom = y_box_top - box_h + 0.3
    word_area_h = word_area_top - word_area_bottom
    spacing = word_area_h / n

    centers_y = []
    for i, (word, note, w_themes) in enumerate(chain):
        cy = word_area_top - spacing * (i + 0.5)
        centers_y.append(cy)

        pill_w = box_w - 0.5
        pill_h = 0.46
        px = x0 + 0.25
        py = cy - pill_h / 2

        is_bridge = len(w_themes) > 1

        # If bridge: draw split background showing both colors
        if is_bridge:
            other_themes = [t for t in w_themes if t != home_key]
            other_color = COLORS[other_themes[0]] if other_themes else color
            # Left half - home color tint
            left = FancyBboxPatch(
                (px, py), pill_w / 2 + 0.1, pill_h,
                boxstyle="round,pad=0.02,rounding_size=0.18",
                linewidth=0, facecolor=color, alpha=0.25
            )
            ax.add_patch(left)
            # Right half - other theme color tint
            right = FancyBboxPatch(
                (px + pill_w / 2 - 0.1, py), pill_w / 2 + 0.1, pill_h,
                boxstyle="round,pad=0.02,rounding_size=0.18",
                linewidth=0, facecolor=other_color, alpha=0.25
            )
            ax.add_patch(right)
            # Outline
            outline = FancyBboxPatch(
                (px, py), pill_w, pill_h,
                boxstyle="round,pad=0.02,rounding_size=0.18",
                linewidth=1.6, edgecolor=other_color, facecolor="none",
                linestyle="--"
            )
            ax.add_patch(outline)
            outline2 = FancyBboxPatch(
                (px, py), pill_w, pill_h,
                boxstyle="round,pad=0.02,rounding_size=0.18",
                linewidth=1.6, edgecolor=color, facecolor="none"
            )
            ax.add_patch(outline2)
        else:
            pill = FancyBboxPatch(
                (px, py), pill_w, pill_h,
                boxstyle="round,pad=0.02,rounding_size=0.18",
                linewidth=1, edgecolor=color, facecolor="#262626"
            )
            ax.add_patch(pill)

        # Rank number
        ax.text(px + 0.18, cy, f"{i+1}",
                ha="left", va="center", fontsize=10, color=color, fontweight="bold")
        # Word
        weight = "bold"
        ax.text(px + 0.55, cy, word,
                ha="left", va="center", fontsize=10.5, color="white", fontweight=weight)
        # Note
        ax.text(px + pill_w - 0.12, cy, note,
                ha="right", va="center", fontsize=7.8, color="#9ca3af", style="italic")

        # Bridge badge
        if is_bridge:
            badges = [t for t in w_themes if t != home_key]
            badge_text = "+" + "/".join(b[:3] for b in badges)
            other_color = COLORS[badges[0]]
            ax.text(px + pill_w - 0.12, cy + 0.32, badge_text,
                    ha="right", va="center", fontsize=7, color=other_color,
                    fontweight="bold")

    # Downward arrows
    for i in range(n - 1):
        y_from = centers_y[i] - 0.24
        y_to = centers_y[i + 1] + 0.24
        arrow = FancyArrowPatch(
            (x0 + box_w / 2, y_from), (x0 + box_w / 2, y_to),
            arrowstyle="->,head_width=4,head_length=6",
            linewidth=1.6, color=color, alpha=0.8, mutation_scale=10
        )
        ax.add_patch(arrow)

# Legend at bottom
legend_y = 0.6
ax.text(11, legend_y + 0.25,
        "BRIDGE WORDS (dashed outline + 2 colors) activate TWO themes at once → highest information value if Trump says them.",
        ha="center", va="center", fontsize=11.5, color="#fbbf24", fontweight="bold")
ax.text(11, legend_y - 0.15,
        "e.g. 'Venezuela' = Border + Foreign  |  'Hormuz' = Iran + Foreign  |  'DEI/Woke' = Military + Grievance  |  'Trillion' = Economy + Tech  |  'Eight War' = Iran + Grievance",
        ha="center", va="center", fontsize=9.5, color="#d1d5db", style="italic")
ax.text(11, legend_y - 0.45,
        "Ranking within card = specificity. Rank 1 is rare/high-signal; lower ranks are broader and near-certain at a USCG commencement.",
        ha="center", va="center", fontsize=8.5, color="#6b7280", style="italic")

plt.tight_layout()
out = r"C:\Users\Riyan\Downloads\trump_themes_chains.png"
plt.savefig(out, dpi=160, facecolor="#0a0a0a", bbox_inches="tight")
print(f"Saved -> {out}")
