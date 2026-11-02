#!/usr/bin/env python3
"""Run the canonical Python SDK engineering validation."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if sys.flags.optimize != 0 or not __debug__:
    print("Python SDK validation requires optimization level zero. Run without -O/-OO and unset PYTHONOPTIMIZE.", file=sys.stderr)
    raise SystemExit(1)

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = next((candidate for candidate in (ROOT.parent, ROOT.parent.parent) if (candidate / "Developer-Toolkit/scripts/release-preflight/python_sdk.py").is_file()), ROOT.parent)
VALIDATOR = WORKSPACE / "Developer-Toolkit/scripts/release-preflight/python_sdk.py"

if not VALIDATOR.is_file() or not (WORKSPACE / "AGENTS.md").is_file():
    print("Validation requires the Raims engineering workspace and its Developer-Toolkit checkout. No checks were run.", file=sys.stderr)
    raise SystemExit(1)
raise SystemExit(subprocess.call([sys.executable, str(VALIDATOR), "--source", str(ROOT), "--workspace", str(WORKSPACE), *sys.argv[1:]]))
