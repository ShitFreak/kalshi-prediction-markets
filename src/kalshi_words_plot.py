import json, urllib.request, urllib.parse, collections, bisect
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

API = "https://api.elections.kalshi.com/trade-api/v2"
def get(u, tries=4):
    import time
    for t in range(tries):
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if t == tries - 1: return None
            time.sleep(0.5 * (t + 1))
    return None

# 1) which series did we use? derive from raw tickers
raw = json.load(open(r"C:\Users\Riyan\Downloads\kalshi_mention_raw.json"))
series = sorted(set(w['ticker'].split('-')[0] for w in raw))

# 2) re-enumerate to map ticker -> word (yes_sub_title)
wordmap = {}
def enum(tk):
    out = {}; cur = ''
    for _ in range(3):
        q = {'series_ticker': tk, 'status': 'settled', 'limit': '1000'}
        if cur: q['cursor'] = cur
        d = get(API + '/markets?' + urllib.parse.urlencode(q))
        if not d: break
        for m in d.get('markets', []):
            out[m['ticker']] = m.get('yes_sub_title') or ''
        cur = d.get('cursor') or ''
        if not cur: break
    return out
with ThreadPoolExecutor(max_workers=6) as ex:
    for f in as_completed([ex.submit(enum, tk) for tk in series]):
        wordmap.update(f.result())
print("word labels mapped:", len(wordmap))

# 3) recompute the 1,620 points and attach word
by_ev = collections.defaultdict(list)
for w in raw: by_ev[w['event']].append(w)
def price_at(seq, q):
    ts = [p[0] for p in seq]; i = bisect.bisect_right(ts, q) - 1
    return seq[i][1] if i >= 0 else None
BAD = ('does not qualify', 'none of', 'cancel', 'event does not')
pts = []
for ev, ws in by_ev.items():
    yj = [w['jump'] for w in ws if w['win'] == 1 and w['jump']]
    if not yj: continue
    t = min(yj); q = t - 600
    for w in ws:
        if not w['seq'] or w['seq'][0][0] > q: continue
        px = price_at(w['seq'], q)
        if px is None or not (0 < px < 1): continue
        word = wordmap.get(w['ticker'], '').strip()
        if not word or any(b in word.lower() for b in BAD): continue
        pts.append((px, w['win'], word))

# 4) aggregate by word
agg = collections.defaultdict(list)
for px, win, word in pts: agg[word].append((px, win))
rows = []
for word, lst in agg.items():
    n = len(lst)
    if n < 4: continue                      # need repetition to estimate a rate
    mp = np.mean([a[0] for a in lst]); mr = np.mean([a[1] for a in lst])
    rows.append((word, n, mp, mr, mp - mr))  # edge = implied - actual (overpriced if >0)
rows.sort(key=lambda r: -r[4])
print(f"words with >=4 appearances: {len(rows)}  (from {len(pts)} word-points)")
print("\n--- 12 MOST overpriced words ---")
for w, n, mp, mr, e in rows[:12]:
    print(f"  {w[:24]:24} n={n:3} implied {mp*100:4.0f}c  said {mr*100:4.0f}%  over {e*100:+5.0f}pp")
print("--- 8 MOST underpriced words ---")
for w, n, mp, mr, e in rows[-8:]:
    print(f"  {w[:24]:24} n={n:3} implied {mp*100:4.0f}c  said {mr*100:4.0f}%  over {e*100:+5.0f}pp")

# 5) plot: scatter of words, implied vs actual
fig, ax = plt.subplots(figsize=(11, 9))
xs = [r[2] for r in rows]; ys = [r[3] for r in rows]; ns = [r[1] for r in rows]; es = [r[4] for r in rows]
sizes = [20 + n * 6 for n in ns]
sc = ax.scatter(xs, ys, s=sizes, c=es, cmap='RdYlGn_r', vmin=-0.3, vmax=0.3, alpha=0.8, edgecolor='k', lw=0.4)
ax.plot([0, 1], [0, 1], 'k--', lw=1.5, label='fair (45°)')
plt.colorbar(sc, label='overpriced (red) -> underpriced (green)   [implied - actual]')
# label the most frequent + most mispriced
to_label = sorted(rows, key=lambda r: -(r[1] + abs(r[4]) * 40))[:26]
for w, n, mp, mr, e in to_label:
    ax.annotate(w[:16], (mp, mr), fontsize=7.5, xytext=(3, 3), textcoords='offset points')
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.grid(alpha=.3); ax.legend(loc='lower right')
ax.set_xlabel("pre-speech implied chance the word is said")
ax.set_ylabel("actual rate the word was said")
ax.set_title(f"Politician mention WORDS: implied vs actual (n={len(rows)} words, >=4 appearances each)\n"
             "below 45° = overpriced (market expects it more than it happens)", weight='bold')
out = r"C:\Users\Riyan\Downloads\kalshi_words.png"
fig.tight_layout(); fig.savefig(out, dpi=130); print("\nsaved", out)
