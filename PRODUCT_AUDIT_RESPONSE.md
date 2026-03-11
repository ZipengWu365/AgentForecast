# Product audit response for v1.7

This iteration focuses on the most leverage-heavy fixes from the v1.6 audit:

1. **Fresh install reliability**: removed the hidden `tabulate` runtime dependency instead of adding a surprise base dependency.
2. **Trust surface**: added standard OSS files at the repository root.
3. **Validation honesty**: added a dedicated fresh-wheel smoke test script and aligned the validation notes with the actual install path.
4. **Cross-disciplinary adoption**: added richer bundled datasets, cases, provenance notes, and notebooks.
5. **Benchmark honesty**: separated internal demo benchmarks from the external benchmark hub.

One thing remains intentionally incomplete: real public `project.urls` are still not hardcoded into package metadata because publishing fake URLs would be a trust regression. Instead, the release template still requires you to fill the real repo/docs/gallery URLs before a public launch.
