#!/usr/bin/env bash
# 跳过功能包中不需要的角色步骤（见 status.yaml skips）
# 用法: ./scripts/pipeline-skip.sh <功能ID或 feature_dir> [--dry-run]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"
exec ruby "$ROOT/scripts/lib/pipeline-skip-apply.rb" "$@"
