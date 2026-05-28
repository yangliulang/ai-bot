#!/usr/bin/env bash
# 根据 pipeline.project.yaml 生成 .cursor/rules/api-dev.mdc 与 web-dev.mdc
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=scripts/lib/read-pipeline-project.sh
source "$ROOT/scripts/lib/read-pipeline-project.sh"

export PIPELINE_PROJECT_ROOT="$ROOT"

BACKEND_PATH="$(pp_get apps.backend.path)"
FRONTEND_PATH="$(pp_get apps.frontend.path)"
API_BASE_URL="$(pp_get apps.backend.dev.base_url)"
WEB_DEV_URL="$(pp_get apps.frontend.dev.base_url)"
CORS_ORIGIN="$(pp_get apps.backend.dev.cors_origin)"

BACKEND_GLOB="${BACKEND_PATH}/**/*"
FRONTEND_GLOB="${FRONTEND_PATH}/**/*"

substitute() {
  local tmpl="$1"
  local out="$2"
  sed \
    -e "s|@BACKEND_PATH@|${BACKEND_PATH}|g" \
    -e "s|@FRONTEND_PATH@|${FRONTEND_PATH}|g" \
    -e "s|@BACKEND_GLOB@|${BACKEND_GLOB}|g" \
    -e "s|@FRONTEND_GLOB@|${FRONTEND_GLOB}|g" \
    -e "s|@API_BASE_URL@|${API_BASE_URL}|g" \
    -e "s|@WEB_DEV_URL@|${WEB_DEV_URL}|g" \
    -e "s|@CORS_ORIGIN@|${CORS_ORIGIN}|g" \
    "$tmpl" >"$out"
}

TMPL_API="$ROOT/handoff/templates/cursor/api-dev.mdc.tmpl"
TMPL_WEB="$ROOT/handoff/templates/cursor/web-dev.mdc.tmpl"
OUT_API="$ROOT/.cursor/rules/api-dev.mdc"
OUT_WEB="$ROOT/.cursor/rules/web-dev.mdc"

for f in "$TMPL_API" "$TMPL_WEB"; do
  if [ ! -f "$f" ]; then
    echo "错误: 缺少模板 $f" >&2
    exit 1
  fi
done

substitute "$TMPL_API" "$OUT_API"
substitute "$TMPL_WEB" "$OUT_WEB"

echo "已生成:"
echo "  $OUT_API  (globs: $BACKEND_GLOB)"
echo "  $OUT_WEB  (globs: $FRONTEND_GLOB)"
