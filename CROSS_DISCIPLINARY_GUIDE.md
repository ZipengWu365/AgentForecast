
# Cross-disciplinary guide

`agentforecast` is designed for people who care about the **forecast pack** more than the forecasting framework itself.

## Starter domains

- medicine: ICU bed stress, outpatient no-show risk
- physics / engineering: beamline drift, grid heatwave stress
- climate / public risk: smoke watch, river flood risk
- markets: gold arena, exogenous gold watch
- public ops / social science: transit demand shock, GitHub breakout radar

## Best first commands

```bash
python -m agentforecast.cli shoot sales --outdir demo
python -m agentforecast.cli run-case icu-bed-stress-watch --outdir demo
python -m agentforecast.cli run-case grid-heatwave-stress-watch --outdir demo
python -m agentforecast.cli run-case river-flood-risk-watch --outdir demo
```

## If you do not know which backend to use

Start with `backend=auto` and one of these strategies:

- `fast` for first-look demos
- `accurate` for broader batch comparison
- `streaming` for live updates and drift alerts
- `low_data` when the series is short

## Provenance note

Bundled datasets are demo-ready snapshots packaged with the library. They are meant to teach the workflow, not to replace a domain-specific evaluation dataset.
