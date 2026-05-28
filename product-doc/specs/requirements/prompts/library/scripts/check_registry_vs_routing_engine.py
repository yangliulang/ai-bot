#!/usr/bin/env python3
"""
Cross-check scenarioIds listed in prompts/library/scenarios/registry.md against
domains/agent/agent-orchestration/routing-engine.md tables.

Run from repo root:
  python3 specs/requirements/prompts/library/scripts/check_registry_vs_routing_engine.py

Exit 0 if registry ⊆ routing SSOT (every registry id appears in routing tables).
Exit 1 on mismatch or unreadable files.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Repo root: .../Agent (six parents up from this file)
_REPO_ROOT = Path(__file__).resolve().parents[5]
_ROUTING = _REPO_ROOT / "specs/requirements/domains/agent/agent-orchestration/routing-engine.md"
_REGISTRY = _REPO_ROOT / "specs/requirements/prompts/library/scenarios/registry.md"


_SCENARIO_SLUG = re.compile(r"^[a-z][a-z0-9_.]*$")


def _routing_scenario_ids(text: str) -> set[str]:
    """Parse first Markdown table column only (avoid **`FR-T02`** in later cells)."""
    ids: set[str] = set()
    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        first = parts[1]
        if not first.startswith("**`"):
            continue
        for m in re.finditer(r"\*\*`([^`]+)`\*\*", first):
            raw = m.group(1).strip()
            if raw == "scenarioId":
                continue
            if _SCENARIO_SLUG.fullmatch(raw):
                ids.add(raw)
    return ids


def _registry_scenario_ids(text: str) -> set[str]:
    ids: set[str] = set()
    header_cells = frozenset({"`scenarioId`"})
    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped.startswith("| `"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        cell = parts[1]
        if cell in header_cells:
            continue
        for m in re.finditer(r"`([^`]+)`", cell):
            raw = m.group(1).strip()
            if raw == "scenarioId":
                continue
            ids.add(raw)
    return ids


def main() -> int:
    if not _ROUTING.is_file() or not _REGISTRY.is_file():
        print("ERROR: routing-engine.md or registry.md not found.", file=sys.stderr)
        return 1

    routing = _routing_scenario_ids(_ROUTING.read_text(encoding="utf-8"))
    registry = _registry_scenario_ids(_REGISTRY.read_text(encoding="utf-8"))

    extra_in_registry = sorted(registry - routing)

    if extra_in_registry:
        print("FAIL: registry lists scenarioIds not found in routing-engine tables:", file=sys.stderr)
        for x in extra_in_registry:
            print(f"  - {x}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Hint: update routing-engine.md or fix registry.md.", file=sys.stderr)
        return 1

    print("OK: all registry scenarioIds appear in routing-engine.md")

    orphan_routing = sorted(routing - registry)
    if orphan_routing:
        print("")
        print("WARN: routing-engine registers scenarioIds not listed in prompts/library/registry.md:")
        for x in orphan_routing:
            print(f"  - {x}")
        print("(Consider extending registry rows when adding routing keys.)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
