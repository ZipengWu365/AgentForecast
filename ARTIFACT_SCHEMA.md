# Artifact Schema

Every publishable pack is written under:

```text
<outdir>/<series-name>/
  data/
  plots/
  reports/
  meta/
```

## Required files

- `data/history.csv`
- `data/forecast.csv`
- `data/leaderboard.csv`
- `reports/summary.md`
- `meta/metadata.json`
- `meta/artifact_manifest.json`

Plot outputs are required for pack and compare flows:

- `plots/forecast.png`
- `plots/forecast_card.png`
- `plots/backend_comparison.png`
- `plots/leaderboard_card.png`
- `plots/winner_vs_runnerup_delta.png`

Streaming runs also add:

- `plots/drift_alert_card.png`

## metadata.json

`metadata.json` is the structured run result consumed by scripts and agents. It contains:

- result schema metadata
- run type
- selected backend
- candidate backends
- summary, diagnostics, metrics
- warnings
- resolution provenance
- artifact references

## artifact_manifest.json

`artifact_manifest.json` is the artifact contract for release validation. It contains:

- artifact schema version
- package version
- run type
- selected backend
- inputs
- resolution provenance
- warnings
- flat artifact listing

The manifest is the file used for contract tests across releases.
