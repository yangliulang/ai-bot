#!/usr/bin/env bash
# 在仓库根目录执行日报脚本；存在 feishu.env 时加载（请勿提交 feishu.env）
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/feishu.env"
cd "$ROOT"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$ENV_FILE"
  set +a
fi

exec node "$ROOT/scripts/product-daily-brief/send-feishu-daily-brief.mjs" "$@"
