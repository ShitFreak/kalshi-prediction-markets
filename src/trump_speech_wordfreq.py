import re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import Counter

# ── Read file ─────────────────────────────────────────────────────────────────
with open(r"C:\Users\Riyan\Downloads\Speaker 1 (0000).txt", encoding="utf-8") as f:
    raw = f.read()

# ── Extract ONLY Trump's spoken lines ─────────────────────────────────────────
# Keep text that follows "President Trump" speaker labels, remove other speakers
# Strategy: split on speaker tags, keep Trump's chunks
chunks = re.split(r'\n(?:Curt Cignetti|Charlie Becker|Jamari Sharpe|Group|Speaker 1)\s*\([^)]*\):\s*\n', raw)
trump_text = ""
for chunk in chunks:
    # Remove timestamp lines like (01:47) and inaudible markers
    cleaned = re.sub(r'\(\d+:\d+\)', '', chunk)
    cleaned = re.sub(r'\[inaudible[^\]]*\]', '', cleaned)
    # Remove speaker header lines
    cleaned = re.sub(r'President Trump\s*\([^)]*\):', '', cleaned)
    trump_text += " " + cleaned

# ── Tokenise ──────────────────────────────────────────────────────────────────
words_raw = re.findall(r"[a-zA-Z']+", trump_text.lower())

# ── Stop-word list (articles, prepositions, pronouns, aux-verbs, fillers) ─────
STOP = {
    # articles / determiners
    "a","an","the","this","that","these","those","some","any","all","both",
    "each","every","no","much","many","more","most","other","such","what",
    "which","whose","who","whom","how","when","where","why","few","own",
    # pronouns
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","he","him","his","himself","she","her","hers","herself","it",
    "its","itself","they","them","their","theirs","themselves","one",
    # prepositions / conjunctions
    "in","on","at","by","for","with","about","against","between","through",
    "during","before","after","above","below","to","from","up","down","of",
    "off","over","under","again","further","then","once","here","there",
    "and","but","or","nor","so","yet","both","either","neither","not",
    "because","as","until","while","although","if","since","than","though",
    # aux verbs / common verbs
    "is","was","are","were","be","been","being","have","has","had","having",
    "do","does","did","will","would","could","should","may","might","shall",
    "can","need","dare","ought","used","said","go","going","get","got",
    "let","say","know","think","come","take","make","see","look","want",
    "keep","put","give","tell","show","call","try","ask","seem","feel",
    "become","leave","find","like","use","turn","move","live","stand",
    "run","play","win","won","lose","lost","just","done","went","came",
    "believe","talk","mean","happen","help","start","end","hold","bring",
    "speak","work","build","watch",
    # filler / common speech words
    "okay","ok","yeah","yes","sir","well","right","now","really","very",
    "so","too","also","even","still","already","always","never","often",
    "maybe","probably","actually","certainly","almost","quite","enough",
    "just","only","back","away","around","out","into","onto","upon",
    "hey","oh","wow","huh","ah","um","uh","gonna","gotta","lotta","kinda",
    "thing","things","way","ways","kind","sort","lot","lots","bit","bit",
    "little","big","small","long","short","old","new","first","last",
    "same","different","next","another","second","third","few","certain",
    "good","great","nice","bad","hard","easy","true","false","real","sure",
    "number","time","times","day","days","year","years","week","weeks",
    "today","yesterday","tomorrow","ago","later","soon","ever","never",
    "something","anything","everything","nothing","someone","anyone",
    "everyone","nobody","somebody","anyone","s","re","ve","m","d","ll",
    "t","n","don","didn","wasn","aren","can't","won't","he's","i've",
    "they're","that's","it's","i'm","we're","you're","he'd","we'd",
    "guys","people","man","men","guy","person","team","teams","coach",
    # too generic for this context
    "point","points","place","down","line","side","hand","head","face",
    "came","went","made","took","gave","got","put","set","told","kept",
    "said","told","wanted","needed","liked","thought","knew","felt",
    "could","would","should","might","must","shall","will","may","had",
    "got","let","say","see","look","go","come","do","make","take",
    "pretty","really","very","quite","rather","somewhat","mostly",
    "together","along","ahead","behind","across","around","inside",
    "outside","front","behind","near","far","high","low",
    "able","ready","open","close","full","empty","whole","half",
    "amount","number","area","part","kind","type","form","case",
    "point","fact","idea","story","reason","result","effect","matter",
}

filtered = [w for w in words_raw if w not in STOP and len(w) > 2]

# ── Count ─────────────────────────────────────────────────────────────────────
freq = Counter(filtered)
top_n = 40
top_words, top_counts = zip(*freq.most_common(top_n))

# ── Colour-code by category ────────────────────────────────────────────────────
CATEGORIES = {
    "Football / Sports": {
        "indiana","hoosiers","football","national","championship","season",
        "quarterback","defense","offense","bowl","rose","peach","big",
        "college","game","games","score","touchdown","sacks","record",
        "winning","players","player","program","signing","nfl","training",
        "camp","lineup","halftime","quarter","victory","victories","yards",
        "passes","touchdowns","field","stadium","playoffs","undefeated",
        "title","champions","champion","champions","coaching",
    },
    "People / Names": {
        "curt","cignetti","fernando","jamari","coogan","jd","vance","doug",
        "brooke","howard","kelly","todd","jim","banks","victoria","spartz",
        "mendoza","sharpe","becker","charlie","pat","ali","muhammad",
        "trent","green","sage","steele","lutnick","rollins","burgum","wright",
        "loeffler","hassett","young","stutzman","baird","yakym","houchin",
        "begich","messmer","shreve","sonderling","greer","jamieson","ohio",
    },
    "Places / Teams": {
        "ohio","state","alabama","oregon","miami","indiana","purdue",
        "hoosiers","buckeyes","hurricanes","crimson","tide","raiders",
        "las","vegas","rose","peach","national","oval","office","white",
        "house","washington","carolina","tennessee","nashville","titans",
    },
    "Politics / Economy": {
        "iran","tariffs","tariff","nuclear","weapon","inflation","prices",
        "country","america","american","military","victory","winning",
        "world","greatest","strong","strength","border","security","deal",
        "economy","operation","election","endorsed","landslide","primary",
        "republican","patriots","insurgency","democratic","candidates",
        "trump","president","secretary","senator","representative",
    },
    "Character / Achievement": {
        "incredible","fantastic","great","amazing","legendary","special",
        "discipline","grit","determination","character","mindset","winning",
        "talent","talented","skilled","dominant","commanding","historic",
        "unbelievable","powerful","greatest","best","spectacular","elite",
        "cocky","winner","champion","proud","honor","honored","inspiration",
        "inspired","millions","future","potential","success","successful",
    },
}

def get_cat(word):
    for cat, words in CATEGORIES.items():
        if word in words:
            return cat
    return "Other"

CAT_COLORS = {
    "Football / Sports":     "#2196F3",
    "People / Names":        "#9C27B0",
    "Places / Teams":        "#FF9800",
    "Politics / Economy":    "#F44336",
    "Character / Achievement":"#4CAF50",
    "Other":                 "#607D8B",
}

bar_colors = [CAT_COLORS[get_cat(w)] for w in top_words]

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(20, 13), facecolor="#0D1117")
ax.set_facecolor("#0D1117")

bars = ax.barh(
    range(top_n), top_counts[::-1],
    color=bar_colors[::-1],
    edgecolor="none", height=0.72,
)

# Value labels
for bar, val in zip(bars, top_counts[::-1]):
    ax.text(
        val + 0.3, bar.get_y() + bar.get_height() / 2,
        str(val), va="center", ha="left",
        color="white", fontsize=9,
    )

ax.set_yticks(range(top_n))
ax.set_yticklabels(
    [w.capitalize() for w in top_words[::-1]],
    fontsize=10.5, color="white",
)
ax.set_xlabel("Frequency (occurrences)", color="#8B949E", fontsize=11)
ax.tick_params(axis="x", colors="#8B949E")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#30363D")
ax.spines["bottom"].set_color("#30363D")
ax.xaxis.set_tick_params(color="#30363D")

# Title
fig.text(
    0.5, 0.97,
    "TRUMP'S WHITE HOUSE SPEECH  -  Word Frequency Analysis",
    ha="center", fontsize=19, fontweight="bold", color="white",
)
fig.text(
    0.5, 0.935,
    "Welcoming the 2025 College Football National Champions  |  Indiana University Hoosiers\n"
    "Stop-words removed  -  meaningful nouns, adjectives & key terms only",
    ha="center", fontsize=11, color="#8B949E", linespacing=1.5,
)

# Legend
legend_patches = [
    mpatches.Patch(color=v, label=k) for k, v in CAT_COLORS.items()
]
ax.legend(
    handles=legend_patches,
    loc="lower right", fontsize=9.5,
    framealpha=0.2, labelcolor="white",
    edgecolor="#30363D", facecolor="#161B22",
)

plt.tight_layout(rect=[0, 0, 1, 0.925])
out = r"C:\Users\Riyan\Downloads\trump_speech_wordfreq.png"
plt.savefig(out, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: {out}")

# ── Print top words by category for summary ────────────────────────────────────
print("\n--- TOP WORDS BY CATEGORY ---")
by_cat = {}
for w, c in freq.most_common(100):
    cat = get_cat(w)
    by_cat.setdefault(cat, []).append((w, c))
for cat, items in by_cat.items():
    print(f"\n{cat}:")
    for w, c in items[:8]:
        print(f"  {w}: {c}")
