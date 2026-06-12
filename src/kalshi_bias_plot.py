import json, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

raw = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_bias_raw2.json"))
summ = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_bias_summary2.json"))

# order by bias slope (descending)
order = sorted(summ.keys(), key=lambda g: -summ[g]['beta'])
betas = [summ[g]['beta'] for g in order]
ns = [summ[g]['n'] for g in order]
cheap = [summ[g]['cheap'] for g in order]
dear = [summ[g]['dear'] for g in order]

fig, (axA, axB) = plt.subplots(1, 2, figsize=(17, 8))

# ---------- Panel A: bias gradient bar chart ----------
ypos = np.arange(len(order))[::-1]
colors = ['#d7301f' if b > 0 else '#2c7fb8' for b in betas]   # red=favorite-longshot, blue=reverse
axA.barh(ypos, betas, color=colors, alpha=0.85)
axA.axvline(0, color='black', lw=1)
for y, g, b, n in zip(ypos, order, betas, ns):
    axA.text(b + (0.002 if b >= 0 else -0.002), y, f"{b:+.3f}  (n={n})",
             va='center', ha='left' if b >= 0 else 'right', fontsize=9)
axA.set_yticks(ypos); axA.set_yticklabels(order, fontsize=10)
axA.set_xlabel("bias slope  b  =  Cov(price,outcome)/Var(price) - 1", fontsize=11)
axA.set_title("FAVORITE-LONGSHOT BIAS GRADIENT by market\n"
              "red = longshots overpriced (classic);  blue = favorites overpriced (reverse)",
              fontsize=12, weight='bold')
axA.set_xlim(-0.075, 0.095)
axA.grid(axis='x', alpha=0.3)

# ---------- Panel B: calibration curves for selected groups ----------
sel = ['Financials', 'Crypto', 'Mentions: Earnings calls', 'Economics', 'Entertainment']
sel = [g for g in sel if g in raw]
edges = np.linspace(0, 1, 11)
cmap = plt.cm.tab10(np.linspace(0, 1, len(sel)))
axB.plot([0, 1], [0, 1], 'k--', lw=1.5, label='fair (45°)')
for g, col in zip(sel, cmap):
    p = np.array([r['price'] for r in raw[g]]); y = np.array([r['win'] for r in raw[g]])
    xs, ws = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p >= lo) & (p < hi)
        if m.sum() >= 20:
            xs.append(p[m].mean()); ws.append(y[m].mean())
    if len(xs) >= 3:
        axB.plot(xs, ws, '-o', color=col, lw=2, ms=5, label=f"{g} (b={summ[g]['beta']:+.3f})")
axB.set_xlabel("contract price  =  implied probability", fontsize=11)
axB.set_ylabel("actual win rate", fontsize=11)
axB.set_title("Calibration: actual win rate vs price\n"
              "below 45° = overpriced (you lose);  above = underpriced (you win)", fontsize=12, weight='bold')
axB.set_xlim(0, 1); axB.set_ylim(0, 1); axB.legend(fontsize=9, loc='upper left'); axB.grid(alpha=0.3)

fig.suptitle("Live Kalshi favorite-longshot bias  —  100,460 settled markets (sports excluded)",
             fontsize=15, weight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.95])
out = r"C:\Users\Riyan\Downloads\kalshi_bias_gradient.png"
fig.savefig(out, dpi=130); print("saved:", out)
