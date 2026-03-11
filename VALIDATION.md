# Validation — agentforecast v1.7.0

This file records the validations actually run for `agentforecast v1.7.0` inside the build container.

## What changed in this validation pass

This iteration specifically re-checked the failure that showed up in the v1.6 audit:

- **fresh wheel install -> copy-paste quickstart -> real output**

The v1.7 fix removes the hidden runtime dependence on `tabulate` by rendering markdown tables in-package.

## Commands actually run

### 1) Editable install

```bash
python -m pip install -e . --no-build-isolation
```

Result: **PASS**

### 2) Wheel build

```bash
python -m pip wheel . -w dist --no-deps --no-build-isolation
```

Result: **PASS**

Produced artifact:
- `dist/agentforecast-1.7.0-py3-none-any.whl`

### 3) Unit tests

```bash
python -m unittest discover -s tests -v
```

Result: **PASS**

Summary:
- `10/10` tests passed

Validated areas:
- forecast pack generation on bundled datasets
- backend comparison on bundled datasets
- routing logic for streaming strategy
- built-in streaming backends
- tool-server structured errors
- MCP resource surface
- hosted gallery build
- markdown summary generation without `tabulate`
- new dataset provenance entries

### 4) Internal benchmark regeneration

```bash
python scripts/build_benchmarks.py
```

Result: **PASS**

Notes:
- `statsmodels` emitted start-parameter warnings on some ARIMA fits, but the benchmark completed successfully.
- Generated files were refreshed under `benchmarks/generated/`.

### 5) Demo gallery regeneration

```bash
python scripts/build_demo_gallery.py
python scripts/build_gallery_preview.py
```

Result: **PASS**

Generated files include:
- `public_gallery/site/index.html`
- `public_gallery/site/feed.json`
- per-case HTML pages under `public_gallery/site/cases/`
- `assets/hosted_gallery_preview.png`

### 6) Asset validation script

```bash
python scripts/validate_v1_7.py
```

Result: **PASS**

### 7) Fresh wheel smoke test

```bash
python scripts/smoke_test_wheel.py
```

Result: **PASS**

What this script does:
- creates a fresh venv
- installs `dist/agentforecast-1.7.0-py3-none-any.whl`
- runs `python -m agentforecast.cli shoot sales --outdir demo`
- checks that `summary.md` exists

This directly validates the first-run path that previously broke in v1.6.

### 8) Additional CLI checks

Commands run:

```bash
python -m agentforecast.cli run-case river-flood-risk-watch --outdir tmp_case
python -m agentforecast.cli serve-tools --once '{"tool":"describe_package","args":{"language":"en"}}'
python -m agentforecast.cli serve-mcp --once '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
python -m agentforecast.cli benchmark-hub
```

Result: **PASS**

## Known boundaries of this validation

The following paths are wired in code but were **not** end-to-end validated in this container:

- optional `river_*` adapters using the external River package
- optional `statsforecast_*` adapters
- optional `mlforecast_*` adapters
- optional `neural_*` adapters
- optional `automl_*` / AutoGluon adapters
- optional `tabpfn_*` adapters
- real hosted deployment to GitHub Pages or another public static host
- real public repo/docs/gallery URLs in package metadata

## Trust and packaging notes

v1.7 now includes the standard OSS root files that were missing in v1.6:

- `LICENSE`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `CITATION.cff`

`pyproject.toml` now also includes truthful `project.urls` entries for benchmark-hub style public references, while still keeping real repo/docs/gallery URLs as release-time values to avoid publishing fake metadata.

## Overall verdict

`agentforecast v1.7.0` is validated in this environment as:

- a working lightweight base package,
- a multi-backend forecast-to-publish layer,
- a working streaming-capable package with built-in online backends,
- a working hosted gallery generator,
- and a working agent/tool/MCP-style integration surface.

Most importantly, the **fresh wheel quickstart path now works** for the base package in a new virtual environment.
