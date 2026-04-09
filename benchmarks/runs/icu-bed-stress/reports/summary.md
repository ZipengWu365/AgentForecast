# icu_bed_stress

- backend_selected: `ml_ridge`
- candidate_backends: `ml_ridge, moving_average, seasonal_naive, stats_arima, naive, stats_ets, stream_ewm`
- artifact_count: `11`
- requested_backend: `arena`
- resolved_backend: `ml_ridge`
- support_tier: `reviewed`
- latest_observed: `93.4200`
- projected_end: `89.0699`

Compared 7 backend(s) and routed the series to 'ml_ridge'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ml_ridge | 2.72892 | 3.91303 | 3.13165 | 3.03682 | 1 | 35.0573 | 2.58481 | 1 | 44.9952 | 2.01391 | 14 |
| moving_average | 3.43071 | 4.86646 | 3.95242 | 3.79889 | 1 | 30.982 | 2.92481 | 1 | 39.7646 | 2.27882 | 14 |
| seasonal_naive | 4.94357 | 5.71633 | 5.54603 | 5.39135 | 1 | 42.4452 | 2.1349 | 1 | 54.4774 | 1.66338 | 14 |
| stats_arima | 5.93272 | 7.00893 | 6.73459 | 6.42297 | 1 | 30.9828 | 2.92473 | 1 | 39.7657 | 2.27876 | 14 |
| naive | 6.11357 | 7.16251 | 6.9345 | 6.60983 | 1 | 30.982 | 2.92481 | 1 | 39.7646 | 2.27882 | 14 |
| stats_ets | 6.6755 | 7.68419 | 7.55708 | 7.18659 | 1 | 31.2565 | 2.89913 | 1 | 40.1169 | 2.25881 | 14 |
| stream_ewm | 10.6529 | 11.9451 | 11.9962 | 11.1404 | 0.857143 | 28.7335 | 2.70316 | 1 | 36.8788 | 2.45714 | 14 |

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
