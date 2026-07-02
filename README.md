# Quapybara — `/backtest` Page (Code-Tab-Rewrite)

Screenshots of the rewritten standalone backtest page. It now reuses the whole
Code-tab editor (`backtest_mode=True`), so a backtest draft has the same degrees
of freedom as a live strategy — tab bar **Settings · Data Config · Custom Data ·
Strategy Code · Run**, plus an isolated draft store and Run gating.

## Settings (live-only blocks dropped — only Identity / Universe / Sim-Costs)
![settings](./bt_settings_t20260702b.png)

## Data Config
![dataconfig](./bt_dataConfig_t20260702b.png)

## Custom Data (frozen — shown but disabled, with banner)
![customdata](./bt_customData_t20260702b.png)

## Strategy Code
![code](./bt_strategyCode_t20260702c.png)

## Run sub-tab (params + results + History; Run disabled until draft saved)
![run](./bt_run_t20260702b.png)
