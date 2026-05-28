from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    app_dir = Path(__file__).resolve().parents[1]

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "--app-dir",
        str(app_dir),
        "api.main:app",
        "--reload",
        *sys.argv[1:],
    ]

    try:
        raise SystemExit(subprocess.call(cmd))
    except KeyboardInterrupt:
        raise SystemExit(0)
