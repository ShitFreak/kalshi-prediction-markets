"""
Presentation-quality image of Trump 2026 speech vocabulary analysis.
Speeches: Davos (1/21), Prayer Breakfast (2/5), SOTU (2/24), Iran Address (4/1)
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

# 2026 speeches and their per-word frequency
speeches_2026 = ["Davos\n1/21/26\n62 min", "Prayer Bfst\n2/5/26\n76 min",
                 "SOTU\n2/24/26\n107 min", "Iran Addr\n4/1/26\n18 min"]

# Word -> [Davos, Prayer, SOTU, Iran]
words_data = {
    # BRAGGING
    "Greatest":      [12, 8, 0, 0],
    "Tremendous":    [8, 7, 2, 1],
    "Best":          [6, 6, 3, 0],
    "Billion":       [16, 3, 2, 0],
    "Trillion":      [8, 3, 2, 1],
    "Records":       [3, 0, 3, 1],
    "Nobody":        [7, 5, 2, 1],
    "Like Never B.": [0, 0, 2, 1],
    "Hottest":       [1, 0, 1, 1],
    "First Term":    [3, 2, 1, 1],
    "Election":      [5, 3, 1, 0],
    "Stock Market":  [5, 0, 1, 1],
    "250":           [0, 0, 3, 0],
    # POLICY
    "Tariff":        [11, 1, 2, 0],
    "Border":        [8, 2, 4, 0],
    "Iran":          [0, 2, 0, 23],
    "China":         [9, 0, 0, 0],
    "Venezuela":     [4, 2, 1, 2],
    "Russia":        [4, 0, 0, 1],
    "Hormuz":        [0, 0, 0, 3],
    "Fentanyl":      [0, 0, 1, 0],
    "Illegal Alien": [0, 0, 1, 0],
    "Recruit":       [0, 0, 1, 0],
    # GRIEVANCE
    "Democrat":      [0, 3, 2, 0],
    "Fake News":     [2, 2, 0, 0],
    "DEI":           [0, 0, 1, 0],
    # FRINGE
    "AI":            [4, 0, 0, 0],
    "Crypto/BTC":    [3, 0, 0, 0],
    "Sleepy Joe":    [0, 0, 0, 0],
    "Witch Hunt":    [0, 0, 0, 0],
    "Gulf of America":[0, 0, 0, 0],
    "Space Force":   [0, 0, 0, 0],
}

# Category & color
brag_words = {"Greatest","Tremendous","Best","Billion","Trillion","Records","Nobody",
              "Like Never B.","Hottest","First Term","Election","Stock Market","250"}
policy_words = {"Tariff","Border","Iran","China","Venezuela","Russia","Hormuz",
                "Fentanyl","Illegal Alien","Recruit"}
grievance_words = {"Democrat","Fake News","DEI"}

def get_color(w):
    if w in brag_words: return "#10b981"
    if w in policy_words: return "#ef4444"
    if w in grievance_words: return "#a855f7"
    return "#6b7280"

# Compute totals & sort
totals = {w: sum(v) for w, v in words_data.items()}
sorted_words = sorted(words_data.keys(), key=lambda w: -totals[w])

# ====== BUILD FIGURE ======
fig = plt.figure(figsize=(22, 14), facecolor="#0a0a0a")
gs = fig.add_gridspec(2, 2, width_ratios=[1.4, 1], height_ratios=[1, 1],
                      hspace=0.35, wspace=0.18)

# Master title
fig.text(0.5, 0.965,
         "TRUMP'S 2026 VOCABULARY",
         ha="center", fontsize=28, color="white", fontweight="bold")
fig.text(0.5, 0.935,
         "Word frequency across 4 major 2026 speeches  •  263 min of speech analyzed",
         ha="center", fontsize=13, color="#9ca3af", style="italic")

# ===== PANEL 1: Stacked horizontal bar =====
ax1 = fig.add_subplot(gs[:, 0])
ax1.set_facecolor("#0a0a0a")

y_pos = np.arange(len(sorted_words))
left = np.zeros(len(sorted_words))
speech_colors = ["#3b82f6", "#a855f7", "#f59e0b", "#ef4444"]
speech_alphas = [1.0, 0.85, 0.7, 0.55]

for i, sp in enumerate(speeches_2026):
    vals = [words_data[w][i] for w in sorted_words]
    ax1.barh(y_pos, vals, left=left, color=speech_colors[i],
             alpha=speech_alphas[i], edgecolor="#0a0a0a", linewidth=0.6,
             label=sp.replace("\n"," "))
    left += vals

ax1.set_yticks(y_pos)
ax1.set_yticklabels(sorted_words, color="white", fontsize=10)
ax1.invert_yaxis()
ax1.set_xlabel("Total mentions across 4 speeches", color="#d1d5db", fontsize=11)
ax1.tick_params(axis="x", colors="#d1d5db")
ax1.set_title("WORD FREQUENCY — 2026 SPEECHES (stacked by speech)",
              color="white", fontsize=14, fontweight="bold", pad=12)
ax1.grid(axis="x", color="#374151", linestyle="--", alpha=0.4)
ax1.set_axisbelow(True)
for s in ax1.spines.values(): s.set_color("#374151")

# Annotate totals
for i, w in enumerate(sorted_words):
    t = totals[w]
    if t > 0:
        ax1.text(t + 0.5, i, str(t), va="center", color="white", fontsize=9)
    else:
        ax1.text(0.3, i, "0", va="center", color="#6b7280", fontsize=9, style="italic")

ax1.legend(loc="lower right", facecolor="#171717", edgecolor="#374151",
           labelcolor="white", fontsize=10, title="Speech",
           title_fontsize=10)

# Color word labels by category
for i, w in enumerate(sorted_words):
    ax1.get_yticklabels()[i].set_color(get_color(w))

# ===== PANEL 2: Top Bragging Words =====
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor("#0a0a0a")
ax2.set_title("TOP BRAGGING WORDS (2026)",
              color="white", fontsize=13, fontweight="bold", pad=10)

brag_sorted = [(w, totals[w]) for w in sorted_words if w in brag_words and totals[w] > 0][:10]
b_words = [w for w, _ in brag_sorted]
b_counts = [c for _, c in brag_sorted]
ypos2 = np.arange(len(b_words))
ax2.barh(ypos2, b_counts, color="#10b981", edgecolor="white", linewidth=0.5)
ax2.set_yticks(ypos2)
ax2.set_yticklabels(b_words, color="white", fontsize=10)
ax2.invert_yaxis()
ax2.tick_params(axis="x", colors="#d1d5db")
for i, c in enumerate(b_counts):
    ax2.text(c + 0.3, i, str(c), va="center", color="#10b981",
             fontsize=10, fontweight="bold")
ax2.grid(axis="x", color="#374151", linestyle="--", alpha=0.4)
ax2.set_axisbelow(True)
for s in ax2.spines.values(): s.set_color("#374151")

# ===== PANEL 3: Out-of-Context Tangents =====
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_facecolor("#0a0a0a")
ax3.axis("off")
ax3.set_title("OUT-OF-CONTEXT TANGENTS (2026)",
              color="white", fontsize=13, fontweight="bold", pad=10, loc="left")

tangents = [
    ("DAVOS",        "#3b82f6", "Swiss watch tariff escalated 30%→39% mid-call due to PM 'rudeness'"),
    ("DAVOS",        "#3b82f6", "Pressuring Macron to RAISE Euro drug prices 2-3x"),
    ("DAVOS",        "#3b82f6", "Windmills rant — China makes them but won't use them"),
    ("PRAYER BFST",  "#a855f7", "'I needed it for my own ego' confession at religious event"),
    ("PRAYER BFST",  "#a855f7", "3 AM phone calls with Speaker Johnson over 9 holdouts"),
    ("PRAYER BFST",  "#a855f7", "Pardoned 22 imprisoned soldiers framed as martyrs"),
    ("SOTU",         "#f59e0b", "Michael Dell dorm-room startup story"),
    ("SOTU",         "#f59e0b", "Asked Olympic hockey goalie Hellebuyck a save-technique Q"),
    ("SOTU",         "#f59e0b", "Live ad-read: 'go to TrumpAccounts.gov'"),
    ("IRAN ADDR",    "#ef4444", "Opened with NASA Artemis 2 rocket launch praise"),
    ("IRAN ADDR",    "#ef4444", "'Take Venezuela in a matter of minutes'"),
    ("IRAN ADDR",    "#ef4444", "Stock-market + oil + tax-refund brags mid-war update"),
]

n = len(tangents)
y_start = 0.95
y_step = 0.075
for i, (src, color, text) in enumerate(tangents):
    y = y_start - i * y_step
    # Source tag
    ax3.add_patch(Rectangle((0.0, y - 0.025), 0.16, 0.05,
                            facecolor=color, alpha=0.85,
                            transform=ax3.transAxes, clip_on=False))
    ax3.text(0.08, y, src, ha="center", va="center", fontsize=8,
             color="white", fontweight="bold", transform=ax3.transAxes)
    # Text
    ax3.text(0.18, y, text, ha="left", va="center", fontsize=9.2,
             color="#e5e7eb", transform=ax3.transAxes)

# ===== Bottom legend strip =====
fig.text(0.5, 0.015,
         "● BRAGGING (self-praise)    ● POLICY/THREAT    ● GRIEVANCE/RIVAL    ● FRINGE/DEAD",
         ha="center", color="#d1d5db", fontsize=10)
fig.text(0.5, -0.005,
         "Word label colors match category. Stacked bars show which 2026 speech contributed each mention.",
         ha="center", color="#6b7280", fontsize=9, style="italic")

plt.tight_layout(rect=[0, 0.02, 1, 0.92])
out = r"C:\Users\Riyan\Downloads\trump_2026_presentation.png"
plt.savefig(out, dpi=160, facecolor="#0a0a0a", bbox_inches="tight")
print(f"Saved -> {out}")
