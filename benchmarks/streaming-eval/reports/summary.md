# Streaming evaluation pilot

Streaming pilot completed on one public real series plus one synthetic drift companion.

## Scope

- This file is a research annex for the software-first release.
- It is not a field-wide streaming superiority claim.
- Evaluated backends: `stream_ewm, river_linear, river_snarimax`
- Evaluated datasets: `daily-min-temperatures, river-flood-risk`

## Aggregated metrics

| dataset_id | backend_id | support_tier | n_steps | prequential_mae | prequential_rmse | rolling_window_error_before_drift | rolling_window_error_after_drift | mean_update_latency_ms | total_runtime_s | peak_memory_bytes | provenance_class |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| daily-min-temperatures | river_linear | reviewed | 96 | 1.91931 | 2.57829 | 2.06038 | 1.77825 | 711.266 | 68.3306 | 28486752 | public_example |
| daily-min-temperatures | river_snarimax | reviewed | 96 | 2.07083 | 2.65685 | 2.3693 | 1.77235 | 258.696 | 24.8817 | 740855 | public_example |
| daily-min-temperatures | stream_ewm | reviewed | 96 | 2.12391 | 2.75841 | 2.33355 | 1.91428 | 16.3608 | 1.61083 | 356797 | public_example |
| river-flood-risk | river_linear | reviewed | 96 | 5.05251 | 5.86522 | 6.242 | 4.33881 | 88.1756 | 8.50997 | 285377 | bundled_demo |
| river-flood-risk | river_snarimax | reviewed | 96 | 0.800021 | 1.01268 | 0.833632 | 0.779854 | 41.9811 | 4.07453 | 280140 | bundled_demo |
| river-flood-risk | stream_ewm | reviewed | 96 | 1.03028 | 1.24781 | 1.09823 | 0.989507 | 5.32742 | 0.546813 | 168151 | bundled_demo |

## Artifacts

- `metrics/prequential_metrics.csv`
- `metrics/system_metrics.json`
- `plots/prequential_error.png`
- `reports/summary.md`
- `meta/streaming_eval_manifest.json`
