#!/usr/bin/env bash
# 清除当前阶段未交付规划，或整阶段重置后重新 plan
# 用法: ./scripts/plan-reset.sh [--dry-run] [--force] [--mode soft|full] [--phase N]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"
exec ruby "$ROOT/scripts/lib/plan-reset.rb" "$@"
