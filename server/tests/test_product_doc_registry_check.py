"""Regression: product-doc registry ⊆ routing-engine (same check as F1 script)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = (
    _REPO_ROOT
    / "product-doc"
    / "specs"
    / "requirements"
    / "prompts"
    / "library"
    / "scripts"
    / "check_registry_vs_routing_engine.py"
)


@pytest.mark.skipif(not _SCRIPT.is_file(), reason="product-doc check script missing")
def test_product_doc_registry_vs_routing_engine_script_exits_zero() -> None:
    """AC-09q: server CI runs the same semantic check as product-doc F1 (when present)."""
    r = subprocess.run(
        [sys.executable, str(_SCRIPT)],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert r.returncode == 0, f"stderr={r.stderr!r}\nstdout={r.stdout!r}"
