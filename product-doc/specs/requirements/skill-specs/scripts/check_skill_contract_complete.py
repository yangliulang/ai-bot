#!/usr/bin/env python3
"""
Validate skill-spec markdown files are contract-complete (FR-T11 / Publish ready).

Run from repo root:
  python3 specs/requirements/skill-specs/scripts/check_skill_contract_complete.py

Exit 0 if all publishRequired skills pass.
Exit 1 on missing sections, incremental-only drafts, or manifest drift.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SKILL_ROOT = _REPO_ROOT / "specs/requirements/skill-specs"
_MANIFEST = _SKILL_ROOT / "manifest.yaml"

_REQUIRED_SECTIONS = [
    "## 1. Required / Optional Params",
    "## 2. Validation Rules",
    "## 3. Confirmation Schema",
    "## 4. UNKNOWN / 缺槽策略",
    "## 5. Refusal Conditions",
    "## 6. API / 写路径",
]

_INCREMENTAL_PATTERNS = [
    re.compile(r"\*\*除.*外\*\*.*\*\*与\*\*.*\*\*一致\*\*"),
    re.compile(r"^\*\*其余\*\*.*同\s*\["),
    re.compile(r"^同\s*\[`skill\."),
    re.compile(r"\*\*待补\*\*"),
    re.compile(r"\|\s*\*\*状态\*\*\s*\|\s*\*\*骨架\*\*"),
]

_MIN_LINES = 80


def _load_manifest() -> list[dict]:
    if yaml is None:
        print("ERROR: PyYAML required (pip install pyyaml)", file=sys.stderr)
        sys.exit(2)
    data = yaml.safe_load(_MANIFEST.read_text(encoding="utf-8"))
    return list(data.get("skills") or [])


def _check_file(path: Path, skill_id: str) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if len(lines) < _MIN_LINES:
        errors.append(f"{skill_id}: file too short ({len(lines)} lines < {_MIN_LINES})")

    for sec in _REQUIRED_SECTIONS:
        if sec not in text:
            errors.append(f"{skill_id}: missing section {sec!r}")

    if "contract-complete" not in text:
        errors.append(f"{skill_id}: metadata must include status contract-complete")

    for i, line in enumerate(lines, 1):
        for pat in _INCREMENTAL_PATTERNS:
            if pat.search(line):
                errors.append(f"{skill_id}:{i}: incremental/skeleton pattern: {line[:80]!r}")
                break

    if path.name.replace(".md", "") != skill_id:
        errors.append(f"{skill_id}: filename must equal skillId ({path.name})")

    return errors


def main() -> int:
    entries = _load_manifest()
    errors: list[str] = []

    for entry in entries:
        skill_id = entry["skillId"]
        rel = entry.get("path")
        required = bool(entry.get("publishRequired"))

        if not required:
            if rel:
                p = _SKILL_ROOT / rel
                if not p.is_file():
                    errors.append(f"{skill_id}: optional path missing {rel}")
            continue

        if not rel:
            errors.append(f"{skill_id}: publishRequired=true but path is null")
            continue

        path = _SKILL_ROOT / rel
        if not path.is_file():
            errors.append(f"{skill_id}: missing file {rel}")
            continue

        errors.extend(_check_file(path, skill_id))

    # Orphan .md under skill-specs (except README, TEMPLATE, PUBLISH)
    allowed_orphans = {"README.md", "TEMPLATE.md", "PUBLISH.md"}
    published_paths = {
        e["path"] for e in entries if e.get("path") and e.get("publishRequired")
    }
    for md in _SKILL_ROOT.rglob("*.md"):
        if md.parent == _SKILL_ROOT:
            continue
        rel = md.relative_to(_SKILL_ROOT).as_posix()
        if rel not in published_paths and md.name not in allowed_orphans:
            errors.append(f"orphan skill markdown not in manifest publishRequired: {rel}")

    if errors:
        print("FAIL: skill contract checks:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    n = sum(1 for e in entries if e.get("publishRequired"))
    print(f"OK: {n} publishRequired skill specs are contract-complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
