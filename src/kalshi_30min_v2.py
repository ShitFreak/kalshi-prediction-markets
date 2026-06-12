import json, urllib.request, urllib.error, urllib.parse, time, threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

API = "https://api.elections.kalshi.com/trade-api/v2"
def get(url, tries=5):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(1.5 * (t + 1)); continue
            if t == tries - 1: return None
            time.sleep(0.5 * (t + 1))
        except Exception:
            if t == tries - 1: return None
            time.sleep(0.5 * (t + 1))
    return None

cat_map = {s['ticker']: s.get('category') for s in (get(API + '/series') or {}).get('series', [])}
targets = {'Financials', 'Economics', 'Mentions', 'Politics'}
series = [tk for tk, c in cat_map.items() if c in targets]
print("target series:", len(series), flush=True)

# enumerate settled markets for target series (threaded, lightweight, no nesting)
cand = []; lock = threading.Lock()
def enum(st):
    out = []; cur = ''
    for _ in range(4):
        q = {'series_ticker': st, 'status': 'settled', 'limit': '200'}
        if cur: q['cursor'] = cur
        d = get(API + '/markets?' + urllib.parse.urlencode(q))
        if not d: break
        for m in d.get('markets', []):
            if m.get('result') in ('yes', 'no') and m.get('close_time') and float(m.get('volume_fp') or 0) >= 100:
                out.append({'ticker': m['ticker'], 'series': st, 'close': m['close_time'],
                            'win': 1 if m['result'] == 'yes' else 0, 'vol': float(m['volume_fp']), 'cat': cat_map[st]})
        cur = d.get('cursor') or ''
        if not cur: break
    return out
with ThreadPoolExecutor(max_workers=10) as ex:
    for fut in as_completed([ex.submit(enum, st) for st in series]):
        cand += fut.result()
print("candidate settled markets (vol>=100):", len(cand), flush=True)

cand.sort(key=lambda x: -x['vol'])
CAP = 1600
sel = cand[:CAP]
print("candlestick pulling:", len(sel), "(workers=5, 429-safe, incremental save)", flush=True)

OUT = r"C:\Users\Riyan\Downloads\kalshi_30min_raw.json"
def p30(x):
    end = int(datetime.fromisoformat(x['close'].replace('Z', '+00:00')).timestamp()); start = end - 3600
    d = get(f"{API}/series/{x['series']}/markets/{x['ticker']}/candlesticks?start_ts={start}&end_ts={end}&period_interval=1")
    if not d: return None
    seq = []
    for c in d.get('candlesticks', []):
        pr = c.get('price') or {}; v = None
        for k in ('close_dollars', 'mean_dollars', 'previous_dollars', 'open_dollars'):
            if pr.get(k) not in (None, ''):
                fv = float(pr[k])
                if fv > 0: v = fv; break
        if v is None:
            yb = (c.get('yes_bid') or {}).get('close_dollars'); ya = (c.get('yes_ask') or {}).get('close_dollars')
            if yb and ya and float(yb) > 0 and float(ya) > 0: v = (float(yb) + float(ya)) / 2
        if v is not None: seq.append((c['end_period_ts'], v))
    if not seq: return None
    seq.sort(); target = end - 1800
    before = [tv for tv in seq if tv[0] <= target]
    ch = before[-1] if before else seq[0]
    return {'p30': ch[1], 'win': x['win'], 'cat': x['cat'], 'vol': x['vol'],
            'lead': round((end - ch[0]) / 60, 1), 'ticker': x['ticker']}

out = []; done = [0]
with ThreadPoolExecutor(max_workers=5) as ex:
    for fut in as_completed([ex.submit(p30, x) for x in sel]):
        r = fut.result()
        with lock:
            done[0] += 1
            if r: out.append(r)
            if done[0] % 200 == 0:
                print(f"  {done[0]}/{len(sel)} (usable {len(out)})", flush=True)
                json.dump(out, open(OUT, "w"))
json.dump(out, open(OUT, "w"))
print("DONE. usable 30-min-prior prices:", len(out), flush=True)
