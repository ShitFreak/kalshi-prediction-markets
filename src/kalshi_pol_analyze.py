import json, numpy as np, collections
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

words = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_pol_raw.json"))
by_ev = collections.defaultdict(list)
for w in words: by_ev[w['event']].append(w)

points = []         # (pre_price, win, event, vol)
skip_no_t = 0
for ev, ws in by_ev.items():
    yes_jumps = [w['jump'] for w in ws if w['win'] == 1 and w['jump']]
    if not yes_jumps:
        skip_no_t += 1; continue
    t = min(yes_jumps)                       # first word -> YES = speech anchor
    tgt = t - 600                            # 10 minutes before
    for w in ws:
        seq = w['seq']
        before = [pv for pv in seq if pv[0] <= tgt]
        if not before: continue              # no quote 10 min before speech
        ts, px = before[-1]
        if (t - ts) > 25 * 60: continue      # require the quote be within ~25min of t (not stale)
        if 0.0 < px < 1.0:
            points.append((px, w['win'], ev, w['vol']))

print(f"events: {len(by_ev)} | usable (with t): {len(by_ev)-skip_no_t} | skipped(no YES jump): {skip_no_t}")
print(f"pre-speech word-points: {len(points)} across {len(set(p[2] for p in points))} speeches")

p = np.array([x[0] for x in points]); y = np.array([x[1] for x in points])
beta = np.cov(p, y, bias=True)[0,1]/p.var() - 1.0
alpha = (y-p).mean() - beta*p.mean()
cheap = [x for x in points if x[0] < 0.25]; dear = [x for x in points if x[0] > 0.75]
print(f"\nbias slope b = {beta:+.3f} | alpha = {alpha:+.3f} | mean price {p.mean()*100:.0f}c | avg ret {(y-p).mean()*100:+.1f}%")
print(f"cheap<25c avg ret {np.mean([x[1]-x[0] for x in cheap])*100:+.1f}% (n={len(cheap)}) | dear>75c {np.mean([x[1]-x[0] for x in dear])*100:+.1f}% (n={len(dear)})")

# calibration curve
edges = np.linspace(0,1,11)
xs, ws_, ns = [], [], []
for lo,hi in zip(edges[:-1], edges[1:]):
    m = (p>=lo)&(p<hi)
    if m.sum() >= 20: xs.append(p[m].mean()); ws_.append(y[m].mean()); ns.append(int(m.sum()))

fig, ax = plt.subplots(figsize=(9.5,8))
ax.plot([0,1],[0,1],'k--',lw=1.5,label='fair (45°)')
ax.plot(xs, ws_, '-o', color='#6a1b9a', lw=2.5, ms=7, label=f'actual (n={len(points)} words, {len(set(x[2] for x in points))} speeches)')
for x,w,n in zip(xs,ws_,ns): ax.annotate(str(n),(x,w),textcoords='offset points',xytext=(0,7),fontsize=8,ha='center')
ax.set_title(f"Politician mention markets: pre-speech (t-10min) odds vs actual\nbias slope b = {beta:+.3f}  —  below 45° = overpriced longshot words",weight='bold')
ax.set_xlabel("pre-speech price = market's implied chance the word is said")
ax.set_ylabel("actual rate the word was said")
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.legend(loc='upper left'); ax.grid(alpha=.3)
out = r"C:\Users\Riyan\Downloads\kalshi_politician_calibration.png"
fig.tight_layout(); fig.savefig(out, dpi=130); print("\nsaved", out)
