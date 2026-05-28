#!/usr/bin/env bash
# 校验功能包 AC ↔ 测试用例追溯是否完备
# 用法: ./scripts/check-test-coverage.sh handoff/features/2026-05-25--xxx

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FEATURE_DIR="${1:-}"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

ok() {
  echo "OK: $*"
}

if [ -z "$FEATURE_DIR" ]; then
  fail "用法: $0 handoff/features/2026-05-25--xxx"
fi

if [[ "$FEATURE_DIR" != /* ]]; then
  FEATURE_DIR="$ROOT/$FEATURE_DIR"
fi

[ -d "$FEATURE_DIR" ] || fail "功能包目录不存在: $FEATURE_DIR"

BRIEF="$FEATURE_DIR/brief.md"
COVERAGE="$FEATURE_DIR/test/coverage.md"
CASES="$FEATURE_DIR/test/cases.md"
E2E="$FEATURE_DIR/test/e2e-cases.md"
OPENAPI="$FEATURE_DIR/api.openapi.yaml"

[ -f "$BRIEF" ] || fail "缺少 brief.md"
[ -f "$COVERAGE" ] || fail "缺少 test/coverage.md"
[ -f "$CASES" ] || fail "缺少 test/cases.md"
[ -f "$OPENAPI" ] || fail "缺少 api.openapi.yaml"

# --- 收集 AC（brief 验收标准小节）---
ACS_FILE="$(mktemp)"
trap 'rm -f "$ACS_FILE"' EXIT

awk '
  /^## 验收标准/ { in_ac=1; next }
  /^## / && in_ac { exit }
  in_ac { print }
' "$BRIEF" | grep -oE 'AC-[0-9]+' | sort -u > "$ACS_FILE"

if [ ! -s "$ACS_FILE" ]; then
  fail "brief.md「验收标准」中未找到 AC-1、AC-2…"
fi

# --- 是否含页面 ---
HAS_UI=false
if grep -q "## 界面与交互" "$BRIEF"; then
  if awk '/^## 界面与交互/,/^## /' "$BRIEF" | grep -qE '路由|/[a-zA-Z]'; then
    HAS_UI=true
  fi
fi
if grep -qi '含页面.*| 是' "$COVERAGE" 2>/dev/null; then
  HAS_UI=true
fi
if grep -qi '含页面.*| 否' "$COVERAGE" 2>/dev/null; then
  HAS_UI=false
fi

if $HAS_UI; then
  [ -f "$E2E" ] || fail "本功能含页面，缺少 test/e2e-cases.md"
else
  ok "无页面需求，跳过 E2E 列校验"
fi

# --- 用例 ID 是否在文件中 ---
id_exists() {
  local file="$1" id="$2"
  grep -q "$id" "$file" 2>/dev/null
}

# --- P0 表行是否有步骤与预期（用例列表表：步骤=第5列，预期=第6列）---
row_has_steps() {
  local file="$1" id="$2"
  awk -F'|' -v id="$id" '
    $0 ~ id && $0 !~ /^[|[:space:]]*ID/ && $0 !~ /^[|[:space:]]*----/ {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $5);
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", $6);
      if (length($5) >= 3 && length($6) >= 3) found = 1
    }
    END { if (found) exit 0; exit 1 }
  ' "$file"
}

ERRORS=0
AC_COUNT=0

while IFS= read -r ac; do
  [ -n "$ac" ] || continue
  AC_COUNT=$((AC_COUNT + 1))

  line="$(grep "$ac" "$COVERAGE" | grep -v '^#' | head -1 || true)"
  if [ -z "$line" ]; then
    echo "FAIL: test/coverage.md 未包含 $ac 行" >&2
    ERRORS=$((ERRORS + 1))
    continue
  fi

  tc="$(echo "$line" | grep -oE 'TC-[0-9]+' | head -1 || true)"
  e2e="$(echo "$line" | grep -oE 'E2E-[0-9]+' | head -1 || true)"

  if [ -z "$tc" ]; then
    echo "FAIL: $ac 在 coverage.md 中缺少 API 用例 TC-xx" >&2
    ERRORS=$((ERRORS + 1))
  elif ! id_exists "$CASES" "$tc"; then
    echo "FAIL: $ac 引用 $tc，但 test/cases.md 中不存在" >&2
    ERRORS=$((ERRORS + 1))
  elif ! row_has_steps "$CASES" "$tc"; then
    echo "FAIL: $tc 在 test/cases.md 中缺少步骤或预期" >&2
    ERRORS=$((ERRORS + 1))
  fi

  if $HAS_UI; then
    if [ -z "$e2e" ]; then
      echo "FAIL: $ac 在 coverage.md 中缺少 E2E 用例 E2E-xx" >&2
      ERRORS=$((ERRORS + 1))
    elif ! id_exists "$E2E" "$e2e"; then
      echo "FAIL: $ac 引用 $e2e，但 test/e2e-cases.md 中不存在" >&2
      ERRORS=$((ERRORS + 1))
    elif ! row_has_steps "$E2E" "$e2e"; then
      echo "FAIL: $e2e 在 test/e2e-cases.md 中缺少步骤或预期" >&2
      ERRORS=$((ERRORS + 1))
    fi
  fi

  in_cases=false
  in_e2e=false
  grep -q "$ac" "$CASES" && in_cases=true
  $HAS_UI && [ -f "$E2E" ] && grep -q "$ac" "$E2E" && in_e2e=true

  if ! $in_cases && ! $in_e2e; then
    echo "FAIL: $ac 未在 test/cases.md 或 test/e2e-cases.md 中引用" >&2
    ERRORS=$((ERRORS + 1))
  fi
done < "$ACS_FILE"

if ! grep -q 'P0' "$CASES"; then
  echo "FAIL: test/cases.md 无 P0 用例" >&2
  ERRORS=$((ERRORS + 1))
fi

if [ "$ERRORS" -gt 0 ]; then
  echo "" >&2
  echo "共 $ERRORS 项未通过。对照 handoff/pipeline/checklists/contract-test-coverage.md" >&2
  exit 1
fi

ok "AC 追溯完备（${AC_COUNT} 条 AC，含页面=$HAS_UI）: $FEATURE_DIR"
exit 0
