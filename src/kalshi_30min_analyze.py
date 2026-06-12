import json, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

rows = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_30min_raw.json"))
# keep genuine lead (>=20 min before close) so price isn't already settled
rows = [r for r in rows if r.get('lead', 0) >= 20 and 0.0 < r['p30'] < 1.0]
print("usable rows (lead>=20min):", len(rows))

def subcat(r):
    if r['cat'] != 'Mentions': return r['cat']
    s = r['ticker'].upper()
    if any(w in s for w in ('TNF','NFL','NBA','MLB','NHL','UFC','GAME','SOCCER','F1')): return 'Mentions: Sports(skip)'
    if 'EARN' in s or 'BRK' in s: return 'Mentions: Earnings'
    if any(w in s for w in ('POW','TRUMP','MAMDANI','STARMER','CROCKETT','BIANCO','COSTA','DEBATE','PRES','SENATE','CONGRESS','GOV','FINK','MAYOR')):
        return 'Mentions: Politicians'
    return 'Mentions: Media'

for r in rows: r['g'] = subcat(r)

def fit(rs):
    p = np.array([r['p30'] for r in rs]); y = np.array([r['win'] for r in rs])
    if len(rs) < 40 or p.std() < 1e-6: return None
    beta = np.cov(p, y, bias=True)[0,1]/p.var() - 1.0
    alpha = (y-p).mean() - beta*p.mean()
    cheap = [r for r in rs if r['p30'] < 0.25]; dear = [r for r in rs if r['p30'] > 0.75]
    return dict(n=len(rs), mp=float(p.mean()), beta=float(beta), alpha=float(alpha),
                avg=float((y-p).mean()),
                cheap=float(np.mean([r['win']-r['p30'] for r in cheap])) if cheap else float('nan'), nc=len(cheap),
                dear=float(np.mean([r['win']-r['p30'] for r in dear])) if dear else float('nan'), nd=len(dear))

groups = {}
for r in rows: groups.setdefault(r['g'], []).append(r)
res = [(g, fit(v)) for g, v in groups.items() if not g.endswith('(skip)')]
res = [(g, f) for g, f in res if f]; res.sort(key=lambda x: -x[1]['beta'])
pooled = fit([r for r in rows if not r['g'].endswith('(skip)')])

# compare to last-trade betas
try: last = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_bias_summary2.json"))
except: last = {}

print("\n===== BIAS GRADIENT @ 30-MIN-BEFORE-CLOSE PRICE (decontaminated) =====")
h = f"{'group':30}{'n':>6}{'meanP':>7}{'beta30':>8}{'lastTr':>8}{'avgRet':>8}{'cheap<25':>11}{'dear>75':>11}"
print(h); print('-'*len(h))
for g, f in res:
    lb = last.get(g, {}).get('beta')
    print(f"{g:30}{f['n']:>6}{f['mp']*100:>6.0f}c{f['beta']:>+8.3f}{(f'{lb:+.3f}' if lb is not None else '   -'):>8}"
          f"{f['avg']*100:>+7.1f}%{f['cheap']*100:>+8.1f}%({f['nc']:>3}){f['dear']*100:>+7.1f}%({f['nd']:>3})")
print('-'*len(h))
print(f"{'POOLED (all non-sports)':30}{pooled['n']:>6}{pooled['mp']*100:>6.0f}c{pooled['beta']:>+8.3f}{'':>8}{pooled['avg']*100:>+7.1f}%")

# ---------- plots ----------
fig, (axA, axB) = plt.subplots(1, 2, figsize=(17, 7.5))
edges = np.linspace(0,1,21)
def calib(rs):
    p=np.array([r['p30'] for r in rs]); y=np.array([r['win'] for r in rs]); xs,ws,ns=[],[],[]
    for lo,hi in zip(edges[:-1],edges[1:]):
        m=(p>=lo)&(p<hi)
        if m.sum()>=25: xs.append(p[m].mean()); ws.append(y[m].mean()); ns.append(int(m.sum()))
    return xs,ws,ns
# Panel A: pooled calibration
xs,ws,ns=calib([r for r in rows if not r['g'].endswith('(skip)')])
axA.plot([0,1],[0,1],'k--',lw=1.5,label='fair (45°)')
axA.plot(xs,ws,'-o',color='#d7301f',lw=2.5,ms=6,label=f'actual (pooled, n={pooled["n"]})')
for x,w,n in zip(xs,ws,ns): axA.annotate(str(n),(x,w),textcoords='offset points',xytext=(0,6),fontsize=7,ha='center')
axA.set_title('Calibration at 30-min-before-close price (POOLED)\nbelow 45° = overpriced longshots; above = underpriced favorites',weight='bold')
axA.set_xlabel('price 30 min before close = implied probability'); axA.set_ylabel('actual win rate')
axA.set_xlim(0,1); axA.set_ylim(0,1); axA.legend(loc='upper left'); axA.grid(alpha=.3)
# Panel B: per-category bias gradient (30-min) vs last-trade
order=[g for g,_ in res]; b30=[dict(res)[g]['beta'] for g in order]
blast=[last.get(g,{}).get('beta',np.nan) for g in order]
yy=np.arange(len(order))[::-1]
axB.barh(yy+0.18,b30,height=0.36,color='#d7301f',alpha=.85,label='30-min price (clean)')
axB.barh(yy-0.18,blast,height=0.36,color='#9ecae1',alpha=.9,label='last-trade price (contaminated)')
axB.axvline(0,color='black',lw=1)
axB.set_yticks(yy); axB.set_yticklabels(order,fontsize=9)
axB.set_xlabel('bias slope b'); axB.set_title('Bias slope by market: 30-min vs last-trade price',weight='bold')
axB.legend(fontsize=9); axB.grid(axis='x',alpha=.3)
fig.suptitle(f'Kalshi favorite-longshot bias, de-contaminated (price 30 min before resolution)  —  n={pooled["n"]}',fontsize=14,weight='bold')
fig.tight_layout(rect=[0,0,1,0.95])
out=r"C:\Users\Riyan\Downloads\kalshi_bias_30min.png"; fig.savefig(out,dpi=130); print("\nsaved",out)
