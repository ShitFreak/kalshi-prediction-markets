"""
Aggregate Trump word frequency across 11 speeches (Jan 2025 - April 2026).
Visualize bragging words and out-of-context tangents.
"""
import matplotlib.pyplot as plt
import numpy as np

# Word -> total mentions across all 11 speeches
data = {
    # CORE BRAGGING / SIGNATURE
    "Tariff":          78,
    "Border":          48,
    "Iran":            45,
    "Best":            40,
    "Illegal Alien":   32,
    "Billion":         31,
    "Greatest":        28,
    "China":           25,
    "Tremendous":      24,
    "Trillion":        23,
    "Democrat":        23,
    "Records":         23,
    "Election":        20,
    "Nobody":          19,
    "Like Never B.":   15,
    "First Term":      14,
    "Russia":          14,
    "Fake News":       11,
    "Hottest":          7,
    "Stock Market":     7,
    "Woke":             7,
    "Recruit":          7,
    "Venezuela":        5,
    "250":              5,
    "America First":    5,
    "DEI":              5,
    "Fentanyl":         4,
    "Transgender":      4,
    "Hormuz":           3,
    "Space Force":      2,
    "Gulf of America":  1,
    # Zero mentions
    "Sleepy Joe":       0,
    "Crypto/Bitcoin":   0,
    "AI":               0,
    "Witch Hunt":       0,
    "Hoax":             0,
    "Eight War":        0,
}

# Categorize
brag_words = ["Best", "Greatest", "Tremendous", "Records", "Hottest",
              "Trillion", "Billion", "Like Never B.", "Nobody", "First Term",
              "Election", "America First", "250", "Stock Market", "Recruit",
              "Space Force", "Gulf of America"]
policy_words = ["Tariff", "Border", "Illegal Alien", "Fentanyl", "China",
                "Iran", "Russia", "Venezuela", "Hormuz"]
grievance_words = ["Democrat", "Fake News", "Woke", "DEI", "Transgender",
                   "Sleepy Joe", "Witch Hunt", "Hoax"]
fringe_words = ["Crypto/Bitcoin", "AI", "Eight War"]

def cat(w):
    if w in brag_words: return ("BRAG", "#10b981")
    if w in policy_words: return ("POLICY", "#ef4444")
    if w in grievance_words: return ("GRIEVANCE", "#a855f7")
    return ("FRINGE", "#6b7280")

# Sort by frequency
sorted_items = sorted(data.items(), key=lambda x: -x[1])
words = [w for w, _ in sorted_items]
counts = [c for _, c in sorted_items]
colors = [cat(w)[1] for w in words]

fig, ax = plt.subplots(figsize=(15, 12), facecolor="#0a0a0a")
ax.set_facecolor("#0a0a0a")

y_pos = np.arange(len(words))
bars = ax.barh(y_pos, counts, color=colors, edgecolor="white", linewidth=0.5)
ax.set_yticks(y_pos)
ax.set_yticklabels(words, color="white", fontsize=10.5)
ax.invert_yaxis()
ax.set_xlabel("Total mentions across 11 speeches (Jan 2025 - Apr 2026)",
              color="#d1d5db", fontsize=11)
ax.tick_params(axis="x", colors="#d1d5db")
ax.set_title("TRUMP'S VOCABULARY — 11-SPEECH FREQUENCY MAP",
             color="white", fontsize=17, fontweight="bold", pad=20)

# Annotate counts at end of bars
for i, (w, c) in enumerate(sorted_items):
    ax.text(c + 1, i, str(c), color="white", va="center", fontsize=9.5)

# Subtle grid
ax.grid(axis="x", color="#374151", linestyle="--", alpha=0.4)
ax.set_axisbelow(True)
for spine in ax.spines.values():
    spine.set_color("#374151")

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor="#10b981", label="BRAGGING (self-praise)"),
    Patch(facecolor="#ef4444", label="POLICY/THREAT"),
    Patch(facecolor="#a855f7", label="GRIEVANCE/RIVAL"),
    Patch(facecolor="#6b7280", label="FRINGE (rare)"),
]
ax.legend(handles=legend_elements, loc="lower right",
          facecolor="#171717", edgecolor="#374151", labelcolor="white",
          fontsize=10)

# Footer with key insight
fig.text(0.5, 0.01,
         "Speeches sampled: Inauguration, Inaugural Rally, Joint Session, Liberation Day Tariffs, West Point, Iran Strikes,\n"
         "Salute to America, UN General Assembly, Prayer Breakfast, SOTU 2026, Iran Address April 2026",
         ha="center", color="#6b7280", fontsize=8.5, style="italic")

plt.tight_layout(rect=[0, 0.03, 1, 1])
out = r"C:\Users\Riyan\Downloads\trump_wordfreq.png"
plt.savefig(out, dpi=160, facecolor="#0a0a0a", bbox_inches="tight")
print(f"Saved -> {out}")
