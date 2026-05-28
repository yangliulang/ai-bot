#!/usr/bin/env bash
# product.plan 后：roadmap phase-N backlog 表 → backlog.yaml
# 用法: ./scripts/sync-backlog-from-phase.sh [--phase N] [--dry-run]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"
exec ruby "$ROOT/scripts/lib/sync-backlog-from-phase.rb" "$@"
