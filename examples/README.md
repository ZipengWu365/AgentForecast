# Examples

This folder is organized around the easiest paths for first-time users.

## Base quickstart

```bash
python -m agentforecast.cli shoot sales --outdir demo
```

## Compare backends on one dataset

```bash
python -m agentforecast.cli compare-dataset gold --backends naive,stats_arima,ml_ridge,stream_ewm --outdir arena
```

## Time series to regression demo

```bash
python -m agentforecast.cli run-case time-series-regression-lab --outdir regression_case
python -m agentforecast.cli forecast-dataset gold-exogenous --backend ml_ridge --lag-points 1,2,3,7,14,28 --tsfresh --outdir regression_features
```

## Streaming demo

```bash
python -m agentforecast.cli run-case icu-bed-stress-watch --outdir demo
```

## Hosted gallery demo

```bash
python -m agentforecast.cli demo-gallery --outdir public_gallery/demo_runs --site-dir public_gallery/site
```

## Beginner notebooks

- `forecast_your_csv.ipynb`
- `url_to_pack.ipynb`
- `messy_csv_cleanup.ipynb`
- `compare_methods_on_one_series.ipynb`
- `gold_price_with_exogenous_csv.ipynb`
- `choose_backend_by_strategy.ipynb`
- `when_ridge_beats_transformer.ipynb`
- `time_series_to_regression.md`

## Cross-disciplinary notebooks

- `icu_bed_stress_watch.ipynb`
- `beamline_drift_watch.ipynb`
- `air_quality_smoke_watch.ipynb`
- `grid_heatwave_stress_watch.ipynb`
- `river_flood_risk_watch.ipynb`
- `outpatient_no_show_watch.ipynb`
