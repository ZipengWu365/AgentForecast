# Changelog

## 1.7.0

- documented the benchmark-oriented low-level `OnlineForecaster` surface with explicit `fit / predict / update`, `horizons`, `lookback / max_history`, `strict_mode`, and direct versus recursive modes
- added `doctor` environment diagnostics, explicit `validate_series_frame` versus `clean_series_frame` surfaces, and a backend capability/install matrix
- removed the hidden runtime dependency on `tabulate` by generating markdown tables in-package
- added a fresh-wheel smoke test script and updated validation to match the real install path
- added OSS trust files: LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CITATION
- added dataset provenance fields and new cross-disciplinary datasets and cases
- expanded notebooks with exogenous, backend-choice, and cross-domain starter paths
- refreshed benchmark hub docs to separate internal demo benchmarks from external benchmark resources
- reduced plotting warnings by switching datetime plotting to `to_numpy()`
