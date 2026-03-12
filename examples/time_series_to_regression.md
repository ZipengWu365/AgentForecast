# Time Series To Regression

`agentforecast` can turn a single series into a supervised regression matrix without making you hand-build lag columns.

## What you can control

- `--lag-points`: choose exact delay taps such as `1,2,7,14,28`
- `--lag-step` and `--lag-count`: generate evenly spaced delay features
- `--rolling-windows`: choose rolling summary windows
- `--disable-calendar`: remove calendar-derived regressors
- `--tsfresh`: add a compact optional tsfresh descriptor block
- `--tsfresh-window`: set how much history each tsfresh block sees

## CLI example

```bash
python -m agentforecast.cli forecast-dataset gold-exogenous \
  --backend ml_ridge \
  --lag-points 1,2,3,7,14,28 \
  --lag-step 7 \
  --lag-count 6 \
  --rolling-windows 3,7,14,28 \
  --tsfresh \
  --tsfresh-window 28 \
  --outdir regression_case
```

## Python example

```python
from agentforecast import FeatureSpec, forecast_dataset

result = forecast_dataset(
    "gold-exogenous",
    backend="ml_ridge",
    feature_spec=FeatureSpec(
        lag_points=(1, 2, 3, 7, 14, 28),
        lag_step=7,
        lag_count=6,
        rolling_windows=(3, 7, 14, 28),
        include_tsfresh=True,
        tsfresh_window=28,
    ),
    outdir="regression_case",
)

print(result.feature_spec)
```

## Built-in case

```bash
python -m agentforecast.cli run-case time-series-regression-lab --outdir regression_lab
```

This case compares regression-style backends over `gold-exogenous` with selected lag points, spaced delays, and optional tsfresh descriptors when `tsfresh` is installed.
