#!/usr/bin/env bash
# 当前 roadmap.active_phase 是否全部 done（可 phase-close）
# 退出码 0 = 可收束；1 = 否
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"
exec ruby "$ROOT/scripts/lib/phase-close-ready.rb" "$@"
