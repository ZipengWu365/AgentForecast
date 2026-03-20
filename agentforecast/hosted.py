from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import html
import json
import shutil

from .backends import list_backend_capabilities, list_backends
from .benchmark_hub import list_external_benchmarks
from .doctor import diagnose_environment
from .utils import ensure_dir, read_json

AUTHOR_NAME = "Zipeng Wu"
AUTHOR_EMAIL = "zxw365@student.bham.ac.uk"
AUTHOR_AFFILIATION = "The University of Birmingham"

_FAMILY_COPY = {
    "baseline": (
        "Baseline references",
        "Fast reference models for last-value carry, recent averages, drift, and simple seasonal repeats.",
    ),
    "classical": (
        "Classical forecasting",
        "ARIMA and ETS style models for interpretable seasonality, smoother long-horizon structure, and low-data runs.",
    ),
    "tabular": (
        "Time series as regression",
        "Lag-feature regression with Ridge, boosting, tree ensembles, and optional MLForecast-style adapters.",
    ),
    "streaming": (
        "Streaming and online learning",
        "Incremental forecasters and online regressors for rolling updates, drift monitoring, and low-latency refreshes.",
    ),
    "deep": (
        "Deep forecasting adapters",
        "Optional neural backends for longer-horizon experiments when the lean surface is not enough.",
    ),
    "automl": (
        "AutoML adapters",
        "Optional automation paths for larger search spaces and managed forecasting workflows.",
    ),
    "tabpfn": (
        "Experimental tabular priors",
        "Optional TabPFN-style regressors for compact tabular forecasting experiments.",
    ),
}

_CAPABILITY_COPY = (
    ("Auto routing", "Compare candidate backends automatically and keep the leaderboard visible instead of hiding model choice."),
    ("Time series as regression", "Expose lag points, spaced delays, rolling windows, calendar fields, and optional tsfresh descriptors."),
    ("Prediction intervals", "Emit conformal-style lower_* / upper_* bands with coverage and width diagnostics."),
    ("Exogenous signals", "Carry external regressors through lag-feature backends and adapters that support exogenous inputs."),
    ("Streaming drift watch", "Publish rolling diagnostics and drift alert cards alongside streaming forecast packs."),
    ("Publishable artifacts", "Export plots, cards, CSV, markdown, and JSON for both human readers and agents."),
)

_SURFACE_COPY = (
    ("Pack Surface", "One-shot forecast packs, backend comparison, charts, cards, markdown, and JSON artifacts.", "forecast_dataframe, compare_backends_frame, forecast_csv"),
    ("Research Surface", "Explicit benchmark-first APIs with fit / predict / update, strict_mode, multi-horizon output, and auditable defaults.", "OnlineForecaster, forecast_benchmark_dataframe"),
    ("Operations Surface", "Streaming watch flows, drift diagnostics, and low-latency rolling forecast outputs.", "forecast_stream_dataframe, stream_ewm, river_*"),
    ("Agent Surface", "Tool server, MCP, structured JSON contracts, and environment diagnostics for automation.", "doctor, tool_server, mcp_server"),
)

_INSTALL_MATRIX = (
    ("beginner / pack user", "pip install agentforecast", "one-shot forecast packs and backend auto-routing"),
    ("research / benchmark", 'pip install "agentforecast[stats,ml]"', "strict benchmark runs, comparison work, OnlineForecaster"),
    ("streaming / operations", 'pip install "agentforecast[stream]"', "River backends and streaming watch flows"),
    ("full optional stack", 'pip install "agentforecast[all]"', "widest adapter coverage"),
)

_MODEL_SELECTION_COPY = (
    (
        "Baseline and seasonal references",
        "Real practical baselines for sanity checks and low-data series.",
        "naive, seasonal_naive, moving_average, drift",
    ),
    (
        "Statistical workhorses",
        "Classical models that remain strong in real business forecasting when data is limited and seasonality matters.",
        "stats_ets, stats_arima, statsforecast_autoets, statsforecast_autoarima",
    ),
    (
        "Time series as regression",
        "Lag-feature regressors for practical tabular forecasting with exogenous variables.",
        "ml_ridge, ml_histgb, ml_xgboost, ml_lightgbm, ml_catboost, mlforecast_linear, mlforecast_xgboost",
    ),
    (
        "Streaming and online models",
        "Incremental models for rolling updates, low-latency refreshes, and drift-aware operation.",
        "stream_ewm, stream_sgd, river_linear, river_snarimax, river_holtwinters",
    ),
)

_API_SURFACE_COPY = (
    {
        "badge": "research",
        "name": "OnlineForecaster",
        "headline": "The stable low-level forecasting contract for fit / predict / update benchmark workflows.",
        "details": (
            ("Call", "OnlineForecaster(backend='river_linear', horizons=[1,3,6], strict_mode=True)"),
            ("Use when", "You need a serious forecasting core instead of a one-shot pack helper."),
            ("Returns", "A stateful object with fit(), predict(), update(), and auditable state()."),
        ),
        "tags": ("python", "research", "stateful"),
    },
    {
        "badge": "benchmark",
        "name": "forecast_benchmark_dataframe",
        "headline": "One-shot low-level benchmark forecasting with horizons=[...] and recursive or direct mode.",
        "details": (
            ("Call", "forecast_benchmark_dataframe(df, backend='ml_ridge', horizons=[1,3,6], mode='direct')"),
            ("Use when", "You want benchmark-safe forecasting without pack/report generation."),
            ("Returns", "Forecast rows, prediction dict, feature spec, cleanup, and diagnostics."),
        ),
        "tags": ("python", "benchmark", "multi-horizon"),
    },
    {
        "badge": "doctor",
        "name": "diagnose_environment",
        "headline": "Report which backends are importable, which extras are missing, and which workflows the environment supports.",
        "details": (
            ("Call", "diagnose_environment()"),
            ("Use when", "You want a calm answer to what is installed and what command to run next."),
            ("Returns", "Profiles, install hints, available backends, and capability metadata."),
        ),
        "tags": ("python", "doctor", "environment"),
    },
    {
        "badge": "data",
        "name": "validate_series_frame / clean_series_frame",
        "headline": "Separate strict validation from forgiving cleanup instead of hiding data mutation behind one helper.",
        "details": (
            ("Call", "validate_series_frame(df, strict_mode=True) or clean_series_frame(df)"),
            ("Use when", "You need to inspect timestamps, duplicates, cadence, and cleanup behavior explicitly."),
            ("Returns", "Validation report or cleaned PreparedSeries."),
        ),
        "tags": ("python", "validation", "cleanup"),
    },
    {
        "badge": "pack",
        "name": "forecast_dataframe / build_hosted_site",
        "headline": "The pack-oriented path for public forecast artifacts and static gallery publishing.",
        "details": (
            ("Call", "forecast_dataframe(df, name='series', horizon=12, backend='auto')"),
            ("Use when", "You want publishable charts, cards, markdown, JSON, and a browsable gallery."),
            ("Returns", "RunResult artifacts or a generated static site."),
        ),
        "tags": ("python", "static-site", "pages"),
    },
)


@dataclass
class GalleryEntry:
    slug: str
    title: str
    headline: str
    backend_selected: str
    summary: dict[str, Any]
    diagnostics: dict[str, Any]
    metrics: dict[str, Any]
    artifact_map: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "title": self.title,
            "headline": self.headline,
            "backend_selected": self.backend_selected,
            "summary": self.summary,
            "diagnostics": self.diagnostics,
            "metrics": self.metrics,
            "artifacts": self.artifact_map,
        }


def _copy_artifact(src: Path, dst_root: Path, slug: str) -> str:
    dst_dir = ensure_dir(dst_root / "assets" / slug)
    dst = dst_dir / src.name
    shutil.copy2(src, dst)
    return dst.relative_to(dst_root).as_posix()


def _portable_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def collect_gallery_entries(runs_root: str | Path) -> list[GalleryEntry]:
    runs_root = Path(runs_root)
    entries: list[GalleryEntry] = []
    if not runs_root.exists():
        return entries
    for meta in sorted(runs_root.glob("*/meta/metadata.json")):
        payload = read_json(meta)
        root = meta.parent.parent
        artifact_map = {item["kind"]: _portable_path(root / item["path"]) for item in payload.get("artifacts", [])}
        entries.append(
            GalleryEntry(
                slug=root.name,
                title=payload.get("inputs", {}).get("name") or root.name,
                headline=payload.get("summary", {}).get("headline", root.name),
                backend_selected=payload.get("backend_selected", "unknown"),
                summary=payload.get("summary", {}),
                diagnostics=payload.get("diagnostics", {}),
                metrics=payload.get("metrics", {}),
                artifact_map=artifact_map,
            )
        )
    return entries


_BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

:root {
  --bg: #ffffff;
  --bg-soft: #fffdf5;
  --surface: #fafafa;
  --surface-strong: #ffffff;
  --card: #fafafa;
  --text: #1f2937;
  --text-muted: #6b7280;
  --border: #e5e7eb;
  --border-strong: #d8dde6;
  --sun: #ffc83d;
  --sun-soft: #fff4c2;
  --sun-strong: #efb81c;
  --blue: #2f6bff;
  --blue-soft: #eef4ff;
  --success: #1f8a5b;
  --warning: #ac6a00;
  --shadow-sm: 0 10px 30px rgba(31, 41, 55, 0.06);
  --shadow-lg: 0 18px 60px rgba(31, 41, 55, 0.1);
  --radius-xl: 28px;
  --radius-lg: 22px;
  --radius-md: 16px;
  --radius-sm: 12px;
}

* { box-sizing: border-box; }

html {
  scroll-behavior: smooth;
  background:
    radial-gradient(circle at top left, rgba(255, 244, 194, 0.68), transparent 28%),
    radial-gradient(circle at top right, rgba(47, 107, 255, 0.08), transparent 26%),
    var(--bg);
}

body {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  color: var(--text);
  line-height: 1.55;
}

a {
  color: inherit;
  text-decoration: none;
}

img {
  max-width: 100%;
  display: block;
}

.shell {
  width: min(1180px, calc(100vw - 32px));
  margin: 0 auto;
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  backdrop-filter: blur(16px);
  background: rgba(255, 255, 255, 0.84);
  border-bottom: 1px solid rgba(229, 231, 235, 0.9);
}

.topbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 16px 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  font-weight: 800;
  letter-spacing: -0.03em;
}

.brand-mark {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  background: linear-gradient(145deg, var(--sun), #ffe27a);
  color: #111827;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-sm);
}

.brand-copy small,
.eyebrow,
.meta-line,
.muted,
.footer-note {
  color: var(--text-muted);
}

.brand-copy strong {
  display: block;
  font-size: 0.97rem;
}

.brand-copy small {
  display: block;
  margin-top: 2px;
  font-size: 0.76rem;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.nav-link {
  color: var(--text-muted);
  font-size: 0.94rem;
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  border-radius: 999px;
  padding: 12px 18px;
  font-weight: 700;
  border: 1px solid transparent;
  transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}

.button:hover {
  transform: translateY(-1px);
}

.button-primary {
  background: linear-gradient(135deg, var(--sun), #ffe27a);
  color: #111827;
  box-shadow: var(--shadow-sm);
}

.button-secondary {
  background: var(--surface-strong);
  color: var(--text);
  border-color: var(--border);
}

.page {
  padding: 40px 0 72px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.9fr);
  gap: 28px;
  padding: 28px;
  border-radius: var(--radius-xl);
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(250, 250, 250, 0.98)),
    linear-gradient(145deg, rgba(255, 200, 61, 0.12), rgba(47, 107, 255, 0.05));
  border: 1px solid rgba(229, 231, 235, 0.9);
  box-shadow: var(--shadow-lg);
}

.hero h1,
.section-head h2,
.case-header h1 {
  margin: 0;
  letter-spacing: -0.04em;
  line-height: 1.05;
}

.hero h1 {
  font-size: clamp(2.6rem, 5vw, 4.7rem);
  max-width: 11ch;
}

.hero-copy p {
  margin: 18px 0 0;
  font-size: 1.06rem;
  max-width: 64ch;
  color: var(--text-muted);
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  font-size: 0.84rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.eyebrow::before {
  content: "";
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: var(--sun);
  box-shadow: 0 0 0 6px rgba(255, 200, 61, 0.18);
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface-strong);
  color: var(--text-muted);
  font-size: 0.87rem;
  font-weight: 600;
}

.pill-accent {
  background: var(--sun-soft);
  border-color: rgba(255, 200, 61, 0.35);
  color: #805400;
}

.pill-blue {
  background: var(--blue-soft);
  border-color: rgba(47, 107, 255, 0.18);
  color: var(--blue);
}

.author-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.author-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.82);
  color: var(--text-muted);
  font-size: 0.86rem;
  font-weight: 600;
}

.author-pill strong {
  color: var(--text);
}

.author-pill-uob {
  background: rgba(156, 28, 64, 0.08);
  border-color: rgba(156, 28, 64, 0.18);
  color: #7b1733;
}

.author-mark {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  background: linear-gradient(145deg, var(--sun), #ffe27a);
  color: #111827;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  font-weight: 800;
}

.panel {
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: var(--surface-strong);
  box-shadow: var(--shadow-sm);
}

.hero-panel {
  padding: 22px;
  display: grid;
  gap: 18px;
}

.hero-panel .stat-grid {
  grid-template-columns: repeat(2, minmax(160px, 1fr));
}

.stat-grid,
.feature-grid,
.card-grid,
.workflow-grid,
.metric-grid,
.artifact-grid,
.surface-grid,
.capability-grid {
  display: grid;
  gap: 16px;
}

.stat-grid,
.feature-grid,
.workflow-grid,
.capability-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.card-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.surface-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.metric-grid,
.artifact-grid {
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.stat-card,
.feature-card,
.workflow-card,
.gallery-card,
.artifact-card,
.metric-card,
.bench-card,
.case-panel,
.surface-card {
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--card);
}

.stat-card,
.metric-card {
  padding: 16px;
}

.stat-card strong,
.metric-card strong {
  display: block;
  margin-top: 10px;
  font-size: 1.42rem;
  line-height: 1;
  letter-spacing: -0.04em;
}

.feature-card,
.workflow-card,
.bench-card,
.case-panel,
.surface-card {
  padding: 18px;
}

.feature-card h3,
.workflow-card h3,
.section-head h2,
.gallery-card h3,
.bench-card h3,
.case-panel h3,
.surface-card h3 {
  margin: 0 0 10px;
}

.section {
  margin-top: 28px;
  padding: 28px;
  border-radius: var(--radius-xl);
  border: 1px solid rgba(229, 231, 235, 0.9);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: var(--shadow-sm);
}

.section-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
}

.section-head h2 {
  font-size: clamp(1.9rem, 3vw, 2.7rem);
}

.section-head p {
  max-width: 62ch;
  margin: 0;
  color: var(--text-muted);
}

.code-block {
  border-radius: var(--radius-md);
  border: 1px solid rgba(47, 107, 255, 0.12);
  background: #f8fbff;
  padding: 16px 18px;
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 0.88rem;
  color: #163063;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.gallery-card {
  overflow: hidden;
  transition: transform 0.24s ease, box-shadow 0.24s ease, border-color 0.24s ease;
}

.gallery-card-link {
  display: block;
}

.gallery-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(255, 200, 61, 0.48);
}

.gallery-card-media {
  padding: 16px 16px 0;
}

.gallery-card-media img {
  border-radius: 16px;
  border: 1px solid rgba(229, 231, 235, 0.85);
  background: #fff;
}

.gallery-card-body {
  padding: 18px;
}

.gallery-card-headline {
  color: var(--text-muted);
  min-height: 48px;
}

.gallery-card-footer,
.mini-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.mini-row {
  color: var(--text-muted);
  font-size: 0.9rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 0.8rem;
  font-weight: 700;
  background: var(--blue-soft);
  color: var(--blue);
}

.table-wrap {
  overflow-x: auto;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--surface-strong);
}

.surface-stack {
  display: grid;
  gap: 18px;
}

.section-subhead {
  display: grid;
  gap: 6px;
}

.section-subhead h3 {
  margin: 0;
  font-size: 1.1rem;
  letter-spacing: -0.02em;
}

.surface-pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.surface-list {
  margin: 12px 0 0;
  padding-left: 18px;
  color: var(--text-muted);
}

.surface-list li + li {
  margin-top: 6px;
}

.surface-card code {
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 0.85rem;
  color: #163063;
}

.table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.table thead th {
  background: #fffdf6;
  color: var(--text-muted);
  font-size: 0.82rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.table th,
.table td {
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  text-align: left;
}

.table tr:last-child td {
  border-bottom: 0;
}

.artifact-card {
  padding: 16px;
  display: grid;
  gap: 8px;
}

.artifact-card strong {
  font-size: 0.95rem;
}

.artifact-card code,
.mono {
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Consolas, monospace;
}

.artifact-card code {
  color: var(--text-muted);
  font-size: 0.8rem;
  word-break: break-word;
}

.artifact-card a {
  color: var(--blue);
  font-weight: 700;
}

.case-header {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(280px, 0.78fr);
  gap: 24px;
  padding: 28px;
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
  background: linear-gradient(160deg, rgba(255, 244, 194, 0.28), rgba(255, 255, 255, 0.94) 40%, rgba(47, 107, 255, 0.05));
  box-shadow: var(--shadow-lg);
}

.case-header h1 {
  font-size: clamp(2.2rem, 4vw, 4rem);
}

.case-lead {
  color: var(--text-muted);
  max-width: 64ch;
}

.case-panel {
  display: grid;
  gap: 14px;
}

.case-media img {
  border-radius: 20px;
  border: 1px solid rgba(229, 231, 235, 0.9);
  box-shadow: var(--shadow-sm);
}

.stack {
  display: grid;
  gap: 18px;
}

.footer {
  margin-top: 32px;
  padding: 24px 0 8px;
}

.footer-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 22px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: linear-gradient(145deg, #fffefb, #ffffff);
  box-shadow: var(--shadow-sm);
}

.footer-note {
  font-size: 0.92rem;
}

@media (max-width: 980px) {
  .hero,
  .case-header {
    grid-template-columns: 1fr;
  }

  .stat-grid,
  .feature-grid,
  .workflow-grid,
  .capability-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .shell {
    width: min(100vw - 20px, 1180px);
  }

  .topbar-inner,
  .section-head,
  .footer-card,
  .gallery-card-footer,
  .mini-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .page {
    padding: 24px 0 48px;
  }

  .hero,
  .section,
  .case-header {
    padding: 20px;
  }

  .hero h1,
  .case-header h1 {
    max-width: none;
  }

  .stat-grid,
  .feature-grid,
  .workflow-grid,
  .metric-grid,
  .artifact-grid,
  .capability-grid,
  .surface-grid {
    grid-template-columns: 1fr;
  }

  .hero-panel .stat-grid {
    grid-template-columns: 1fr;
  }
}
"""


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        magnitude = abs(value)
        if magnitude >= 1000:
            return f"{value:,.0f}"
        if magnitude >= 100:
            return f"{value:,.2f}"
        if magnitude >= 1:
            return f"{value:,.3f}".rstrip("0").rstrip(".")
        return f"{value:.4f}".rstrip("0").rstrip(".")
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def _escape(value: Any) -> str:
    return html.escape(str(value))


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{_escape(title)}</title>
<style>{_BASE_CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def _topbar(anchor_links: list[tuple[str, str]]) -> str:
    links = "".join(f"<a class='nav-link' href='{_escape(href)}'>{_escape(label)}</a>" for label, href in anchor_links)
    return (
        "<header class='topbar'><div class='shell topbar-inner'>"
        "<a class='brand' href='index.html'>"
        "<span class='brand-mark'>AF</span>"
        "<span class='brand-copy'><strong>agentforecast</strong><small>sunny scientific open source</small></span>"
        "</a>"
        f"<nav class='nav-links'>{links}<a class='button button-primary' href='#packs'>Browse packs</a></nav>"
        "</div></header>"
    )


def _summary_cards(entries: list[dict[str, Any]], benchmark_count: int) -> str:
    backend_count = len({entry["backend_selected"] for entry in entries})
    cards = [
        ("Published packs", len(entries), "Real forecast packs with charts, markdown, JSON, and cards."),
        ("Backends visible", backend_count, "A small public surface over heterogeneous forecasting families."),
        ("Benchmark links", benchmark_count, "Internal demo evidence kept separate from broader public benchmark hubs."),
        ("Launch posture", "public beta", "Bright, legible, white-first UI designed for technical trust."),
    ]
    return (
        "<div class='stat-grid'>"
        + "".join(
            "<article class='stat-card'>"
            f"<div class='muted'>{_escape(label)}</div><strong>{_escape(value)}</strong><div class='muted'>{_escape(copy)}</div>"
            "</article>"
            for label, value, copy in cards
        )
        + "</div>"
    )


def _selection_grid() -> str:
    return (
        "<div class='feature-grid'>"
        + "".join(
            "<article class='feature-card'>"
            f"<h3>{_escape(title)}</h3>"
            f"<p class='muted'>{_escape(copy)}</p>"
            f"<div class='code-block'>{_escape(model_ids)}</div>"
            "</article>"
            for title, copy, model_ids in _MODEL_SELECTION_COPY
        )
        + "</div>"
    )


def _workflow_grid() -> str:
    steps = [
        ("1. Point", "Use a dataset id, case id, local CSV, directory, or URL."),
        ("2. Route", "Let backend auto-selection compare candidate methods or choose one explicitly."),
        ("3. Publish", "Get charts, cards, markdown, JSON, and leaderboard artifacts."),
        ("4. Reuse", "Push the static gallery to GitHub Pages or consume the JSON from an agent."),
    ]
    return (
        "<div class='workflow-grid'>"
        + "".join(
            "<article class='workflow-card'>"
            f"<h3>{_escape(title)}</h3><p class='muted'>{_escape(copy)}</p>"
            "</article>"
            for title, copy in steps
        )
        + "</div>"
    )


def _surface_grid() -> str:
    return (
        "<div class='feature-grid'>"
        + "".join(
            "<article class='feature-card'>"
            f"<h3>{_escape(title)}</h3>"
            f"<p class='muted'>{_escape(copy)}</p>"
            f"<div class='code-block'>{_escape(symbols)}</div>"
            "</article>"
            for title, copy, symbols in _SURFACE_COPY
        )
        + "</div>"
    )


def _install_matrix() -> str:
    doctor = diagnose_environment()
    rows = "".join(
        "<tr>"
        f"<td>{_escape(persona)}</td>"
        f"<td><code>{_escape(command)}</code></td>"
        f"<td>{_escape(best_for)}</td>"
        "</tr>"
        for persona, command, best_for in _INSTALL_MATRIX
    )
    unavailable = doctor.get("unavailable_backends", [])
    missing = ", ".join(item["backend_id"] for item in unavailable[:6]) if unavailable else "none"
    return (
        "<div class='surface-stack'>"
        + "<div class='table-wrap'><table class='table'>"
        + "<thead><tr><th>Persona</th><th>Install command</th><th>Best for</th></tr></thead>"
        + f"<tbody>{rows}</tbody></table></div>"
        + "<div class='feature-grid'>"
        + "<article class='feature-card'>"
        + "<h3>Doctor first</h3>"
        + "<p class='muted'>Run environment diagnostics before guessing which backend or extra to trust.</p>"
        + "<div class='code-block'>python -m agentforecast.cli doctor</div>"
        + "</article>"
        + "<article class='feature-card'>"
        + "<h3>Current environment snapshot</h3>"
        + f"<p class='muted'>Available workflows: pack={doctor['profiles']['pack']}, research={doctor['profiles']['research']}, streaming={doctor['profiles']['streaming']}.</p>"
        + f"<div class='code-block'>missing extras now: {_escape(missing)}</div>"
        + "</article>"
        + "</div>"
        + "</div>"
    )


def _author_strip() -> str:
    return (
        "<div class='author-strip'>"
        f"<a class='author-pill' href='mailto:{_escape(AUTHOR_EMAIL)}'><span class='author-mark'>ZW</span><span><strong>{_escape(AUTHOR_NAME)}</strong></span></a>"
        f"<span class='author-pill author-pill-uob'>{_escape(AUTHOR_AFFILIATION)}</span>"
        f"<a class='author-pill' href='mailto:{_escape(AUTHOR_EMAIL)}'>{_escape(AUTHOR_EMAIL)}</a>"
        "</div>"
    )


def _entry_card(entry: dict[str, Any]) -> str:
    public_artifacts = entry["public_artifacts"]
    preview = (
        public_artifacts.get("comparison_png")
        or public_artifacts.get("forecast_card_png")
        or public_artifacts.get("forecast_png")
    )
    latest = _format_value(entry["summary"].get("latest_observed", "n/a"))
    projected = _format_value(entry["summary"].get("projected_end", "n/a"))
    preview_html = f"<div class='gallery-card-media'><img src='{_escape(preview)}' alt='{_escape(entry['title'])}'></div>" if preview else ""
    return (
        f"<a class='gallery-card-link' href='cases/{_escape(entry['slug'])}.html'>"
        "<article class='gallery-card'>"
        f"{preview_html}"
        "<div class='gallery-card-body'>"
        f"<div class='mini-row'><span class='badge'>{_escape(entry['backend_selected'])}</span><span class='muted'>{_escape(entry['slug'])}</span></div>"
        f"<h3>{_escape(entry['title'])}</h3>"
        f"<p class='gallery-card-headline'>{_escape(entry['headline'])}</p>"
        f"<div class='gallery-card-footer'><div class='mini-row'><span>latest</span><strong>{_escape(latest)}</strong></div>"
        f"<div class='mini-row'><span>projected end</span><strong>{_escape(projected)}</strong></div></div>"
        "</div>"
        "</article>"
        "</a>"
    )


def _benchmark_table() -> str:
    rows = "".join(
        "<tr>"
        f"<td>{_escape(item['name'])}</td>"
        f"<td>{_escape(item['kind'])}</td>"
        f"<td><a href='{_escape(item['url'])}'>{_escape(item['url'])}</a></td>"
        "</tr>"
        for item in list_external_benchmarks()
    )
    return (
        "<div class='table-wrap'><table class='table'>"
        "<thead><tr><th>Name</th><th>Kind</th><th>Link</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )


def _capability_grid() -> str:
    return (
        "<div class='capability-grid'>"
        + "".join(
            "<article class='feature-card'>"
            f"<h3>{_escape(title)}</h3><p class='muted'>{_escape(copy)}</p>"
            "</article>"
            for title, copy in _CAPABILITY_COPY
        )
        + "</div>"
    )


def _backend_capability_table() -> str:
    rows = "".join(
        "<tr>"
        f"<td><code>{_escape(row['backend_id'])}</code></td>"
        f"<td>{_escape(row['extra'])}</td>"
        f"<td>{_escape(row['stability_tier'])}</td>"
        f"<td>{'yes' if row['supports_streaming'] else 'no'}</td>"
        f"<td>{'yes' if row['supports_exogenous'] else 'no'}</td>"
        f"<td>{'yes' if row['supports_conformal'] else 'no'}</td>"
        f"<td>{'yes' if row['supports_direct'] else 'no'}</td>"
        f"<td>{'yes' if row['supports_recursive'] else 'no'}</td>"
        "</tr>"
        for row in list_backend_capabilities()
    )
    return (
        "<div class='table-wrap'><table class='table'>"
        "<thead><tr><th>Backend</th><th>Extra</th><th>Tier</th><th>Streaming</th><th>Exogenous</th><th>Conformal</th><th>Direct</th><th>Recursive</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )


def _backend_surface_cards() -> str:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for spec in list_backends(include_unavailable=True):
        grouped.setdefault(spec["family"], []).append(spec)

    ordered_families = [
        family
        for family in ("baseline", "classical", "tabular", "streaming", "deep", "automl", "tabpfn")
        if family in grouped
    ]
    cards = []
    for family in ordered_families:
        specs = grouped[family]
        title, copy = _FAMILY_COPY.get(family, (family.title(), ""))
        installed = sum(1 for spec in specs if spec["available"])
        model_ids = ", ".join(spec["backend_id"] for spec in specs)
        providers = ", ".join(dict.fromkeys(spec["provider"] for spec in specs))
        extras = sorted({spec["extra"] for spec in specs})
        tags = sorted({tag for spec in specs for tag in spec.get("tags", [])})[:5]
        extra_copy = ", ".join(extras)
        cards.append(
            "<article class='surface-card'>"
            f"<div class='mini-row'><span class='badge'>{_escape(family)}</span><span class='muted'>{installed}/{len(specs)} available in this build</span></div>"
            f"<h3>{_escape(title)}</h3>"
            f"<p class='muted'>{_escape(copy)}</p>"
            "<ul class='surface-list'>"
            f"<li><strong>Model ids:</strong> <code>{_escape(model_ids)}</code></li>"
            f"<li><strong>Providers:</strong> {_escape(providers)}</li>"
            f"<li><strong>Install extras:</strong> {_escape(extra_copy)}</li>"
            "</ul>"
            + (
                "<div class='surface-pill-row'>"
                + "".join(f"<span class='pill pill-blue'>{_escape(tag)}</span>" for tag in tags)
                + "</div>"
                if tags
                else ""
            )
            + "</article>"
        )
    return "<div class='surface-grid'>" + "".join(cards) + "</div>"


def _api_surface_cards() -> str:
    cards = []
    for item in _API_SURFACE_COPY:
        cards.append(
            "<article class='surface-card'>"
            f"<div class='mini-row'><span class='badge'>{_escape(item['badge'])}</span><span class='muted'>Python API</span></div>"
            f"<h3><code>{_escape(item['name'])}</code></h3>"
            f"<p class='muted'>{_escape(item['headline'])}</p>"
            "<ul class='surface-list'>"
            + "".join(
                f"<li><strong>{_escape(label)}:</strong> <code>{_escape(copy)}</code></li>" if label == "Call" else f"<li><strong>{_escape(label)}:</strong> {_escape(copy)}</li>"
                for label, copy in item["details"]
            )
            + "</ul>"
            + "<div class='surface-pill-row'>"
            + "".join(f"<span class='pill pill-blue'>{_escape(tag)}</span>" for tag in item["tags"])
            + "</div>"
            + "</article>"
        )
    return "<div class='surface-grid'>" + "".join(cards) + "</div>"


def _artifact_cards(public_artifacts: dict[str, str]) -> str:
    cards = []
    for kind, path in public_artifacts.items():
        cards.append(
            "<article class='artifact-card'>"
            f"<strong>{_escape(kind)}</strong>"
            f"<code>{_escape(path)}</code>"
            f"<a href='../{_escape(path)}'>Open artifact</a>"
            "</article>"
        )
    return "<div class='artifact-grid'>" + "".join(cards) + "</div>"


def _leaderboard_table(leaderboard: list[dict[str, Any]]) -> str:
    rows = "".join(
        "<tr>"
        f"<td><span class='badge'>{_escape(row.get('backend_id', 'unknown'))}</span></td>"
        f"<td>{_escape(_format_value(row.get('mae', 'n/a')))}</td>"
        f"<td>{_escape(_format_value(row.get('rmse', 'n/a')))}</td>"
        f"<td>{_escape(_format_value(row.get('smape', 'n/a')))}</td>"
        "</tr>"
        for row in leaderboard[:8]
    )
    return (
        "<div class='table-wrap'><table class='table'>"
        "<thead><tr><th>Backend</th><th>MAE</th><th>RMSE</th><th>sMAPE</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></div>"
    )


def _case_metrics(entry: dict[str, Any]) -> str:
    metrics = [
        ("Selected backend", entry["backend_selected"]),
        ("Latest observed", _format_value(entry["summary"].get("latest_observed", "n/a"))),
        ("Projected end", _format_value(entry["summary"].get("projected_end", "n/a"))),
        ("Artifacts", len(entry["public_artifacts"])),
    ]
    return (
        "<div class='metric-grid'>"
        + "".join(
            "<article class='metric-card'>"
            f"<div class='muted'>{_escape(label)}</div><strong>{_escape(value)}</strong>"
            "</article>"
            for label, value in metrics
        )
        + "</div>"
    )


def _routing_snippet(entry: dict[str, Any]) -> str:
    routing = entry["diagnostics"].get("routing", {})
    snippet = {
        "profile": routing.get("profile"),
        "reason": routing.get("reason"),
        "candidate_backends": routing.get("candidate_backends", []),
        "recommended_extras": routing.get("recommended_extras", []),
    }
    return "<div class='code-block'>" + _escape(json.dumps(snippet, ensure_ascii=False, indent=2)) + "</div>"


def build_hosted_site(runs_root: str | Path, site_dir: str | Path, *, gallery_title: str = "agentforecast public gallery") -> dict[str, Any]:
    runs_root = Path(runs_root)
    site_dir = Path(site_dir)
    if site_dir.exists():
        shutil.rmtree(site_dir)
    site_dir = ensure_dir(site_dir)
    ensure_dir(site_dir / "cases")
    entries = collect_gallery_entries(runs_root)

    public_entries = []
    for entry in entries:
        copied: dict[str, str] = {}
        for kind, raw_path in entry.artifact_map.items():
            src = Path(raw_path)
            if src.exists() and src.suffix.lower() in {".png", ".csv", ".json", ".md"}:
                copied[kind] = _copy_artifact(src, site_dir, entry.slug)
        public_entries.append({**entry.to_dict(), "public_artifacts": copied})

    benchmark_items = list_external_benchmarks()
    topbar = _topbar([("Surfaces", "#surfaces"), ("Install", "#install"), ("Models", "#models"), ("Workflow", "#workflow"), ("Packs", "#packs"), ("Benchmarks", "#benchmarks"), ("Feed", "feed.json")])
    hero = (
        "<section class='hero'>"
        + "<div class='hero-copy'>"
        + "<div class='eyebrow'>Stable forecasting core</div>"
        + f"<h1>{_escape(gallery_title)}</h1>"
        + "<p>AgentForecast is a lightweight forecast-to-publish layer built on top of a stable forecasting core, with optional research and agent/tooling surfaces.</p>"
        + _author_strip()
        + "<div class='hero-actions'>"
        + "<a class='button button-primary' href='#packs'>Explore public packs</a>"
        + "<a class='button button-secondary' href='#install'>Open install + doctor guide</a>"
        + "</div>"
        + "<div class='hero-meta'>"
        + "<span class='pill pill-accent'>white-background-first</span>"
        + "<span class='pill'>research + pack surfaces</span>"
        + "<span class='pill pill-blue'>agent-friendly outputs</span>"
        + "</div>"
        + "</div>"
        + "<aside class='hero-panel panel'>"
        + "<div><strong>Product promise</strong><p class='muted'>Use the pack surface for charts, cards, markdown, CSV, and JSON. Use the research surface for OnlineForecaster, strict_mode, doctor, and benchmark-safe low-level forecasting.</p></div>"
        + _summary_cards(public_entries, len(benchmark_items))
        + "<div class='code-block'>from agentforecast import OnlineForecaster\n\nforecaster = OnlineForecaster(backend=\"river_linear\", horizons=[1, 3, 6], strict_mode=True)\nforecaster.fit(history)\nyhat = forecaster.predict()</div>"
        + "</aside></section>"
    )

    surfaces_section = (
        "<section class='section' id='surfaces'>"
        "<div class='section-head'><div><div class='eyebrow'>Product surfaces</div><h2>One package, four explicit surfaces</h2></div>"
        "<p>The goal is not to blur packs, research, operations, and agent tooling into one contract. The homepage should make those boundaries obvious.</p></div>"
        + _surface_grid()
        + "</section>"
    )

    install_section = (
        "<section class='section' id='install'>"
        "<div class='section-head'><div><div class='eyebrow'>Install and doctor</div><h2>Choose a calm first path</h2></div>"
        "<p>README and the public homepage should agree on install modes, backend expectations, and the first diagnostic command to run.</p></div>"
        + _install_matrix()
        + "</section>"
    )

    selection_section = (
        "<section class='section' id='models'>"
        "<div class='section-head'><div><div class='eyebrow'>Model selection</div><h2>Real forecasting models, not toy demos</h2></div>"
        "<p>agentforecast is built around practical forecasting families that people actually use: baseline references, ETS and ARIMA, lag-feature regression, and online River-style models. Optional deep or AutoML adapters stay secondary instead of dominating the public surface.</p></div>"
        + "<div class='section-subhead'><h3>What the package actually includes</h3><p class='muted'>The public homepage should answer model choice first. Auto routing stays grounded in these real, usable model families rather than novelty-only showcase algorithms.</p></div>"
        + _selection_grid()
        + "</section>"
    )

    workflow_section = (
        "<section class='section' id='workflow'>"
        "<div class='section-head'><div><div class='eyebrow'>Workflow</div><h2>Point. Route. Publish.</h2></div>"
        "<p>The gallery builder is opinionated about clarity: clean stats, high-contrast cards, simple code blocks, and obvious links to the underlying artifacts.</p></div>"
        + _workflow_grid()
        + "</section>"
    )

    packs_section = (
        "<section class='section' id='packs'>"
        "<div class='section-head'><div><div class='eyebrow'>Forecast packs</div><h2>Public runs, ready to scan</h2></div>"
        "<p>Every card is built from the same product contract: selected backend, transparent metrics, copied artifacts, and a clean path into the case detail page.</p></div>"
        + "<div class='card-grid'>"
        + "".join(_entry_card(entry) for entry in public_entries)
        + "</div></section>"
    )

    benchmark_section = (
        "<section class='section' id='benchmarks'>"
        "<div class='section-head'><div><div class='eyebrow'>Model surface</div><h2>What is inside this package</h2></div>"
        "<p>Before anyone looks at external benchmarks, they should be able to scan the backend families, concrete model ids, install tiers, serious Python entry points, and capability matrix that agentforecast exposes.</p></div>"
        + "<div class='surface-stack'>"
        + "<div class='section-subhead'><h3>Backend families and model ids</h3><p class='muted'>This is the forecasting surface behind the gallery, grouped the way a human evaluator would usually reason about model choice.</p></div>"
        + _backend_surface_cards()
        + "<div class='section-subhead'><h3>Backend capability matrix</h3><p class='muted'>Trust tiers and capability flags should be visible instead of hidden behind README prose or runtime surprises.</p></div>"
        + _backend_capability_table()
        + "<div class='section-subhead'><h3>Python API surface</h3><p class='muted'>These are the serious importable functions and objects a human reader can actually call, without having to start from a CLI command.</p></div>"
        + _api_surface_cards()
        + "<div class='section-subhead'><h3>Package capabilities</h3><p class='muted'>These are the workflow-level features that matter in practice beyond the estimator list itself.</p></div>"
        + _capability_grid()
        + "<div class='section-subhead' id='external-benchmarks'><h3>External benchmark hubs</h3><p class='muted'>Internal demo evidence stays visible, but broader public benchmark hubs are still the right place to compare against the field.</p></div>"
        + _benchmark_table()
        + "</div>"
        + "</section>"
    )

    cta_section = (
        "<section class='section'>"
        "<div class='footer-card'>"
        "<div><div class='eyebrow'>Launch CTA</div><h2 style='margin:0 0 10px;'>Use the gallery as the ecosystem front door</h2>"
        "<p class='muted' style='max-width:60ch;'>Keep the repo bright, legible, and optimistic. Lead with public packs, then let users drill into markdown, CSV, JSON, and benchmark links.</p></div>"
        "<div class='hero-actions'><a class='button button-primary' href='feed.json'>Download feed</a><a class='button button-secondary' href='#packs'>Review cases</a></div>"
        "</div></section>"
    )

    index_body = (
        topbar
        + "<main class='page'><div class='shell'>"
        + hero
        + surfaces_section
        + install_section
        + selection_section
        + workflow_section
        + packs_section
        + benchmark_section
        + cta_section
        + "<div class='footer'><div class='footer-card'><div><h3 style='margin:0 0 8px;'>Author</h3>"
        + f"<p class='muted' style='margin:0;'>Created by {_escape(AUTHOR_NAME)} at {_escape(AUTHOR_AFFILIATION)}. Contact: <a href='mailto:{_escape(AUTHOR_EMAIL)}'>{_escape(AUTHOR_EMAIL)}</a>.</p></div>"
        + "<div class='footer-note'>Built by the agentforecast hosted gallery builder. White-first design language tuned for modern scientific open source.</div></div></div>"
        + "</div></main>"
    )
    (site_dir / "index.html").write_text(_page(gallery_title, index_body), encoding="utf-8")

    for entry in public_entries:
        public_artifacts = entry["public_artifacts"]
        hero_image = (
            public_artifacts.get("comparison_png")
            or public_artifacts.get("forecast_png")
            or public_artifacts.get("forecast_card_png")
        )
        case_body = (
            _topbar([("Back to gallery", "../index.html"), ("Artifacts", "#artifacts"), ("Leaderboard", "#leaderboard")])
            + "<main class='page'><div class='shell'>"
            + "<section class='case-header'>"
            + "<div class='stack'>"
            + "<div class='eyebrow'>Case detail</div>"
            + f"<h1>{_escape(entry['title'])}</h1>"
            + f"<p class='case-lead'>{_escape(entry['headline'])}</p>"
            + _case_metrics(entry)
            + "<div class='case-panel'>"
            + "<h3>Routing snapshot</h3>"
            + "<p class='muted'>A compact JSON view of why the visible backend set was routed the way it was.</p>"
            + _routing_snippet(entry)
            + "</div>"
            + "</div>"
            + "<div class='stack'>"
            + (
                f"<div class='case-media'><img src='../{_escape(hero_image)}' alt='{_escape(entry['title'])}'></div>"
                if hero_image
                else ""
            )
            + "<div class='case-panel'><h3>Summary</h3>"
            + f"<p class='muted'>{_escape(entry['summary'].get('narrative', 'Forecast pack built and exported.'))}</p>"
            + _author_strip()
            + "<div class='hero-meta'>"
            + f"<span class='pill pill-accent'>backend {_escape(entry['backend_selected'])}</span>"
            + f"<span class='pill'>artifacts {_escape(len(public_artifacts))}</span>"
            + f"<span class='pill pill-blue'>schema-ready JSON</span>"
            + "</div></div>"
            + "</div></section>"
            + "<section class='section' id='leaderboard'>"
            + "<div class='section-head'><div><div class='eyebrow'>Leaderboard</div><h2>Visible backend performance</h2></div>"
            + "<p>Keep the leaderboard tight and readable. This page should communicate confidence, not overwhelm users with an estimator zoo.</p></div>"
            + _leaderboard_table(entry["diagnostics"].get("leaderboard", []))
            + "</section>"
            + "<section class='section' id='artifacts'>"
            + "<div class='section-head'><div><div class='eyebrow'>Artifacts</div><h2>Every useful file, one click away</h2></div>"
            + "<p>Cards are intentionally simple: obvious file type, obvious path, obvious action. That keeps the page friendly for researchers and agents alike.</p></div>"
            + _artifact_cards(public_artifacts)
            + "</section>"
            + "<div class='footer'><div class='footer-card'><div><h3 style='margin:0 0 8px;'>Back to the ecosystem</h3><p class='muted' style='margin:0;'>Use the gallery homepage to compare multiple scientific, market, and operational examples in one visual system. Built by "
            + _escape(AUTHOR_NAME)
            + " at "
            + _escape(AUTHOR_AFFILIATION)
            + ".</p></div><a class='button button-primary' href='../index.html'>Return to gallery</a></div></div>"
            + "</div></main>"
        )
        (site_dir / "cases" / f"{entry['slug']}.html").write_text(_page(entry["title"], case_body), encoding="utf-8")

    feed = {
        "name": gallery_title,
        "items": public_entries,
        "benchmark_hub": benchmark_items,
    }
    (site_dir / "feed.json").write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "site_dir": Path(site_dir).as_posix(),
        "entry_count": len(public_entries),
        "index_html": (site_dir / "index.html").as_posix(),
        "feed_json": (site_dir / "feed.json").as_posix(),
    }
