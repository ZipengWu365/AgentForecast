# Benchmark Hub

This file defines the evidence boundary for benchmark language.

## Internal benchmark evidence

Internal benchmark outputs in this repository are for:

- routing smoke tests
- artifact contract checks
- gallery and report generation checks
- product UX inspection

They are not external leaderboard evidence and should not be cited as universal performance claims.

## External benchmark context

External benchmark links exist to orient readers toward broader forecasting ecosystems and public evaluation resources. They are context, not a substitute for the reviewed software boundary.

## Strict research semantics

For benchmark-safe research calls:

- requested backend identity must remain explicit
- missing requested backends fail in strict mode
- fallback only happens with explicit opt-in outside strict mode
- provenance is written into `metadata.json` and `artifact_manifest.json`

## Streaming pilot annex

`stream-eval` is a research annex for prequential streaming evaluation on:

- `daily-min-temperatures` as the real external-lite series
- `river-flood-risk` as the synthetic drift companion

It is useful for error trajectories, update latency, runtime, and memory proxies. It is not a claim that streaming models dominate batch models in general.
