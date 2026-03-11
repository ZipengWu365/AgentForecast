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
- `run_case`
- `build_hosted_site`

## Why this matters

The package tries to minimize:

- framework-specific API branching
- token-heavy docs lookup
- ad hoc output parsing
- artifact discovery cost

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
