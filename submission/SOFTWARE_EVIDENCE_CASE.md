# Software Evidence Case - monthly-car-sales

## Dataset provenance

- public example: `monthly-car-sales`
- vendored in the repository under `agentforecast/package_data/public_examples`
- used as software evidence because it is public, stable, and easy to reproduce

## Chosen baseline

- a reviewed backend path from the package registry
- pack generation and artifact export through the normal public interface

## Artifact outputs

- forecast CSV
- forecast chart
- forecast card
- markdown summary
- `metadata.json`
- `artifact_manifest.json`

## Expected user workflow

1. install from source or wheel
2. run one command or one Python call
3. inspect chart/card/CSV/JSON outputs
4. rebuild the hosted site if needed

## Failure modes

- missing optional backend extras
- explicit strict backend request against an unavailable backend
- over-reading internal benchmark outputs as external performance evidence

## Non-claim statement

This case demonstrates software reproducibility and artifact quality. It does not demonstrate domain science novelty or field-wide forecasting superiority.
