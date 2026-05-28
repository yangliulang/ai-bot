# 计费域 · 商业模型与分层（Commerce & Billing Layers）

**路径**：`specs/requirements/domains/admin/billing-management/commerce-model.md`。  
**上级真源**：[`overview.md`](overview.md)（`billing.md`）· **消费主路径**：[`consume-and-bill.md`](../../../flows/consume-and-bill.md) · **产品方向**：[`product.md`](../../../product.md)。

---

## 1. 目的

将 **「对用户卖什么」** 与 **「系统怎么钉账」** 分离：

- **Capability（能力商品）**：用户理解与付费的主对象（如 AI 分析、自动交易、盯盘等 **SKU 语义**）。
- **Execution（运行锚）**：**`executionId`** — **可追溯、幂等、审计、观测**；**不对客作为商品名**。
- **Metering（计量）**：Token、工具次数等 **成本读数**（**观测 / 运营**）；**不等价于对客扣款单元**。
- **Settlement（清算）**：**本产品 Agent 消耗计费 — 仅轨 B**（**订阅 / 加购包权益核销**）；**不**在 S5 对 Agent 消耗再落 **子账户 USDT · Token 扣费（原轨 A）**。

**子账户 USDT** 仍用于 **交易/理财等交易所侧消耗**（与 **Agent 消耗计费** **分域**）；**不**混为「Agent 按 Token 从子账户后付」。

---

## 2. 用户商业规则（已定稿方向）

| 规则 | 说明 |
|------|------|
| **订阅 + Capability 配额** | 用户购买 **档位（如 Free / Pro / Ultra）**；各档位绑定 **Capability 开关与周期配额**。 |
| **配额用尽 → 即停** | 对应 Capability **不得继续产生可计费成功路径**（**`FR-T02`/`FR-T05`**）；**禁止**套餐外按量后付。 |
| **续用方式** | **仅** **升级订阅** 或 **购买加购包**；用尽前 **宜** 阈值提醒（80%/100% 等）。 |
| **结算** | **S5 仅 `ENTITLEMENT_DEBIT`（轨 B）**；**不**默认 **`CHARGE` Token/USDT（轨 A）**。 |

---

## 3. 概念栈（对内实现序）

```text
Capability SKU（对客）
  → 映射 / 聚合（scenario → SKU；见 BILLING_CAPABILITY_MAP）
  → executionId（结算锚）
  → Metering（Token 等 · 观测，非对客扣款）
  → Settlement：轨 B · ENTITLEMENT_DEBIT
```

**映射与聚合（强制）**：**不得**默认 **一比一** 对用户计 **裸 execution 次数** — **须在** **`BILLING_CAPABILITY_MAP`** **冻结**（[`keys` §5](../trading-agent-config/keys.md)）。

---

## 4. 清算轨（Settlement · 产品默认）

| 轨 | 本产品 Agent 消耗计费 | 说明 |
|----|----------------------|------|
| **轨 B · 权益 / 加购包** | **唯一清算轨（默认）** | **`GET …/entitlements/balance`（S2）** · **`POST …/entitlements/debit`（S5）** · OpenAPI [`internal/billing-entitlements.yaml`](../../../../openapi/internal/billing-entitlements.yaml) |
| **轨 A · Token → USDT（子账户）** | **不在 Agent 消耗 S5 使用** | 历史规格 / OpenAPI [`billing-token`](../../../../openapi/internal/billing-token.yaml) **可保留** **供它域或迁移对读**；**本产品** **关单与实现** **以轨 B + `me/commerce` 为主链**，**不**要求 **消费 S5 双轨** |

**核销顺序（`BILLING_SETTLE_POLICY` 默认 `ENTITLEMENT_ONLY`）**：

1. **S2 门禁**：订阅/包 **额度** 是否允许本笔商业动作（**FR-B19**、**SC-B21**）；**不允许** → **阻断**。
2. **S5 落账**：**仅** **`ENTITLEMENT_DEBIT`** 核销（**SC-B20**）；**成功** → 得 **`billingTraceId`**（**`commercialSettlementType=ENTITLEMENT_DEBIT`**）。
3. **无轨 A 步骤**：**`INSUFFICIENT`** **时** **终止**；**不得** **fallback** 为 **子账户 Token 扣费**（**FR-B21**）。

---

## 5. 契约同窗（OpenAPI）

**登记 SSOT**：[`design/api.md`](../../../../design/api.md) **模块五 · 内部商业轨 · 用户 `me/commerce*`**；[`billing-schemas.yaml`](../../../../openapi/components/billing-schemas.yaml)。

| 面 | OpenAPI 包 | 路径（节选） | 主要 FR / SC |
|----|------------|--------------|--------------|
| **内部 · 轨 B（主链）** | [`internal/billing-entitlements.yaml`](../../../../openapi/internal/billing-entitlements.yaml) | `…/entitlements/debit` · `…/entitlements/balance` · `…/commerce/pack-grants/apply` | **FR-B18**、**SC-B20**、S2/S5 |
| **用户 · 商业摘要 / 消耗视图** | [`user/commerce-me.yaml`](../../../../openapi/user/commerce-me.yaml) | `GET …/me/commerce/entitlements/summary` | **FR-B17** |
| **运营 · 商业** | [`admin/billing-admin.yaml`](../../../../openapi/admin/billing-admin.yaml) **`commerce_phase2`** | `…/commerce/*` | **FR-MC509～512** |
| **（非本产品 Agent S5）轨 A 参考** | [`internal/billing-token.yaml`](../../../../openapi/internal/billing-token.yaml)、[`user/billing-me.yaml`](../../../../openapi/user/billing-me.yaml) | Token 账务三线 | **历史 / 对读**；**不**纳入 **Agent 消耗关单 DoD** |

### 5.1 幂等（SC-B20）

**原则**：**同一 `executionId`** **至多一条成功 `ENTITLEMENT_DEBIT` 核销**（**安全重放** **得等价 `billingTraceId`/状态**）。

| 建议 `idempotencyKey` | 绑定 |
|------------------------|------|
| `{executionId}:rail-b:entitlement-debit` | **`capabilitySkuId`**（可选 **`packGrantId`**） |

**实现对照小样**：[`consumptionBillingHost.ts`](../../../../src/admin/src/productionRuntime/consumptionBillingHost.ts)、[`commerceEntitlementS5Settle.ts`](../../../../src/admin/src/productionRuntime/commerceEntitlementS5Settle.ts) — **S5 默认** **不传 `tokenCharge`**。

### 5.2 配置与开关

| 键（示意） | 说明 |
|------------|------|
| **`BILLING_SETTLE_POLICY`** | **默认 `ENTITLEMENT_ONLY`** — S5 **仅轨 B**；**禁止** **未 ADR** **启用 `DUAL_RAIL` 或 `TOKEN_CHARGE`** |
| **`PHASE2_COMMERCE_RAILS_ENABLED`** | **产品目标 `true`**（所内部署可 staged）；**关** = 轨 B HTTP 未接线（**非**「回退轨 A 扣 Agent 费」） |
| **`BILLING_CAPABILITY_MAP`** | **scenario → SKU** — [`keys` §5](../trading-agent-config/keys.md) |
| **`COMMERCE_SKU_CATALOG_REF`** | **套餐目录** — **FR-MC509** |

---

### 5.3 执行记录 ↔ 计费（join · 产品下限）

**每条可计费 `executionId`** **须** **在终局（S4→S5）** **可 join** **至** **至多一条成功 **`ENTITLEMENT_DEBIT`** **（** **`SC-B20`** **）**：

| 面 | 下限 |
|----|------|
| **观测时间线（FR-MC801）** | **`billing.entitlement_debit_*`** **或** **等价 API**；**含** **`billingTraceId`、`capabilitySkuId`、核销状态** |
| **执行详情 · 计费镜像** | **总览卡** **须** **可读** **上述三键**（**无则** **显式** **skipped/非可计费**） |
| **运营协查（FR-MC503）** | **`executionId` ↔ `billingTraceId`** **三联跳转** **与** **D-5** **一致** |
| **Metering** | **Token 等** **可** **并列** **于** **工具/LLM 事件**；**不** **替代** **核销主列** |

**详** [`observability/overview.md` §2](../../../observability/overview.md)、[`observability-management/functions.md` §2](../observability-management/functions.md)、[`admin-console/page-specs.md`](../../../admin-console/page-specs.md) **`runtime.execution-detail`**。

---

## 6. 文档互引

| 文档 | 作用 |
|------|------|
| [`functions.md` §5](functions.md) | **FR-B17～B21、SC-B20/B21** |
| [`flow.md`](flow.md) | **S2/S5 · 轨 B Mermaid** |
| [`consume-and-bill.md`](../../../flows/consume-and-bill.md) | **主路径** |
| [`web/agent-billing.md`](../../web/agent-billing.md) | **FR-B17 · 配额 UX** |
| [`observability/overview.md` §2](../../../observability/overview.md) | **执行时间线 · 计费事件** |
| [`admin-console/page-specs.md`](../../../admin-console/page-specs.md) | **`runtime.execution-detail` · 计费镜像** |

---

**文档版本**：0.3.1 · **维护**：产品 + 账务 owner · **本版**：**§5.3 执行记录 ↔ 计费 join**。**承** **0.3.0**。
