#!/usr/bin/env bash
# MR-BILL-B1/B2 · 本地 Dev BFF / staging 探针（同窗 staging-mr-bill-runbook.md · Web staging-me-commerce-runbook.md）
# 用法：
#   ADMIN_ORIGIN=http://localhost:5173 WEB_ORIGIN=http://localhost:5175 ./scripts/staging-mr-bill-probe.sh
#   ./scripts/staging-mr-bill-probe.sh --web-only
#   EXECUTION_ID=202605271200000001 USER_ID=u-10482 ./scripts/staging-mr-bill-probe.sh
set -euo pipefail

WEB_ONLY=0
for arg in "$@"; do
  if [[ "$arg" == "--web-only" ]]; then
    WEB_ONLY=1
  fi
done

# 兼容旧变量 ORIGIN → Admin
ADMIN_ORIGIN="${ADMIN_ORIGIN:-${ORIGIN:-http://localhost:5173}}"
ADMIN_ORIGIN="${ADMIN_ORIGIN%/}"
WEB_ORIGIN="${WEB_ORIGIN:-http://localhost:5175}"
WEB_ORIGIN="${WEB_ORIGIN%/}"
USER_ID="${USER_ID:-u-10482}"
EXECUTION_ID="${EXECUTION_ID:-202605271200000001}"
IDEM_KEY="${IDEM_KEY:-${EXECUTION_ID}:rail-b:entitlement-debit}"
CAPABILITY_SKU="${CAPABILITY_SKU:-cap.agent.trade}"

fail=0
ok=0

probe() {
  local origin="$1"
  local name="$2"
  local method="$3"
  local path="$4"
  local body="${5:-}"
  local extra_headers="${6:-}"

  local url="${origin}${path}"
  echo ">> ${name}"
  echo "   ${method} ${url}"

  local tmp
  tmp="$(mktemp)"
  local code
  if [[ -n "$body" ]]; then
    # shellcheck disable=SC2086
    code="$(curl -sS -o "$tmp" -w "%{http_code}" -X "$method" \
      -H "Content-Type: application/json" \
      $extra_headers \
      -d "$body" \
      "$url" || echo "000")"
  else
    # shellcheck disable=SC2086
    code="$(curl -sS -o "$tmp" -w "%{http_code}" -X "$method" \
      $extra_headers \
      "$url" || echo "000")"
  fi

  if [[ "$code" =~ ^2 ]]; then
    echo "   OK HTTP ${code}"
    head -c 400 "$tmp" | tr '\n' ' '
    echo
    ok=$((ok + 1))
  else
    echo "   FAIL HTTP ${code}"
    cat "$tmp" || true
    echo
    fail=$((fail + 1))
  fi
  rm -f "$tmp"
  echo
}

echo "== staging-mr-bill-probe =="
echo "ADMIN_ORIGIN=${ADMIN_ORIGIN} WEB_ORIGIN=${WEB_ORIGIN}"
echo "USER_ID=${USER_ID} EXECUTION_ID=${EXECUTION_ID} WEB_ONLY=${WEB_ONLY}"
echo

if [[ "$WEB_ONLY" -eq 0 ]]; then
  # MR-BILL-B1 · S2 balance
  probe "$ADMIN_ORIGIN" "B1 balance" GET "/api/v1/internal/billing/entitlements/balance?userId=${USER_ID}"

  # MR-BILL-B2 · S5 debit + idempotent replay
  DEBIT_BODY="$(cat <<EOF
{"executionId":"${EXECUTION_ID}","idempotencyKey":"${IDEM_KEY}","capabilitySkuId":"${CAPABILITY_SKU}"}
EOF
)"
  probe "$ADMIN_ORIGIN" "B2 debit (first)" POST "/api/v1/internal/billing/entitlements/debit" "$DEBIT_BODY"
  probe "$ADMIN_ORIGIN" "B2 debit (replay)" POST "/api/v1/internal/billing/entitlements/debit" "$DEBIT_BODY"

  probe "$ADMIN_ORIGIN" "MC503 traces by execution" GET "/api/v1/admin/billing/traces?executionId=${EXECUTION_ID}"
  probe "$ADMIN_ORIGIN" "MC509 capability-catalog" GET "/api/v1/admin/billing/commerce/capability-catalog"
  probe "$ADMIN_ORIGIN" "MC512 quota-blocked" GET "/api/v1/admin/billing/commerce/quota-blocked-summary"
  probe "$ADMIN_ORIGIN" "MC502 pricing" GET "/api/v1/admin/billing/pricing"
fi

# 用户侧 · Web dev BFF（端口常为 5175）
probe "$WEB_ORIGIN" "FR-B17 me/commerce summary" GET "/api/v1/me/commerce/entitlements/summary"
probe "$WEB_ORIGIN" "FR-WEB08 consumptions page1" GET "/api/v1/me/commerce/consumptions?pageSize=10"
echo "== summary: ${ok} ok, ${fail} failed =="
if [[ "$fail" -ne 0 ]]; then
  echo "Hint: Admin 'cd src/admin && npm run dev' (${ADMIN_ORIGIN}); Web 'cd src/Web && npm run dev' (${WEB_ORIGIN})"
  exit 1
fi

echo "Paste results into specs/requirements/closure-staging-evidence-log.md §2.4"
exit 0
