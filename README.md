# Kalshi Prediction-Market Mispricing

Quantitative research into pricing inefficiencies on [Kalshi](https://kalshi.com)
political and "mention" prediction markets — measuring the **favourite–longshot
bias**, mining **phrase correlation baskets** from political speeches, and ranking
contracts by a **rank-adjusted hit rate** to surface the most mispriced odds.

All data is pulled from Kalshi's **public** trade API (no credentials required).

---

## Key findings

**1. Favourite–longshot bias.** Across 33,000+ settled contracts, cheap longshots
are systematically overpriced and favourites underpriced. The bias is quantified
as the slope of profit on price:

```
β = Cov(price, profit) / Var(price)
```

| Price bucket | Avg. return |
|--------------|-------------|
| Cheap longshots (< 25¢) | **≈ −1.6%** |
| Favourites (> 75¢)      | **≈ +1.0%** |

The effect persists net of the bid–ask spread and is strongest in the broad
Politics / Economics groups. See `results/cov_var_kalshi.png` for a geometric
(variance / covariance / slope) decomposition of the bias.

**2. Phrase correlation baskets.** From 41 Trump speeches and 226 phrase markets,
pairwise **co-occurrence**, **lift**, and conditional probabilities `P(B|A)`,
`P(A|B)` are computed and filtered to *strong pairs* and **80–100 %-confidence
implication rules** (e.g. *"Obliterate" ⇒ "Oil"*, lift ≈ 2.6). See
`results/trump_phrase_correlations_*.xlsx`.

**3. Hit-rate inefficiency ranking.** For each phrase, the raw pre-speech implied
`YES%` is compared against the realised **hit rate**, then adjusted into a
**rank-weighted hit rate** with a **Brier score** for calibration. The most
mispriced phrases are ranked by the **coefficient of variation (std ÷ mean)** of
the traded `YES` price. See `results/phrase_odds_adjusted_v2.xlsx`.

---

## Repository layout

```
src/        analysis + data-pull scripts (Python)
results/    calibration plots, bias charts, and Excel workbooks of findings
data/       price-history CSVs, speech text, and small summary JSON
```

### Notable scripts
| Script | Purpose |
|--------|---------|
| `src/kalshi_bias_scan2.py`        | Pull settled markets, group by category, fit the bias per group |
| `src/cov_var_kalshi.py`           | Variance / covariance / slope visualisation of the bias |
| `src/kalshi_mention_analyze.py`   | Pre-speech (t−10 min) odds vs. realised word-say rate |
| `src/kalshi_quote_leads.py`       | Bid/ask-quote calibration at t−10 / 20 / 30 min leads |
| `src/trump_themes_chains.py`      | Thematic "bridge-word" implication chains |

---

## Running it

```bash
pip install -r requirements.txt
python src/kalshi_bias_scan2.py      # re-pulls live settled markets from the public API
python src/cov_var_kalshi.py         # regenerates the bias visualisation
```

> **Note:** scripts currently use absolute local paths (`C:\Users\...\Downloads\...`)
> for their data and output files; adjust these to a local `data/` path before
> running elsewhere. The large raw API dumps (50 MB+) are intentionally excluded
> from version control — they regenerate from the `*_pull.py` scripts.

---

## Tech

Python · NumPy · pandas · SciPy · Matplotlib · openpyxl · Kalshi public trade API
