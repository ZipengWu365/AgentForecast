# Streaming Pilot Appendix

## Role in the submission

This appendix is a research annex. It does not expand the reviewed core claim.

## Command

```bash
python -m agentforecast.cli stream-eval --outdir outputs
```

## Fixed datasets

- `daily-min-temperatures`
- `river-flood-risk`

## Fixed backends

- `stream_ewm`
- `river_linear`
- `river_snarimax`

## Exported artifacts

- `metrics/prequential_metrics.csv`
- `metrics/system_metrics.json`
- `plots/prequential_error.png`
- `reports/summary.md`
- `meta/streaming_eval_manifest.json`

## Metrics

- prequential `MAE`
- prequential `RMSE`
- drift-window error before and after the split
- mean update latency
- total runtime
- peak memory proxy
