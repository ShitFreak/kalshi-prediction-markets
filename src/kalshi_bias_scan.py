import json, urllib.request, urllib.parse, time, collections
import numpy as np

API = "https://api.elections.kalshi.com/trade-api/v2"

def get(url, tries=3):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=40))
        except Exception as e:
            if t == tries - 1: raise
            time.sleep(1.0)

def pull_category(cat, max_pages=45):
    """Return settled markets (with result + interior last price + real volume) for a category."""
    cur, out = '', []
    for _ in range(max_pages):
        q = {'category': cat, 'status': 'settled', 'with_nested_markets': 'true', 'limit': '200'}
        if cur: q['cursor'] = cur
        d = get(API + '/events?' + urllib.parse.urlencode(q))
        for e in d.get('events', []):
            for m in (e.get('markets') or []):
                res = m.get('result')
                px = float(m.get('last_price_dollars') or 0)
                vol = float(m.get('volume_fp') or 0)
                if res in ('yes', 'no') and 0.01 <= px <= 0.99 and vol >= 20:
                    out.append({'ticker': m['ticker'], 'series': m['ticker'].split('-')[0],
                                'price': px, 'win': 1 if res == 'yes' else 0, 'vol': vol})
        cur = d.get('cursor') or ''
        if not cur: break
    return out

def classify_mention(series):
    s = series.upper()
    sports = ('TNF', 'NFL', 'NBA', 'MLB', 'NHL', 'UFC', 'SOCCER', 'F1', 'GAME', 'WNBA', 'PGA', 'GOLF')
    if any(w in s for w in sports): return 'SKIP-sports'
    if 'EARN' in s or 'BRKMENTION' in s: return 'Mentions: Earnings calls'
    politicians = ('POW', 'JPOW', 'TRUMP', 'MAMDANI', 'STARMER', 'CROCKETT', 'BIANCO', 'COSTA',
                   'CANDEB', 'LEADER', 'SENATE', 'PRES', 'CONGRESS', 'GOV', 'POLI', 'FED', 'FINK')
    if any(w in s for w in politicians): return 'Mentions: Politicians/officials'
    return 'Mentions: Media/public figures'

def fit(rows):
    p = np.array([r['price'] for r in rows]); y = np.array([r['win'] for r in rows])
    n = len(rows)
    if n < 8 or p.std() < 1e-6: return None
    beta = np.cov(p, y, bias=True)[0, 1] / p.var()          # slope of (outcome) on price ...
    beta_bias = beta - 1.0                                  # ... minus 1 = favorite-longshot slope
    alpha = (y - p).mean() - beta_bias * p.mean()
    avg_ret = float((y - p).mean())                         # pre-fee avg profit per $1 contract
    cheap = [r for r in rows if r['price'] < 0.25]
    dear = [r for r in rows if r['price'] > 0.75]
    cr = float(np.mean([r['win'] - r['price'] for r in cheap])) if cheap else float('nan')
    dr = float(np.mean([r['win'] - r['price'] for r in dear])) if dear else float('nan')
    return dict(n=n, meanp=float(p.mean()), beta=float(beta_bias), alpha=float(alpha),
                avg_ret=avg_ret, cheap_ret=cr, n_cheap=len(cheap), dear_ret=dr, n_dear=len(dear))

# ---- collect ----
CATS = ['Economics', 'Mentions', 'Politics', 'Financials', 'Companies',
        'Climate and Weather', 'Entertainment', 'Science and Technology']
groups = collections.defaultdict(list)
for cat in CATS:
    rows = pull_category(cat)
    if cat == 'Mentions':
        for r in rows:
            g = classify_mention(r['series'])
            if g != 'SKIP-sports':
                groups[g].append(r)
    else:
        groups[cat] += rows
    print(f"  pulled {cat:22} usable={len(rows)}")

print("\nGROUP SAMPLES:", {k: len(v) for k, v in groups.items()})

# ---- analyze ----
res = []
for g, rows in groups.items():
    f = fit(rows)
    if f: res.append((g, f))
res.sort(key=lambda x: -x[1]['beta'])   # most biased (steepest positive slope) first

print("\n================ FAVORITE-LONGSHOT BIAS GRADIENT (live Kalshi settled data) ================")
hdr = f"{'market group':32} {'n':>4} {'meanPx':>6} {'bias b':>7} {'alpha':>7} {'avgRet':>7} {'cheap<25c':>10} {'dear>75c':>9}"
print(hdr); print('-' * len(hdr))
for g, f in res:
    print(f"{g:32} {f['n']:>4} {f['meanp']*100:>5.0f}c {f['beta']:>+7.3f} {f['alpha']:>+7.3f} "
          f"{f['avg_ret']*100:>+6.1f}% {f['cheap_ret']*100:>+8.1f}%({f['n_cheap']:>2}) {f['dear_ret']*100:>+6.1f}%({f['n_dear']:>2})")

json.dump({g: rows for g, rows in groups.items()},
          open(r"C:\Users\Riyan\Downloads\kalshi_bias_raw.json", "w"))
json.dump({g: f for g, f in res}, open(r"C:\Users\Riyan\Downloads\kalshi_bias_summary.json", "w"))
print("\nsaved raw + summary json to Downloads")
print("interpretation: bias b > 0 & negative avg cheap return = favorite-longshot bias present (more biased = higher b).")
