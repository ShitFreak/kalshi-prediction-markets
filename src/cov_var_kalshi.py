import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# x = contract PRICE (cents).  y = average PROFIT at that price = payout - price (cents).
# Cheap contracts lose (negative profit), expensive ones gain -> favorite-longshot bias.
price  = np.array([5, 15, 25, 35, 45, 55, 65, 75, 85, 95], float)
profit = np.array([-2.0, -1.0, -1.1, -0.3, -0.5, 0.4, 0.2, 0.9, 1.0, 1.6], float)

pbar, ybar = price.mean(), profit.mean()
dp, dy = price - pbar, profit - ybar
var_p = (dp ** 2).mean()
cov = (dp * dy).mean()
beta = cov / var_p
alpha = ybar - beta * pbar

BLUE, RED = "#2c7fb8", "#d7301f"
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# ===== Panel 1: VARIANCE of PRICE =====
ax = axes[0]
for pi, d in zip(price, dp):
    s = abs(d)
    ax.add_patch(Rectangle((min(pi, pbar), 0), s, s,
                           facecolor=BLUE, alpha=0.20, edgecolor=BLUE))
ax.scatter(price, np.zeros_like(price), color="black", zorder=5)
ax.axvline(pbar, color="black", lw=2)
ax.text(pbar + 1, -4, f"mean price = {pbar:.0f}c", fontsize=10)
ax.set_aspect("equal")
ax.set_xlim(-2, 102); ax.set_ylim(-6, 50)
ax.set_title("VARIANCE of PRICE\nVar = avg of (price - mean)$^2$\n= avg area of these squares",
             fontsize=12)
ax.text(2, 46, f"Var(price) = {var_p:.0f}", fontsize=12, color=BLUE, weight="bold")
ax.set_xlabel("contract price (cents)")

# ===== Panel 2: COVARIANCE of price & profit =====
ax = axes[1]
for pi, yi, ddp, ddy in zip(price, profit, dp, dy):
    c = BLUE if ddp * ddy > 0 else RED
    ax.add_patch(Rectangle((min(pbar, pi), min(ybar, yi)), abs(ddp), abs(ddy),
                           facecolor=c, alpha=0.32, edgecolor=c))
ax.axhline(0, color="gray", ls=":", lw=1.5)
ax.text(2, 0.12, "break-even (profit = 0)", color="gray", fontsize=9)
ax.axvline(pbar, color="black", lw=1.5)
ax.axhline(ybar, color="black", lw=1.5)
ax.scatter(price, profit, color="black", zorder=5)
ax.scatter([pbar], [ybar], color="gold", edgecolor="black", s=130, zorder=6,
           label="mean point")
ax.text(80, 1.45, "+  expensive\n& you profit", color=BLUE, fontsize=9, ha="center")
ax.text(18, 1.45, "-  cheap\n& you profit", color=RED, fontsize=9, ha="center")
ax.text(18, -1.9, "+  cheap\n& you lose", color=BLUE, fontsize=9, ha="center")
ax.text(80, -1.9, "-  expensive\n& you lose", color=RED, fontsize=9, ha="center")
ax.set_title("COVARIANCE of price & profit\nCov = avg of (price-mean)(profit-mean)\n= avg SIGNED rectangle area",
             fontsize=12)
ax.set_xlim(-2, 102); ax.set_ylim(-2.6, 2.2)
ax.text(2, 1.95, f"Cov = {cov:.1f}  (>0: dearer -> more profit)",
        fontsize=11, color=BLUE, weight="bold")
ax.set_xlabel("contract price (cents)"); ax.set_ylabel("profit (cents)")
ax.legend(loc="lower right", fontsize=9)

# ===== Panel 3: SLOPE = Cov / Var = the bias =====
ax = axes[2]
ax.axhline(0, color="gray", ls=":", lw=1.5)
ax.scatter(price, profit, color="black", zorder=5)
xs = np.linspace(0, 100, 50)
ax.plot(xs, alpha + beta * xs, color=BLUE, lw=2.5,
        label=f"bias line\nslope b = Cov/Var = {beta:.3f}")
ax.scatter([pbar], [ybar], color="gold", edgecolor="black", s=130, zorder=6)
ax.annotate("cheap longshots\nLOSE", (5, -2.0), (12, -2.3), fontsize=9, color=RED,
            arrowprops=dict(arrowstyle="->", color=RED))
ax.annotate("favorites\nWIN", (95, 1.6), (62, 1.5), fontsize=9, color=BLUE,
            arrowprops=dict(arrowstyle="->", color=BLUE))
ax.set_title("SLOPE = Cov / Var = the favorite-longshot bias\n"
             r"b = $\frac{Cov(price,profit)}{Var(price)}$"
             "  ~ 0.034 in the real Kalshi data", fontsize=12)
ax.set_xlim(-2, 102); ax.set_ylim(-2.8, 2.2)
ax.set_xlabel("contract price (cents)"); ax.set_ylabel("profit (cents)")
ax.legend(loc="upper left", fontsize=9)

fig.suptitle("Kalshi favorite-longshot bias:  x = price,  y = profit (payout - price)",
             fontsize=15, weight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.95])
out = r"C:\Users\Riyan\Downloads\cov_var_kalshi.png"
fig.savefig(out, dpi=130)
print("saved:", out)
print(f"mean price={pbar:.1f}c, mean profit={ybar:.2f}c, Var(price)={var_p:.1f}, "
      f"Cov={cov:.2f}, beta={beta:.4f}, alpha={alpha:.2f}")
