#!/usr/bin/env python3
"""
Cross-check scenarioId → promptPackId between governance-map.md and registry.md.

Run from repo root:
  python3 specs/requirements/prompts/library/scripts/check_governance_map_vs_registry.py

Exit 0 when explicit mappings agree (wildcards in governance §4 expanded per rules below).
Exit 1 on mismatch or unreadable files.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[5]
_GOVERNANCE = _REPO_ROOT / "specs/requirements/prompts/governance-map.md"
_REGISTRY = _REPO_ROOT / "specs/requirements/prompts/library/scenarios/registry.md"

_SCENARIO_SLUG = re.compile(r"^[a-z][a-z0-9_.]*$")
_PACK_ID = re.compile(r"^pp-[a-z0-9-]+$")

# governance-map §4 wildcards → expected pack (registry rows must match)
_WILDCARD_PACK: list[tuple[str, str]] = [
    ("market.read_", "pp-analysis-core"),
    ("futures.read_funding", "pp-analysis-core"),  # exact key, not prefix
    ("research.", "pp-analysis-core"),
    ("orders.read_activity", "pp-analysis-core"),
    ("portfolio.", "pp-analysis-core"),
    ("wealth.holdings_read", "pp-analysis-core"),
    ("wealth.recommend", "pp-analysis-core"),
    ("monitoring.", "pp-analysis-core"),
]


def _expected_pack_from_wildcards(scenario_id: str) -> str | None:
    if scenario_id == "futures.read_funding":
        return "pp-analysis-core"
    for prefix, pack in _WILDCARD_PACK:
        if prefix.endswith(".") and scenario_id.startswith(prefix):
            return pack
        if not prefix.endswith(".") and scenario_id == prefix:
            return pack
        if prefix.endswith("_") and scenario_id.startswith(prefix):
            return pack
    return None


def _parse_table_pairs(text: str) -> dict[str, str]:
    """Parse | `scenarioId` | `promptPackId` | ... rows; skip headers and unreleased."""
    pairs: dict[str, str] = {}
    header_cells = frozenset({"`scenarioId`", "`scenarioId`（族）"})
    for line in text.splitlines():
        stripped = line.lstrip()
        if not stripped.startswith("| `"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        scen_cell, pack_cell = parts[1], parts[2]
        if scen_cell in header_cells or "scenarioId" in scen_cell and "族" in scen_cell:
            continue
        pack_m = re.search(r"`(pp-[^`]+)`", pack_cell)
        if not pack_m:
            continue
        pack_id = pack_m.group(1)
        if not _PACK_ID.fullmatch(pack_id):
            continue
        for m in re.finditer(r"`([^`]+)`", scen_cell):
            raw = m.group(1).strip()
            if raw == "scenarioId" or "*" in raw:
                continue
            if not _SCENARIO_SLUG.fullmatch(raw):
                continue
            pairs[raw] = pack_id
    return pairs


def _governance_explicit(text: str) -> dict[str, str]:
    return _parse_table_pairs(text)


def _registry_pairs(text: str) -> dict[str, str]:
    return _parse_table_pairs(text)


def _governance_expected(scenario_id: str, explicit: dict[str, str]) -> str | None:
    if scenario_id in explicit:
        return explicit[scenario_id]
    return _expected_pack_from_wildcards(scenario_id)


def main() -> int:
    if not _GOVERNANCE.is_file() or not _REGISTRY.is_file():
        print("ERROR: governance-map.md or registry.md not found.", file=sys.stderr)
        return 1

    gov_text = _GOVERNANCE.read_text(encoding="utf-8")
    reg_text = _REGISTRY.read_text(encoding="utf-8")
    gov_explicit = _governance_explicit(gov_text)
    registry = _registry_pairs(reg_text)

    errors: list[str] = []

    for sid, reg_pack in sorted(registry.items()):
        expected = _governance_expected(sid, gov_explicit)
        if expected is None:
            errors.append(f"registry `{sid}` → `{reg_pack}` has no governance-map rule (add §3/§4 row)")
            continue
        if reg_pack != expected:
            errors.append(
                f"`{sid}`: registry=`{reg_pack}` vs governance=`{expected}`",
            )

    for sid, gov_pack in sorted(gov_explicit.items()):
        if sid not in registry:
            errors.append(f"governance-map lists `{sid}` → `{gov_pack}` but registry.md has no row")

    if errors:
        print("FAIL: governance-map ↔ registry promptPackId mismatch:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "Hint: update governance-map.md §3–§4 and registry.md together; "
            "run both check scripts before MR.",
            file=sys.stderr,
        )
        return 1

    print(
        f"OK: {len(registry)} registry scenarioIds match governance-map "
        f"({len(gov_explicit)} explicit + wildcard rules)",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
