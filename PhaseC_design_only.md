# Phase C — Fundamental & News Strategies (Design-Only, NOT Backtested)

Step 0 (`STEP0_lookahead.md`) established that the two data families Phase C
depends on are **not usable for an honest backtest** on this platform:

- **Fundamentals** (eps, revenue, margins, ROE, debt_to_equity, analyst_rating,
  pe_ratio, market_cap, …) are served as a **current snapshot repeated across
  all historical bars** (`yfinance_extended.fetch_history`: *"repeat current
  value across all bars"*). Backtesting on them would apply *today's* financials
  to 2020 prices — pure look-ahead.
- **News** (news_count, news_sentiment) has **no history beyond ~1 month** on the
  free tier, so multi-year backtests are impossible.

Publishing return numbers for these would be misleading, so we **design the
strategies here but do not backtest them.** Each becomes runnable the moment a
point-in-time data source is connected.

---

## C1 — Quality-Value Composite

**Thesis.** Own companies that are both *high quality* (profitable, low
leverage) and *cheap* (low valuation) — the Novy-Marx profitability + Fama-French
value combination, which historically beats either sleeve alone.

**Signal (once PIT fundamentals exist).**
- Quality = z(ROE) + z(gross_margin) − z(debt_to_equity)
- Value   = −z(pe_ratio)  (or z(earnings_yield), z(fcf_yield))
- score   = 0.5·Quality + 0.5·Value, cross-sectional
- hold top quartile, risk-parity sized (A4), monthly rebalance.

**Data requirement.** Point-in-time fundamentals with the correct *as-reported*
date and lag (10-K/10-Q filing dates). Vendors: Sharadar SF1, Compustat PIT.
Without them, the snapshot bias fabricates the entire edge.

---

## C2 — News-Sentiment Tilt

**Thesis.** Tilt a base momentum/quality book toward names with improving news
sentiment; sentiment is a fast, orthogonal signal that leads price on a
days-to-weeks horizon.

**Signal (once a news archive exists).**
- base_w = A2 residual-momentum weights
- tilt   = 1 + λ·zscore(ts_delta(news_sentiment, 5))   (λ ≈ 0.3)
- weights = normalize(base_w · clip(tilt, 0.5, 1.5))

**Data requirement.** A multi-year historical news-sentiment archive with
timestamps (RavenPack, Tiingo/AlphaVantage news history, or an LLM-scored
archive). The free news source cannot backfill it.

---

## Recommendation
Both C1 and C2 are sound designs and worth revisiting **only after** a
point-in-time fundamentals feed and a historical news archive are wired into
Quapybara's data sources. Until then, Phase A/B price-and-trend strategies are
the only ones this platform can validate honestly.
