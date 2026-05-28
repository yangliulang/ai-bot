#!/usr/bin/env bash
# 规格仓 A 阶段自检 — 关单/走读前运行
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== closure-preflight =="
echo "repo: $ROOT"
echo

fail=0
run() {
  echo ">> $*"
  if ! "$@"; then
    echo "FAILED: $*"
    fail=1
  fi
  echo
}

run python3 specs/requirements/skill-specs/scripts/check_skill_contract_complete.py
run python3 specs/requirements/prompts/library/scripts/check_registry_vs_routing_engine.py
run python3 specs/requirements/prompts/library/scripts/check_governance_map_vs_registry.py
run node specs/requirements/skill-specs/scripts/build_runtime_publish_bundle.mjs --check

if [[ -d src/admin/node_modules ]]; then
  run npm test --prefix src/admin
else
  echo ">> skip admin vitest (run: cd src/admin && npm ci && npm test)"
  echo
fi

if [[ "$fail" -ne 0 ]]; then
  echo "PREFLIGHT: FAIL"
  exit 1
fi

echo "PREFLIGHT: OK"
echo "Next: closure-internal-sprint.md §2 (W1) · closure-staging-evidence-log.md after staging"
echo "Optional (Dev BFF up): ADMIN_ORIGIN=http://localhost:5173 WEB_ORIGIN=http://localhost:5175 ./scripts/staging-mr-bill-probe.sh"
