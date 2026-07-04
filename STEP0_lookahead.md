# Step 0 — Look-Ahead Verification

**Question:** Which Quapybara data fields serve genuine *point-in-time* history
(safe for backtesting) vs. a *current snapshot* repeated across all past bars
(look-ahead bias)?

**Method:** Read the `fetch_history()` implementation of every data source in
`PROJECTS/Quapybara/data/sources/` (read-only; no code changed).

---

## Findings

### ✅ SAFE — genuine per-bar history

| Field group | Source | Evidence |
|---|---|---|
| OHLCV: open, high, low, close, volume | `yfinance_source.py` | `yf.download()` returns real daily bars per date. |
| day_change_pct | `yfinance_source.py` | Line 295–296: "computed from historical close, not as a fundamental." |
| Macro (FRED): treasury_2y/10y/30y, yield_spread_10y2y, fed_funds_rate, cpi_yoy, unemployment_rate, … | `fred_source.py` | `fetch_history` calls `fred.get_series(observation_start=…, observation_end=…)` (line 182) — genuine dated observations. Point-in-time lookup uses "closest observation at or before target_date." |

### ❌ LOOK-AHEAD — current snapshot repeated across all bars

| Field group | Source | Evidence |
|---|---|---|
| market_cap, pe_ratio, week52_high, week52_low | `yfinance_source.py` | Line 405: *"For fundamentals: no per-bar history, repeat current value."* |
| All 30 fundamentals: eps, revenue, gross/operating/net_margin, debt_to_equity, ROE, analyst_target_price, analyst_rating, short_ratio, float_shares, institutional_pct, earnings/ex-div dates, … | `yfinance_extended.py` | Line 108 docstring: *"Fundamentals have no per-bar history — repeat current value across all bars."* Line 139: `result[field_name][i, :] = val  # repeat across all bars`. |

### ⚠️ NOT BACKTESTABLE — no history available

| Field group | Source | Evidence |
|---|---|---|
| news_count, news_sentiment | `news_source.py` | Line 165: *"Free tier does not support historical queries beyond 1 month."* |

---

## Caveat on FRED (safe, but note)

FRED `get_series` returns the **latest revised** values (not the ALFRED
real-time vintage), and macro series carry a **publication lag** (e.g. CPI for
month *M* is released mid-*M+1*). So a macro value dated inside a bar may not
have been *published* by that bar's date. This is a mild, well-understood bias
— far smaller than the fundamentals snapshot problem — and macro fields change
slowly. **Verdict: usable for a coarse macro gate**, with the revision/lag
caveat disclosed in every report that uses it.

---

## Impact on the project plan

- **Phase A (A1–A5, price/volume): GO.** OHLCV + volume are clean. This is the
  bulk of the work and is fully backtestable.
- **Phase B (B1, dual-momentum + macro gate): GO** using FRED fields, with the
  revision/lag caveat.
- **Phase C (C1 quality-value, C2 news-sentiment): DISQUALIFIED for honest
  backtesting.**
  - C1 depends on fundamentals that are current-snapshot → severe look-ahead
    (e.g. today's ROE/margins applied to 2020 bars). Any backtest would be
    fiction.
  - C2 depends on news history that the source cannot provide beyond ~1 month.
  - These ideas remain **conceptually valid**; they would require a
    point-in-time fundamentals vendor (e.g. Sharadar/Compustat PIT) or ALFRED
    vintages + a historical news archive. We will describe them in the final
    report as "designed but not backtestable with current data sources" rather
    than publish misleading numbers.

**Net:** proceed with A1–A5 and B1. Skip Phase C backtests; document why.
