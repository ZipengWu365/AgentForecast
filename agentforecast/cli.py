from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import sys

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
from .backends import list_backends, list_backend_families, route_backends
from .resources import api_catalog, describe_package, package_overview
from .tool_server import serve_json_tools
from .mcp_server import serve_mcp
from .benchmark_hub import list_external_benchmarks
from .hosted import build_hosted_site


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
    # fast demos that are wheel-safe and work without heavy extras
    shoot("sales", outdir=runs_root, strategy="fast")
    compare_backends_dataset("gold", backends=["naive", "moving_average", "stats_arima", "ml_ridge"], outdir=runs_root)
    run_case("github-breakout-radar", outdir=runs_root)
    return build_hosted_site(runs_root, site_dir)


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

    p_fdataset = sub.add_parser("forecast-dataset", help="Forecast a bundled dataset.")
    p_fdataset.add_argument("dataset_id")
    p_fdataset.add_argument("--horizon", type=int, default=None)
    p_fdataset.add_argument("--backend", default="auto")
    p_fdataset.add_argument("--strategy", default="fast", choices=["fast", "accurate", "streaming", "long_horizon", "low_data"])
    p_fdataset.add_argument("--outdir", default="outputs")
    p_fdataset.add_argument("--output", choices=["json", "text"], default="json")

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

    p_compare_csv = sub.add_parser("compare-csv", help="Compare multiple backends on a local CSV.")
    p_compare_csv.add_argument("path")
    p_compare_csv.add_argument("--backends", required=True, help="Comma-separated backend ids.")
    p_compare_csv.add_argument("--date-col", default="ds")
    p_compare_csv.add_argument("--value-col", default="y")
    p_compare_csv.add_argument("--horizon", type=int, default=30)
    p_compare_csv.add_argument("--outdir", default="outputs")
    p_compare_csv.add_argument("--series-kind", default="auto", choices=["auto", "price", "cumulative"])
    p_compare_csv.add_argument("--output", choices=["json", "text"], default="json")

    p_compare_dataset = sub.add_parser("compare-dataset", help="Compare multiple backends on a bundled dataset.")
    p_compare_dataset.add_argument("dataset_id")
    p_compare_dataset.add_argument("--backends", required=True, help="Comma-separated backend ids.")
    p_compare_dataset.add_argument("--horizon", type=int, default=None)
    p_compare_dataset.add_argument("--outdir", default="outputs")
    p_compare_dataset.add_argument("--output", choices=["json", "text"], default="json")

    p_stream = sub.add_parser("forecast-stream", help="Run a streaming backend.")
    p_stream.add_argument("path")
    p_stream.add_argument("--backend", default="stream_ewm")
    p_stream.add_argument("--date-col", default="ds")
    p_stream.add_argument("--value-col", default="y")
    p_stream.add_argument("--horizon", type=int, default=7)
    p_stream.add_argument("--outdir", default="outputs")
    p_stream.add_argument("--series-kind", default="auto", choices=["auto", "price", "cumulative"])
    p_stream.add_argument("--output", choices=["json", "text"], default="json")

    p_case = sub.add_parser("run-case", help="Run a built-in case.")
    p_case.add_argument("case_id")
    p_case.add_argument("--outdir", default="outputs")
    p_case.add_argument("--backend", default=None)
    p_case.add_argument("--strategy", default=None)
    p_case.add_argument("--output", choices=["json", "text"], default="json")

    p_cases = sub.add_parser("list-cases", help="List built-in cases.")
    p_cases.add_argument("--language", default="en")
    p_cases.add_argument("--output", choices=["json", "text"], default="json")

    p_case_show = sub.add_parser("case", help="Show one case spec.")
    p_case_show.add_argument("case_id")
    p_case_show.add_argument("--language", default="en")
    p_case_show.add_argument("--output", choices=["json", "text"], default="json")

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

    p_gallery = sub.add_parser("build-gallery", help="Build a static gallery site from run directories.")
    p_gallery.add_argument("--runs-root", required=True)
    p_gallery.add_argument("--site-dir", required=True)
    p_gallery.add_argument("--output", choices=["json", "text"], default="json")

    p_demo_gallery = sub.add_parser("demo-gallery", help="Generate demo runs and build a static gallery site.")
    p_demo_gallery.add_argument("--outdir", default="public_gallery/demo_runs")
    p_demo_gallery.add_argument("--site-dir", default="public_gallery/site")
    p_demo_gallery.add_argument("--output", choices=["json", "text"], default="json")

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
            result = shoot(args.target, backend=args.backend, strategy=args.strategy, horizon=args.horizon, outdir=args.outdir)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "forecast-csv":
            result = forecast_csv(args.path, date_col=args.date_col, value_col=args.value_col, horizon=args.horizon, backend=args.backend, strategy=args.strategy, outdir=args.outdir, series_kind=args.series_kind)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "forecast-url":
            result = forecast_url(args.url, date_col=args.date_col, value_col=args.value_col, horizon=args.horizon, backend=args.backend, strategy=args.strategy, outdir=args.outdir, series_kind=args.series_kind)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "forecast-dataset":
            result = forecast_dataset(args.dataset_id, horizon=args.horizon, backend=args.backend, strategy=args.strategy, outdir=args.outdir)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "forecast-dir":
            result = forecast_dir(args.directory, pattern=args.pattern, date_col=args.date_col, value_col=args.value_col, horizon=args.horizon, backend=args.backend, strategy=args.strategy, outdir=args.outdir, series_kind=args.series_kind)
            _print(result.to_dict() if args.output == "json" else f"forecasted {len(result.runs)} file(s)", args.output)
        elif args.command == "compare-csv":
            result = compare_backends_csv(args.path, backends=[item.strip() for item in args.backends.split(",") if item.strip()], date_col=args.date_col, value_col=args.value_col, horizon=args.horizon, outdir=args.outdir, series_kind=args.series_kind)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "compare-dataset":
            result = compare_backends_dataset(args.dataset_id, backends=[item.strip() for item in args.backends.split(",") if item.strip()], horizon=args.horizon, outdir=args.outdir)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "forecast-stream":
            result = forecast_stream_csv(args.path, backend=args.backend, date_col=args.date_col, value_col=args.value_col, horizon=args.horizon, outdir=args.outdir, series_kind=args.series_kind)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "run-case":
            result = run_case(args.case_id, outdir=args.outdir, backend=args.backend, strategy=args.strategy)
            _print(result.to_dict() if args.output == "json" else result.summary["headline"], args.output)
        elif args.command == "list-cases":
            _print(list_cases(args.language), args.output)
        elif args.command == "case":
            _print(get_case(args.case_id, args.language), args.output)
        elif args.command == "list-datasets":
            _print(list_datasets(args.language), args.output)
        elif args.command == "dataset":
            _print(get_dataset_spec(args.dataset_id).to_dict(args.language), args.output)
        elif args.command == "write-dataset":
            path = write_dataset(args.dataset_id, args.outdir)
            print(path.as_posix())
        elif args.command == "list-backends":
            _print(list_backends(), args.output)
        elif args.command == "backend-families":
            _print(list_backend_families(), args.output)
        elif args.command == "route-backends":
            payload = route_backends(history_len=args.history_len, horizon=args.horizon, strategy=args.strategy, exogenous_cols=[item for item in args.exogenous_cols.split(",") if item])
            _print(payload, args.output)
        elif args.command == "benchmark-hub":
            _print(list_external_benchmarks(), args.output)
        elif args.command == "api-tour":
            _print(api_catalog(), args.output)
        elif args.command == "build-gallery":
            payload = build_hosted_site(args.runs_root, args.site_dir)
            _print(payload, args.output)
        elif args.command == "demo-gallery":
            payload = _demo_gallery(args.outdir, args.site_dir)
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
