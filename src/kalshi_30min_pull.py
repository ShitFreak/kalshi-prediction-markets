import json, urllib.request, urllib.parse, time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

API = "https://api.elections.kalshi.com/trade-api/v2"
def get(url, tries=4):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=45))
        except Exception:
            if t == tries - 1: return None
            time.sleep(0.6 * (t + 1))

def iso2u(s):
    return int(datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())

# 1) catalog -> category
cat_map = {}
for s in (get(API + '/series') or {}).get('series', []):
    cat_map[s['ticker']] = s.get('category')
print("catalog:", len(cat_map), flush=True)

# 2) re-pull settled markets keeping ticker, close_time, result, vol, category
cur, items = '', []
for i in range(160):
    q = {'status': 'settled', 'with_nested_markets': 'true', 'limit': '200'}
    if cur: q['cursor'] = cur
    d = get(API + '/events?' + urllib.parse.urlencode(q))
    if not d: break
    for e in d.get('events', []):
        for m in (e.get('markets') or []):
            res = m.get('result'); ct = m.get('close_time'); vol = float(m.get('volume_fp') or 0)
            if res in ('yes', 'no') and ct and vol >= 100:
                ser = m['ticker'].split('-')[0]; cat = cat_map.get(ser)
                if cat and cat != 'Sports':
                    items.append({'ticker': m['ticker'], 'series': ser, 'close': ct,
                                  'win': 1 if res == 'yes' else 0, 'vol': vol, 'cat': cat})
    cur = d.get('cursor') or ''
    if not cur: break
print("eligible non-sports settled (vol>=100):", len(items), flush=True)

# selection: ALL Financials + Economics + Mentions + Politics, plus top-by-volume of the rest, cap 12000
prio = {'Financials', 'Economics', 'Politics'}
keep = [x for x in items if x['cat'] in prio or x['series'].upper().find('MENTION') >= 0 or 'Mention' in x['cat']]
rest = sorted([x for x in items if x not in keep], key=lambda x: -x['vol'])
sel = keep + rest[:max(0, 12000 - len(keep))]
print("selected for candlestick pull:", len(sel), flush=True)

def price_30min(x):
    end = iso2u(x['close']); start = end - 2 * 3600
    u = f"{API}/series/{x['series']}/markets/{x['ticker']}/candlesticks?start_ts={start}&end_ts={end}&period_interval=1"
    d = get(u)
    if not d: return None
    cs = d.get('candlesticks', [])
    seq = []
    for c in cs:
        pr = c.get('price') or {}
        v = None
        for k in ('close_dollars', 'mean_dollars', 'previous_dollars', 'open_dollars'):
            if pr.get(k) not in (None, ''):
                fv = float(pr[k])
                if fv > 0: v = fv; break
        if v is None:
            yb = (c.get('yes_bid') or {}).get('close_dollars'); ya = (c.get('yes_ask') or {}).get('close_dollars')
            if yb and ya and float(yb) > 0 and float(ya) > 0: v = (float(yb) + float(ya)) / 2
        if v is not None: seq.append((c['end_period_ts'], v))
    if not seq: return None
    seq.sort()
    target = end - 1800
    before = [tv for tv in seq if tv[0] <= target]
    chosen = before[-1] if before else seq[0]
    lead_min = (end - chosen[0]) / 60.0
    return {'p30': chosen[1], 'win': x['win'], 'cat': x['cat'], 'vol': x['vol'],
            'lead': round(lead_min, 1), 'ticker': x['ticker']}

out = []
done = [0]; lock = threading.Lock()
with ThreadPoolExecutor(max_workers=12) as ex:
    futs = {ex.submit(price_30min, x): x for x in sel}
    for f in as_completed(futs):
        r = f.result()
        with lock:
            done[0] += 1
            if done[0] % 1000 == 0: print(f"  candles {done[0]}/{len(sel)}", flush=True)
        if r: out.append(r)
print("usable 30-min-prior prices:", len(out), flush=True)
json.dump(out, open(r"C:\Users\Riyan\Downloads\kalshi_30min_raw.json", "w"))
print("saved kalshi_30min_raw.json", flush=True)
