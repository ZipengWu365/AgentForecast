# Reproduction

## Install from source

```bash
python -m pip install .
python -m pytest
```

## Build and install the local wheel

```bash
python -m pip wheel . -w dist --no-deps
python -m pip install dist/agentforecast-1.8.0-py3-none-any.whl
python scripts/smoke_test_wheel.py
```

## Minimal quickstart

```bash
python -m agentforecast.cli shoot sales --outdir demo
```

## Build docs and gallery

```bash
python scripts/build_demo_gallery.py
```

## Strict benchmark reproduction

```python
import pandas as pd

from agentforecast import OnlineForecaster

df = pd.read_csv("agentforecast/package_data/public_examples/airline-passengers.csv")
forecaster = OnlineForecaster(backend="stats_ets", strict_backend=True)
result = forecaster.backtest(df, horizon=12)
print(result["resolution"])
```
