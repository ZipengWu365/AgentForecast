# Surfaces

`agentforecast` is organized around four public surfaces.

## Pack

The pack surface turns one series into publishable outputs.

Core entries:

- `forecast_dataframe`
- `forecast_csv`
- `forecast_url`
- `forecast_dataset`
- `forecast_dir`
- `shoot`

## Research

The research surface exists for explicit protocol control.

Core entries:

- `OnlineForecaster`
- strict backend resolution
- visible fallback provenance when explicitly allowed

## Operations

The operations surface exists for validation, release hygiene, and publishing.

Core entries:

- `doctor`
- `build_hosted_site`
- `demo-gallery`
- `stream-eval`

`stream-eval` is part of operations because it generates annex evidence, not because it changes the reviewed forecasting claim.

## Agent

The agent surface exists for tool and MCP consumption.

Core entries:

- `serve-tools`
- `serve-mcp`
- stable schema references
- discoverable backend capabilities
- discoverable `doctor` report
