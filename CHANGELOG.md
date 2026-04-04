# Changelog

## 1.8.0

- aligned package metadata, README, GitHub Pages, gallery, and release notes around one public docs entrypoint
- replaced the leftover template landing page with AgentForecast-specific landing content and docs pages
- introduced reviewed, experimental, and planned backend tiers with structured capability metadata
- added `list_reviewed_backends()`, `backend_capabilities()`, `resolve_backend_request()`, and `OnlineForecaster`
- made benchmark and research flows explicit about strict backend resolution and fallback provenance
- expanded `metadata.json` with resolution provenance and added `meta/artifact_manifest.json`
- rewrote the test suite into pytest modules by surface and added schema and strict-resolution contract coverage
- replaced the single gallery workflow with dedicated CI, docs/pages, release, optional-adapter, and nightly benchmark workflows
- added submission-facing docs for scope, reproduction, related software, and cover-letter evidence

## 1.7.0

- removed the hidden runtime dependency on `tabulate` by generating markdown tables in-package
- added a fresh-wheel smoke test script and updated validation to match the real install path
- added OSS trust files: LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, CITATION
- added dataset provenance fields and new cross-disciplinary datasets and cases
- expanded notebooks with exogenous, backend-choice, and cross-domain starter paths
- refreshed benchmark hub docs to separate internal demo benchmarks from external benchmark resources
- reduced plotting warnings by switching datetime plotting to `to_numpy()`
