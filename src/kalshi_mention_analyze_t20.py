import json, numpy as np, collections, bisect
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

words = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_mention_raw.json"))
by_ev = collections.defaultdict(list)
for w in words: by_ev[w['event']].append(w)

def price_at(seq, q):
    ts = [p[0] for p in seq]
    i = bisect.bisect_right(ts, q) - 1
    return seq[i][1] if i >= 0 else None

LEAD = 1200   # 20 minutes before first word -> YES
points = []; nojump = 0; cov_drop = 0; contrib_events = set()
for ev, ws in by_ev.items():
    yj = [w['jump'] for w in ws if w['win'] == 1 and w['jump']]
    if not yj: nojump += 1; continue
    t = min(yj); q = t - LEAD
    for w in ws:
        seq = w['seq']
        if not seq: continue
        if seq[0][0] > q: cov_drop += 1; continue
        px = price_at(seq, q)
        if px is None or not (0.0 < px < 1.0): continue
        points.append((px, w['win'], ev, w['vol'])); contrib_events.add(ev)

print(f"LEAD = t-20min | events: {len(by_ev)} | anchorable: {len(by_ev)-nojump} | contributing: {len(contrib_events)}")
print(f"word-points: {len(points)} | dropped (opened after t-20min): {cov_drop}")

p = np.array([x[0] for x in points]); y = np.array([x[1] for x in points])
beta = np.cov(p, y, bias=True)[0,1]/p.var() - 1.0
alpha = (y-p).mean() - beta*p.mean()
cheap = [x for x in points if x[0] < 0.25]; dear = [x for x in points if x[0] > 0.75]
cr = np.mean([x[1]-x[0] for x in cheap]) if cheap else float('nan')
dr = np.mean([x[1]-x[0] for x in dear]) if dear else float('nan')
print(f"bias slope b = {beta:+.3f} | alpha {alpha:+.3f} | mean px {p.mean()*100:.0f}c | avg ret {(y-p).mean()*100:+.1f}%")
print(f"cheap<25c {cr*100:+.1f}% (n={len(cheap)}) | dear>75c {dr*100:+.1f}% (n={len(dear)})")

edges = np.linspace(0,1,11); xs, ws_, ns = [], [], []
for lo,hi in zip(edges[:-1], edges[1:]):
    m = (p>=lo)&(p<hi)
    if m.sum() >= 20: xs.append(p[m].mean()); ws_.append(y[m].mean()); ns.append(int(m.sum()))

fig, ax = plt.subplots(figsize=(9.5,8))
ax.plot([0,1],[0,1],'k--',lw=1.5,label='fair (45°)')
ax.plot(xs, ws_, '-o', color='#1b5e20', lw=2.5, ms=7,
        label=f'actual ({len(points)} words, {len(contrib_events)} speeches)')
for x,w,n in zip(xs,ws_,ns): ax.annotate(str(n),(x,w),textcoords='offset points',xytext=(0,7),fontsize=8,ha='center')
ax.set_title(f"Politician MENTION markets — pre-speech (t-20min) odds vs actual\n"
             f"24h window | bias slope b = {beta:+.3f} | avg ret {(y-p).mean()*100:+.1f}% | dear>75c {dr*100:+.1f}%",weight='bold')
ax.set_xlabel("pre-speech price (t-20min) = implied chance the word is said")
ax.set_ylabel("actual rate the word was said")
ax.set_xlim(0,1); ax.set_ylim(0,1); ax.legend(loc='upper left'); ax.grid(alpha=.3)
out = r"C:\Users\Riyan\Downloads\kalshi_mention_t20.png"
fig.tight_layout(); fig.savefig(out, dpi=130); print("saved", out)
