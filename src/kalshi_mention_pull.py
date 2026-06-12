import json, urllib.request, urllib.error, urllib.parse, time, threading
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
def iso2u(s): return int(datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())
def cprice(c):
    pr = c.get('price') or {}
    for k in ('close_dollars', 'mean_dollars', 'previous_dollars', 'open_dollars'):
        x = pr.get(k)
        if x not in (None, ''):
            v = float(x)
            if v > 0: return v
    yb = (c.get('yes_bid') or {}).get('close_dollars'); ya = (c.get('yes_ask') or {}).get('close_dollars')
    if yb and ya and float(yb) > 0 and float(ya) > 0: return (float(yb) + float(ya)) / 2
    return None

ser = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_series_cache.json"))
SPORT=('TNF','NFL','NBA','MLB','NHL','UFC','GAME','SOCCER','F1','WNBA','PGA','GOLF')
MEDIA=('FOX','CNN','MSNBC','ROGAN','DRAKE','PODCAST','NEWSNATION','NEWS NATION','LOVE ISL','ALLIN','ALL IN','HAYES','THE VIEW','KIMMEL','FALLON','DAILY SHOW','TAYLOR','KELCE')
POL=('TRUMP','BIDEN','HARRIS','POWELL','JPOW','FOMC','MAMDANI','STARMER','CROCKETT','BIANCO','COSTA','NEWSOM','DESANTIS','VANCE','ZELENS','PUTIN','MACRON','OBAMA','KAMALA','PRESIDENT','SENATE','CONGRESS','GOVERNOR','MAYOR','MINISTER','DEBATE','SOTU','SPEECH','PRESSER','RATE DECISION')
def cls(tk, ti):
    s = (tk + ' ' + ti).upper()
    if 'EARN' in s or 'BRK' in tk.upper() or 'BERKSHIRE' in s: return 'earnings'
    if any(w in s for w in SPORT): return 'sports'
    if any(w in s for w in POL): return 'politician'
    if any(w in s for w in MEDIA): return 'media'
    return 'other'
# MENTION-format politician series only; exclude DURATION
mser = [s['ticker'] for s in ser if s.get('category') == 'Mentions'
        and cls(s['ticker'], s.get('title') or '') == 'politician'
        and 'MENTION' in s['ticker'].upper() and 'DURATION' not in s['ticker'].upper()]
print(f"[{el()}s] politician MENTION series: {len(mser)}", flush=True)

def enum(tk):
    out = []; cur = ''
    for _ in range(3):
        q = {'series_ticker': tk, 'status': 'settled', 'limit': '1000'}
        if cur: q['cursor'] = cur
        d = get(API + '/markets?' + urllib.parse.urlencode(q))
        if not d: break
        for m in d.get('markets', []):
            if m.get('result') in ('yes', 'no') and m.get('close_time') and m.get('event_ticker'):
                out.append({'ticker': m['ticker'], 'series': tk, 'event': m['event_ticker'],
                            'close': m['close_time'], 'win': 1 if m['result'] == 'yes' else 0,
                            'vol': float(m.get('volume_fp') or 0)})
        cur = d.get('cursor') or ''
        if not cur: break
    return out
words = []
with ThreadPoolExecutor(max_workers=6) as ex:
    for f in as_completed([ex.submit(enum, tk) for tk in mser]): words += f.result()
print(f"[{el()}s] MENTION word markets: {len(words)} (est ~{int(len(words)*0.13)}s)", flush=True)

def pull(w):
    end = iso2u(w['close']); start = end - 24 * 3600
    d = get(f"{API}/series/{w['series']}/markets/{w['ticker']}/candlesticks?start_ts={start}&end_ts={end}&period_interval=1")
    raw = []
    if d:
        for c in d.get('candlesticks', []):
            v = cprice(c)
            if v is not None: raw.append((c['end_period_ts'], round(v, 4)))
    raw.sort()
    jump = None
    if w['win'] == 1:
        for ts, v in raw:
            if v >= 0.9: jump = ts; break
    comp = []; last = None
    for ts, v in raw:
        if v != last: comp.append([ts, v]); last = v
    time.sleep(0.05)
    return {'ticker': w['ticker'], 'event': w['event'], 'win': w['win'], 'vol': w['vol'], 'seq': comp, 'jump': jump}

RAW = r"C:\Users\Riyan\Downloads\kalshi_mention_raw.json"
out = []; done = [0]; lock = threading.Lock(); N = len(words)
with ThreadPoolExecutor(max_workers=4) as ex:
    for f in as_completed([ex.submit(pull, w) for w in words]):
        r = f.result()
        with lock:
            done[0] += 1; out.append(r)
            if done[0] % 200 == 0 or done[0] == N:
                e = max(time.time() - START, 1); rate = done[0] / e
                eta = int((N - done[0]) / rate) if rate > 0 else 0
                print(f"[{el()}s] candles {done[0]}/{N} | {rate:.1f}/s | ETA {eta}s", flush=True)
                if done[0] % 1000 == 0: json.dump(out, open(RAW, "w"))
json.dump(out, open(RAW, "w"))
print(f"[{el()}s] DONE: {len(out)} MENTION word candle-series saved", flush=True)
