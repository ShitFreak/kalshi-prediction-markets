import json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

rows = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_quote_raw.json"))

def build(lead):  # '10' or '20'
    pts = []
    for r in rows:
        b, a = r.get('bid' + lead), r.get('ask' + lead)
        if b is None or a is None: continue
        mid = (b + a) / 2
        if 0 < mid < 1:
            pts.append((mid, r['win'], a, b))   # mid, win, ask(buy), bid(sell)
    return pts

def stats(pts):
    p = np.array([x[0] for x in pts]); y = np.array([x[1] for x in pts])
    beta = np.cov(p, y, bias=True)[0, 1] / p.var() - 1.0
    spread = np.mean([x[2] - x[3] for x in pts])
    return dict(n=len(pts), meanp=p.mean(), beta=beta, avg=(y - p).mean(),
                cheap=np.mean([x[1]-x[0] for x in pts if x[0] < .25]),
                dear=np.mean([x[1]-x[0] for x in pts if x[0] > .75]), spread=spread, p=p, y=y)

def lastret(lead):  # avg return using LAST-TRADE price (for comparison)
    v = [(r['last'+lead], r['win']) for r in rows if r.get('last'+lead) and 0 < r['last'+lead] < 1]
    return np.mean([w - p for p, w in v]), len(v)

fig, axes = plt.subplots(1, 2, figsize=(16, 7.5))
for ax, lead, col in [(axes[0], '10', '#6a1b9a'), (axes[1], '20', '#1b5e20')]:
    pts = build(lead); s = stats(pts); lr, ln = lastret(lead)
    print(f"=== t-{lead}min  YES mid-quote ===")
    print(f"  n={s['n']} | mean mid {s['meanp']*100:.0f}c | bias b {s['beta']:+.3f} | avg ret {s['avg']*100:+.1f}% "
          f"| cheap {s['cheap']*100:+.1f}% | dear {s['dear']*100:+.1f}% | avg spread {s['spread']*100:.1f}c")
    print(f"  (compare LAST-TRADE avg ret {lr*100:+.1f}% on n={ln})")
    edges = np.linspace(0, 1, 11); xs, ws, ns = [], [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (s['p'] >= lo) & (s['p'] < hi)
        if m.sum() >= 20: xs.append(s['p'][m].mean()); ws.append(s['y'][m].mean()); ns.append(int(m.sum()))
    ax.plot([0, 1], [0, 1], 'k--', lw=1.5, label='fair (45°)')
    ax.plot(xs, ws, '-o', color=col, lw=2.5, ms=7, label=f"YES mid-quote (n={s['n']})")
    for x, w, n in zip(xs, ws, ns): ax.annotate(str(n), (x, w), textcoords='offset points', xytext=(0, 7), fontsize=7.5, ha='center')
    ax.set_title(f"t-{lead}min  |  YES bid/ask MID odds  |  b={s['beta']:+.3f}  avg ret {s['avg']*100:+.1f}%  spread~{s['spread']*100:.1f}c", weight='bold')
    ax.set_xlabel(f"YES mid-quote {lead}min before speech"); ax.set_ylabel("actual rate word was said")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.legend(loc='upper left'); ax.grid(alpha=.3)
fig.suptitle("Politician MENTION words: calibration using YES bid/ask MID (not last trade)", fontsize=14, weight='bold')
fig.tight_layout(rect=[0, 0, 1, 0.95])
out = r"C:\Users\Riyan\Downloads\kalshi_quote_calibration.png"
fig.savefig(out, dpi=130); print("saved", out)
