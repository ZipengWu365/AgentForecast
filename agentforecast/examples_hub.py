from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import importlib.util
import json
import shutil
import tempfile
import warnings

from .backends import is_backend_available
from .conformal import ConformalSpec
from .datasets import dataset_path, get_dataset_spec
from .features import FeatureSpec
from .hosted import (
    _BASE_CSS,
    _artifact_cards,
    _author_strip,
    _copy_artifact,
    _escape,
    _format_value,
    _leaderboard_table,
    _routing_snippet,
)
from .local import compare_backends_dataset, forecast_dataset, forecast_stream_csv
from .utils import ensure_dir, read_json, slugify, write_json

_REPO_ROOT = Path(__file__).resolve().parents[1]

_EXTRA_CSS = """
.example-card-grid,
.media-grid,
.learn-grid {
  display: grid;
  gap: 16px;
}

.example-card-grid,
.media-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.learn-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.learn-card,
.note-card,
.media-card {
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--surface-strong);
  box-shadow: var(--shadow-sm);
}

.learn-card,
.note-card {
  padding: 18px;
}

.learn-card strong,
.note-card strong {
  display: block;
  margin-bottom: 8px;
}

.example-meta,
.breadcrumbs,
.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.breadcrumbs {
  margin-bottom: 18px;
  color: var(--text-muted);
  font-size: 0.92rem;
}

.breadcrumbs a {
  color: var(--blue);
  font-weight: 700;
}

.tag {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 6px 10px;
  background: var(--sun-soft);
  border: 1px solid rgba(255, 200, 61, 0.35);
  color: #805400;
  font-size: 0.8rem;
  font-weight: 700;
}

.example-card {
  overflow: hidden;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: var(--surface-strong);
  box-shadow: var(--shadow-sm);
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
}

.example-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(47, 107, 255, 0.18);
}

.example-card img,
.media-card img {
  width: 100%;
  border-bottom: 1px solid var(--border);
}

.example-card-body,
.media-card-body {
  padding: 18px;
}

.example-card p,
.media-card p {
  color: var(--text-muted);
}

.section-kicker {
  margin: 0 0 10px;
  color: var(--blue);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.note-stack {
  display: grid;
  gap: 12px;
}

.media-card h3 {
  margin: 0 0 10px;
}

@media (max-width: 720px) {
  .example-card-grid,
  .media-grid,
  .learn-grid {
    grid-template-columns: 1fr;
  }
}
"""

_IMAGE_LABELS = {
    "forecast_png": "Forecast chart",
    "comparison_png": "Backend comparison",
    "forecast_card_png": "Forecast card",
    "leaderboard_card_png": "Leaderboard card",
    "delta_card_png": "Winner delta card",
    "drift_alert_card_png": "Drift alert card",
}


@dataclass(frozen=True)
class ExampleSpec:
    example_id: str
    category: str
    title: str
    lead: str
    dataset_id: str
    why_it_matters: str
    tutorial_steps: tuple[str, ...]
    tags: tuple[str, ...]
    script_path: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "example_id": self.example_id,
            "category": self.category,
            "title": self.title,
            "lead": self.lead,
            "dataset_id": self.dataset_id,
            "why_it_matters": self.why_it_matters,
            "tutorial_steps": list(self.tutorial_steps),
            "tags": list(self.tags),
            "script_path": self.script_path,
        }


_EXAMPLES: tuple[ExampleSpec, ...] = (
    ExampleSpec(
        example_id="first-forecast-pack",
        category="Getting Started",
        title="First forecast pack in one command",
        lead="Route a bundled retail series through backend auto-selection and publish charts, CSV, markdown, and JSON.",
        dataset_id="sales",
        why_it_matters="This is the smallest end-to-end workflow. It teaches the artifact contract before any model tuning.",
        tutorial_steps=(
            "Start with a bundled dataset so the entire flow is reproducible.",
            "Inspect the selected backend and the pack written under data, plots, reports, and meta.",
            "Reuse the generated CSV and JSON instead of rebuilding post-processing by hand.",
        ),
        tags=("quickstart", "artifact-contract", "auto-routing"),
        script_path="examples/scripts/first_forecast_pack.py",
    ),
    ExampleSpec(
        example_id="backend-arena",
        category="Model Selection",
        title="Backend arena on the gold series",
        lead="Compare baseline, classical, tabular, and streaming backends on one market-style series.",
        dataset_id="gold",
        why_it_matters="This example shows that the package is not tied to one model family. The point is the common output surface and leaderboard diagnostics.",
        tutorial_steps=(
            "Run several backend families on the same target.",
            "Read the leaderboard before trusting the winner.",
            "Use the comparison chart and delta card when you need a defensible backend choice.",
        ),
        tags=("leaderboard", "comparison", "backend-selection"),
        script_path="examples/scripts/backend_arena.py",
    ),
    ExampleSpec(
        example_id="time-series-as-regression",
        category="Time Series As Regression",
        title="Time series to regression with custom lags",
        lead="Turn a sequence with exogenous signals into a supervised regression problem with lag points, spaced delays, rolling windows, and optional tsfresh descriptors.",
        dataset_id="gold-exogenous",
        why_it_matters="This is the clearest example of the package framing a time series as a tabular regression problem instead of hiding the feature layer.",
        tutorial_steps=(
            "Choose explicit lag points for short and medium memory.",
            "Add evenly spaced delay features with lag_step and lag_count.",
            "Optionally extend the feature block with tsfresh descriptors when the extra is installed.",
        ),
        tags=("lag-features", "regression", "tsfresh"),
        script_path="examples/scripts/time_series_as_regression.py",
    ),
    ExampleSpec(
        example_id="calibrated-intervals",
        category="Uncertainty",
        title="Calibrated prediction intervals",
        lead="Generate interval bands without changing the forecast.csv contract and inspect coverage and width diagnostics.",
        dataset_id="sales",
        why_it_matters="The interval example proves the package can emit calibrated uncertainty artifacts rather than only point forecasts.",
        tutorial_steps=(
            "Enable conformal intervals with a stable list of levels.",
            "Inspect lower_* and upper_* columns in forecast.csv.",
            "Review empirical coverage and interval width from diagnostics before trusting the band.",
        ),
        tags=("conformal", "intervals", "diagnostics"),
        script_path="examples/scripts/calibrated_intervals.py",
    ),
    ExampleSpec(
        example_id="streaming-drift-watch",
        category="Streaming Operations",
        title="Streaming forecast with drift monitoring",
        lead="Run a streaming backend on ICU bed stress data and publish a drift alert card alongside the forecast pack.",
        dataset_id="icu-bed-stress",
        why_it_matters="This example shows how the same product surface supports monitoring-style time series, not just static offline forecasts.",
        tutorial_steps=(
            "Choose a streaming backend and forecast in monitoring mode.",
            "Inspect the drift diagnostics and drift alert card.",
            "Use the same artifacts for dashboards, alerts, and agent workflows.",
        ),
        tags=("streaming", "monitoring", "drift"),
        script_path="examples/scripts/streaming_drift_watch.py",
    ),
)

_EXAMPLE_ORDER = {spec.example_id: index for index, spec in enumerate(_EXAMPLES)}


def list_examples() -> list[dict[str, Any]]:
    return [spec.to_dict() for spec in _EXAMPLES]


def _get_example_spec(example_id: str) -> ExampleSpec:
    for spec in _EXAMPLES:
        if spec.example_id == example_id:
            return spec
    raise ValueError(f"Unknown example '{example_id}'.")


def _examples_page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{_escape(title)}</title>
<style>{_BASE_CSS}{_EXTRA_CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def _examples_topbar(anchor_links: list[tuple[str, str]], *, home_href: str, cta_href: str, cta_label: str) -> str:
    links = "".join(f"<a class='nav-link' href='{_escape(href)}'>{_escape(label)}</a>" for label, href in anchor_links)
    return (
        "<header class='topbar'><div class='shell topbar-inner'>"
        f"<a class='brand' href='{_escape(home_href)}'>"
        "<span class='brand-mark'>AF</span>"
        "<span class='brand-copy'><strong>agentforecast</strong><small>tutorial-grade runnable examples</small></span>"
        "</a>"
        f"<nav class='nav-links'>{links}<a class='button button-primary' href='{_escape(cta_href)}'>{_escape(cta_label)}</a></nav>"
        "</div></header>"
    )


def _example_preview(public_artifacts: dict[str, str]) -> str | None:
    for kind in ("comparison_png", "forecast_png", "forecast_card_png", "drift_alert_card_png", "leaderboard_card_png"):
        if kind in public_artifacts:
            return public_artifacts[kind]
    return None


def _example_card(entry: dict[str, Any]) -> str:
    preview = _example_preview(entry["public_artifacts"])
    preview_html = f"<img src='{_escape(preview)}' alt='{_escape(entry['title'])}'>" if preview else ""
    metrics = entry["result"].get("metrics", {})
    lead_metric = f"MAE {_format_value(metrics.get('mae', 'n/a'))}"
    if "coverage_90" in metrics:
        lead_metric = f"coverage_90 {_format_value(metrics['coverage_90'])}"
    streaming = entry["result"].get("diagnostics", {}).get("streaming", {})
    if streaming and "drift_ratio" in streaming:
        lead_metric = f"drift_ratio {_format_value(streaming['drift_ratio'])}"
    return (
        "<article class='example-card'>"
        f"{preview_html}"
        "<div class='example-card-body'>"
        f"<div class='mini-row'><span class='badge'>{_escape(entry['category'])}</span><span class='muted'>{_escape(entry['result']['backend_selected'])}</span></div>"
        f"<h3><a href='examples/{_escape(entry['example_id'])}.html'>{_escape(entry['title'])}</a></h3>"
        f"<p>{_escape(entry['lead'])}</p>"
        "<div class='example-meta'>"
        f"<span class='pill'>{_escape(entry['dataset_id'])}</span>"
        f"<span class='pill pill-blue'>{_escape(lead_metric)}</span>"
        "</div>"
        "</div>"
        "</article>"
    )


def _metric_grid(entry: dict[str, Any]) -> str:
    result = entry["result"]
    summary = result.get("summary", {})
    metrics = result.get("metrics", {})
    cards: list[tuple[str, Any]] = [
        ("Selected backend", result.get("backend_selected", "unknown")),
        ("Dataset", entry["dataset_id"]),
        ("Horizon", result.get("inputs", {}).get("horizon", "n/a")),
        ("MAE", metrics.get("mae", "n/a")),
        ("Projected end", summary.get("projected_end", "n/a")),
        ("Artifacts", len(entry["public_artifacts"])),
    ]
    if "coverage_90" in metrics:
        cards.append(("Coverage 90", metrics["coverage_90"]))
    if "avg_width_90" in metrics:
        cards.append(("Avg width 90", metrics["avg_width_90"]))
    streaming = result.get("diagnostics", {}).get("streaming", {})
    if "drift_ratio" in streaming:
        cards.append(("Drift ratio", streaming["drift_ratio"]))
    return (
        "<div class='metric-grid'>"
        + "".join(
            "<article class='metric-card'>"
            f"<div class='muted'>{_escape(label)}</div><strong>{_escape(_format_value(value))}</strong>"
            "</article>"
            for label, value in cards
        )
        + "</div>"
    )


def _learn_grid(steps: list[str]) -> str:
    return (
        "<div class='learn-grid'>"
        + "".join(
            "<article class='learn-card'>"
            f"<strong>Step {idx}</strong><div class='muted'>{_escape(step)}</div>"
            "</article>"
            for idx, step in enumerate(steps, start=1)
        )
        + "</div>"
    )


def _media_grid(public_artifacts: dict[str, str]) -> str:
    cards = []
    for kind, label in _IMAGE_LABELS.items():
        path = public_artifacts.get(kind)
        if not path:
            continue
        cards.append(
            "<article class='media-card'>"
            f"<a href='../{_escape(path)}'><img src='../{_escape(path)}' alt='{_escape(label)}'></a>"
            "<div class='media-card-body'>"
            f"<h3>{_escape(label)}</h3>"
            f"<p>{_escape(kind)}</p>"
            "</div>"
            "</article>"
        )
    if not cards:
        return "<div class='note-card'><strong>No preview images</strong><div class='muted'>This example did not publish image artifacts.</div></div>"
    return "<div class='media-grid'>" + "".join(cards) + "</div>"


def _json_block(payload: Any) -> str:
    return "<div class='code-block'>" + _escape(json.dumps(payload, ensure_ascii=False, indent=2)) + "</div>"


def _copy_public_artifacts(example_root: Path, site_dir: Path, example_id: str, entry: dict[str, Any]) -> dict[str, str]:
    copied: dict[str, str] = {}
    pack_root = example_root / entry.get("pack_dir", "run")
    for artifact in entry["result"].get("artifacts", []):
        src = pack_root / artifact["path"]
        if src.exists() and src.suffix.lower() in {".png", ".csv", ".json", ".md"}:
            copied[artifact["kind"]] = _copy_artifact(src, site_dir, example_id)
    script_path = example_root / Path(entry["script_path"]).name
    if script_path.exists():
        copied["source_py"] = _copy_artifact(script_path, site_dir, example_id)
    manifest_path = example_root / "example.json"
    if manifest_path.exists():
        copied["example_json"] = _copy_artifact(manifest_path, site_dir, example_id)
    return copied


def _write_index(site_dir: Path, entries: list[dict[str, Any]]) -> None:
    topbar = _examples_topbar(
        [("Workflow", "#workflow"), ("Examples", "#examples"), ("Feed", "feed.json")],
        home_href="index.html",
        cta_href="#examples",
        cta_label="Browse examples",
    )
    categories = list(dict.fromkeys(entry["category"] for entry in entries))
    datasets = sorted({entry["dataset_id"] for entry in entries})
    png_count = sum(1 for entry in entries for kind in _IMAGE_LABELS if kind in entry["public_artifacts"])
    hero = (
        "<section class='hero'>"
        "<div class='hero-copy'>"
        "<div class='eyebrow'>Runnable tutorial gallery</div>"
        "<h1>agentforecast example hub</h1>"
        "<p>Each example in this gallery is backed by a real run, real artifacts, and a real source script. The goal is not a thin command list. The goal is a reproducible path from idea to forecast pack.</p>"
        "<div class='hero-actions'>"
        "<a class='button button-primary' href='#examples'>Explore examples</a>"
        "<a class='button button-secondary' href='feed.json'>Open feed</a>"
        "</div>"
        "<div class='hero-meta'>"
        "<span class='pill pill-accent'>real runs only</span>"
        "<span class='pill'>scripts included</span>"
        "<span class='pill pill-blue'>visual artifacts copied into the site</span>"
        "</div>"
        f"{_author_strip()}"
        "</div>"
        "<div class='panel hero-panel'>"
        "<h3>How to regenerate</h3>"
        "<p class='muted'>Build the same outputs locally with one command.</p>"
        "<div class='stat-grid'>"
        f"<article class='stat-card'><div class='muted'>Examples</div><strong>{_escape(len(entries))}</strong><div class='muted'>Tutorial-grade runs with copied artifacts.</div></article>"
        f"<article class='stat-card'><div class='muted'>Categories</div><strong>{_escape(len(categories))}</strong><div class='muted'>Grouped like an auto_examples gallery.</div></article>"
        f"<article class='stat-card'><div class='muted'>Datasets</div><strong>{_escape(len(datasets))}</strong><div class='muted'>{_escape(', '.join(datasets))}</div></article>"
        f"<article class='stat-card'><div class='muted'>PNG artifacts</div><strong>{_escape(png_count)}</strong><div class='muted'>Forecast, comparison, leaderboard, and drift cards.</div></article>"
        "</div>"
        "<div class='code-block'>python -m agentforecast.cli demo-examples --outdir examples/generated --site-dir examples/site</div>"
        "</div>"
        "</section>"
    )
    workflow = (
        "<section class='section' id='workflow'>"
        "<div class='section-head'><div><div class='section-kicker'>Workflow</div><h2>Learn from real outputs</h2></div>"
        "<p>This hub pairs a runnable script with published plots, metrics, markdown, CSV, and JSON so the examples are inspectable from several angles.</p></div>"
        "<div class='learn-grid'>"
        "<article class='learn-card'><strong>1. Read the use case</strong><div class='muted'>Each card states why the example exists and what it teaches.</div></article>"
        "<article class='learn-card'><strong>2. Run the command</strong><div class='muted'>Every example page includes a CLI command and the source script used to generate the run.</div></article>"
        "<article class='learn-card'><strong>3. Inspect diagnostics</strong><div class='muted'>Leaderboards, routing, uncertainty, and streaming diagnostics stay visible instead of being buried.</div></article>"
        "<article class='learn-card'><strong>4. Reuse artifacts</strong><div class='muted'>Open forecast.csv, summary.md, metadata.json, and the generated plots directly from the page.</div></article>"
        "</div>"
        "</section>"
    )
    category_sections = []
    for category in categories:
        section_entries = [entry for entry in entries if entry["category"] == category]
        cards = "".join(_example_card(entry) for entry in section_entries)
        category_sections.append(
            f"<section class='section' id='{_escape(slugify(category))}'>"
            f"<div class='section-head'><div><div class='section-kicker'>{_escape(category)}</div><h2>{_escape(category)}</h2></div>"
            "<p>Curated runnable cases with copied artifacts, source scripts, and visible diagnostics.</p></div>"
            f"<div class='example-card-grid'>{cards}</div>"
            "</section>"
        )
    footer = (
        "<footer class='footer'><div class='footer-card'>"
        "<div><strong>Examples live next to the package.</strong><div class='footer-note'>Source scripts are under examples/scripts and generated packs are under examples/generated.</div></div>"
        "<a class='button button-secondary' href='feed.json'>Download feed.json</a>"
        "</div></footer>"
    )
    body = (
        f"{topbar}<main class='page'><div class='shell'>{hero}{workflow}"
        "<section class='section' id='examples'><div class='section-head'><div><div class='section-kicker'>Examples</div><h2>Curated runnable cases</h2></div><p>These cases cover onboarding, backend selection, regression framing, uncertainty, and streaming operations.</p></div></section>"
        f"{''.join(category_sections)}{footer}</div></main>"
    )
    (site_dir / "index.html").write_text(_examples_page("agentforecast example hub", body), encoding="utf-8")


def _write_example_page(site_dir: Path, entry: dict[str, Any]) -> None:
    public_artifacts = entry["public_artifacts"]
    result = entry["result"]
    diagnostics = result.get("diagnostics", {})
    dataset = get_dataset_spec(entry["dataset_id"]).to_dict("en")
    tag_html = "".join(f"<span class='tag'>{_escape(tag)}</span>" for tag in entry["tags"])
    topbar = _examples_topbar(
        [("Examples", "../index.html#examples"), ("Feed", "../feed.json")],
        home_href="../index.html",
        cta_href="../index.html#examples",
        cta_label="Browse examples",
    )
    notes = "".join(
        "<article class='note-card'>"
        f"<strong>Note</strong><div class='muted'>{_escape(note)}</div>"
        "</article>"
        for note in entry.get("runtime_notes", [])
    )
    notes_block = f"<div class='note-stack'>{notes}</div>" if notes else ""
    conformal_block = ""
    if diagnostics.get("conformal"):
        conformal_block = (
            "<section class='section'>"
            "<div class='section-head'><div><div class='section-kicker'>Uncertainty</div><h2>Conformal diagnostics</h2></div>"
            "<p>Coverage and interval width are part of the example, not an afterthought.</p></div>"
            f"{_json_block(diagnostics['conformal'])}"
            "</section>"
        )
    streaming_block = ""
    if diagnostics.get("streaming"):
        streaming_block = (
            "<section class='section'>"
            "<div class='section-head'><div><div class='section-kicker'>Streaming</div><h2>Drift diagnostics</h2></div>"
            "<p>Streaming examples keep drift context visible alongside the forecast pack.</p></div>"
            f"{_json_block(diagnostics['streaming'])}"
            "</section>"
        )
    leaderboard_block = ""
    leaderboard = diagnostics.get("leaderboard") or result.get("leaderboard")
    if leaderboard:
        leaderboard_block = (
            "<section class='section'>"
            "<div class='section-head'><div><div class='section-kicker'>Leaderboard</div><h2>Backend evidence</h2></div>"
            "<p>The winning backend is shown together with the competing candidates.</p></div>"
            f"{_leaderboard_table(leaderboard)}"
            "</section>"
        )
    body = (
        f"{topbar}<main class='page'><div class='shell'>"
        "<div class='breadcrumbs'><a href='../index.html'>Examples</a><span>/</span>"
        f"<span>{_escape(entry['title'])}</span></div>"
        "<section class='case-header'>"
        "<div>"
        f"<div class='eyebrow'>{_escape(entry['category'])}</div>"
        f"<h1>{_escape(entry['title'])}</h1>"
        f"<p class='case-lead'>{_escape(entry['lead'])}</p>"
        f"<div class='tag-row'>{tag_html}</div>"
        f"{_author_strip()}"
        "</div>"
        "<div class='case-panel'>"
        "<h3>Dataset context</h3>"
        f"<div class='muted'>{_escape(dataset['title'])}</div>"
        f"<div class='muted'>{_escape(dataset['description'])}</div>"
        f"<div class='muted'>Provenance: {_escape(dataset['provenance'])}</div>"
        "</div>"
        "</section>"
        "<section class='section'>"
        "<div class='section-head'><div><div class='section-kicker'>Why this example</div><h2>What it teaches</h2></div>"
        f"<p>{_escape(entry['why_it_matters'])}</p></div>"
        f"{_learn_grid(entry['tutorial_steps'])}"
        f"{notes_block}"
        "</section>"
        "<section class='section'>"
        "<div class='section-head'><div><div class='section-kicker'>Run it</div><h2>CLI and source</h2></div>"
        "<p>Use the command below or adapt the source script directly.</p></div>"
        f"<div class='code-block'>{_escape(entry['cli_command'])}</div>"
        f"<div class='code-block'>{_escape(entry.get('script_source', ''))}</div>"
        "</section>"
        "<section class='section'>"
        "<div class='section-head'><div><div class='section-kicker'>Result</div><h2>Executed outcome</h2></div>"
        f"<p>{_escape(result.get('summary', {}).get('narrative', entry['lead']))}</p></div>"
        f"{_metric_grid(entry)}"
        "</section>"
        "<section class='section'>"
        "<div class='section-head'><div><div class='section-kicker'>Visuals</div><h2>Generated charts and cards</h2></div>"
        "<p>These previews are copied from the real run artifacts written under the example output directory.</p></div>"
        f"{_media_grid(public_artifacts)}"
        "</section>"
        f"{leaderboard_block}"
        "<section class='section'>"
        "<div class='section-head'><div><div class='section-kicker'>Routing</div><h2>Routing rationale</h2></div>"
        "<p>The package keeps routing visible so backend choice is inspectable.</p></div>"
        f"{_routing_snippet({'diagnostics': diagnostics})}"
        "</section>"
        f"{conformal_block}"
        f"{streaming_block}"
        "<section class='section'>"
        "<div class='section-head'><div><div class='section-kicker'>Artifacts</div><h2>Open exported files</h2></div>"
        "<p>The example page links directly to the copied artifacts so you can inspect data, reports, and metadata without leaving the site.</p></div>"
        f"{_artifact_cards(public_artifacts)}"
        "</section>"
        "</div></main>"
    )
    page_dir = ensure_dir(site_dir / "examples")
    (page_dir / f"{entry['example_id']}.html").write_text(_examples_page(entry["title"], body), encoding="utf-8")


def _run_example(spec: ExampleSpec, outdir: Path) -> tuple[dict[str, Any], str, list[str]]:
    runtime_notes: list[str] = []
    if spec.example_id == "first-forecast-pack":
        result = forecast_dataset("sales", outdir=outdir, strategy="fast")
        cli_command = "python -m agentforecast.cli shoot sales --outdir examples/generated/first-forecast-pack"
    elif spec.example_id == "backend-arena":
        candidate = [backend_id for backend_id in ["naive", "moving_average", "stats_arima", "stats_ets", "ml_ridge", "stream_ewm"] if is_backend_available(backend_id)]
        result = compare_backends_dataset("gold", backends=candidate, outdir=outdir)
        cli_command = "python -m agentforecast.cli compare-dataset gold --backends " + ",".join(candidate) + " --outdir examples/generated/backend-arena"
        missing = [backend_id for backend_id in ["stats_arima", "stats_ets", "ml_ridge"] if backend_id not in candidate]
        if missing:
            runtime_notes.append("This run excluded unavailable extras: " + ", ".join(missing) + ".")
    elif spec.example_id == "time-series-as-regression":
        include_tsfresh = importlib.util.find_spec("tsfresh") is not None
        feature_spec = FeatureSpec(
            mode="tutorial_regression",
            lag_points=(1, 2, 3, 7, 14, 28),
            lag_step=7,
            lag_count=4,
            rolling_windows=(3, 7, 14, 28),
            include_tsfresh=include_tsfresh,
            tsfresh_window=28,
        )
        result = forecast_dataset("gold-exogenous", backend="ml_ridge", outdir=outdir, feature_spec=feature_spec)
        cli_command = (
            "python -m agentforecast.cli forecast-dataset gold-exogenous --backend ml_ridge "
            "--lag-points 1,2,3,7,14,28 --lag-step 7 --lag-count 4 --rolling-windows 3,7,14,28 "
            "--outdir examples/generated/time-series-as-regression"
        )
        if include_tsfresh:
            cli_command += " --tsfresh --tsfresh-window 28"
            runtime_notes.append("`tsfresh` was installed in this environment, so compact tsfresh descriptors were included.")
        else:
            runtime_notes.append("`tsfresh` was not installed in this environment, so this run used lag, delay, rolling, and calendar features only.")
    elif spec.example_id == "calibrated-intervals":
        backend = "river_linear" if is_backend_available("river_linear") else "stream_ewm"
        conformal = ConformalSpec(
            enabled=True,
            method="auto" if backend == "river_linear" else "rolling_residual",
            levels=(80, 90, 95),
            calibration_window=60,
            warmup_min=10,
        )
        result = forecast_dataset("sales", backend=backend, outdir=outdir, conformal=conformal)
        cli_command = (
            f"python -m agentforecast.cli forecast-dataset sales --backend {backend} --conformal "
            f"--conformal-method {conformal.method} --levels 80,90,95 --calibration-window 60 --warmup-min 10 "
            "--outdir examples/generated/calibrated-intervals"
        )
        if backend == "river_linear":
            runtime_notes.append("This run used River jackknife intervals through `river_linear`.")
        else:
            runtime_notes.append("River was not available, so this run used the rolling residual conformal fallback on `stream_ewm`.")
    elif spec.example_id == "streaming-drift-watch":
        backend = "river_snarimax" if is_backend_available("river_snarimax") else "stream_ewm"
        result = forecast_stream_csv(dataset_path("icu-bed-stress"), backend=backend, horizon=14, outdir=outdir)
        cli_command = (
            f"python -m agentforecast.cli forecast-stream agentforecast/package_data/datasets/icu_bed_stress.csv "
            f"--backend {backend} --horizon 14 --outdir examples/generated/streaming-drift-watch"
        )
        if backend == "river_snarimax":
            runtime_notes.append("This run used the River streaming forecaster path.")
        else:
            runtime_notes.append("River was not available, so this run used the built-in `stream_ewm` fallback.")
    else:
        raise ValueError(f"Unknown example '{spec.example_id}'.")

    payload = result.to_dict() if hasattr(result, "to_dict") else result
    return payload, cli_command, runtime_notes


def demo_examples(
    outdir: str | Path = "examples/generated",
    site_dir: str | Path = "examples/site",
    *,
    example_ids: list[str] | tuple[str, ...] | None = None,
) -> dict[str, Any]:
    runs_root = Path(outdir)
    if runs_root.exists():
        shutil.rmtree(runs_root)
    runs_root.mkdir(parents=True, exist_ok=True)

    chosen_specs = [_get_example_spec(example_id) for example_id in example_ids] if example_ids else list(_EXAMPLES)
    items: list[dict[str, Any]] = []
    warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")

    for spec in chosen_specs:
        example_root = ensure_dir(runs_root / spec.example_id)
        with tempfile.TemporaryDirectory() as tmpdir:
            payload, cli_command, runtime_notes = _run_example(spec, Path(tmpdir))
            pack_root = Path(tmpdir) / slugify(payload["inputs"]["name"])
            shutil.copytree(pack_root, example_root / "run")
        script_source_path = _REPO_ROOT / spec.script_path
        script_source = script_source_path.read_text(encoding="utf-8") if script_source_path.exists() else ""
        if script_source_path.exists():
            shutil.copy2(script_source_path, example_root / script_source_path.name)
        manifest = {
            **spec.to_dict(),
            "pack_dir": "run",
            "cli_command": cli_command,
            "runtime_notes": runtime_notes,
            "script_source": script_source,
            "result": payload,
        }
        write_json(example_root / "example.json", manifest)
        items.append(
            {key: value for key, value in manifest.items() if key not in {"script_source", "result"}}
            | {"backend_selected": payload["backend_selected"], "headline": payload["summary"]["headline"]}
        )

    write_json(runs_root / "manifest.json", {"kind": "agentforecast.examples_manifest", "example_count": len(items), "items": items})
    site_manifest = build_examples_site(runs_root, site_dir)
    return {
        "kind": "agentforecast.demo_examples",
        "example_count": len(items),
        "runs_root": runs_root.resolve().as_posix(),
        "site_dir": Path(site_dir).resolve().as_posix(),
        "items": items,
        "site": site_manifest,
    }


def build_examples_site(runs_root: str | Path, site_dir: str | Path) -> dict[str, Any]:
    runs_root = Path(runs_root)
    site_dir = Path(site_dir)
    if site_dir.exists():
        shutil.rmtree(site_dir)
    ensure_dir(site_dir)

    entries: list[dict[str, Any]] = []
    for example_json in sorted(runs_root.glob("*/example.json")):
        entry = read_json(example_json)
        entry["public_artifacts"] = _copy_public_artifacts(example_json.parent, site_dir, entry["example_id"], entry)
        entries.append(entry)
    entries.sort(key=lambda entry: _EXAMPLE_ORDER.get(entry["example_id"], len(_EXAMPLE_ORDER)))

    _write_index(site_dir, entries)
    for entry in entries:
        _write_example_page(site_dir, entry)

    feed = {
        "kind": "agentforecast.examples_feed",
        "site_title": "agentforecast example hub",
        "entry_count": len(entries),
        "items": [
            {
                "example_id": entry["example_id"],
                "title": entry["title"],
                "category": entry["category"],
                "dataset_id": entry["dataset_id"],
                "backend_selected": entry["result"]["backend_selected"],
                "page": f"examples/{entry['example_id']}.html",
                "headline": entry["result"]["summary"]["headline"],
            }
            for entry in entries
        ],
    }
    write_json(site_dir / "feed.json", feed)
    return {
        "kind": "agentforecast.examples_site",
        "site_dir": site_dir.resolve().as_posix(),
        "entry_count": len(entries),
        "index_path": (site_dir / "index.html").resolve().as_posix(),
        "feed_path": (site_dir / "feed.json").resolve().as_posix(),
        "examples": [
            {
                "example_id": entry["example_id"],
                "page": f"examples/{entry['example_id']}.html",
                "backend_selected": entry["result"]["backend_selected"],
            }
            for entry in entries
        ],
    }
