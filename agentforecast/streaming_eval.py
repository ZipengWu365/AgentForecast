from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from time import perf_counter
import tracemalloc

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .backends import compute_metrics, forecast_with_backend, get_backend_spec, is_backend_available
from .datasets import dataset_path
from .errors import AgentForecastError, ensure
from .features import FeatureSpec, build_feature_spec, prepare_series_frame
from .public_examples import public_example_path
from .types import STREAMING_EVAL_SCHEMA_REF, STREAMING_EVAL_SCHEMA_VERSION, ArtifactRef, StreamingEvalResult
from .utils import dataframe_to_markdown, ensure_dir, load_csv, relative_artifact, write_json
from .version import __version__


_DEFAULT_BACKENDS = ("stream_ewm", "river_linear", "river_snarimax")
_MAX_EVAL_STEPS = 96
_DEFAULT_DATASETS = (
    ("daily-min-temperatures", public_example_path("daily-min-temperatures"), "public_example"),
    ("river-flood-risk", dataset_path("river-flood-risk"), "bundled_demo"),
)


def _artifact(kind: str, path: Path, root: Path, media_type: str, description: str) -> ArtifactRef:
    return ArtifactRef(kind=kind, path=relative_artifact(path, root), media_type=media_type, description=description)


def _safe_memory_bytes() -> int:
    current, peak = tracemalloc.get_traced_memory()
    return int(max(current, peak))


def _evaluate_backend(
    *,
    dataset_id: str,
    frame: pd.DataFrame,
    backend_id: str,
    feature_spec: FeatureSpec | dict[str, object] | None,
    warmup: int,
    drift_split: int,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    prepared = prepare_series_frame(frame, date_col="ds", value_col="y", series_kind="auto")
    built_feature_spec = build_feature_spec(prepared.history, feature_spec=feature_spec)
    history = prepared.history.reset_index(drop=True)
    future_cols = list(prepared.future_features.columns)
    max_lag = max(built_feature_spec.get("lags", [1]))
    start_idx = max(warmup, max_lag + 2)
    if len(history) - start_idx > _MAX_EVAL_STEPS:
        start_idx = len(history) - _MAX_EVAL_STEPS
    ensure(
        len(history) > start_idx,
        "STREAMING_SERIES_TOO_SHORT",
        f"Streaming evaluation needs more history for dataset '{dataset_id}'.",
        details={"dataset_id": dataset_id, "history_length": len(history), "warmup": start_idx},
    )

    split_idx = drift_split if start_idx < drift_split < len(history) else start_idx + max(1, (len(history) - start_idx) // 2)
    rows: list[dict[str, object]] = []
    latencies_ms: list[float] = []
    tracemalloc.start()
    backend_start = perf_counter()
    peak_memory_bytes = 0
    for idx in range(start_idx, len(history)):
        train = history.iloc[:idx].reset_index(drop=True)
        target_row = history.iloc[idx]
        started = perf_counter()
        forecast = forecast_with_backend(
            train,
            pd.DataFrame(columns=future_cols),
            horizon=1,
            backend_id=backend_id,
            feature_spec=built_feature_spec,
            series_kind=prepared.series_kind,
            conformal=None,
        )
        latency_ms = (perf_counter() - started) * 1000.0
        latencies_ms.append(latency_ms)
        peak_memory_bytes = max(peak_memory_bytes, _safe_memory_bytes())
        y_true = float(target_row["y"])
        y_pred = float(forecast["yhat"].iloc[0])
        phase = "pre_drift" if idx < split_idx else "post_drift"
        rows.append(
            {
                "dataset_id": dataset_id,
                "backend_id": backend_id,
                "step_index": idx,
                "ds": str(pd.Timestamp(target_row["ds"]).date()),
                "phase": phase,
                "y_true": y_true,
                "y_pred": y_pred,
                "abs_error": abs(y_true - y_pred),
                "sq_error": (y_true - y_pred) ** 2,
                "latency_ms": round(latency_ms, 6),
            }
        )
    total_runtime_s = perf_counter() - backend_start
    tracemalloc.stop()

    abs_errors = np.asarray([float(row["abs_error"]) for row in rows], dtype=float)
    sq_errors = np.asarray([float(row["sq_error"]) for row in rows], dtype=float)
    pre_errors = np.asarray([float(row["abs_error"]) for row in rows if row["phase"] == "pre_drift"], dtype=float)
    post_errors = np.asarray([float(row["abs_error"]) for row in rows if row["phase"] == "post_drift"], dtype=float)
    summary = {
        "dataset_id": dataset_id,
        "backend_id": backend_id,
        "support_tier": get_backend_spec(backend_id).tier,
        "n_steps": len(rows),
        "prequential_mae": round(float(abs_errors.mean()), 6),
        "prequential_rmse": round(float(np.sqrt(sq_errors.mean())), 6),
        "rolling_window_error_before_drift": round(float(pre_errors.mean()), 6) if pre_errors.size else None,
        "rolling_window_error_after_drift": round(float(post_errors.mean()), 6) if post_errors.size else None,
        "mean_update_latency_ms": round(float(np.mean(latencies_ms)), 6),
        "total_runtime_s": round(float(total_runtime_s), 6),
        "peak_memory_bytes": int(peak_memory_bytes),
    }
    return rows, summary


def _plot_prequential_error(frame: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    for (dataset_id, backend_id), group in frame.groupby(["dataset_id", "backend_id"]):
        rolling = group["abs_error"].rolling(window=min(10, max(3, len(group) // 6))).mean()
        label = f"{dataset_id}: {backend_id}"
        ax.plot(group["step_index"], rolling, label=label)
    ax.set_title("Streaming pilot prequential absolute error")
    ax.set_xlabel("step index")
    ax.set_ylabel("rolling abs error")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best", fontsize=8)
    fig.tight_layout()
    fig.savefig(output_path, dpi=180)
    plt.close(fig)


def _records_with_json_nulls(frame: pd.DataFrame) -> list[dict[str, object]]:
    return frame.where(pd.notna(frame), None).to_dict(orient="records")


def stream_eval(
    *,
    outdir: str | Path = "outputs",
    backends: list[str] | None = None,
    warmup: int = 36,
    feature_spec: FeatureSpec | dict[str, object] | None = None,
    strict_backend: bool = True,
) -> StreamingEvalResult:
    root = ensure_dir(Path(outdir) / "streaming-eval")
    metrics_dir = ensure_dir(root / "metrics")
    plots_dir = ensure_dir(root / "plots")
    reports_dir = ensure_dir(root / "reports")
    meta_dir = ensure_dir(root / "meta")

    candidate_backends = backends or list(_DEFAULT_BACKENDS)
    unavailable = [backend_id for backend_id in candidate_backends if not is_backend_available(backend_id)]
    if unavailable and strict_backend:
        raise AgentForecastError(
            code="BACKEND_UNAVAILABLE",
            message=f"Streaming evaluation requires installed backends: {', '.join(unavailable)}.",
            help_text="Install the 'stream' and 'ml' extras or pass a narrower backend list.",
            details={"requested_backends": candidate_backends, "unavailable_backends": unavailable},
        )
    active_backends = [backend_id for backend_id in candidate_backends if is_backend_available(backend_id)]
    ensure(active_backends, "NO_BACKENDS_AVAILABLE", "No streaming evaluation backends are installed.")

    all_rows: list[dict[str, object]] = []
    summaries: list[dict[str, object]] = []
    warnings: list[str] = []
    for dataset_id, csv_path, provenance_class in _DEFAULT_DATASETS:
        frame = load_csv(csv_path)
        drift_split = max(warmup + 1, int(len(frame) * 0.7))
        for backend_id in active_backends:
            try:
                rows, summary = _evaluate_backend(
                    dataset_id=dataset_id,
                    frame=frame,
                    backend_id=backend_id,
                    feature_spec=feature_spec,
                    warmup=warmup,
                    drift_split=drift_split,
                )
                summary["provenance_class"] = provenance_class
                all_rows.extend(rows)
                summaries.append(summary)
            except AgentForecastError:
                raise
            except Exception as exc:  # noqa: BLE001
                warning = f"{dataset_id}:{backend_id} failed during streaming evaluation: {exc}"
                if strict_backend:
                    raise AgentForecastError(
                        code="STREAMING_EVAL_FAILED",
                        message=warning,
                        details={"dataset_id": dataset_id, "backend_id": backend_id},
                    ) from exc
                warnings.append(warning)

    ensure(summaries, "STREAMING_EVAL_EMPTY", "Streaming evaluation did not produce any backend summaries.")
    metrics_frame = pd.DataFrame(all_rows)
    summary_frame = pd.DataFrame(summaries).sort_values(["dataset_id", "backend_id"]).reset_index(drop=True)
    summary_records = _records_with_json_nulls(summary_frame)

    metrics_csv_path = metrics_dir / "prequential_metrics.csv"
    system_json_path = metrics_dir / "system_metrics.json"
    plot_path = plots_dir / "prequential_error.png"
    report_path = reports_dir / "summary.md"
    manifest_path = meta_dir / "streaming_eval_manifest.json"

    metrics_frame.to_csv(metrics_csv_path, index=False)
    write_json(system_json_path, summary_records)
    _plot_prequential_error(metrics_frame, plot_path)

    headline = "Streaming pilot completed on one public real series plus one synthetic drift companion."
    report_lines = [
        "# Streaming evaluation pilot",
        "",
        headline,
        "",
        "## Scope",
        "",
        "- This file is a research annex for the software-first release.",
        "- It is not a field-wide streaming superiority claim.",
        f"- Evaluated backends: `{', '.join(active_backends)}`",
        f"- Evaluated datasets: `{', '.join(dataset_id for dataset_id, _, _ in _DEFAULT_DATASETS)}`",
        "",
        "## Aggregated metrics",
        "",
        dataframe_to_markdown(summary_frame.where(pd.notna(summary_frame), None)),
        "",
        "## Artifacts",
        "",
        "- `metrics/prequential_metrics.csv`",
        "- `metrics/system_metrics.json`",
        "- `plots/prequential_error.png`",
        "- `reports/summary.md`",
        "- `meta/streaming_eval_manifest.json`",
    ]
    if warnings:
        report_lines.extend(["", "## Warnings", *[f"- {warning}" for warning in warnings]])
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    artifacts = [
        _artifact("prequential_metrics_csv", metrics_csv_path, root, "text/csv", "Per-step streaming errors and latencies."),
        _artifact("system_metrics_json", system_json_path, root, "application/json", "Aggregated streaming pilot metrics by dataset and backend."),
        _artifact("prequential_error_png", plot_path, root, "image/png", "Rolling absolute error plot for the streaming pilot."),
        _artifact("summary_markdown", report_path, root, "text/markdown", "Human-readable streaming pilot summary."),
        _artifact("streaming_eval_manifest_json", manifest_path, root, "application/json", "Streaming pilot manifest and schema-bound metadata."),
    ]
    payload = StreamingEvalResult(
        inputs={
            "datasets": [dataset_id for dataset_id, _, _ in _DEFAULT_DATASETS],
            "requested_backends": candidate_backends,
            "evaluated_backends": active_backends,
            "warmup": warmup,
            "max_eval_steps": _MAX_EVAL_STEPS,
            "strict_backend": strict_backend,
        },
        summary={
            "headline": headline,
            "dataset_count": len(_DEFAULT_DATASETS),
            "backend_count": len(active_backends),
            "metric_rows": int(len(metrics_frame)),
        },
        metrics=summary_records,
        diagnostics={
            "datasets": [
                {"dataset_id": dataset_id, "provenance_class": provenance_class}
                for dataset_id, _, provenance_class in _DEFAULT_DATASETS
            ],
            "schema_ref": STREAMING_EVAL_SCHEMA_REF,
            "package_version": __version__,
        },
        artifacts=artifacts,
        warnings=warnings,
    )
    manifest = payload.to_dict()
    manifest["kind"] = "agentforecast.streaming_eval_manifest"
    manifest["tool_version"] = __version__
    write_json(manifest_path, manifest)
    return payload
