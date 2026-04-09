# sales

- backend_selected: `stats_ets`
- candidate_backends: `stats_ets, ml_ridge, seasonal_naive, stats_arima, naive, moving_average, stream_ewm`
- artifact_count: `11`
- requested_backend: `arena`
- resolved_backend: `stats_ets`
- support_tier: `reviewed`
- latest_observed: `164.0400`
- projected_end: `168.9933`

Compared 7 backend(s) and routed the series to 'stats_ets'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stats_ets | 2.66825 | 3.34 | 1.66006 | 1.66291 | 1 | 23.6706 | 6.83812 | 1 | 30.3805 | 5.32782 | 14 |
| ml_ridge | 3.33187 | 4.0847 | 2.06825 | 2.09282 | 1 | 25.0098 | 6.47195 | 1 | 32.0994 | 5.04252 | 14 |
| seasonal_naive | 4.40929 | 5.81541 | 2.72586 | 2.78914 | 1 | 32.5363 | 4.97482 | 1 | 41.7595 | 3.87606 | 14 |
| stats_arima | 6.71996 | 8.42389 | 4.26758 | 4.15883 | 1 | 65.4267 | 2.47395 | 1 | 83.9735 | 1.92754 | 14 |
| naive | 7.06929 | 8.14532 | 4.32582 | 4.38346 | 1 | 65.2027 | 2.48245 | 1 | 83.6859 | 1.93416 | 14 |
| moving_average | 7.38337 | 8.44123 | 4.50356 | 4.58144 | 1 | 65.2027 | 2.48245 | 1 | 83.6859 | 1.93416 | 14 |
| stream_ewm | 8.83558 | 10.3431 | 5.32818 | 5.50834 | 1 | 65.2244 | 2.48162 | 1 | 83.7138 | 1.93352 | 14 |

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
