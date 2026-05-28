# BFF / Worker · consumptionBillingHost 接线说明（所内 MR）

**用途**：**MR-BILL-B1/B2** 宿主在 **Runtime/BFF** 侧注入；**不进** 浏览器 bundle。  
**对照小样**：[`src/admin/src/productionRuntime/consumptionBillingHost.ts`](../../../../src/admin/src/productionRuntime/consumptionBillingHost.ts) · [`internalBillingEntitlementsAdapter.ts`](../../../../src/admin/src/productionRuntime/internalBillingEntitlementsAdapter.ts)。

**走读**：[`staging-mr-bill-runbook.md`](staging-mr-bill-runbook.md) · **探针** [`scripts/staging-mr-bill-probe.sh`](../../../../scripts/staging-mr-bill-probe.sh)。

---

## 1. 环境变量

| 变量 | 默认 | 说明 |
|------|------|------|
| `PHASE2_COMMERCE_RAILS_ENABLED` | `false` | **`true`** 时 S2/S5 走轨 B；**关** 时 S2 **跳过** balance（**非** 回退轨 A 扣 Agent 费） |
| `INTERNAL_BILLING_BASE_URL` | — | 内网 origin（**勿** 重复 `/api/v1` 前缀，与 adapter 路径键同窗） |

解析：`parseConsumptionBillingHostConfigFromEnv(env)`。

---

## 2. 调用序（写路径）

1. **FR-T02 序内** · **S2**：`runConsumeAndBillS2CommerceGate(config, { userId, scenarioId })`  
   → `resolveCapabilitySkuForScenario` → `GET …/entitlements/balance` → **remaining ≤ 0** 阻断。

2. **S4 终局后** · **S5**：`runConsumeAndBillS5Settlement(config, { executionId, scenarioId })`  
   → **仅** `POST …/entitlements/debit`（**`idempotencyKey`** `{executionId}:rail-b:entitlement-debit`）  
   → **禁止** Agent S5 fallback **`POST …/billing/charges`**。

一键编排对照：`runWritePathConsumeAndBill`（`writePathConsumeAndBillOrchestrator.ts`）。

---

## 3. 与 Admin / Web 边界

| 面 | 路径 | 消费者 |
|----|------|--------|
| **内部** | `internal/billing/entitlements/*` | BFF/Worker **仅** |
| **用户** | `me/commerce/entitlements/summary` | 主站/H5 · [`src/Web`](../../../../src/Web) 原型 |
| **运营** | `admin/billing/commerce/*` | Admin 控制台 |

---

## 4. Staging 验收

- [ ] `PHASE2_COMMERCE_RAILS_ENABLED=true` 在 staging Worker  
- [ ] **SC-B21**：`cap.agent.trade` remaining=0 → 新写被拦  
- [ ] **SC-B20**：同一 `idempotencyKey` 重放等价 `billingTraceId`  
- [ ] 证据填入 [`closure-staging-evidence-log.md`](../../closure-staging-evidence-log.md) **§2.4**

---

**文档版本**：0.1.0 · **维护**：账务 + Runtime owner
