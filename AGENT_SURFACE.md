# Agent surface

`agentforecast` is designed so an agent can learn the package quickly.

## Small action space

- `shoot`
- `forecast_csv`
- `forecast_url`
- `forecast_dataset`
- `forecast_dir`
- `compare_backends_csv`
- `forecast_stream_csv`
- `OnlineForecaster`
- `run_case`
- `build_hosted_site`

## Why this matters

The package tries to minimize:

- framework-specific API branching
- token-heavy docs lookup
- ad hoc output parsing
- artifact discovery cost

The low-level `OnlineForecaster` surface is the benchmark-friendly path when you need explicit `fit / predict / update`, `horizons`, `lookback / max_history`, and `strict_mode` semantics.

## Serving modes

```bash
python -m agentforecast.cli serve-tools
python -m agentforecast.cli serve-mcp
```

The JSON results always aim to keep:

- `schema_version`
- `schema_ref`
- `tool_version`
- `backend_selected`
- `candidate_backends`
- `artifacts`
- `warnings`
