# Quapybara Strategy Research Project — Master Plan

**Goal:** Design more complex / higher-quality trading strategies for the
Quapybara platform, write a detailed report per algorithm idea, and backtest
each rigorously with the platform's own backtest engine. Push all reports +
figures to this output port when complete.

**Hard constraint:** ZERO edits or commits to the Quapybara repo
(`PROJECTS/Quapybara/`). Every backtest runs from throwaway scripts under
`/tmp` that import the platform's `backtest.engine` **read-only**. Outputs land
only in this output-port repo.

---

## 0. Platform recap (what we build on)

- Strategy contract: `main(data) -> np.ndarray` returning **portfolio weights**
  (long-only, each ≥ 0, sum ≤ 1; the shortfall is cash).
- `data` exposes rolling numpy buffers per field (73 fields: market, fundamental,
  FRED macro, news) + the `qp` helper library (36 helpers: rank, zscore,
  neutralize, momentum, vol, risk_parity, optimize, market_regime, group_rank …).
- Backtest engine (`backtest/engine.run_backtest_async`): **daily bars only**
  (intraday rejected). Metrics include sharpe, sortino, calmar,
  **deflated_sharpe** (multiple-testing adjusted via `n_trials`), max drawdown +
  duration, turnover, profit_factor, win_rate, total/annualized return, alpha,
  beta, information_ratio, r_squared, fees. Supports `train_frac` (IS/OOS split)
  and `n_trials`.
- Costs live in one place: `data_config.fee_config`
  (commission_pct, slippage_bps, sell_tax_pct).

---

## 1. Methodology (statistical protocol)

1. **Daily bars only.** No sub-day tickers (engine enforces).
2. **Lock parameters once.** Each strategy's parameters are chosen/frozen using
   data through **~end of 2019** and never touched again. Every later year is
   therefore genuine out-of-sample.
3. **Rolling 1-year OOS windows.** Evaluate on test years **2020, 2021, 2022,
   2023, 2024** (each ~252 bars).
4. **Multiple big universes** (see §3). Verdict is drawn from the **distribution
   across (year × universe) cells**, never a single lucky year — 1-year windows
   are noisy.
5. **Costs always on.** Report turnover and fee drag; sensitivity to costs.
6. **Deflated Sharpe with honest `n_trials`** = number of parameter variants we
   actually tried, to penalize multiple testing.
7. **Survivorship-bias disclosure.** yfinance lacks delisted names → results are
   optimistic on the upside; stated in every report.
8. **Benchmark** each strategy vs equal-weight of its own universe and vs SPY.

---

## 2. Step 0 — Look-ahead verification (gate for Phase C)

Before trusting any fundamental/news field we must confirm whether the data
source serves **point-in-time** values or a **current snapshot** (which would
leak future info into the past).

- FRED macro: genuine historical revisions → assumed safe.
- yfinance fundamentals (eps, margins, analyst_rating, …): suspected
  current-snapshot → **must verify**. Probe the engine's field history for a few
  tickers across dates; if values are flat/identical regardless of the bar date,
  they are snapshots → **Phase C fundamental factors are disqualified** (or
  restricted to lagged, clearly-historical fields only).
- Deliverable: `STEP0_lookahead.md` with the verdict + evidence.

---

## 3. Universes (big, liquid)

- **U1 — US large-cap broad** (~150–300 liquid names, multi-sector).
- **U2 — Nasdaq-100-style tech/growth** (~90–100 names).
- **U3 — Multi-sector balanced** (sector-diversified subset).
- **U4 — KR blue-chip** (Korean large-cap, if data available via yfinance `.KS`).

Ticker lists are hardcoded in the harness (no external files fetched at runtime).
Downloads are cached under `/tmp` so re-runs are cheap.

---

## 4. Strategy shortlist

### Phase A — price / volume (no fundamentals; do first)
- **A1 Cross-sectional multi-factor blend** — rank-combine momentum + low-vol +
  short-term reversal, z-scored, top-k long.
- **A2 Residual (idiosyncratic) momentum** — momentum on market-beta-neutralized
  returns.
- **A3 Volatility-regime switch** — `market_regime` gates between momentum
  (calm) and defensive/low-vol (stress).
- **A4 Risk-parity / min-variance** — `risk_parity` / `optimize` on the universe.
- **A5 Adaptive factor allocation** — weight A1's factors by their recent IC.

### Phase B — macro overlay
- **B1 Dual-momentum + macro gate** — absolute+relative momentum, de-risk when
  yield-spread / fed-funds signal stress.

### Phase C — fundamentals / news (only if Step 0 passes)
- **C1 Quality-value** — ROE / margins / low debt + cheap valuation.
- **C2 News-sentiment tilt** — tilt a base portfolio by `news_sentiment`.

---

## 5. Per-strategy report template (11 sections)

1. Title & one-line thesis
2. Economic rationale
3. Signal construction (fields + qp helpers used)
4. Full `main(data)` code
5. Parameters & how they were locked (through 2019)
6. Universes tested
7. Walk-forward results table (year × universe: return, sharpe, maxDD, turnover)
8. Aggregate verdict (distribution, deflated sharpe, vs benchmark)
9. Cost sensitivity
10. Failure modes & survivorship-bias caveat
11. Verdict: keep / discard / iterate

---

## 6. Harness (in `/tmp`, read-only import)

- `/tmp/qp_research/harness.py`: imports `backtest.engine` from the Quapybara
  repo path, defines universes, cached yfinance loader, walk-forward loop,
  result tabulation + matplotlib figures.
- One driver script per strategy. Figures + tables copied into this repo.
- **No writes** anywhere inside `PROJECTS/Quapybara/`.

---

## 7. Execution order (relay steps)

1. Step 0 — look-ahead verification → `STEP0_lookahead.md`.
2. Build harness + smoke-test on one strategy/universe/year.
3. A1 → A2 → A3 → A4 → A5 (report + walk-forward each).
4. B1.
5. C1, C2 (only if Step 0 passes).
6. Cross-strategy summary report + combined figures.
7. Final push: all `*.md` + `*.png` together to this output port.

Progress is committed here incrementally per relay step; the full figure set is
pushed together at the end.
