from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

from .conformal import ConformalSpec
from .features import FeatureSpec
from .version import __version__
from .errors import AgentForecastError
from .local import (
    compare_backends_csv,
    compare_backends_dataset,
    forecast_csv,
    forecast_dataset,
    forecast_dir,
    forecast_stream_csv,
    forecast_url,
    shoot,
    write_dataset,
)
from .live import get_case, list_cases, run_case
from .datasets import get_dataset_spec, list_datasets
from .backends import backend_capabilities, is_backend_available, list_backends, list_backend_families, list_reviewed_backends, route_backends
from .resources import api_catalog, describe_package, package_overview
from .tool_server import serve_json_tools
from .mcp_server import serve_mcp
from .benchmark_hub import list_external_benchmarks
from .examples_hub import build_examples_site, demo_examples, list_examples
from .hosted import build_hosted_site
from .public_examples import public_example_path
from .doctor import doctor
from .streaming_eval import stream_eval


def _print(payload, output: str = "json") -> None:
    if output == "json" or isinstance(payload, (dict, list)):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(payload)


def _demo_gallery(outdir: str, site_dir: str) -> dict:
    runs_root = Path(outdir)
    if runs_root.exists():
        shutil.rmtree(runs_root)
    runs_root.mkdir(parents=True, exist_ok=True)
    # Public gallery demos now use packaged real public time series instead of synthetic bundled examples.
    forecast_csv(public_example_path("monthly-car-sales"), outdir=runs_root, horizon=12, strategy="fast")
    compare_backends_csv(
        public_example_path("airline-passengers"),
        backends=[backend_id for backend_id in ["naive", "moving_average", "stats_arima", "stats_ets", "ml_ridge", "stream_ewm"] if is_backend_available(backend_id)],
        outdir=runs_root,
        horizon=12,
    )
    forecast_stream_csv(
        public_example_path("daily-min-temperatures"),
        backend="river_snarimax" if is_backend_available("river_snarimax") else "stream_ewm",
        outdir=runs_root,
        horizon=14,
    )
    return build_hosted_site(runs_root, site_dir)


def _add_conformal_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--conformal", action="store_true", help="Enable calibrated prediction intervals when supported.")
    parser.add_argument("--conformal-method", default="auto", choices=["auto", "river_jackknife", "rolling_residual"])
    parser.add_argument("--levels", default="80,90,95", help="Comma-separated interval levels, for example 80,90,95.")
    parser.add_argument("--calibration-window", type=int, default=200)
    parser.add_argument("--warmup-min", type=int, default=40)


def _parse_levels(value: str) -> tuple[int, ...]:
    levels = []
    for item in value.split(","):
        item = item.strip()
        if not item:
            continue
        levels.append(int(item))
    if not levels:
        raise ValueError("At least one conformal level is required.")
    return tuple(levels)


def _conformal_spec_from_args(args: argparse.Namespace) -> ConformalSpec | None:
    if not hasattr(args, "conformal"):
        return None
    default_signature = (
        args.conformal is False
        and args.conformal_method == "auto"
        and args.levels == "80,90,95"
        and args.calibration_window == 200
        and args.warmup_min == 40
    )
    if default_signature:
        return None
    try:
        levels = _parse_levels(args.levels)
    except ValueError as exc:
        raise AgentForecastError(code="INVALID_CONFORMAL_LEVELS", message=str(exc)) from exc
    return ConformalSpec(
        enabled=bool(args.conformal),
        method=args.conformal_method,
        levels=levels,
        calibration_window=args.calibration_window,
        warmup_min=args.warmup_min,
    )


def _parse_csv_items(value: str | None) -> list[str] | None:
    if value is None:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def _add_feature_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--lag-points", default=None, help="Comma-separated lag points such as 1,2,7,14.")
    parser.add_argument("--lag-step", type=int, default=None, help="Lag spacing for generated delay features.")
    parser.add_argument("--lag-count", type=int, default=None, help="How many spaced delay lags to generate.")
    parser.add_argument("--rolling-windows", default=None, help="Comma-separated rolling windows such as 3,7,14.")
    parser.add_argument("--disable-calendar", action="store_true", help="Disable calendar-derived regression features.")
    parser.add_argument("--tsfresh", action="store_true", help="Add a compact optional tsfresh descriptor set.")
    parser.add_argument("--tsfresh-window", type=int, default=30)
    parser.add_argument("--tsfresh-features", default=None, help="Comma-separated tsfresh feature ids to keep.")


def _add_backend_resolution_args(parser: argparse.ArgumentParser, *, strict_default: bool = False) -> None:
    parser.add_argument(
        "--strict-backend",
        action="store_true",
        default=strict_default,
        help="Require requested backends to be available instead of silently skipping or rerouting them.",
    )
    parser.add_argument(
        "--allow-backend-substitution",
        action="store_true",
        help="Allow an explicit unavailable backend to fall back to an installed candidate when strict mode is off.",
    )


def _feature_spec_from_args(args: argparse.Namespace) -> FeatureSpec | None:
    if not hasattr(args, "lag_points"):
        return None
    default_signature = (
        args.lag_points is None
        and args.lag_step is None
        and args.lag_count is None
        and args.rolling_windows is None
        and args.disable_calendar is False
        and args.tsfresh is False
        and args.tsfresh_window == 30
        and args.tsfresh_features is None
    )
    if default_signature:
        return None

    def _parse_optional_ints(raw: str | None) -> tuple[int, ...] | None:
        if raw is None:
            return None
        return _parse_levels(raw)

    tsfresh_features = None
    if args.tsfresh_features:
        tsfresh_features = tuple(item.strip() for item in args.tsfresh_features.split(",") if item.strip())

    return FeatureSpec(
        lag_points=_parse_optional_ints(args.lag_points),
        lag_step=args.lag_step,
        lag_count=args.lag_count,
        rolling_windows=_parse_optional_ints(args.rolling_windows),
        include_calendar=not args.disable_calendar,
        include_tsfresh=bool(args.tsfresh),
        tsfresh_window=args.tsfresh_window,
        tsfresh_features=tsfresh_features or FeatureSpec().tsfresh_features,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentforecast",
        description="Turn any time series into a publishable forecast pack with multi-backend routing and hosted gallery support.",
    )
    parser.add_argument("--version", action="version", version=f"agentforecast {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_desc = sub.add_parser("describe-package", help="Describe the package and quickstart.")
    p_desc.add_argument("--language", default="en")
    p_desc.add_argument("--output", choices=["json", "text"], default="json")

    for alias in ["shoot", "snap", "vibe"]:
        p = sub.add_parser(alias, help="Camera mode: auto-detect dataset id, case id, CSV, directory, or URL.")
        p.add_argument("target")
        p.add_argument("--backend", default="auto")
        p.add_argument("--strategy", default="fast", choices=["fast", "accurate", "streaming", "long_horizon", "low_data"])
        p.add_argument("--horizon", type=int, default=None)
        p.add_argument("--outdir", default="outputs")
        p.add_argument("--output", choices=["json", "text"], default="json")
        _add_conformal_args(p)
        _add_feature_args(p)
        _add_backend_resolution_args(p)

    p_fcsv = sub.add_parser("forecast-csv", help="Forecast a local CSV.")
    p_fcsv.add_argument("path")
    p_fcsv.add_argument("--date-col", default="ds")
    p_fcsv.add_argument("--value-col", default="y")
    p_fcsv.add_argument("--horizon", type=int, default=30)
    p_fcsv.add_argument("--backend", default="auto")
    p_fcsv.add_argument("--strategy", default="fast", choices=["fast", "accurate", "streaming", "long_horizon", "low_data"])
    p_fcsv.add_argument("--outdir", default="outputs")
    p_fcsv.add_argument("--series-kind", default="auto", choices=["auto", "price", "cumulative"])
    p_fcsv.add_argument("--output", choices=["json", "text"], default="json")
    _add_conformal_args(p_fcsv)
    _add_feature_args(p_fcsv)
    _add_backend_resolution_args(p_fcsv)

    p_furl = sub.add_parser("forecast-url", help="Forecast a CSV URL.")
    p_furl.add_argument("url")
    p_furl.add_argument("--date-col", default="ds")
    p_furl.add_argument("--value-col", default="y")
    p_furl.add_argument("--horizon", type=int, default=30)
    p_furl.add_argument("--backend", default="auto")
    p_furl.add_argument("--strategy", default="fast", choices=["fast", "accurate", "streaming", "long_horizon", "low_data"])
    p_furl.add_argument("--outdir", default="outputs")
    p_furl.add_argument("--series-kind", default="auto", choices=["auto", "price", "cumulative"])
    p_furl.add_argument("--output", choices=["json", "text"], default="json")
    _add_conformal_args(p_furl)
    _add_feature_args(p_furl)
    _add_backend_resolution_args(p_furl)

    p_fdataset = sub.add_parser("forecast-dataset", help="Forecast a bundled dataset.")
    p_fdataset.add_argument("dataset_id")
    p_fdataset.add_argument("--horizon", type=int, default=None)
    p_fdataset.add_argument("--backend", default="auto")
    p_fdataset.add_argument("--strategy", default="fast", choices=["fast", "accurate", "streaming", "long_horizon", "low_data"])
    p_fdataset.add_argument("--outdir", default="outputs")
    p_fdataset.add_argument("--output", choices=["json", "text"], default="json")
    _add_conformal_args(p_fdataset)
    _add_feature_args(p_fdataset)
    _add_backend_resolution_args(p_fdataset)

    p_fdir = sub.add_parser("forecast-dir", help="Forecast every CSV in a directory.")
    p_fdir.add_argument("directory")
    p_fdir.add_argument("--pattern", default="*.csv")
    p_fdir.add_argument("--date-col", default="ds")
    p_fdir.add_argument("--value-col", default="y")
    p_fdir.add_argument("--horizon", type=int, default=30)
    p_fdir.add_argument("--backend", default="auto")
    p_fdir.add_argument("--strategy", default="fast", choices=["fast", "accurate", "streaming", "long_horizon", "low_data"])
    p_fdir.add_argument("--outdir", default="outputs")
    p_fdir.add_argument("--series-kind", default="auto", choices=["auto", "price", "cumulative"])
    p_fdir.add_argument("--output", choices=["json", "text"], default="json")
    _add_conformal_args(p_fdir)
    _add_feature_args(p_fdir)
    _add_backend_resolution_args(p_fdir)

    p_compare_csv = sub.add_parser("compare-csv", help="Compare multiple backends on a local CSV.")
    p_compare_csv.add_argument("path")
    p_compare_csv.add_argument("--backends", required=True, help="Comma-separated backend ids.")
    p_compare_csv.add_argument("--date-col", default="ds")
    p_compare_csv.add_argument("--value-col", default="y")
    p_compare_csv.add_argument("--horizon", type=int, default=30)
    p_compare_csv.add_argument("--outdir", default="outputs")
    p_compare_csv.add_argument("--series-kind", default="auto", choices=["auto", "price", "cumulative"])
    p_compare_csv.add_argument("--output", choices=["json", "text"], default="json")
    _add_conformal_args(p_compare_csv)
    _add_feature_args(p_compare_csv)
    _add_backend_resolution_args(p_compare_csv, strict_default=True)

    p_compare_dataset = sub.add_parser("compare-dataset", help="Compare multiple backends on a bundled dataset.")
    p_compare_dataset.add_argument("dataset_id")
    p_compare_dataset.add_argument("--backends", required=True, help="Comma-separated backend ids.")
    p_compare_dataset.add_argument("--horizon", type=int, default=None)
    p_compare_dataset.add_argument("--outdir", default="outputs")
    p_compare_dataset.add_argument("--output", choices=["json", "text"], default="json")
    _add_conformal_args(p_compare_dataset)
    _add_feature_args(p_compare_dataset)
    _add_backend_resolution_args(p_compare_dataset, strict_default=True)

    p_stream = sub.add_parser("forecast-stream", help="Run a streaming backend.")
    p_stream.add_argument("path")
    p_stream.add_argument("--backend", default="stream_ewm")
    p_stream.add_argument("--date-col", default="ds")
    p_stream.add_argument("--value-col", default="y")
    p_stream.add_argument("--horizon", type=int, default=7)
    p_stream.add_argument("--outdir", default="outputs")
    p_stream.add_argument("--series-kind", default="auto", choices=["auto", "price", "cumulative"])
    p_stream.add_argument("--output", choices=["json", "text"], default="json")
    _add_conformal_args(p_stream)
    _add_feature_args(p_stream)
    _add_backend_resolution_args(p_stream)

    p_case = sub.add_parser("run-case", help="Run a built-in case.")
    p_case.add_argument("case_id")
    p_case.add_argument("--outdir", default="outputs")
    p_case.add_argument("--backend", default=None)
    p_case.add_argument("--strategy", default=None)
    p_case.add_argument("--output", choices=["json", "text"], default="json")
    _add_feature_args(p_case)

    p_cases = sub.add_parser("list-cases", help="List built-in cases.")
    p_cases.add_argument("--language", default="en")
    p_cases.add_argument("--output", choices=["json", "text"], default="json")

    p_case_show = sub.add_parser("case", help="Show one case spec.")
    p_case_show.add_argument("case_id")
    p_case_show.add_argument("--language", default="en")
    p_case_show.add_argument("--output", choices=["json", "text"], default="json")

    p_examples = sub.add_parser("list-examples", help="List curated runnable examples.")
    p_examples.add_argument("--output", choices=["json", "text"], default="json")

    p_datasets = sub.add_parser("list-datasets", help="List bundled datasets.")
    p_datasets.add_argument("--language", default="en")
    p_datasets.add_argument("--output", choices=["json", "text"], default="json")

    p_dataset = sub.add_parser("dataset", help="Show one dataset spec.")
    p_dataset.add_argument("dataset_id")
    p_dataset.add_argument("--language", default="en")
    p_dataset.add_argument("--output", choices=["json", "text"], default="json")

    p_write_dataset = sub.add_parser("write-dataset", help="Write a bundled dataset into a local directory.")
    p_write_dataset.add_argument("dataset_id")
    p_write_dataset.add_argument("--outdir", default=".")

    p_backends = sub.add_parser("list-backends", help="List registered backends.")
    p_backends.add_argument("--output", choices=["json", "text"], default="json")

    p_reviewed = sub.add_parser("list-reviewed-backends", help="List the reviewed backend surface.")
    p_reviewed.add_argument("--output", choices=["json", "text"], default="json")

    p_backend_cap = sub.add_parser("backend-capabilities", help="Show support metadata for one backend.")
    p_backend_cap.add_argument("backend_id")
    p_backend_cap.add_argument("--output", choices=["json", "text"], default="json")

    p_backend_families = sub.add_parser("backend-families", help="List backend families.")
    p_backend_families.add_argument("--output", choices=["json", "text"], default="json")

    p_route = sub.add_parser("route-backends", help="Show backend routing rationale.")
    p_route.add_argument("--history-len", type=int, required=True)
    p_route.add_argument("--horizon", type=int, required=True)
    p_route.add_argument("--strategy", default="fast", choices=["fast", "accurate", "streaming", "long_horizon", "low_data"])
    p_route.add_argument("--exogenous-cols", default="")
    p_route.add_argument("--output", choices=["json", "text"], default="json")

    p_benchmark = sub.add_parser("benchmark-hub", help="Show external benchmark and leaderboard links.")
    p_benchmark.add_argument("--output", choices=["json", "text"], default="json")

    p_api = sub.add_parser("api-tour", help="Show the compact API catalog.")
    p_api.add_argument("--output", choices=["json", "text"], default="json")

    p_doctor = sub.add_parser("doctor", help="Inspect installed extras, reviewed workflows, and next-step guidance.")
    p_doctor.add_argument("--output", choices=["json", "text"], default="json")

    p_stream_eval = sub.add_parser("stream-eval", help="Run the streaming evaluation pilot and export the annex artifacts.")
    p_stream_eval.add_argument("--outdir", default="outputs")
    p_stream_eval.add_argument("--backends", default="stream_ewm,river_linear,river_snarimax")
    p_stream_eval.add_argument("--warmup", type=int, default=36)
    p_stream_eval.add_argument("--output", choices=["json", "text"], default="json")

    p_gallery = sub.add_parser("build-gallery", help="Build a static gallery site from run directories.")
    p_gallery.add_argument("--runs-root", required=True)
    p_gallery.add_argument("--site-dir", required=True)
    p_gallery.add_argument("--output", choices=["json", "text"], default="json")

    p_demo_gallery = sub.add_parser("demo-gallery", help="Generate demo runs and build a static gallery site.")
    p_demo_gallery.add_argument("--outdir", default="public_gallery/demo_runs")
    p_demo_gallery.add_argument("--site-dir", default="public_gallery/site")
    p_demo_gallery.add_argument("--output", choices=["json", "text"], default="json")

    p_examples_site = sub.add_parser("build-examples", help="Build a tutorial-style examples site from generated example runs.")
    p_examples_site.add_argument("--runs-root", required=True)
    p_examples_site.add_argument("--site-dir", required=True)
    p_examples_site.add_argument("--output", choices=["json", "text"], default="json")

    p_demo_examples = sub.add_parser("demo-examples", help="Generate curated example runs and build the tutorial-style examples site.")
    p_demo_examples.add_argument("--outdir", default="examples/generated")
    p_demo_examples.add_argument("--site-dir", default="examples/site")
    p_demo_examples.add_argument("--examples", default=None, help="Comma-separated example ids to generate.")
    p_demo_examples.add_argument("--output", choices=["json", "text"], default="json")

    p_tools = sub.add_parser("serve-tools", help="Run the lean JSON tool server.")
    p_tools.add_argument("--once", default=None, help="Run one request and exit. Pass a JSON object string.")

    p_mcp = sub.add_parser("serve-mcp", help="Run the MCP-style JSON-RPC server.")
    p_mcp.add_argument("--once", default=None, help="Run one JSON-RPC request and exit. Pass a JSON object string.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "describe-package":
            payload = describe_package(args.language)
            _print(payload if args.output == "json" else payload["headline"] + "\n" + "\n".join(payload["quickstart"]), args.output)
        elif args.command in {"shoot", "snap", "vibe"}:
            result = shoot(args.target, backend=args.backend, strategy=args.strategy, horizon=args.horizon, outdir=args.outdir, conformal=_conformal_spec_from_args(args), feature_spec=_feature_spec_from_args(args), strict_backend=args.strict_backend, allow_backend_substitution=args.allow_backend_substitution)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "forecast-csv":
            result = forecast_csv(args.path, date_col=args.date_col, value_col=args.value_col, horizon=args.horizon, backend=args.backend, strategy=args.strategy, outdir=args.outdir, series_kind=args.series_kind, conformal=_conformal_spec_from_args(args), feature_spec=_feature_spec_from_args(args), strict_backend=args.strict_backend, allow_backend_substitution=args.allow_backend_substitution)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "forecast-url":
            result = forecast_url(args.url, date_col=args.date_col, value_col=args.value_col, horizon=args.horizon, backend=args.backend, strategy=args.strategy, outdir=args.outdir, series_kind=args.series_kind, conformal=_conformal_spec_from_args(args), feature_spec=_feature_spec_from_args(args), strict_backend=args.strict_backend, allow_backend_substitution=args.allow_backend_substitution)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "forecast-dataset":
            result = forecast_dataset(args.dataset_id, horizon=args.horizon, backend=args.backend, strategy=args.strategy, outdir=args.outdir, conformal=_conformal_spec_from_args(args), feature_spec=_feature_spec_from_args(args), strict_backend=args.strict_backend, allow_backend_substitution=args.allow_backend_substitution)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "forecast-dir":
            result = forecast_dir(args.directory, pattern=args.pattern, date_col=args.date_col, value_col=args.value_col, horizon=args.horizon, backend=args.backend, strategy=args.strategy, outdir=args.outdir, series_kind=args.series_kind, conformal=_conformal_spec_from_args(args), feature_spec=_feature_spec_from_args(args), strict_backend=args.strict_backend, allow_backend_substitution=args.allow_backend_substitution)
            _print(result.to_dict() if args.output == "json" else f"forecasted {len(result.runs)} file(s)", args.output)
        elif args.command == "compare-csv":
            result = compare_backends_csv(args.path, backends=[item.strip() for item in args.backends.split(",") if item.strip()], date_col=args.date_col, value_col=args.value_col, horizon=args.horizon, outdir=args.outdir, series_kind=args.series_kind, conformal=_conformal_spec_from_args(args), feature_spec=_feature_spec_from_args(args), strict_backend=args.strict_backend, allow_backend_substitution=args.allow_backend_substitution)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "compare-dataset":
            result = compare_backends_dataset(args.dataset_id, backends=[item.strip() for item in args.backends.split(",") if item.strip()], horizon=args.horizon, outdir=args.outdir, conformal=_conformal_spec_from_args(args), feature_spec=_feature_spec_from_args(args), strict_backend=args.strict_backend, allow_backend_substitution=args.allow_backend_substitution)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "forecast-stream":
            result = forecast_stream_csv(args.path, backend=args.backend, date_col=args.date_col, value_col=args.value_col, horizon=args.horizon, outdir=args.outdir, series_kind=args.series_kind, conformal=_conformal_spec_from_args(args), feature_spec=_feature_spec_from_args(args), strict_backend=args.strict_backend, allow_backend_substitution=args.allow_backend_substitution)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "run-case":
            result = run_case(args.case_id, outdir=args.outdir, backend=args.backend, strategy=args.strategy, feature_spec=_feature_spec_from_args(args))
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "list-cases":
            _print(list_cases(args.language), args.output)
        elif args.command == "case":
            _print(get_case(args.case_id, args.language), args.output)
        elif args.command == "list-examples":
            _print(list_examples(), args.output)
        elif args.command == "list-datasets":
            _print(list_datasets(args.language), args.output)
        elif args.command == "dataset":
            _print(get_dataset_spec(args.dataset_id).to_dict(args.language), args.output)
        elif args.command == "write-dataset":
            path = write_dataset(args.dataset_id, args.outdir)
            print(path.as_posix())
        elif args.command == "list-backends":
            _print(list_backends(), args.output)
        elif args.command == "list-reviewed-backends":
            _print(list_reviewed_backends(), args.output)
        elif args.command == "backend-capabilities":
            _print(backend_capabilities(args.backend_id), args.output)
        elif args.command == "backend-families":
            _print(list_backend_families(), args.output)
        elif args.command == "route-backends":
            payload = route_backends(history_len=args.history_len, horizon=args.horizon, strategy=args.strategy, exogenous_cols=[item for item in args.exogenous_cols.split(",") if item])
            _print(payload, args.output)
        elif args.command == "benchmark-hub":
            _print(list_external_benchmarks(), args.output)
        elif args.command == "api-tour":
            _print(api_catalog(), args.output)
        elif args.command == "doctor":
            payload = doctor()
            if args.output == "json":
                _print(payload, args.output)
            else:
                lines = [
                    "agentforecast doctor",
                    f"reviewed_backends: {', '.join(payload['reviewed_backends'])}",
                    f"missing_promoted_backends: {', '.join(payload['missing_promoted_backends']) or 'none'}",
                    f"recommended_next_command: {payload['recommended_next_command']}",
                ]
                _print("\n".join(lines), args.output)
        elif args.command == "stream-eval":
            payload = stream_eval(
                outdir=args.outdir,
                backends=[item.strip() for item in args.backends.split(",") if item.strip()],
                warmup=args.warmup,
            )
            _print(payload.to_dict() if args.output == "json" else payload.summary["headline"], args.output)
        elif args.command == "build-gallery":
            payload = build_hosted_site(args.runs_root, args.site_dir)
            _print(payload, args.output)
        elif args.command == "demo-gallery":
            payload = _demo_gallery(args.outdir, args.site_dir)
            _print(payload, args.output)
        elif args.command == "build-examples":
            payload = build_examples_site(args.runs_root, args.site_dir)
            _print(payload, args.output)
        elif args.command == "demo-examples":
            payload = demo_examples(args.outdir, args.site_dir, example_ids=_parse_csv_items(args.examples))
            _print(payload, args.output)
        elif args.command == "serve-tools":
            return serve_json_tools(once_payload=args.once)
        elif args.command == "serve-mcp":
            return serve_mcp(once_payload=args.once)
        else:
            parser.error(f"Unknown command '{args.command}'.")
        return 0
    except AgentForecastError as exc:
        print(json.dumps({"ok": False, "error": exc.to_dict()}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
