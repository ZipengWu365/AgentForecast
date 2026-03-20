
# Benchmark hub

`agentforecast` ships two different evidence layers on purpose:

1. **Internal demo benchmark**: a transparent, reproducible holdout comparison on bundled datasets. It is useful for smoke-testing backend routing, artifact generation, and product UX.
2. **External benchmark hub**: links to broader time-series benchmark repositories, competitions, and leaderboards. Use these for field-wide evidence, not the internal demo table.

For paper-style evaluation, pair those evidence layers with the low-level `OnlineForecaster` benchmark surface. That keeps protocol details explicit: `fit / predict / update`, `horizons=[...]`, `lookback / max_history`, `strict_mode`, and direct versus recursive multi-horizon behavior.

## Internal benchmark files

- `benchmarks/generated/transparent_public_benchmark.csv`
- `benchmarks/generated/backend_rank_summary.csv`
- `benchmarks/generated/transparent_public_benchmark.png`

These files summarize performance on the bundled demo datasets only.

## External benchmark hub

See `benchmarks/generated/external_benchmark_links.csv` or run:

```bash
python -m agentforecast.cli benchmark-hub
```

The hub includes ForecastingData / Monash, M4, M5, OpenTS-Bench / TFB, GIFT-Eval, and ForecastBench.

## Honest reading rule

Do not present the internal benchmark as a community-wide leaderboard. Use it as product evidence and use the external hub when you need broader benchmark context.

Do not present the pack-oriented demo API as a benchmark protocol either. It is a publishing surface, not a leak-free evaluation contract.
