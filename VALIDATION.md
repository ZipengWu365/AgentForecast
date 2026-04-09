# Validation - agentforecast v1.9.0

This file records the validations actually run for the `v1.9.0` software-first reviewed release response pass.

## Environment

| Field | Value |
|---|---|
| Python | `3.11.9` |
| OS | `Windows-10-10.0.26200-SP0` |
| Shell | `powershell` |
| Package baseline | `agentforecast 1.9.0` |

## Truth table: reviewed / experimental / planned backends

| Tier | Backends |
|---|---|
| reviewed | `naive`, `seasonal_naive`, `moving_average`, `drift`, `stats_arima`, `stats_ets`, `ml_ridge`, `mlforecast_linear`, `stream_ewm`, `river_linear`, `river_snarimax` |
| experimental | `statsforecast_autoarima`, `statsforecast_autoets`, `ml_histgb`, `ml_xgboost`, `ml_lightgbm`, `ml_catboost`, `mlforecast_xgboost`, `stream_sgd`, `river_holtwinters`, `tabpfn_regression` |
| planned | `neural_nhits`, `automl_autogluon` |

## Truth table: surface validation boundary

| Surface | Status | Evidence |
|---|---|---|
| pack APIs | validated | end-to-end pytest plus wheel smoke |
| strict research API | validated | `OnlineForecaster` strict resolution tests |
| operations surface | validated | `doctor`, hosted site build, benchmark build, `stream-eval` |
| artifact contract | validated | `metadata.json`, `artifact_manifest.json`, schema checks |
| tool surface | validated | stable success/error envelope tests |
| MCP surface | validated | JSON-RPC tool/resource/error tests |
| optional adapters outside reviewed claim | smoke-only unless promoted | explicit `optional` test suite |
| cross-domain starter flows | demo-only | not used as domain-science evidence |

## Truth table: public release paths

| Path | Status | Evidence |
|---|---|---|
| source install | supported | `python -m pip install .[dev,stats,ml,stream]` |
| local wheel install | supported | `python -m build --wheel` and `scripts/smoke_test_wheel.py` |
| GitHub release artifact | supported once wheel exists | same smoke path against the built wheel |
| GitHub Pages docs/gallery | supported | `scripts/build_demo_gallery.py`, `scripts/build_gallery_preview.py`, `scripts/validate_v1_9.py` |
| PyPI install | not claimed | not used as the primary public install path in this release |

## Commands actually run

| Command | Result | Notes |
|---|---|---|
| `python -m pip install .[dev,stats,ml,stream]` | PASS | installed reviewed MLForecast and River candidates plus classical extras |
| `python -m pytest -q` | PASS | `38 passed`, coverage `80.44%` |
| `python -m build --wheel` | PASS | built `dist/agentforecast-1.9.0-py3-none-any.whl` |
| `python scripts/smoke_test_wheel.py` | PASS | fresh-wheel smoke path succeeded |
| `python scripts/build_benchmarks.py` | PASS | regenerated canonical internal benchmark artifacts |
| `python scripts/build_demo_gallery.py` | PASS | rebuilt demo runs and Pages site content |
| `python scripts/build_gallery_preview.py` | PASS | refreshed preview assets |
| `python -m agentforecast.cli stream-eval --outdir benchmarks --output json` | PASS | generated canonical streaming annex artifacts under `benchmarks/streaming-eval` |
| `python scripts/validate_v1_9.py` | PASS | docs, Pages, submission links, and reviewed-boundary consistency checks succeeded |

## Streaming annex output

The canonical streaming annex command generated:

- `benchmarks/streaming-eval/metrics/prequential_metrics.csv`
- `benchmarks/streaming-eval/metrics/system_metrics.json`
- `benchmarks/streaming-eval/plots/prequential_error.png`
- `benchmarks/streaming-eval/reports/summary.md`
- `benchmarks/streaming-eval/meta/streaming_eval_manifest.json`

## Known limits

- the streaming pilot is annex evidence, not a main release claim
- optional adapters remain outside the reviewed claim unless explicitly promoted
- public adoption is still limited and should stay disclosed as a residual risk
- cross-domain starter flows remain demos rather than domain-validation studies

## Overall verdict

`agentforecast v1.9.0` is validated in this environment as:

- a working software-first forecast-to-publish package
- a reviewed strict-backend research surface through `OnlineForecaster`
- a reviewed operations surface through `doctor`
- a stable artifact-producing workflow
- a tested tool and MCP contract with explicit schemas
- a reproducible Pages and gallery build
