from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import re
import urllib.request

import pandas as pd


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "series"


def posix_path(path: str | Path) -> str:
    return Path(path).as_posix()


def relative_artifact(path: str | Path, root: str | Path) -> str:
    return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()


def write_json(path: str | Path, payload: Any) -> None:
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def load_csv_from_url(url: str) -> pd.DataFrame:
    with urllib.request.urlopen(url) as response:
        return pd.read_csv(response)


def read_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _markdown_escape(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6g}"
    return str(value).replace("|", "\\|").replace("\n", " ")


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    """Return a GitHub-flavored markdown table without requiring tabulate."""
    if frame.empty:
        return "| (empty) |\n|---|\n| no rows |"
    columns = [str(col) for col in frame.columns]
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = []
    for row in frame.itertuples(index=False, name=None):
        body.append("| " + " | ".join(_markdown_escape(value) for value in row) + " |")
    return "\n".join([header, divider] + body)
