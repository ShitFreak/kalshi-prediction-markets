import json, urllib.request, urllib.error, time, threading, bisect
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

API = "https://api.elections.kalshi.com/trade-api/v2"
START = time.time(); el = lambda: int(time.time() - START)
def get(url, tries=5, to=40):
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
import collections
by_ev = collections.defaultdict(list)
for w in raw: by_ev[w['event']].append(w)
def price_at(seq, q):
    ts = [p[0] for p in seq]; i = bisect.bisect_right(ts, q) - 1
    return seq[i][1] if i >= 0 else None

# build per-word jobs (only anchorable events), carry t + last-trade prices for comparison
jobs = []
for ev, ws in by_ev.items():
    yj = [w['jump'] for w in ws if w['win'] == 1 and w['jump']]
    if not yj: continue
    t = min(yj)
    for w in ws:
        jobs.append({'ticker': w['ticker'], 'series': w['ticker'].split('-')[0], 'event': ev,
                     'win': w['win'], 'vol': w['vol'], 't': t,
                     'last10': price_at(w['seq'], t - 600), 'last20': price_at(w['seq'], t - 1200)})
print(f"[{el()}s] jobs (words in anchorable events): {len(jobs)}", flush=True)

def pull(j):
    t = j['t']; start = t - 7200; end = t                # 2h window up to t
    d = get(f"{API}/series/{j['series']}/markets/{j['ticker']}/candlesticks?start_ts={start}&end_ts={end}&period_interval=1")
    cs = []
    if d:
        for c in d.get('candlesticks', []):
            yb = (c.get('yes_bid') or {}).get('close_dollars'); ya = (c.get('yes_ask') or {}).get('close_dollars')
            if yb not in (None, '') and ya not in (None, ''):
                b = float(yb); a = float(ya)
                if 0 < b <= a < 1.0001: cs.append((c['end_period_ts'], b, a))
    cs.sort()
    def at(q):
        best = None
        for ts, b, a in cs:
            if ts <= q: best = (b, a)
            else: break
        return best
    ba10 = at(t - 600); ba20 = at(t - 1200)
    time.sleep(0.05)
    return {'ticker': j['ticker'], 'event': j['event'], 'win': j['win'], 'vol': j['vol'],
            'last10': j['last10'], 'last20': j['last20'],
            'bid10': ba10[0] if ba10 else None, 'ask10': ba10[1] if ba10 else None,
            'bid20': ba20[0] if ba20 else None, 'ask20': ba20[1] if ba20 else None}

OUT = r"C:\Users\Riyan\Downloads\kalshi_quote_raw.json"
out = []; done = [0]; lock = threading.Lock(); N = len(jobs)
with ThreadPoolExecutor(max_workers=4) as ex:
    for f in as_completed([ex.submit(pull, j) for j in jobs]):
        r = f.result()
        with lock:
            done[0] += 1; out.append(r)
            if done[0] % 200 == 0 or done[0] == N:
                e = max(time.time() - START, 1); rate = done[0] / e
                eta = int((N - done[0]) / rate) if rate > 0 else 0
                print(f"[{el()}s] {done[0]}/{N} | {rate:.1f}/s | ETA {eta}s", flush=True)
                if done[0] % 1000 == 0: json.dump(out, open(OUT, "w"))
json.dump(out, open(OUT, "w"))
print(f"[{el()}s] DONE: {len(out)} words with YES bid/ask at t-10 & t-20", flush=True)
