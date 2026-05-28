#!/usr/bin/env bash
# 指定 phase 对齐准备：快照 + 切换 active_phase + soft reset planned
# 用法: ./scripts/phase-realign-prepare.sh --phase N [--dry-run] [--no-switch] [--no-reset] [--note "变更说明"]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"
exec ruby "$ROOT/scripts/lib/phase-realign-prepare.rb" "$@"
