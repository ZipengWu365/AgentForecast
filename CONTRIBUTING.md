# Contributing

Thanks for considering a contribution.

## Good first contributions

- fix a forecast-pack bug or missing artifact
- improve bundled dataset provenance notes
- add a notebook or cross-domain case
- improve backend routing documentation
- improve structured errors or tool manifests

## Development loop

```bash
python -m pip install -e .[dev]
python -m pytest -q
python scripts/build_benchmarks.py
python scripts/build_demo_gallery.py
```

## Style

- keep the public API surface small
- prefer explicit structured outputs over ad-hoc print output
- preserve the base install path as light as possible
- route heavy dependencies through extras
