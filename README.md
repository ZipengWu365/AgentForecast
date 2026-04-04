<p align="center">
  <img src="assets/agentforecast-mark.svg" alt="agentforecast logo" width="88" />
</p>

<h1 align="center">agentforecast</h1>

<p align="center"><strong>A reviewed forecast-to-publish layer for time-series forecasting across heterogeneous backends.</strong></p>

<p align="center">
  <a href="https://zipengwu365.github.io/AgentForecast/">Docs</a> |
  <a href="https://zipengwu365.github.io/AgentForecast/gallery/">Gallery</a> |
  <a href="https://zipengwu365.github.io/AgentForecast/papers/jmlr-mloss/">JMLR entry</a> |
  <a href="https://github.com/ZipengWu365/AgentForecast/issues">Issues</a>
</p>

`agentforecast` is a small forecasting surface that sits above multiple backend families and exports a publishable pack:

- reviewed pack APIs for local forecasting, backend comparison, and static gallery publishing
- explicit artifact outputs for humans and agents: CSV, chart, card, markdown, JSON, and artifact manifest
- benchmark-safe strict backend resolution for research through `OnlineForecaster`

It is not a replacement for specialized forecasting frameworks such as `sktime`, `StatsForecast`, `MLForecast`, or `River`. It is a forecast-to-publish layer that keeps routing, artifacts, and agent/tool consumption consistent.

## Quickstart

Source install:

```bash
python -m pip install .
python -m agentforecast.cli shoot sales --outdir demo
```

Local wheel install:

```bash
python -m pip wheel . -w dist --no-deps
python -m pip install dist/agentforecast-1.8.0-py3-none-any.whl
python -m agentforecast.cli shoot sales --outdir demo
```

GitHub release artifact install:

```bash
python -m pip install <downloaded-release-wheel>.whl
python -m agentforecast.cli shoot sales --outdir demo
```

Python API:

```python
import pandas as pd

from agentforecast import forecast_dataframe

df = pd.read_csv("https://raw.githubusercontent.com/jbrownlee/Datasets/master/monthly-car-sales.csv")
result = forecast_dataframe(
    df,
    name="monthly_car_sales",
    horizon=12,
    strategy="fast",
    outdir="demo",
)
print(result.summary["headline"])
```

## Surfaces

- `Pack`: `forecast_dataframe`, `forecast_csv`, `forecast_url`, `forecast_dataset`, `shoot`
- `Research`: `OnlineForecaster` plus strict backend resolution and visible provenance
- `Artifacts`: `meta/metadata.json`, `meta/artifact_manifest.json`, charts, cards, CSV, markdown
- `Agent`: `serve-tools`, `serve-mcp`, stable JSON payloads, backend capability metadata

## Support policy

- `Reviewed`: covered by tests, docs, and the reviewed release claim
- `Experimental`: exposed publicly but not part of the reviewed paper claim
- `Planned`: registered or discussed as roadmap, not part of the reviewed surface

Current reviewed backends:

- `naive`
- `seasonal_naive`
- `moving_average`
- `drift`
- `stats_arima`
- `stats_ets`
- `ml_ridge`
- `stream_ewm`

See [SUPPORT_POLICY.md](SUPPORT_POLICY.md), [REVIEWED_SURFACE.md](REVIEWED_SURFACE.md), and [BACKENDS.md](BACKENDS.md).

## Install extras

```bash
python -m pip install ".[stats]"
python -m pip install ".[ml]"
python -m pip install ".[stream]"
python -m pip install ".[features]"
python -m pip install ".[deep]"
python -m pip install ".[automl]"
python -m pip install ".[tabpfn]"
```

Optional adapters stay outside the reviewed claim unless they are explicitly tested and listed in the support policy.

## Docs map

- [SUPPORT_POLICY.md](SUPPORT_POLICY.md)
- [REVIEWED_SURFACE.md](REVIEWED_SURFACE.md)
- [BACKENDS.md](BACKENDS.md)
- [BENCHMARK_SEMANTICS.md](BENCHMARK_SEMANTICS.md)
- [ARTIFACT_SCHEMA.md](ARTIFACT_SCHEMA.md)
- [COMMUNITY.md](COMMUNITY.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [HOSTED_GALLERY_GUIDE.md](HOSTED_GALLERY_GUIDE.md)

## Community

- Bugs: [GitHub Issues](https://github.com/ZipengWu365/AgentForecast/issues)
- Feature requests: [GitHub Issues](https://github.com/ZipengWu365/AgentForecast/issues)
- Usage questions and showcase threads: GitHub Discussions once enabled on the public repo

## Citation and release

- Citation metadata: [CITATION.cff](CITATION.cff)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Submission materials: [submission/JMLR_SCOPE.md](submission/JMLR_SCOPE.md), [submission/REPRODUCTION.md](submission/REPRODUCTION.md)
