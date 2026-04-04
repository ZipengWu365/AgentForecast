# Benchmark Semantics

AgentForecast distinguishes between convenience forecasting and research-safe benchmarking.

## Strict research mode

Use `OnlineForecaster` or comparison APIs with `strict_backend=True`.

Properties:

- the requested backend must be available
- unavailable backends raise an error instead of being silently skipped
- backend provenance is recorded in `resolution`
- metadata and artifact manifests record `requested_backend`, `resolved_backend`, `dependency_state`, and `fallback_reason`

This is the only mode whose backend claims should be carried into the paper.

## Convenience mode

Convenience forecasting is used by high-level pack APIs such as `forecast_dataframe(..., backend="auto")`.

Properties:

- routing may choose among installed candidates
- `backend="auto"` is allowed to select a winner from visible candidates
- explicit fallback is only allowed when `allow_backend_substitution=True`
- all routing decisions still appear in `metadata.json` and `artifact_manifest.json`

Convenience mode is suitable for demos and operational pack generation, but not for paper claims about one unavailable backend.

## Internal benchmarks

Internal benchmark outputs are engineering evidence and transparency aids. They are not field-wide leaderboards and should not be presented as universal superiority claims.
