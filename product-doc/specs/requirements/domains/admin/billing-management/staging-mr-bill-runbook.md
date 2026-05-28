# MR-BILL-B1/B2 · 本地 / Staging 走读 Runbook

**用途**：所内 BFF/Worker 接 **`consumptionBillingHost`** 前，用 **规格仓 Dev BFF** 验证 **OpenAPI 路径** 与 **SC-B20/SC-B21** 叙事。  
**证据回填**：[`closure-staging-evidence-log.md`](../../../closure-staging-evidence-log.md) **§2.4** · [`closure-internal-sprint.md`](../../../closure-internal-sprint.md) **§3.7～3.8**。

**禁止**：在未批准环境对真用户账户做写路径走读。

---

## 1. 本地 Dev BFF（`src/admin`）

**一键探针**（Vite 已 `npm run dev` 后）：

```bash
ADMIN_ORIGIN=http://localhost:5173 WEB_ORIGIN=http://localhost:5175 ./scripts/staging-mr-bill-probe.sh
# 兼容：ORIGIN= 等同 ADMIN_ORIGIN
```

脚本覆盖：**Admin**：balance · debit 幂等 · traces · commerce · pricing；**Web（5175）**：`me/commerce`。仅 Web：`./scripts/staging-mr-bill-probe.sh --web-only`。同窗 [`domains/web/staging-me-commerce-runbook.md`](../../web/staging-me-commerce-runbook.md)。

```bash
cd src/admin
# .env.development 示例（端口以 Vite 输出为准，常见 5173/5174）
# VITE_API_BASE_URL=http://localhost:5173
# VITE_USE_BILLING_COMMERCE_API=true
# VITE_USE_BILLING_LEDGER_API=true
npm run dev
```

`npm run dev` 内置 mock：

| 路径 | MR | 说明 |
|------|-----|------|
| `GET /api/v1/internal/billing/entitlements/balance` | **B1** | `userId` → buckets.remaining |
| `POST /api/v1/internal/billing/entitlements/debit` | **B2** | 幂等键重放；`remaining≤0` → **INSUFFICIENT** |
| `GET /api/v1/admin/billing/traces` | **MC503** | 同窗 `mockBillingLedger` |
| `GET/PATCH …/admin/billing/commerce/capability-catalog` | **MC509** | PATCH 仅 Dev 内存；UI **双签抽屉** · **If-Match** → **409** 可测 |
| `GET/PATCH …/admin/billing/pricing` | **MC502** | Token 单价/门槛 · **双签** · `pricingRevision` |

实现：`src/admin/dev/internalBillingEntitlementsBffMiddleware.ts`、`billingLedgerBffMiddleware.ts`、`billingCommerceBffMiddleware.ts`。

---

## 2. 宿主小样（Vitest · 无 HTTP）

对照 **`productionRuntime`**：

- `runConsumeAndBillS2CommerceGate` · `commerceEntitlementS2Evaluate.test.ts`
- `runConsumeAndBillS5Settlement` · `commerceEntitlementS5Settle.test.ts`
- 一键 `runWritePathConsumeAndBill` · `writePathConsumeAndBillOrchestrator.test.ts`

所内接线时 **注入** `fetchImpl` 指向 staging **`INTERNAL_BILLING_BASE_URL`**（**勿**进浏览器 bundle）。

---

## 3. Staging 环境变量（BFF/Worker）

| 变量 | MR | 说明 |
|------|-----|------|
| `PHASE2_COMMERCE_RAILS_ENABLED` | B1/B2 | **`true`** 才走轨 B；默认 **false** |
| `INTERNAL_BILLING_BASE_URL` | B1/B2 | 内网 origin（含 `/api/v1` 前缀策略由实现终裁） |

解析小样：`parseConsumptionBillingHostConfigFromEnv`（`consumptionBillingHost.ts`）。

---

## 4. curl 探针（替换 `$ORIGIN`）

### 4.1 SC-B21 · S2 balance（剩余 0 应阻断）

```bash
curl -sS "$ORIGIN/api/v1/internal/billing/entitlements/balance?userId=u-10482" | jq .
```

记录 **`cap.agent.trade` · remaining** → 填入证据 log **§2.4**。

### 4.2 SC-B20 · S5 debit（幂等）

```bash
curl -sS -X POST "$ORIGIN/api/v1/internal/billing/entitlements/debit" \
  -H 'Content-Type: application/json' \
  -d '{
    "executionId": "20260501999001",
    "idempotencyKey": "20260501999001:rail-b:entitlement-debit",
    "capabilitySkuId": "cap.agent.trade"
  }' | jq .
```

**重复同一 `idempotencyKey`** → 须 **等价** `billingTraceId`/status。

### 4.3 Admin join · traces

```bash
curl -sS "$ORIGIN/api/v1/admin/billing/traces?executionId=20260501999001" | jq .
```

---

## 5. Admin UI 走读（可选）

| 页 | 开关 | 验收 |
|----|------|------|
| `/billing/overview` | `VITE_USE_BILLING_COMMERCE_API`（MC512） | 运行四卡 + 趋势 + 健康 + **配额阻断** 汇总 |
| `/billing/operations` | 同上 | **`tab=subscriptions`** 套餐 · **`packs`** 资源 · **`rules`** 扣减/场景/**MC509 双签** · **`orders`** Crypto 订单 · **`consumption`** 用户协查 |
| `/billing/ledger` | `VITE_USE_BILLING_LEDGER_API` | 核销列表 / 单笔追踪 |
| 执行详情 | mock/API 时间线 | **核销摘要** + **ENTITLEMENT_DEBIT** |

**遗留书签**：`/billing/commerce` → **`/billing/operations?tab=rules`**；`/billing/pricing` → **`/billing/overview`**。

---

## 6. 关单勾选

- [`closure-remaining.md`](../../../closure-remaining.md) **OP-BILL · MR-BILL-B1/B2**
- [`contract-closure.md`](../../../contract-closure.md) **§8 轨 B MR**（生产宣称前）

---

**文档版本**：0.1.0 · **维护**：账务 + Runtime owner
