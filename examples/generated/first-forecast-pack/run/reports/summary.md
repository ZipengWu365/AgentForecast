# monthly_car_sales

- backend_selected: `stats_ets`
- candidate_backends: `stats_ets, ml_ridge, seasonal_naive, moving_average, naive, stream_ewm`
- artifact_count: `10`
- latest_observed: `14577.0000`
- projected_end: `17096.3906`

Compared 6 backend(s) and routed the series to 'stats_ets'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stats_ets | 1325.07 | 1691.22 | 7.21191 | 7.494 | 1 | 10260.4 | 1.77655 | 1 | 13169 | 1.38417 | 12 |
| ml_ridge | 1706.53 | 2073.44 | 9.16454 | 8.97637 | 1 | 12559.1 | 1.45139 | 1 | 16119.3 | 1.13083 | 12 |
| seasonal_naive | 1959.5 | 2290.83 | 10.8324 | 11.6671 | 1 | 10746.5 | 1.6962 | 1 | 13792.9 | 1.32157 | 12 |
| moving_average | 3567.9 | 4479.06 | 17.8548 | 19.7429 | 1 | 26157.6 | 0.696859 | 1 | 33572.6 | 0.542948 | 12 |
| naive | 4599 | 5865.37 | 22.2688 | 26.5965 | 0.916667 | 26157.6 | 0.638787 | 1 | 33572.6 | 0.542948 | 12 |
| stream_ewm | 5123.31 | 6107.27 | 25.693 | 30.5339 | 0.916667 | 25988.4 | 0.642946 | 1 | 33355.4 | 0.546483 | 12 |

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
