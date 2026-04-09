<p align="center">
  <img src="assets/agentforecast-mark.svg" alt="agentforecast logo" width="88" />
</p>

<h1 align="center">agentforecast</h1>

<p align="center"><strong>A software-first forecast-to-publish layer with reviewed pack, research, operations, and agent surfaces.</strong></p>

<p align="center">
  <a href="https://zipengwu365.github.io/AgentForecast/">Docs</a> |
  <a href="https://zipengwu365.github.io/AgentForecast/gallery/">Gallery</a> |
  <a href="https://zipengwu365.github.io/AgentForecast/papers/jmlr-mloss/">Paper entry</a> |
  <a href="https://github.com/ZipengWu365/AgentForecast/issues">Issues</a>
</p>

`agentforecast` routes one series through a compact forecasting surface, keeps backend identity explicit, and exports publishable artifacts: CSV, chart, card, markdown, JSON, and `artifact_manifest.json`.

This release is a software contribution. It is not a new forecasting method, does not claim field-wide SOTA, does not replace `sktime`, `StatsForecast`, `MLForecast`, or `River`, and does not present internal benchmark outputs as external performance evidence.

## Quickstart

Source install:

```bash
python -m pip install .
python -m agentforecast.cli shoot sales --outdir demo
```

Local wheel install:

```bash
python -m pip wheel . -w dist --no-deps
python -m pip install dist/agentforecast-1.9.0-py3-none-any.whl
python -m agentforecast.cli shoot sales --outdir demo
```

GitHub release artifact install:

```bash
python -m pip install <downloaded-release-wheel>.whl
python scripts/smoke_test_wheel.py
```

Health check and reviewed workflow guidance:

```bash
python -m agentforecast.cli doctor
python -m agentforecast.cli stream-eval --outdir outputs
```

## Surfaces

- `Pack`: `forecast_dataframe`, `forecast_csv`, `forecast_url`, `forecast_dataset`, `forecast_dir`, `shoot`
- `Research`: `OnlineForecaster` and strict backend resolution with visible provenance
- `Operations`: `doctor`, `build_hosted_site`, `demo-gallery`, `stream-eval`
- `Agent`: `serve-tools`, `serve-mcp`, stable JSON envelopes, schema references, capability discovery

Artifact outputs are part of the stable contract across these surfaces, but the package is intentionally not trying to become a general-purpose forecasting framework.

## Reviewed backends in v1.9.0

- `naive`
- `seasonal_naive`
- `moving_average`
- `drift`
- `stats_arima`
- `stats_ets`
- `ml_ridge`
- `mlforecast_linear`
- `stream_ewm`
- `river_linear`
- `river_snarimax`

Still not promoted in this release:

- `mlforecast_xgboost`
- `river_holtwinters`
- `stream_sgd`
- all `statsforecast_*` adapters
- all `tabpfn_*`, `neural_*`, and `automl_*` paths

## Evidence boundary

- Internal benchmark outputs are software evidence for routing, artifacts, and UX.
- The streaming pilot is a research annex, not a general streaming-superiority claim.
- Cross-domain starter flows are demos, not domain-grounded scientific results.
- Community adoption remains a residual risk and is documented honestly in the submission pack.

## Docs map

- [SURFACES.md](SURFACES.md)
- [SUPPORT_POLICY.md](SUPPORT_POLICY.md)
- [REVIEWED_SURFACE.md](REVIEWED_SURFACE.md)
- [BACKENDS.md](BACKENDS.md)
- [BENCHMARK_HUB.md](BENCHMARK_HUB.md)
- [AGENT_SURFACE.md](AGENT_SURFACE.md)
- [SCHEMA_POLICY.md](SCHEMA_POLICY.md)
- [VALIDATION.md](VALIDATION.md)
- [HOSTED_GALLERY_GUIDE.md](HOSTED_GALLERY_GUIDE.md)
- [CROSS_DISCIPLINARY_GUIDE.md](CROSS_DISCIPLINARY_GUIDE.md)
- [COMMUNITY.md](COMMUNITY.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [ROADMAP.md](ROADMAP.md)

## Submission map

- [submission/JMLR_SCOPE.md](submission/JMLR_SCOPE.md)
- [submission/OUTLET_FIT.md](submission/OUTLET_FIT.md)
- [submission/SCIENTIFIC_SOFTWARE_CONTRIBUTION.md](submission/SCIENTIFIC_SOFTWARE_CONTRIBUTION.md)
- [submission/REVIEWER_RESPONSE_MAP.md](submission/REVIEWER_RESPONSE_MAP.md)
- [submission/SOFTWARE_EVIDENCE_CASE.md](submission/SOFTWARE_EVIDENCE_CASE.md)
- [submission/STREAMING_PILOT_APPENDIX.md](submission/STREAMING_PILOT_APPENDIX.md)
- [submission/REPRODUCTION.md](submission/REPRODUCTION.md)
- [submission/RELATED_SOFTWARE_TABLE.md](submission/RELATED_SOFTWARE_TABLE.md)
- [submission/COVER_LETTER_EVIDENCE.md](submission/COVER_LETTER_EVIDENCE.md)
- [submission/COVER_LETTER_DRAFT.md](submission/COVER_LETTER_DRAFT.md)
- [submission/SOFTWARE_PAPER_OUTLINE.md](submission/SOFTWARE_PAPER_OUTLINE.md)
- [submission/RESEARCH_BACKLOG.md](submission/RESEARCH_BACKLOG.md)

## Community routing

- Bugs: [GitHub Issues](https://github.com/ZipengWu365/AgentForecast/issues)
- Feature requests: [GitHub Issues](https://github.com/ZipengWu365/AgentForecast/issues)
- Usage questions, backend requests, and showcase threads: GitHub Discussions once enabled

## Release metadata

- Citation metadata: [CITATION.cff](CITATION.cff)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Release-note checklist: [release/PROJECT_URLS_RELEASE_NOTES.md](release/PROJECT_URLS_RELEASE_NOTES.md)
