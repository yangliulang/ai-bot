#!/usr/bin/env bash
# 从模板创建功能包
# 用法:
#   ./scripts/new-feature.sh 2026-05-25--greeting "问候 API"
#   ./scripts/new-feature.sh greeting "问候 API"   # 自动加当天日期前缀

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PIPELINE_PROJECT_ROOT="$ROOT"
# shellcheck source=scripts/lib/read-pipeline-project.sh
source "$ROOT/scripts/lib/read-pipeline-project.sh"

TEMPLATE="$ROOT/handoff/templates/feature"
FEATURES="$(pp_get features.root)"
FEATURES_ABS="$ROOT/$FEATURES"
API_BASE_URL="$(pp_get apps.backend.dev.base_url)"

if [ $# -lt 2 ]; then
  echo "用法: $0 <功能ID或slug> <功能标题>"
  echo "功能 ID 格式: YYYY-MM-DD--kebab-slug（双横线后为英文 slug）"
  echo "示例: $0 2026-05-25--user-profile \"用户资料查看/编辑\""
  echo "示例: $0 user-profile \"用户资料\"  # 使用当天日期 → \$(date +%Y-%m-%d)--user-profile"
  echo "功能包目录见 pipeline.project.yaml → features.root（当前: $FEATURES）"
  exit 1
fi

RAW="$1"
TITLE="$2"

if [[ "$RAW" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}--[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  FEATURE_ID="$RAW"
else
  FEATURE_ID="$(date '+%Y-%m-%d')--${RAW}"
fi

TARGET="$FEATURES_ABS/$FEATURE_ID"

if [ -d "$TARGET" ]; then
  echo "错误: 功能包已存在: $TARGET"
  exit 1
fi

mkdir -p "$FEATURES_ABS"
cp -r "$TEMPLATE" "$TARGET"

if sed --version >/dev/null 2>&1; then
  SED_INPLACE=(sed -i)
else
  SED_INPLACE=(sed -i '')
fi

"${SED_INPLACE[@]}" "s/2026-05-25--slug/$FEATURE_ID/g" "$TARGET/status.yaml"
"${SED_INPLACE[@]}" "s/功能标题（创建时修改）/$TITLE/g" "$TARGET/status.yaml"
"${SED_INPLACE[@]}" "s|@API_BASE_URL@|$API_BASE_URL|g" "$TARGET/api.openapi.yaml"

NOW="$(date '+%Y-%m-%dT%H:%M:%S%z')"
"${SED_INPLACE[@]}" "s/2026-05-25T00:00:00+08:00/$NOW/g" "$TARGET/status.yaml"

echo "已创建功能包: $TARGET"
echo "功能 ID: $FEATURE_ID"
echo "OpenAPI servers.url: $API_BASE_URL"
echo "下一步: product-agent 完成 brief、api.openapi.yaml、test/coverage.md 与用例，并运行:"
echo "  ./scripts/check-test-coverage.sh $TARGET"
