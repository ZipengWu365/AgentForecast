from __future__ import annotations

from pathlib import Path
from typing import Any
import tempfile

import numpy as np
import pandas as pd

from .backends import candidate_backends, compute_metrics, forecast_with_backend, get_backend_spec, list_backends, score_backend, route_backends
from .errors import AgentForecastError, ensure
from .features import build_feature_spec, prepare_series_frame
from .plots import plot_forecast, plot_forecast_card, plot_leaderboard_card, plot_backend_comparison, plot_delta_card, plot_drift_alert_card
from .types import ArtifactRef, CompareResult, DirectoryRunResult, RunResult
from .utils import dataframe_to_markdown, ensure_dir, load_csv, load_csv_from_url, posix_path, relative_artifact, slugify, write_json
from .datasets import dataset_path, get_dataset_spec, list_datasets as _list_datasets, write_dataset as _write_dataset


def _pack_dirs(outdir: str | Path, name: str) -> dict[str, Path]:
    root = ensure_dir(Path(outdir) / slugify(name))
    return {
        "root": root,
        "data": ensure_dir(root / "data"),
        "plots": ensure_dir(root / "plots"),
        "reports": ensure_dir(root / "reports"),
        "meta": ensure_dir(root / "meta"),
    }


def _build_leaderboard(scores: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for item in scores:
        rows.append(
            {
                "backend_id": item["backend_id"],
                "mae": item["metrics"]["mae"],
                "rmse": item["metrics"]["rmse"],
                "mape": item["metrics"]["mape"],
                "smape": item["metrics"]["smape"],
                "backtest_horizon": item["backtest_horizon"],
            }
        )
    return pd.DataFrame(rows).sort_values(["mae", "rmse", "smape"]).reset_index(drop=True)


def _artifact(kind: str, path: Path, root: Path, media_type: str, description: str) -> ArtifactRef:
    return ArtifactRef(kind=kind, path=relative_artifact(path, root), media_type=media_type, description=description)


def _write_compare_pack(
    *,
    name: str,
    history: pd.DataFrame,
    selected_backend: str,
    future_forecast: pd.DataFrame,
    leaderboard: pd.DataFrame,
    scores: list[dict[str, Any]],
    feature_spec: dict[str, Any],
    outdir: str | Path,
    inputs: dict[str, Any],
    warnings: list[str] | None = None,
    used_live_data: bool = False,
) -> CompareResult:
    dirs = _pack_dirs(outdir, name)
    history_path = dirs["data"] / "history.csv"
    forecast_path = dirs["data"] / "forecast.csv"
    leaderboard_path = dirs["data"] / "leaderboard.csv"
    comparison_path = dirs["plots"] / "backend_comparison.png"
    card_path = dirs["plots"] / "forecast_card.png"
    chart_path = dirs["plots"] / "forecast.png"
    leaderboard_card_path = dirs["plots"] / "leaderboard_card.png"
    delta_path = dirs["plots"] / "winner_vs_runnerup_delta.png"
    report_path = dirs["reports"] / "summary.md"
    meta_path = dirs["meta"] / "metadata.json"

    history.to_csv(history_path, index=False)
    future_forecast.to_csv(forecast_path, index=False)
    leaderboard.to_csv(leaderboard_path, index=False)

    plot_forecast(history, future_forecast, title=name, output_path=chart_path)
    plot_forecast_card(history, future_forecast, title=name, output_path=card_path)
    plot_leaderboard_card(leaderboard, title=f"{name}: backend leaderboard", output_path=leaderboard_card_path)
    forecast_map = {item["backend_id"]: item["forecast"] for item in scores[: min(4, len(scores))]}
    plot_backend_comparison(history, forecast_map, title=f"{name}: backend comparison", output_path=comparison_path)
    plot_delta_card(leaderboard, title=f"{name}: winner vs runner-up", output_path=delta_path)

    selected_metrics = leaderboard[leaderboard["backend_id"] == selected_backend].iloc[0].to_dict()
    headline = f"{name}: {selected_backend} won the backend comparison and produced a publishable pack."
    narrative = (
        f"Compared {len(leaderboard)} backend(s) and routed the series to '{selected_backend}'. "
        f"Exported CSV, chart, card, markdown, and JSON artifacts."
    )
    summary_lines = [
        f"# {name}",
        "",
        f"- backend_selected: `{selected_backend}`",
        f"- candidate_backends: `{', '.join(leaderboard['backend_id'])}`",
        f"- artifact_count: `10`",
        f"- latest_observed: `{float(history['y'].iloc[-1]):.4f}`",
        f"- projected_end: `{float(future_forecast['yhat'].iloc[-1]):.4f}`",
        "",
        narrative,
        "",
        "## Leaderboard",
        "",
        dataframe_to_markdown(leaderboard),
        "",
        "## Artifacts",
        f"- `data/history.csv`",
        f"- `data/forecast.csv`",
        f"- `data/leaderboard.csv`",
        f"- `plots/forecast.png`",
        f"- `plots/forecast_card.png`",
        f"- `plots/backend_comparison.png`",
        f"- `plots/leaderboard_card.png`",
        f"- `plots/winner_vs_runnerup_delta.png`",
        f"- `reports/summary.md`",
        f"- `meta/metadata.json`",
    ]
    if warnings:
        summary_lines.extend(["", "## Warnings"] + [f"- {w}" for w in warnings])
    report_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    result = CompareResult(
        run_type="compare_backends",
        backend_selected=selected_backend,
        candidate_backends=leaderboard["backend_id"].tolist(),
        feature_spec=feature_spec,
        inputs=inputs,
        summary={
            "headline": headline,
            "latest_observed": float(history["y"].iloc[-1]),
            "projected_end": float(future_forecast["yhat"].iloc[-1]),
            "artifact_count": 10,
            "narrative": narrative,
        },
        diagnostics={
            "leaderboard": leaderboard.to_dict(orient="records"),
        },
        metrics={k: float(v) if isinstance(v, (int, float)) else v for k, v in selected_metrics.items()},
        leaderboard=leaderboard.to_dict(orient="records"),
        artifacts=[
            _artifact("history_csv", history_path, dirs["root"], "text/csv", "Normalized history"),
            _artifact("forecast_csv", forecast_path, dirs["root"], "text/csv", "Winner backend forecast"),
            _artifact("leaderboard_csv", leaderboard_path, dirs["root"], "text/csv", "Backend comparison leaderboard"),
            _artifact("forecast_png", chart_path, dirs["root"], "image/png", "Forecast chart"),
            _artifact("forecast_card_png", card_path, dirs["root"], "image/png", "Shareable forecast card"),
            _artifact("comparison_png", comparison_path, dirs["root"], "image/png", "Backend comparison chart"),
            _artifact("leaderboard_card_png", leaderboard_card_path, dirs["root"], "image/png", "Leaderboard card"),
            _artifact("delta_card_png", delta_path, dirs["root"], "image/png", "Winner vs runner-up delta card"),
            _artifact("summary_markdown", report_path, dirs["root"], "text/markdown", "Human-readable report"),
            _artifact("metadata_json", meta_path, dirs["root"], "application/json", "Structured compare result"),
        ],
        warnings=warnings or [],
        used_live_data=used_live_data,
    )
    write_json(meta_path, result.to_dict())
    return result


def _to_run_result(compare: CompareResult) -> RunResult:
    return RunResult(
        run_type=compare.run_type,
        backend_selected=compare.backend_selected,
        candidate_backends=compare.candidate_backends,
        feature_spec=compare.feature_spec,
        inputs=compare.inputs,
        summary=compare.summary,
        diagnostics=compare.diagnostics,
        metrics=compare.metrics,
        artifacts=compare.artifacts,
        warnings=compare.warnings,
        used_live_data=compare.used_live_data,
    )


def compare_backends_frame(
    frame: pd.DataFrame,
    *,
    name: str,
    date_col: str = "ds",
    value_col: str = "y",
    horizon: int = 30,
    backends: list[str] | None = None,
    strategy: str = "fast",
    outdir: str | Path = "outputs",
    series_kind: str = "auto",
    source: str | None = None,
    used_live_data: bool = False,
) -> CompareResult:
    prepared = prepare_series_frame(frame, date_col=date_col, value_col=value_col, series_kind=series_kind)
    feature_spec = build_feature_spec(prepared.history)
    route = route_backends(history_len=len(prepared.history), horizon=horizon, strategy=strategy, exogenous_cols=prepared.exogenous_cols)
    candidate = backends or route['candidate_backends'] or candidate_backends(strategy)
    if backends is not None:
        route = {
            'profile': 'explicit',
            'history_len': len(prepared.history),
            'horizon': horizon,
            'candidate_backends': candidate,
            'missing_backends': [],
            'recommended_extras': [],
            'reason': 'explicit_backends_provided',
        }
    ensure(len(candidate) > 0, "NO_BACKENDS_AVAILABLE", "No forecast backends are available for the requested strategy.")
    warnings: list[str] = []
    scores = []
    for backend_id in candidate:
        try:
            scored = score_backend(
                prepared.history,
                prepared.future_features,
                backend_id=backend_id,
                horizon=horizon,
                feature_spec=feature_spec,
                series_kind=prepared.series_kind,
            )
            scores.append(scored)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{backend_id}: {exc}")
    ensure(len(scores) > 0, "ALL_BACKENDS_FAILED", "All candidate backends failed.", help_text="Try 'agentforecast list-backends' and choose an installed backend.")
    leaderboard = _build_leaderboard(scores)
    winner = leaderboard.iloc[0]["backend_id"]
    winner_score = next(item for item in scores if item["backend_id"] == winner)
    result = _write_compare_pack(
        name=name,
        history=prepared.history,
        selected_backend=winner,
        future_forecast=winner_score["forecast"],
        leaderboard=leaderboard,
        scores=scores,
        feature_spec=feature_spec,
        outdir=outdir,
        inputs={
            "name": name,
            "horizon": int(horizon),
            "strategy": strategy,
            "source": source or "dataframe",
            "date_col": date_col,
            "value_col": value_col,
            "series_kind": prepared.series_kind,
            "candidate_backends": candidate,
        },
        warnings=warnings,
        used_live_data=used_live_data,
    )
    result.diagnostics['cleanup'] = prepared.cleanup
    result.diagnostics['routing'] = route
    result.summary['routing_reason'] = route['reason']
    result.inputs['routing'] = route
    write_json(Path(outdir) / slugify(name) / 'meta' / 'metadata.json', result.to_dict())
    return result


def forecast_dataframe(
    frame: pd.DataFrame,
    *,
    name: str = "series",
    date_col: str = "ds",
    value_col: str = "y",
    horizon: int = 30,
    backend: str = "auto",
    strategy: str = "fast",
    outdir: str | Path = "outputs",
    series_kind: str = "auto",
    source: str | None = None,
) -> RunResult:
    if backend == "auto":
        compare = compare_backends_frame(
            frame,
            name=name,
            date_col=date_col,
            value_col=value_col,
            horizon=horizon,
            strategy=strategy,
            outdir=outdir,
            series_kind=series_kind,
            source=source,
        )
        run = _to_run_result(compare)
        write_json(Path(outdir) / slugify(name) / "meta" / "metadata.json", run.to_dict())
        return run

    prepared = prepare_series_frame(frame, date_col=date_col, value_col=value_col, series_kind=series_kind)
    feature_spec = build_feature_spec(prepared.history)
    scored = score_backend(
        prepared.history,
        prepared.future_features,
        backend_id=backend,
        horizon=horizon,
        feature_spec=feature_spec,
        series_kind=prepared.series_kind,
    )
    compare = _write_compare_pack(
        name=name,
        history=prepared.history,
        selected_backend=backend,
        future_forecast=scored["forecast"],
        leaderboard=pd.DataFrame([{
            "backend_id": backend,
            **scored["metrics"],
            "backtest_horizon": scored["backtest_horizon"],
        }]),
        scores=[scored],
        feature_spec=feature_spec,
        outdir=outdir,
        inputs={
            "name": name,
            "horizon": int(horizon),
            "strategy": strategy,
            "source": source or "dataframe",
            "date_col": date_col,
            "value_col": value_col,
            "series_kind": prepared.series_kind,
            "candidate_backends": [backend],
        },
        warnings=[],
        used_live_data=False,
    )
    run = _to_run_result(compare)
    run.run_type = "forecast_dataframe"
    run.diagnostics['cleanup'] = prepared.cleanup
    run.diagnostics['routing'] = {
        'profile': 'explicit',
        'history_len': len(prepared.history),
        'horizon': horizon,
        'candidate_backends': [backend],
        'missing_backends': [],
        'recommended_extras': [],
        'reason': 'explicit_backend_selected',
    }
    run.summary['routing_reason'] = 'explicit_backend_selected'
    write_json(Path(outdir) / slugify(name) / 'meta' / 'metadata.json', run.to_dict())
    return run


def forecast_csv(
    path: str | Path,
    *,
    date_col: str = "ds",
    value_col: str = "y",
    horizon: int = 30,
    backend: str = "auto",
    strategy: str = "fast",
    outdir: str | Path = "outputs",
    series_kind: str = "auto",
) -> RunResult:
    csv_path = Path(path)
    ensure(csv_path.exists(), "CSV_NOT_FOUND", f"CSV file not found: {csv_path}")
    frame = load_csv(csv_path)
    result = forecast_dataframe(
        frame,
        name=csv_path.stem,
        date_col=date_col,
        value_col=value_col,
        horizon=horizon,
        backend=backend,
        strategy=strategy,
        outdir=outdir,
        series_kind=series_kind,
        source=posix_path(csv_path),
    )
    result.run_type = "forecast_csv"
    result.inputs["csv_path"] = posix_path(csv_path)
    write_json(Path(outdir) / slugify(csv_path.stem) / "meta" / "metadata.json", result.to_dict())
    return result


def forecast_url(
    url: str,
    *,
    date_col: str = "ds",
    value_col: str = "y",
    horizon: int = 30,
    backend: str = "auto",
    strategy: str = "fast",
    outdir: str | Path = "outputs",
    series_kind: str = "auto",
    name: str | None = None,
) -> RunResult:
    frame = load_csv_from_url(url)
    safe_name = name or slugify(Path(url.rstrip("/").split("/")[-1]).stem or "remote_series")
    result = forecast_dataframe(
        frame,
        name=safe_name,
        date_col=date_col,
        value_col=value_col,
        horizon=horizon,
        backend=backend,
        strategy=strategy,
        outdir=outdir,
        series_kind=series_kind,
        source=url,
    )
    result.run_type = "forecast_url"
    result.inputs["source_url"] = url
    write_json(Path(outdir) / slugify(safe_name) / "meta" / "metadata.json", result.to_dict())
    return result


def forecast_dataset(
    dataset_id: str,
    *,
    horizon: int | None = None,
    backend: str = "auto",
    strategy: str = "fast",
    outdir: str | Path = "outputs",
) -> RunResult:
    spec = get_dataset_spec(dataset_id)
    result = forecast_csv(
        dataset_path(dataset_id),
        date_col=spec.date_col,
        value_col=spec.value_col,
        horizon=horizon or spec.default_horizon,
        backend=backend,
        strategy=strategy,
        outdir=outdir,
        series_kind=spec.series_kind,
    )
    result.run_type = "forecast_dataset"
    result.inputs["dataset_id"] = dataset_id
    result.inputs["csv_path"] = f"package_data/datasets/{spec.file_name}"
    write_json(Path(outdir) / slugify(Path(spec.file_name).stem) / "meta" / "metadata.json", result.to_dict())
    return result


def compare_backends_csv(
    path: str | Path,
    *,
    backends: list[str],
    date_col: str = "ds",
    value_col: str = "y",
    horizon: int = 30,
    outdir: str | Path = "outputs",
    series_kind: str = "auto",
) -> CompareResult:
    csv_path = Path(path)
    frame = load_csv(csv_path)
    result = compare_backends_frame(
        frame,
        name=csv_path.stem,
        date_col=date_col,
        value_col=value_col,
        horizon=horizon,
        backends=backends,
        outdir=outdir,
        series_kind=series_kind,
        source=posix_path(csv_path),
    )
    return result


def compare_backends_dataset(
    dataset_id: str,
    *,
    backends: list[str],
    horizon: int | None = None,
    outdir: str | Path = "outputs",
) -> CompareResult:
    spec = get_dataset_spec(dataset_id)
    frame = load_csv(dataset_path(dataset_id))
    result = compare_backends_frame(
        frame,
        name=Path(spec.file_name).stem,
        date_col=spec.date_col,
        value_col=spec.value_col,
        horizon=horizon or spec.default_horizon,
        backends=backends,
        outdir=outdir,
        series_kind=spec.series_kind,
        source=f"package_data/datasets/{spec.file_name}",
    )
    return result


def forecast_dir(
    directory: str | Path,
    *,
    pattern: str = "*.csv",
    date_col: str = "ds",
    value_col: str = "y",
    horizon: int = 30,
    backend: str = "auto",
    strategy: str = "fast",
    outdir: str | Path = "outputs",
    series_kind: str = "auto",
) -> DirectoryRunResult:
    directory = Path(directory)
    ensure(directory.exists(), "DIRECTORY_NOT_FOUND", f"Directory not found: {directory}")
    files = sorted(directory.glob(pattern))
    ensure(len(files) > 0, "NO_CSV_FILES", f"No files matched pattern '{pattern}' in {directory}")
    runs = []
    warnings = []
    for csv_file in files:
        try:
            runs.append(
                forecast_csv(
                    csv_file,
                    date_col=date_col,
                    value_col=value_col,
                    horizon=horizon,
                    backend=backend,
                    strategy=strategy,
                    outdir=outdir,
                    series_kind=series_kind,
                )
            )
        except AgentForecastError as exc:
            warnings.append(f"{csv_file.name}: {exc.code} - {exc.message}")
    return DirectoryRunResult(
        inputs={
            "directory": posix_path(directory),
            "pattern": pattern,
            "horizon": horizon,
            "backend": backend,
            "strategy": strategy,
            "date_col": date_col,
            "value_col": value_col,
        },
        runs=runs,
        warnings=warnings,
    )


def forecast_stream_csv(
    path: str | Path,
    *,
    backend: str = "river_snarimax",
    date_col: str = "ds",
    value_col: str = "y",
    horizon: int = 7,
    outdir: str | Path = "outputs",
    series_kind: str = "auto",
) -> RunResult:
    ensure(backend.startswith(('river_', 'stream_')), 'STREAM_BACKEND_REQUIRED', 'forecast_stream_csv currently requires a streaming backend.')
    result = forecast_csv(
        path,
        date_col=date_col,
        value_col=value_col,
        horizon=horizon,
        backend=backend,
        strategy="streaming",
        outdir=outdir,
        series_kind=series_kind,
    )
    csv_path = Path(path)
    frame = load_csv(csv_path)
    prepared = prepare_series_frame(frame, date_col=date_col, value_col=value_col, series_kind=series_kind)
    step_errors = []
    history = prepared.history
    # lightweight progressive diagnostics using rolling one-step comparisons
    if len(history) >= 20:
        for split in range(max(8, len(history) // 2), len(history) - 1):
            train = history.iloc[:split].reset_index(drop=True)
            test_value = float(history.iloc[split]["y"])
            scored = score_backend(
                train,
                pd.DataFrame(columns=prepared.future_features.columns),
                backend_id=backend,
                horizon=1,
                feature_spec=build_feature_spec(train),
                series_kind=prepared.series_kind,
            )
            pred = float(scored["forecast"]["yhat"].iloc[0])
            step_errors.append(abs(test_value - pred))
    rolling_mae = float(np.mean(step_errors[-5:])) if step_errors else None
    base_mae = float(np.mean(step_errors[:5])) if len(step_errors) >= 5 else rolling_mae
    drift_ratio = (rolling_mae / base_mae) if (rolling_mae and base_mae and base_mae > 0) else 1.0
    drift_alert = bool(drift_ratio > 1.5) if rolling_mae is not None and base_mae is not None else False

    root = Path(outdir) / slugify(csv_path.stem)
    drift_path = root / "plots" / "drift_alert_card.png"
    plot_drift_alert_card(
        title=f"{csv_path.stem}: streaming drift watch",
        backend=backend,
        rolling_mae=rolling_mae,
        base_mae=base_mae,
        drift_ratio=drift_ratio,
        alert=drift_alert,
        output_path=drift_path,
    )
    meta_path = root / "meta" / "metadata.json"
    result.run_type = "forecast_stream_csv"
    payload = result.to_dict()
    payload["diagnostics"]["streaming"] = {
        "backend_family": "streaming",
        "rolling_mae_last_5": rolling_mae,
        "baseline_mae_first_5": base_mae,
        "drift_ratio": drift_ratio,
        "drift_alert": drift_alert,
    }
    payload["artifacts"].append(
        ArtifactRef("drift_alert_card_png", relative_artifact(drift_path, root), "image/png", "Streaming drift alert card").to_dict()
    )
    write_json(meta_path, payload)
    result.diagnostics["streaming"] = payload["diagnostics"]["streaming"]
    result.artifacts.append(ArtifactRef("drift_alert_card_png", relative_artifact(drift_path, root), "image/png", "Streaming drift alert card"))
    return result


def shoot(
    target: str,
    *,
    backend: str = "auto",
    strategy: str = "fast",
    horizon: int | None = None,
    outdir: str | Path = "outputs",
) -> RunResult | DirectoryRunResult:
    from .live import list_cases

    if target in {item["dataset_id"] for item in _list_datasets()}:
        return forecast_dataset(target, horizon=horizon, backend=backend, strategy=strategy, outdir=outdir)
    if target in {item["case_id"] for item in list_cases()}:
        from .live import run_case
        return run_case(target, outdir=outdir, backend=backend if backend != "auto" else None, strategy=strategy)
    path = Path(target)
    if path.exists() and path.is_dir():
        return forecast_dir(path, horizon=horizon or 14, backend=backend, strategy=strategy, outdir=outdir)
    if path.exists() and path.suffix.lower() == ".csv":
        return forecast_csv(path, horizon=horizon or 14, backend=backend, strategy=strategy, outdir=outdir)
    if target.startswith(("http://", "https://", "file://")):
        return forecast_url(target, horizon=horizon or 14, backend=backend, strategy=strategy, outdir=outdir)
    raise AgentForecastError(
        code="SHOOT_TARGET_NOT_UNDERSTOOD",
        message=f"Could not route target '{target}'.",
        help_text="Use a bundled dataset id, a built-in case id, a CSV path, a directory path, or a CSV URL.",
    )


def snap(*args: Any, **kwargs: Any) -> RunResult | DirectoryRunResult:
    return shoot(*args, **kwargs)


def write_dataset(dataset_id: str, outdir: str | Path = ".") -> Path:
    return _write_dataset(dataset_id, outdir)


def compare_backends(
    target: str,
    *,
    backends: list[str],
    date_col: str = "ds",
    value_col: str = "y",
    horizon: int | None = None,
    outdir: str | Path = "outputs",
    series_kind: str = "auto",
) -> CompareResult:
    dataset_ids = {item["dataset_id"] for item in _list_datasets()}
    if target in dataset_ids:
        return compare_backends_dataset(target, backends=backends, horizon=horizon, outdir=outdir)
    path = Path(target)
    if path.exists() and path.suffix.lower() == ".csv":
        return compare_backends_csv(path, backends=backends, date_col=date_col, value_col=value_col, horizon=horizon or 30, outdir=outdir, series_kind=series_kind)
    raise AgentForecastError(
        code="COMPARE_TARGET_NOT_UNDERSTOOD",
        message=f"Could not compare target '{target}'.",
        help_text="Use a bundled dataset id or a local CSV path.",
    )
