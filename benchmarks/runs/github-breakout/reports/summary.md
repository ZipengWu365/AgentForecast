# github_breakout

- backend_selected: `ml_ridge`
- candidate_backends: `ml_ridge, stream_ewm, stats_ets, stats_arima, naive, seasonal_naive, moving_average`
- artifact_count: `11`
- requested_backend: `arena`
- resolved_backend: `ml_ridge`
- support_tier: `reviewed`
- latest_observed: `14643.0000`
- projected_end: `20203.1274`

Compared 7 backend(s) and routed the series to 'ml_ridge'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ml_ridge | 50.1214 | 64.2571 | 0.371262 | 0.370199 | 1 | 236.856 | 53.8465 | 1 | 303.999 | 41.9537 | 24 |
| stream_ewm | 150.863 | 182.507 | 1.1279 | 1.13658 | 1 | 535.248 | 23.828 | 1 | 686.977 | 18.5652 | 24 |
| stats_ets | 362.055 | 425.397 | 2.70863 | 2.75782 | 0.708333 | 738.201 | 12.2378 | 0.833333 | 947.462 | 11.2176 | 24 |
| stats_arima | 443.312 | 535.669 | 3.29876 | 3.37621 | 0.25 | 497.038 | 6.41494 | 0.291667 | 637.935 | 5.83113 | 24 |
| naive | 1961.88 | 2253.66 | 14.7351 | 16.2564 | 1 | 4472.82 | 2.85142 | 1 | 5740.74 | 2.22164 | 24 |
| seasonal_naive | 2080.42 | 2288.68 | 15.7971 | 17.385 | 0.916667 | 4121.74 | 2.83643 | 1 | 5088.75 | 2.50629 | 24 |
| moving_average | 2368.3 | 2615.13 | 17.9462 | 20.0562 | 1 | 4472.82 | 2.85142 | 1 | 5740.74 | 2.22164 | 24 |

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
- `meta/artifact_manifest.json`
- `meta/metadata.json`
