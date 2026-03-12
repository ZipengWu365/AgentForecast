# Examples

`agentforecast` now ships with a tutorial-style examples hub instead of a thin command list.

The example hub is built from packaged real public time series, not the synthetic bundled quickstart datasets.

The website now leads with short Python API snippets, then keeps the CLI as a secondary equivalent for automation.

Every curated example has:

- a runnable source script under `examples/scripts/`
- a real generated pack under `examples/generated/`
- a static tutorial page under `examples/site/`
- copied plots, cards, CSV, markdown, and JSON artifacts

## Generate The Full Hub

```python
from agentforecast import demo_examples

demo_examples("examples/generated", "examples/site")
```

Open:

```text
examples/site/index.html
```

## Curated Examples

| Example id | Focus | Script |
| --- | --- | --- |
| `first-forecast-pack` | monthly car sales with the stable artifact contract | `examples/scripts/first_forecast_pack.py` |
| `backend-arena` | airline passengers with leaderboard-driven backend choice | `examples/scripts/backend_arena.py` |
| `time-series-as-regression` | daily temperatures reframed with lag points, delay features, rolling windows, optional tsfresh descriptors | `examples/scripts/time_series_as_regression.py` |
| `calibrated-intervals` | airline passengers with conformal prediction intervals and interval diagnostics | `examples/scripts/calibrated_intervals.py` |
| `streaming-drift-watch` | daily temperatures with streaming and drift monitoring artifacts | `examples/scripts/streaming_drift_watch.py` |

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

## Python-First Pattern

```python
import pandas as pd

from agentforecast import forecast_dataframe

df = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv")
result = forecast_dataframe(df, name="monthly_car_sales", horizon=12, strategy="fast", outdir="demo")
print(result.summary["headline"])
```

## CLI Equivalents

Quick onboarding:

```bash
python -m agentforecast.cli forecast-csv agentforecast/package_data/public_examples/monthly_car_sales.csv --horizon 12 --outdir examples/generated/first-forecast-pack
```

Backend arena:

```bash
python -m agentforecast.cli compare-csv agentforecast/package_data/public_examples/airline_passengers.csv --backends naive,moving_average,stats_arima,stats_ets,ml_ridge,stream_ewm --horizon 12 --outdir examples/generated/backend-arena
```

Time series as regression:

```bash
python -m agentforecast.cli forecast-csv agentforecast/package_data/public_examples/daily_min_temperatures.csv --backend ml_ridge --lag-points 1,2,3,7,14,28 --lag-step 7 --lag-count 4 --rolling-windows 3,7,14,28 --outdir examples/generated/time-series-as-regression
```

Conformal intervals:

```bash
python -m agentforecast.cli forecast-csv agentforecast/package_data/public_examples/airline_passengers.csv --backend stream_ewm --conformal --conformal-method rolling_residual --levels 80,90,95 --calibration-window 60 --warmup-min 10 --horizon 12 --outdir examples/generated/calibrated-intervals
```

Streaming watch:

```bash
python -m agentforecast.cli forecast-stream agentforecast/package_data/public_examples/daily_min_temperatures.csv --backend stream_ewm --horizon 14 --outdir examples/generated/streaming-drift-watch
```

## Related Material

- `time_series_to_regression.md`
- `examples/scripts/`
- `examples/generated/`
- `examples/site/`
