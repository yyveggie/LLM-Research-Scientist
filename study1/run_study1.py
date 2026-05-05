#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = Path(__file__).resolve().parent / "outputs" / "raw_model_responses"


def main():
    cmd = [
        sys.executable,
        str(ROOT / "reproduce.py"),
        "study1",
        "--out-dir",
        str(OUT_DIR),
    ]
    cmd.extend(sys.argv[1:])
    raise SystemExit(subprocess.call(cmd, cwd=str(ROOT)))


if __name__ == "__main__":
    main()
