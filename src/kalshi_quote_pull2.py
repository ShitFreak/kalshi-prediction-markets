import json, urllib.request, urllib.error, time, threading, bisect, collections
from concurrent.futures import ThreadPoolExecutor, as_completed

API = "https://api.elections.kalshi.com/trade-api/v2"
START = time.time(); el = lambda: int(time.time() - START)
def get(url, tries=5, to=45):
    for t in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=to))
        except urllib.error.HTTPError as e:
            if getattr(e, 'code', 0) == 429: time.sleep(2.0 * (t + 1)); continue
            if t == tries - 1: return None
            time.sleep(0.5 * (t + 1))
        except Exception:
            if t == tries - 1: return None
            time.sleep(0.5 * (t + 1))
    return None

raw = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_mention_raw.json"))
by_ev = collections.defaultdict(list)
for w in raw: by_ev[w['event']].append(w)
jobs = []
for ev, ws in by_ev.items():
    yj = [w['jump'] for w in ws if w['win'] == 1 and w['jump']]
    if not yj: continue
    t = min(yj)
    for w in ws:
        jobs.append({'ticker': w['ticker'], 'series': w['ticker'].split('-')[0],
                     'event': ev, 'win': w['win'], 'vol': w['vol'], 't': t})
print(f"[{el()}s] jobs: {len(jobs)}", flush=True)

def pull(j):
    t = j['t']; start = t - 4 * 3600; end = t          # 4h window -> supports any lead up to t-4h
    d = get(f"{API}/series/{j['series']}/markets/{j['ticker']}/candlesticks?start_ts={start}&end_ts={end}&period_interval=1")
    seq = []  # compressed [ts, bid, ask] change-points
    if d:
        last = None
        for c in sorted(d.get('candlesticks', []), key=lambda c: c['end_period_ts']):
            yb = (c.get('yes_bid') or {}).get('close_dollars'); ya = (c.get('yes_ask') or {}).get('close_dollars')
            if yb in (None, '') or ya in (None, ''): continue
            b = round(float(yb), 4); a = round(float(ya), 4)
            if not (0 < b <= a < 1.0001): continue
            if (b, a) != last:
                seq.append([c['end_period_ts'], b, a]); last = (b, a)
    time.sleep(0.05)
    return {'ticker': j['ticker'], 'event': j['event'], 'win': j['win'], 'vol': j['vol'], 't': t, 'ba': seq}

OUT = r"C:\Users\Riyan\Downloads\kalshi_quote_seq.json"
out = []; done = [0]; lock = threading.Lock(); N = len(jobs)
with ThreadPoolExecutor(max_workers=4) as ex:
    for f in as_completed([ex.submit(pull, j) for j in jobs]):
        r = f.result()
        with lock:
            done[0] += 1; out.append(r)
            if done[0] % 200 == 0 or done[0] == N:
                e = max(time.time() - START, 1); rate = done[0] / e
                print(f"[{el()}s] {done[0]}/{N} | {rate:.1f}/s | ETA {int((N-done[0])/rate)}s", flush=True)
                if done[0] % 1000 == 0: json.dump(out, open(OUT, "w"))
json.dump(out, open(OUT, "w"))
print(f"[{el()}s] DONE: {len(out)} words with full YES bid/ask seq", flush=True)
