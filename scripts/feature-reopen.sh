#!/usr/bin/env bash
# 功能包返工重置：status.yaml + roadmap 行 → planned
# 用法: ./scripts/feature-reopen.sh --feature 2026-05-25--greeting [--phase N] [--dry-run]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"
exec ruby "$ROOT/scripts/lib/feature-reopen.rb" "$@"
