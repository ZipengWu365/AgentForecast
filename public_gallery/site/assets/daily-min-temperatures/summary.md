# daily_min_temperatures

- backend_selected: `river_snarimax`
- candidate_backends: `river_snarimax`
- artifact_count: `11`
- requested_backend: `river_snarimax`
- resolved_backend: `river_snarimax`
- support_tier: `experimental`
- latest_observed: `13.0000`
- projected_end: `13.2914`

Compared 1 backend(s) and routed the series to 'river_snarimax'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| river_snarimax | 1.19638 | 1.62944 | 9.00743 | 8.69576 | 1 | 23.5601 | 0.590586 | 1 | 30.2388 | 0.460147 | 14 |

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
