from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import venv

ROOT = Path(__file__).resolve().parents[1]
DIST = next((ROOT / "dist").glob("agentforecast-*.whl"))


def run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=True)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        env_dir = tmp_path / 'venv'
        venv.EnvBuilder(with_pip=True).create(env_dir)
        py = env_dir / ('Scripts' if sys.platform.startswith('win') else 'bin') / 'python'
        run([str(py), '-m', 'pip', 'install', str(DIST)])
        demo = tmp_path / 'demo'
        run([str(py), '-m', 'agentforecast.cli', 'shoot', 'sales', '--outdir', str(demo)])
        summary = demo / 'sales' / 'reports' / 'summary.md'
        if not summary.exists():
            raise SystemExit('summary.md not generated in fresh wheel smoke test')
        print(summary.as_posix())


if __name__ == '__main__':
    main()
