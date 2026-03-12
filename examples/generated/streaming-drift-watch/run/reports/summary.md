# icu_bed_stress

- backend_selected: `river_snarimax`
- candidate_backends: `river_snarimax`
- artifact_count: `10`
- latest_observed: `93.4200`
- projected_end: `94.6904`

Compared 1 backend(s) and routed the series to 'river_snarimax'. Exported CSV, chart, card, markdown, and JSON artifacts.

## Intervals

- enabled: `False`
- method: `residual_heuristic`
- levels: `80, 90`

## Leaderboard

| backend_id | mae | rmse | mape | smape | coverage_80 | avg_width_80 | wnc_80 | coverage_90 | avg_width_90 | wnc_90 | backtest_horizon |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| river_snarimax | 7.47417 | 8.4898 | 8.44956 | 8.00093 | 1 | 30.0485 | 3.01567 | 1 | 38.5664 | 2.34962 | 14 |

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
