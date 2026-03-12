# Examples

`agentforecast` now ships with a tutorial-style examples hub instead of a thin command list.

Every curated example has:

- a runnable source script under `examples/scripts/`
- a real generated pack under `examples/generated/`
- a static tutorial page under `examples/site/`
- copied plots, cards, CSV, markdown, and JSON artifacts

## Generate The Full Hub

```bash
python -m agentforecast.cli demo-examples --outdir examples/generated --site-dir examples/site
```

Open:

```text
examples/site/index.html
```

## Curated Examples

| Example id | Focus | Script |
| --- | --- | --- |
| `first-forecast-pack` | first end-to-end forecast pack with the stable artifact contract | `examples/scripts/first_forecast_pack.py` |
| `backend-arena` | backend comparison and leaderboard-driven model choice | `examples/scripts/backend_arena.py` |
| `time-series-as-regression` | lag points, spaced delays, rolling windows, optional tsfresh descriptors | `examples/scripts/time_series_as_regression.py` |
| `calibrated-intervals` | conformal prediction intervals and interval diagnostics | `examples/scripts/calibrated_intervals.py` |
| `streaming-drift-watch` | streaming forecasting and drift monitoring artifacts | `examples/scripts/streaming_drift_watch.py` |

## Useful Commands

List the curated examples:

```bash
python -m agentforecast.cli list-examples
```

Rebuild the site from existing generated runs:

```bash
python -m agentforecast.cli build-examples --runs-root examples/generated --site-dir examples/site
```

Generate only a subset:

```bash
python -m agentforecast.cli demo-examples --examples first-forecast-pack,time-series-as-regression --outdir examples/generated --site-dir examples/site
```

## Direct Commands

Quick onboarding:

```bash
python -m agentforecast.cli shoot sales --outdir examples/generated/first-forecast-pack
```

Backend arena:

```bash
python -m agentforecast.cli compare-dataset gold --backends naive,moving_average,stats_arima,stats_ets,ml_ridge,stream_ewm --outdir examples/generated/backend-arena
```

Time series as regression:

```bash
python -m agentforecast.cli forecast-dataset gold-exogenous --backend ml_ridge --lag-points 1,2,3,7,14,28 --lag-step 7 --lag-count 4 --rolling-windows 3,7,14,28 --outdir examples/generated/time-series-as-regression
```

Conformal intervals:

```bash
python -m agentforecast.cli forecast-dataset sales --backend stream_ewm --conformal --conformal-method rolling_residual --levels 80,90,95 --calibration-window 60 --warmup-min 10 --outdir examples/generated/calibrated-intervals
```

Streaming watch:

```bash
python -m agentforecast.cli forecast-stream agentforecast/package_data/datasets/icu_bed_stress.csv --backend stream_ewm --horizon 14 --outdir examples/generated/streaming-drift-watch
```

## Related Material

- `time_series_to_regression.md`
- `examples/scripts/`
- `examples/generated/`
- `examples/site/`
