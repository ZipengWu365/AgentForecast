# github_breakout

- backend_selected: `ml_ridge`
- candidate_backends: `ml_ridge, stream_ewm, stats_ets, stats_arima, naive, seasonal_naive, moving_average`
- artifact_count: `10`
- latest_observed: `14643.0000`
- projected_end: `20203.1274`

Compared 7 backend(s) and routed the series to 'ml_ridge'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Leaderboard

| backend_id | mae | rmse | mape | smape | backtest_horizon |
| --- | --- | --- | --- | --- | --- |
| ml_ridge | 50.1214 | 64.2571 | 0.371262 | 0.370199 | 24 |
| stream_ewm | 150.863 | 182.507 | 1.1279 | 1.13658 | 24 |
| stats_ets | 362.058 | 425.4 | 2.70865 | 2.75784 | 24 |
| stats_arima | 443.312 | 535.669 | 3.29876 | 3.37621 | 24 |
| naive | 1961.88 | 2253.66 | 14.7351 | 16.2564 | 24 |
| seasonal_naive | 2080.42 | 2288.68 | 15.7971 | 17.385 | 24 |
| moving_average | 2368.3 | 2615.13 | 17.9462 | 20.0562 | 24 |

## Artifacts
- `data/history.csv`
- `data/forecast.csv`
- `data/leaderboard.csv`
- `plots/forecast.png`
- `plots/forecast_card.png`
- `plots/backend_comparison.png`
- `plots/leaderboard_card.png`
- `plots/winner_vs_runnerup_delta.png`
- `reports/summary.md`
- `meta/metadata.json`
