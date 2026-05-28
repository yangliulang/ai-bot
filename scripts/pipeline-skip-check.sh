#!/usr/bin/env bash
# 检查功能包当前是否应跳过下一正向步骤
# 退出码 0 = 应跳过；1 = 否
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"

INPUT="${1:?feature_dir or status.yaml}"
if [[ "$INPUT" == *status.yaml ]]; then
  STATUS="$INPUT"
elif [[ "$INPUT" = /* ]]; then
  STATUS="$INPUT/status.yaml"
else
  STATUS="$ROOT/$INPUT/status.yaml"
fi
exec ruby "$ROOT/scripts/lib/pipeline-skip-apply.rb" "$STATUS" "${@:2}"
