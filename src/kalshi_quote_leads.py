import json, numpy as np, bisect
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

rows = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_quote_seq.json"))
def ba_at(seq, q):
    ts = [p[0] for p in seq]; i = bisect.bisect_right(ts, q) - 1
    if i < 0: return None
    return seq[i][1], seq[i][2]   # bid, ask

def points(lead):
    out = []
    for r in rows:
        if not r['ba']: continue
        ba = ba_at(r['ba'], r['t'] - lead)
        if ba is None: continue
        b, a = ba; mid = (b + a) / 2
        if 0 < mid < 1: out.append((mid, r['win'], a - b))
    return out

def stats(pts):
    p = np.array([x[0] for x in pts]); y = np.array([x[1] for x in pts])
    beta = np.cov(p, y, bias=True)[0,1]/p.var() - 1.0
    spr = np.array([x[2] for x in pts])
    tight = [x for x in pts if x[2] <= 0.05]
    tnet = (np.mean([x[1]-x[0] for x in tight]) - 0.025) if tight else float('nan')
    return dict(n=len(pts), mp=p.mean(), b=beta, avg=(y-p).mean(),
                cheap=np.mean([x[1]-x[0] for x in pts if x[0]<.25]),
                dear=np.mean([x[1]-x[0] for x in pts if x[0]>.75]),
                spr_mean=spr.mean(), spr_med=np.median(spr), ntight=len(tight), tnet=tnet, p=p, y=y)

leads = [('t-10', 600, '#6a1b9a'), ('t-20', 1200, '#1b5e20'), ('t-30', 1800, '#d7301f')]
S = {}
print(f"{'lead':6}{'n':>6}{'meanMid':>8}{'biasB':>8}{'avgRet':>8}{'cheap':>8}{'dear':>8}{'sprMean':>9}{'sprMed':>8}{'tightNet':>9}")
for name, L, _ in leads:
    s = stats(points(L)); S[name] = s
    print(f"{name:6}{s['n']:>6}{s['mp']*100:>7.0f}c{s['b']:>+8.3f}{s['avg']*100:>+7.1f}%{s['cheap']*100:>+7.1f}%{s['dear']*100:>+7.1f}%{s['spr_mean']*100:>8.1f}c{s['spr_med']*100:>7.1f}c{s['tnet']*100:>+8.1f}%")

# plot: left = t-30 calibration; right = all three leads overlaid
fig, (a1, a2) = plt.subplots(1, 2, figsize=(16, 7.5))
def calib(s):
    e = np.linspace(0,1,11); xs, ws, ns = [], [], []
    for lo, hi in zip(e[:-1], e[1:]):
        m = (s['p']>=lo)&(s['p']<hi)
        if m.sum() >= 20: xs.append(s['p'][m].mean()); ws.append(s['y'][m].mean()); ns.append(int(m.sum()))
    return xs, ws, ns
s30 = S['t-30']; xs, ws, ns = calib(s30)
a1.plot([0,1],[0,1],'k--',lw=1.5,label='fair (45°)')
a1.plot(xs, ws, '-o', color='#d7301f', lw=2.5, ms=7, label=f"t-30 YES mid (n={s30['n']})")
for x,w,n in zip(xs,ws,ns): a1.annotate(str(n),(x,w),textcoords='offset points',xytext=(0,7),fontsize=7.5,ha='center')
a1.set_title(f"t-30min | YES bid/ask MID | b={s30['b']:+.3f} | avg ret {s30['avg']*100:+.1f}% | spread med {s30['spr_med']*100:.0f}c",weight='bold')
a1.set_xlabel("YES mid-quote 30 min before speech"); a1.set_ylabel("actual rate word was said")
a1.set_xlim(0,1); a1.set_ylim(0,1); a1.legend(loc='upper left'); a1.grid(alpha=.3)
a2.plot([0,1],[0,1],'k--',lw=1.5,label='fair (45°)')
for name, L, col in leads:
    xs, ws, ns = calib(S[name]); a2.plot(xs, ws, '-o', color=col, lw=2, ms=5, label=f"{name} (n={S[name]['n']})")
a2.set_title("All leads overlaid (YES mid) — does the bias change with lead time?",weight='bold')
a2.set_xlabel("YES mid-quote before speech"); a2.set_ylabel("actual rate"); a2.set_xlim(0,1); a2.set_ylim(0,1); a2.legend(loc='upper left'); a2.grid(alpha=.3)
fig.suptitle("Politician MENTION words — YES quote calibration at t-30 (and t-10/20 for context)", fontsize=14, weight='bold')
fig.tight_layout(rect=[0,0,1,0.95])
out = r"C:\Users\Riyan\Downloads\kalshi_quote_t30.png"
fig.savefig(out, dpi=130); print("\nsaved", out)
