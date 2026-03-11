# v1.7 development plan

This iteration focuses on turning the first-run path from "good in the source tree" into "reliable from a fresh wheel install", while strengthening trust and cross-disciplinary adoption.

## Goals

1. Fix the fresh-install path so `shoot sales` works without hidden runtime dependencies.
2. Add standard OSS trust files at the repository root.
3. Make validation honest: include a real fresh-wheel smoke test.
4. Expand cross-disciplinary starter paths with more datasets, cases, and notebooks.
5. Clarify benchmark evidence by separating internal demo benchmarks from external benchmark hubs.

## Main code changes

- remove runtime dependence on `DataFrame.to_markdown()` / `tabulate`
- improve structured errors
- expand dataset and case registry
- refresh benchmark hub links
- keep base install light while preserving extras

## Deliverables

- updated wheel and source snapshot
- fresh-wheel smoke test script
- root OSS trust files
- new bundled datasets and cases
- richer notebooks and guides
- refreshed demo gallery and benchmark outputs
