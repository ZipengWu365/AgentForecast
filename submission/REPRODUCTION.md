# Reproduction

## Environment

- Python `3.11+`
- source tree rooted at `agentforecast_v1_8`
- install path: source, local wheel, or GitHub release artifact

## Core commands

```bash
python -m pip install .[dev,ml,stream]
python -m pytest -q
python -m build --wheel
python scripts/smoke_test_wheel.py
python scripts/build_benchmarks.py
python scripts/build_demo_gallery.py
python scripts/build_gallery_preview.py
python scripts/validate_v1_9.py
python -m agentforecast.cli doctor
python -m agentforecast.cli stream-eval --outdir outputs
```

## Reproduced public evidence

- package and schema validation
- demo gallery build
- submission document consistency
- streaming annex artifacts
