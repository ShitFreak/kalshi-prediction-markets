import json, urllib.request, urllib.parse, time, collections
import numpy as np

API = "https://api.elections.kalshi.com/trade-api/v2"
def get(url, tries=3):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=45))
        except Exception as e:
            if t == tries - 1: raise
            time.sleep(1.0)

# 1) series -> (category, title) map from the full catalog
cat_map = {}
sd = get(API + '/series')
for s in sd.get('series', []):
    cat_map[s['ticker']] = (s.get('category'), s.get('title') or '')
print("catalog series:", len(cat_map))

# 2) pull settled markets ONCE (category param is ignored, so just take all), dedup by ticker
cur, mk = '', {}
for i in range(140):
    q = {'status': 'settled', 'with_nested_markets': 'true', 'limit': '200'}
    if cur: q['cursor'] = cur
    d = get(API + '/events?' + urllib.parse.urlencode(q))
    for e in d.get('events', []):
        for m in (e.get('markets') or []):
            res = m.get('result'); px = float(m.get('last_price_dollars') or 0); vol = float(m.get('volume_fp') or 0)
            if res in ('yes', 'no') and 0.01 <= px <= 0.99 and vol >= 20:
                mk[m['ticker']] = {'series': m['ticker'].split('-')[0], 'price': px,
                                   'win': 1 if res == 'yes' else 0, 'vol': vol}
    cur = d.get('cursor') or ''
    if not cur: break
rows = list(mk.values())
print("settled markets (deduped, interior price, vol>=20):", len(rows))

# 3) assign real category + mention subtype
def mention_sub(series, title):
    s = (series + ' ' + title).upper()
    if any(w in s for w in ('TNF','NFL','NBA','MLB','NHL','UFC','SOCCER','F1','WNBA','PGA','GOLF','GAME','BOXING')):
        return None  # skip sports
    if 'EARN' in s or 'BERKSHIRE' in s or 'BRKMENTION' in series.upper():
        return 'Mentions: Earnings calls'
    pol = ('POWELL','JPOW','TRUMP','MAMDANI','STARMER','CROCKETT','BIANCO','COSTA','DEBATE',
           'PRESIDENT','SENATE','CONGRESS','GOVERNOR','MINISTER','POLITIC','FINK','MAYOR','ZELENS','PUTIN')
    if any(w in s for w in pol):
        return 'Mentions: Politicians/officials'
    return 'Mentions: Media/public figures'

groups = collections.defaultdict(list)
unmapped = 0
for r in rows:
    cat, title = cat_map.get(r['series'], (None, ''))
    if cat is None: unmapped += 1; continue
    if cat == 'Sports': continue
    if cat == 'Mentions':
        g = mention_sub(r['series'], title)
        if g: groups[g].append(r)
    else:
        groups[cat].append(r)
print("unmapped series rows:", unmapped)
print("group sizes:", {k: len(v) for k, v in sorted(groups.items(), key=lambda x: -len(x[1]))})

# 4) bias fit per group
def fit(rs):
    p = np.array([x['price'] for x in rs]); y = np.array([x['win'] for x in rs])
    if len(rs) < 30 or p.std() < 1e-6: return None
    beta = np.cov(p, y, bias=True)[0, 1] / p.var() - 1.0
    alpha = (y - p).mean() - beta * p.mean()
    cheap = [x for x in rs if x['price'] < 0.25]; dear = [x for x in rs if x['price'] > 0.75]
    f = dict(n=len(rs), meanp=float(p.mean()), beta=float(beta), alpha=float(alpha),
             avg=float((y - p).mean()),
             cheap=float(np.mean([x['win']-x['price'] for x in cheap])) if cheap else float('nan'), nc=len(cheap),
             dear=float(np.mean([x['win']-x['price'] for x in dear])) if dear else float('nan'), nd=len(dear),
             brier=float(np.mean((p - y) ** 2)))
    return f

res = [(g, fit(v)) for g, v in groups.items()]
res = [(g, f) for g, f in res if f]
res.sort(key=lambda x: -x[1]['beta'])

print("\n=========== FAVORITE-LONGSHOT BIAS GRADIENT  (live Kalshi settled markets) ===========")
h = f"{'market group':33}{'n':>5}{'meanPx':>7}{'bias b':>8}{'alpha':>7}{'avgRet':>8}{'cheap<25c':>13}{'dear>75c':>12}"
print(h); print('-' * len(h))
for g, f in res:
    print(f"{g:33}{f['n']:>5}{f['meanp']*100:>6.0f}c{f['beta']:>+8.3f}{f['alpha']:>+7.3f}"
          f"{f['avg']*100:>+7.1f}%{f['cheap']*100:>+9.1f}%({f['nc']:>3}){f['dear']*100:>+7.1f}%({f['nd']:>3})")

json.dump({g: v for g, v in groups.items()}, open(r"C:\Users\Riyan\Downloads\kalshi_bias_raw2.json", "w"))
json.dump({g: f for g, f in res}, open(r"C:\Users\Riyan\Downloads\kalshi_bias_summary2.json", "w"))
print("\nMORE BIASED = higher 'bias b' AND more negative 'cheap<25c' return. saved json to Downloads.")
