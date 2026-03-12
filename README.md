<p align="center">
  <img src="assets/agentforecast-mark.svg" alt="agentforecast logo" width="88" />
</p>

<h1 align="center">agentforecast</h1>

<p align="center"><strong>Forecast any time series with classical, tabular, streaming, and optional adapter backends, then publish charts, CSV, cards, markdown, and JSON in one command.</strong></p>

<p align="center">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-1f2937?style=flat-square"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-2F6BFF?style=flat-square">
  <img alt="GitHub Pages" src="https://img.shields.io/badge/gallery-GitHub%20Pages-FFC83D?style=flat-square&logo=github">
  <img alt="Author" src="https://img.shields.io/badge/author-Zipeng%20Wu-1F2937?style=flat-square">
  <img alt="Affiliation" src="https://img.shields.io/badge/The%20University%20of%20Birmingham-research-9C1C40?style=flat-square">
</p>

<p align="center">
  <a href="mailto:zxw365@student.bham.ac.uk">zxw365@student.bham.ac.uk</a>
</p>

<p align="center">
  <img src="assets/hosted_gallery_preview.png" alt="agentforecast hosted gallery preview" width="940" />
</p>

`agentforecast` is a **multi-backend, agent-friendly forecast-to-publish layer**.

It does three jobs at once:

1. routes one series through a small forecasting surface
2. compares or selects backends such as **statsmodels**, **scikit-learn/XGBoost**, **streaming online models**, and optional adapters for **StatsForecast / MLForecast / River / AutoGluon / TabPFN**
3. exports a **forecast pack** that is ready for humans, scripts, and agents

## Author

- **Zipeng Wu**
- **The University of Birmingham**
- **Email:** [zxw365@student.bham.ac.uk](mailto:zxw365@student.bham.ac.uk)

## Why use it

Use `agentforecast` when you want:

- **one command, many backends**
- **backend=auto** instead of stitching framework-specific APIs together
- **publishable artifacts** instead of only a NumPy array
- **agent-friendly JSON outputs** with stable fields and schema refs
- **streaming / online learning** paths without changing the outer product surface
- **hosted gallery output** that can be pushed to GitHub Pages or any static host

Do **not** use it when your main need is:

- the deepest estimator zoo
- the heaviest probabilistic research stack
- huge distributed training
- a full replacement for a specialized forecasting framework

## 60-second quickstart

Lean path:

```bash
python -m pip install .
python -m agentforecast.cli shoot sales --outdir demo
python -c "from pathlib import Path; print((Path('demo')/'sales'/'reports'/'summary.md').read_text(encoding='utf-8'))"
```

Local wheel path:

```bash
python -m pip install dist/agentforecast-1.7.0-py3-none-any.whl
```

Hosted gallery path:

```bash
python -m agentforecast.cli demo-gallery --outdir demo_gallery_runs --site-dir public_gallery/site
python -c "from pathlib import Path; print((Path('public_gallery')/'site'/'index.html').resolve())"
```

Multi-backend compare path:

```bash
python -m pip install "agentforecast[stats,ml]"
python -m agentforecast.cli compare-dataset gold --backends naive,stats_arima,ml_ridge,ml_xgboost --outdir arena
```

Streaming path:

```bash
python -m agentforecast.cli forecast-stream agentforecast/package_data/datasets/icu_bed_stress.csv --backend stream_ewm --outdir stream_demo
```


## Why this version is safer

- base quickstart no longer depends on `tabulate`
- `python -m agentforecast.cli ...` remains the most distribution-safe copy-paste path
- root OSS trust files are included in the repository snapshot
- internal demo benchmarks are explicitly separated from external benchmark hubs

## The simplest mental model

`agentforecast` is a **forecast camera**.

You point it at:

- a bundled dataset id
- a built-in case id
- a local CSV
- a directory of CSV files
- a CSV URL

and it returns a pack.

```bash
agentforecast shoot sales
agentforecast shoot github-breakout-radar
agentforecast shoot ./my_series.csv
agentforecast shoot ./many_csvs/
agentforecast shoot https://example.com/series.csv
```

There is also a vibe-coding alias:

```bash
agentforecast vibe sales
```

## What comes out

A typical pack contains:

```text
outputs/<series-name>/
  data/
    history.csv
    forecast.csv
    leaderboard.csv
  plots/
    forecast.png
    forecast_card.png
    backend_comparison.png
    leaderboard_card.png
    winner_vs_runnerup_delta.png
    drift_alert_card.png   # streaming runs
  reports/
    summary.md
  meta/
    metadata.json
```

The JSON is structured for agents and scripts. Core fields include:

- `kind`
- `schema_version`
- `schema_ref`
- `tool_version`
- `backend_selected`
- `candidate_backends`
- `feature_spec`
- `inputs`
- `summary`
- `diagnostics`
- `metrics`
- `artifacts`
- `warnings`
- `used_live_data`

## Backends

### Lean base path
- `naive`
- `seasonal_naive`
- `moving_average`
- `drift`
- `stream_ewm`

### Classical
- `stats_arima`
- `stats_ets`
- `statsforecast_autoarima` *(optional adapter)*
- `statsforecast_autoets` *(optional adapter)*

### Tabular
- `ml_ridge`
- `ml_histgb`
- `ml_xgboost`
- `ml_lightgbm`
- `ml_catboost`
- `mlforecast_linear` *(optional adapter)*
- `mlforecast_xgboost` *(optional adapter)*

### Streaming / online learning
- `stream_sgd`
- `stream_ewm`
- `river_linear` *(optional adapter)*
- `river_snarimax` *(optional adapter)*
- `river_holtwinters` *(optional adapter)*

### High-end optional adapters
- `neural_nhits`
- `automl_autogluon`
- `tabpfn_regression`

## Install modes

Base install for this source snapshot or local wheel:

```bash
python -m pip install .
# or install the built wheel shown in dist/
```

Optional extras after installation:

```bash
pip install "agentforecast[stats]"
pip install "agentforecast[ml]"
pip install "agentforecast[stream]"
pip install "agentforecast[features]"
pip install "agentforecast[deep]"
pip install "agentforecast[automl]"
pip install "agentforecast[tabpfn]"
pip install "agentforecast[stats,ml,stream,features]"
```

## Time Series To Regression

`agentforecast` can now expose the regression framing directly instead of hiding it behind fixed defaults.

You can choose specific lag points:

```bash
python -m agentforecast.cli forecast-dataset gold-exogenous \
  --backend ml_ridge \
  --lag-points 1,2,3,7,14,28 \
  --rolling-windows 3,7,14 \
  --outdir regression_demo
```

You can generate evenly spaced delay features:

```bash
python -m agentforecast.cli forecast-dataset gold-exogenous \
  --backend ml_ridge \
  --lag-step 7 \
  --lag-count 6 \
  --outdir spaced_delay_demo
```

You can also add a compact optional tsfresh descriptor layer:

```bash
python -m agentforecast.cli forecast-dataset gold-exogenous \
  --backend ml_ridge \
  --lag-points 1,2,3,7,14,28 \
  --tsfresh \
  --tsfresh-window 28 \
  --outdir tsfresh_regression_demo
```

There is now a built-in runnable case for this workflow:

```bash
python -m agentforecast.cli run-case time-series-regression-lab --outdir case_demo
```

## Hosted gallery

`agentforecast` can now turn run directories into a **static hosted gallery**.

```bash
python -m agentforecast.cli build-gallery --runs-root demo_gallery_runs --site-dir public_gallery/site
```

Output:

```text
public_gallery/site/
  index.html
  feed.json
  cases/
    sales.html
    gold.html
    github-breakout.html
    icu-bed-stress.html
  assets/
    ...copied charts, cards, markdown, JSON, CSV...
```

## Agent surface

Small API surface:

- `shoot`
- `forecast_csv`
- `forecast_url`
- `forecast_dataset`
- `forecast_dir`
- `compare_backends_csv`
- `compare_backends_dataset`
- `forecast_stream_csv`
- `run_case`
- `build_hosted_site`

Serving modes:

```bash
python -m agentforecast.cli serve-tools
python -m agentforecast.cli serve-mcp
```

## Benchmark hub

There are **two benchmark layers**:

1. **repo-internal transparent benchmark tables** over bundled datasets
2. **external benchmark links** to broader public leaderboard and dataset hubs

See:

- [BENCHMARK_HUB.md](BENCHMARK_HUB.md)
- [benchmarks/generated/transparent_public_benchmark.csv](benchmarks/generated/transparent_public_benchmark.csv)
- [benchmarks/generated/backend_rank_summary.csv](benchmarks/generated/backend_rank_summary.csv)
- [benchmarks/generated/external_benchmark_links.csv](benchmarks/generated/external_benchmark_links.csv)

## Cross-disciplinary starter flows

Built-in cases include:

- `github-breakout-radar`
- `gold-forecaster-arena`
- `time-series-regression-lab`
- `air-quality-smoke-watch`
- `icu-bed-stress-watch`
- `beamline-drift-watch`
- `transit-demand-shock-watch`

See:

- [CROSS_DISCIPLINARY_GUIDE.md](CROSS_DISCIPLINARY_GUIDE.md)
- [examples/README.md](examples/README.md)

## Honest positioning

`agentforecast` is **not** trying to beat dedicated frameworks on breadth.

Its differentiator is:

> **a unified, agent-friendly forecasting layer that routes across heterogeneous backends and exports a publishable pack**

See:

- [HONEST_SWITCHING_GUIDE.md](HONEST_SWITCHING_GUIDE.md)
- [BACKENDS.md](BACKENDS.md)
- [VIBE_CODING_GUIDE.md](VIBE_CODING_GUIDE.md)
- [HOSTED_GALLERY_GUIDE.md](HOSTED_GALLERY_GUIDE.md)
- [ADAPTERS.md](ADAPTERS.md)

## Status

This release is **v1.7.0 Hosted Multi-Backend Launch Edition**.

It is designed to keep the base path light while widening the forecasting surface and adding hosted-output workflows.
