#!/usr/bin/env python3
"""Verify Admin execution timeline matches write-path pipeline order (P-08 staging helper).

Usage (from repo root, after staging walkthrough records executionId):

  cd server && uv run python ../handoff/features/2026-05-27--telegram-write-path-staging/scripts/verify_timeline_order.py \\
    --execution-id exec-XXXXXXXXXXXXXX \\
    --base-url https://staging-agent.example.invalid \\
    --token "$ADMIN_BEARER"

Exit 0 = order OK; non-zero = HTTP failure or assert_write_path_pipeline_order failed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SERVER_ROOT = _REPO_ROOT / "server"
if str(_SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(_SERVER_ROOT))

from chainup_agent.application.write_path_pipeline import assert_write_path_pipeline_order  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution-id", required=True, help="staging evidence §2 executionId")
    parser.add_argument("--base-url", default="http://127.0.0.1:8080")
    parser.add_argument("--token", default="", help="Admin Bearer JWT (if required)")
    parser.add_argument("--pretty", action="store_true", help="Print timeline JSON to stdout")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    url = f"{base}/api/v1/admin/observability/executions/{args.execution_id}/timeline"
    headers: dict[str, str] = {}
    if args.token.strip():
        headers["Authorization"] = f"Bearer {args.token.strip()}"

    try:
        resp = httpx.get(url, headers=headers, timeout=60.0)
    except httpx.HTTPError as exc:
        print(f"HTTP error: {exc}", file=sys.stderr)
        return 2

    if resp.status_code != 200:
        print(f"GET timeline → {resp.status_code}: {resp.text[:500]}", file=sys.stderr)
        return 3

    body = resp.json()
    items = body.get("items") or body.get("events") or []
    if not isinstance(items, list):
        print("Unexpected timeline body: missing items[]", file=sys.stderr)
        return 4

    if args.pretty:
        print(json.dumps(body, ensure_ascii=False, indent=2))

    try:
        assert_write_path_pipeline_order(items)
    except AssertionError as exc:
        print(f"Pipeline order check failed: {exc}", file=sys.stderr)
        return 5

    print(f"OK: write-path pipeline order verified for {args.execution_id} ({len(items)} events)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
