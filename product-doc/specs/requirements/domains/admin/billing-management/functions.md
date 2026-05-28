# Billing Management · 功能清单、规划与验收索引

**叙事 / 锚点**：[`overview.md`](overview.md)（**`billing.md`**）· **商业分层 SSOT** [`commerce-model.md`](commerce-model.md)；**聚合 PRD**：[`../management-console-v1-prd.md`](../management-console-v1-prd.md) **§8 模块五**（**`FR-MC501～508`**）；**消费主路径**：[`../../../flows/consume-and-bill.md`](../../../flows/consume-and-bill.md)。**契约闭环**：[`../../contract-closure.md`](../../contract-closure.md) **§8（Agent 消耗）**、**CC-P0-03～05**（**历史 Token OpenAPI / 观测**）。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. 划界

| 主题 | 说明 |
|------|------|
| **本模块（运营台 · 模块五）** | **Commerce/SKU 配置**（**FR-MC509～512**）、**Token 费率/Metering**（**对读**）、**平台流水/退款**（**轨 A 历史面**）；**权限**财务/运营/只读分拆（[`rules.md`](rules.md)）。 |
| **Runtime 侧** | **门禁顺序**、**`executionId` 分配**、**在途终局** — **[`exchange-agent`](../../agent/exchange-agent/overview.md)**；**不**重复 **§7 公式**（**消费** [`overview` §7](overview.md)）。 |
| **用户侧** | **主站/H5**：**`/subaccount/billing` · `me/commerce`**（**FR-B17～B20**）；**FR-B12～B16** **仅 OpenAPI 归档**（**§0**） |
| **真源** | **`BILLING_*` / `COMMERCE_*`** → [`keys.md`](../trading-agent-config/keys.md)；**HTTP** → [`design/api.md`](../../../../design/api.md)（**Agent 主链 + CC-P0-03 历史包**） |

**编号说明**：**`FR-MC501～508`** 以 **PRD §8** 为准；历史草稿若出现 **509～515**，**须 MR 合并进 501～508 或标为 backlog**，**避免**与 **PRD** **双轨**。

---

## 2. FR-MC501～508（规划展开 · V1）

下列 **为规划条**；**Given/When/Then** **细表** **随 OpenAPI 填链 MR** 收口。

| FR | 对象 | 行为（摘要） | 互引 |
|----|------|--------------|------|
| **FR-MC501** | 运营 | **计费健康看板**：`BILLING_MODE`、**`effectiveMinChargeUsdt`**（最小扣费生效值）、**`BILLING_TOKEN_RATE`** 生效摘要；网关失败率见 **FR-MC506** | [`config.md`](config.md)、[`keys` §5](../trading-agent-config/keys.md) |
| **FR-MC502** | 运营（双签） | **Token 费率定义**：input/output（及可选 **模型/场景** 维）**→ USDT** 规则；**审计**；**与 `keys` 同窗 MR** | [`keys` §5 `BILLING_TOKEN_RATE`](../trading-agent-config/keys.md) |
| **FR-MC503** | 运营 | **单笔协查**：`userId`、`executionId`、`billingTraceId` **贯通** **`billing.entitlement_debit_*`**（**主链**）+ **时间线** **`FR-MC801`/`SC-OM-01`** | [`observability/overview.md`](../../../observability/overview.md)；[`observability-management/functions.md`](../observability-management/functions.md) |
| **FR-MC504** | 运营 | **平台级流水查询**：时间窗、`userId`、状态、`billingTraceId` 等；**归因列**；**不含 Secret** | **读 API** 与 **`FR-MC507` 导出同源**；附录 A **§7.4** 为 **协查/导出 UX** 名称 |
| **FR-MC505** | 财务主导 | **退款/冲正**：工单、审批、**幂等退款键**、绑定原 **`billingTraceId`**；**USDT 退回子账户** + **收入专户冲减** **双分录**；审计 | [`flow.md`](flow.md)、[`rules.md` §6–7](rules.md) |
| **FR-MC506** | 运营 | **核销/账务错误聚合**（**`ENTITLEMENT_DEBIT` 失败** + **轨 A `CHARGE` 对读**；下钻 **FR-MC503**） | [`overview` §7.3](overview.md) **`CHARGE_GATEWAY_ERROR`** / **配额族** |
| **FR-MC507** | 财务 | **平台级异步导出**：流水 CSV、**自然月 rollup**（与 **FR-B16** 字段同窗）；水印/脱敏/IAM 见 [`rules` §4–7](rules.md) | 数据源 **FR-MC504** |
| **FR-MC508** | 财务 | **财务对账文件**：字段模板、PSP 映射、与 **`D-12`** **对签字段** | [`config` §3](config.md) |

> **若有**所内表格 **已定 501～508 含义不同**：**不改 runtime 语义**，**仅需**在本表 **做了一行映射** **并更新 PRD §8**。

---

## 3. FR-B · SC-B（产品级 · 与 runtime 联考）

### 3.1 FR-B（正文摘要 [`overview` §9–§12](overview.md)）

| FR | Then（下限） |
|----|----------------|
| **FR-B02** | 用户可见 **计费说明**；须展示 **Token 费率口径**（与 **`BILLING_TOKEN_RATE`** **读者安全子集**） |
| **FR-B05** | **`idempotencyKey` 拼装须绑定 `executionId`，与 runtime 一致** |
| **FR-B07** | **`BLOCK_NEW`**、**`INSUFFICIENT_BALANCE`** 与用户提示须与 **`FR-T03`** 一致 |
| **FR-B11/B14** | **（轨 A 对读）** 扣减 HTTP 成功语义、收入专户双分录 |
| **FR-B12/B14/B15** | **用户级**：本人流水列表、单条详情、**明细 CSV**；分页 **SC-B13** |
| **FR-B13** | **运营台** 附录 A **§7.4** 协查导出；与 **FR-MC507** **同窗权限/水印**（可并入 MC507 而不单独编号） |
| **FR-B16** | **用户级月度账单**：自然月（或产品账期）**汇总** Token 量、USDT、笔数；**列表 + 下载**（`design` · `me/billing`） |

### 3.2 SC-B（验收主题）

| 编号 | Given | When | Then |
|------|--------|------|------|
| **SC-B01** | 单笔未达 **`PER_EXECUTION_FINAL`** | 触发结算评估 | **不**产生 **成功 **`ENTITLEMENT_DEBIT`** **（** **Agent 主链** **）** |
| **SC-B02** | **Capability 配额用尽** **或** **交易侧 USDT 不足** | 用户发起新可计费/写 **或** **在途失败** | **核销 INSUFFICIENT** **与** **交易余额族** **分族**；**与** **`FR-T03`、`FR-B19`、`D-1`** **一致** |
| **SC-B08** | 同一 `executionId` 多次触发 **轨 A** 计费评估 | 结算重试或多路回调 | **`CHARGE` SUCCESS** 至多一条（**非 Agent S5 默认**） |
| **SC-B13** | 任意用户 | 账单列表 `pageSize` 超限 | 返回 **400** 或为网关冻结上界语义 |
| **SC-B14** | 给定自然月 | 用户打开 **月度账单** | **仅本人**；与 **该月** 明细流水 **rollup** 一致（舍入容差 **`design` 定**） |
| **SC-B15** | 已成功扣费 | 财务 **批准** 退款 | **子账户 USDT 增加** + **收入专户冲减** 可追溯；**同一 `billingTraceId`** **成功退款** **至多一次**（**`refundIdempotencyKey`** **幂等**） |

**扩展**：与 **`metrics` SC-T02、SC-T04** **同场景扩写** [`../../../metrics/trading-metrics.md`](../../../metrics/trading-metrics.md)。

---

## 4. 产品议题 → FR 映射（收口表）

| # | 议题 | 用户侧 | 平台侧（模块五） | `configKey` / 契约 |
|---|------|--------|------------------|-------------------|
| 1 | **Token 费率定义** | **FR-B02** 展示 | **FR-MC502** 编辑 | **`BILLING_TOKEN_RATE`**（[`keys` §5](../trading-agent-config/keys.md)） |
| 2 | **最小扣费单位** | **FR-B02** 展示生效值 | **FR-MC502** 或 **全局配置 Tab**（与模块五划界 **ADR**） | **`effectiveMinChargeUsdt`** |
| 3 | **消耗/流水查询** | **FR-B17～B20**、**演进 FR-B12/B15** | **FR-MC504/510** | **`me/commerce`** + **`admin/billing/commerce/*`** |
| 4 | **退款** | 用户 **仅展示** **退款结果/状态**（**不**开放自助发起 **V1 默认**） | **FR-MC505** | **幂等 + 审计 + 对账**（[`rules` §6](rules.md)） |
| 5 | **月度账单** | **FR-B16** | **FR-MC507** **月维度批量** + **FR-MC508** **对账** | **关账任务 cron / `design`** |
| 6 | **交易侧 USDT 门禁** | **FR-T03**、写路径 **FR-T02** | **运营健康 / 协查** **FR-MC503**、**FR-MC506** | **§7.4.1 缓冲键**（[`keys` §5](../trading-agent-config/keys.md)） |
| 7 | **订阅 / Capability / 加购包 · Agent S5** | **FR-B17～B21**（§5） | **FR-MC509～512**（§5） | **`COMMERCE_*` / `BILLING_CAPABILITY_*`**；**轨 B OpenAPI** · **MR-BILL-B1/B2** |

---

## 5. Phase 2 · 商业层（订阅 · Capability · 加购包）

**SSOT** [`commerce-model.md`](commerce-model.md) **§4～§5.3**（**核销序 · 执行 join · OpenAPI**）。**OpenAPI 骨架 + 宿主对照小样** **已入库**。**Agent 消耗关单** **`contract-closure` §8**；**轨 A** **不** **替代** **§8 DoD**。

### 5.0 契约索引（与 OpenAPI 同窗）

| 能力 | `operationId` / 路径示意 | OpenAPI |
|------|---------------------------|---------|
| S2 · 服务侧余额 | `getInternalBillingEntitlementsBalance` · `GET …/entitlements/balance` | [`internal/billing-entitlements.yaml`](../../../../openapi/internal/billing-entitlements.yaml) |
| S5 · 核销（**Agent 主链**） | `postInternalBillingEntitlementsDebit` · `POST …/entitlements/debit` | [`internal/billing-entitlements.yaml`](../../../../openapi/internal/billing-entitlements.yaml) |
| S5 · 加购入账 | `postInternalCommercePackGrantsApply` · `POST …/commerce/pack-grants/apply` | 同上 |
| （**轨 A 对读**）Token 扣费 | `postInternalBillingCharge` · `POST …/billing/charges` | [`internal/billing-token.yaml`](../../../../openapi/internal/billing-token.yaml) |
| 用户 · 配额摘要 | `getMyCommerceEntitlementsSummary` · `GET …/me/commerce/entitlements/summary` | [`user/commerce-me.yaml`](../../../../openapi/user/commerce-me.yaml) |
| 运营 · SKU 矩阵 | `get|patchAdminBillingCommerceCapabilityCatalog` | [`admin/billing-admin.yaml`](../../../../openapi/admin/billing-admin.yaml) |
| 运营 · 用户权益 | `getAdminBillingCommerceUserOverview` | 同上 |
| 运营 · 阻断健康 | `getAdminBillingCommerceQuotaBlockedSummary` | 同上 |
| **宿主接线（小样 · 非 SSOT）** | **`runConsumeAndBillS2CommerceGate` / `runConsumeAndBillS5Settlement`** | [`consumptionBillingHost.ts`](../../../../src/admin/src/productionRuntime/consumptionBillingHost.ts) · [`closure-internal-sprint` §3.7～3.8](../../../closure-internal-sprint.md) · **走读** [`staging-mr-bill-runbook.md`](staging-mr-bill-runbook.md) |

### 5.1 FR-B17～B21（用户侧 · 规划）

| FR | 对象 | 行为（摘要） | 互引 |
|----|------|--------------|------|
| **FR-B17** | 用户 | **档位与 Capability 配额**可读：当前订阅、剩余额度、加购包余额（**主站/H5**） | [`web/agent-billing.md`](../../web/agent-billing.md) **§2.1**；[`user/commerce-me.yaml`](../../../../openapi/user/commerce-me.yaml) |
| **FR-B18** | 用户 / 后台 | **加购包购买**完成 → **额度入账**可查；**`POST …/pack-grants/apply`** **由支付成功作业调用**（**非** 用户直连） | **PSP** **`design`/integrations MR** |
| **FR-B19** | 用户 / Runtime | **配额用尽**：**阻断**对应 Capability **可计费执行**；**`FR-T05`** **可读下一步**（升级 / 买包 Deeplink）；**禁止**静默 **套餐外按量后付** | [`consume-and-bill`](../../../flows/consume-and-bill.md) **S2**；[`exchange-agent`](../../agent/exchange-agent/overview.md) **`FR-T02`** |
| **FR-B20** | 用户 | **流水/月度**：**主展示** **Capability / SKU 归因**；**Token 量**可为 **明细列** **非唯一主标题** | **FR-B12～B16** **扩展 MR** |
| **FR-B21** | 产品（负向） | **默认不包含** 「订阅周期外 **按单价实时累积、事后从子账户划扣」**作为** **主计费模式** | [`commerce-model.md`](commerce-model.md) **§2** |

### 5.2 FR-MC509～512（运营台 · 规划）

| FR | 对象 | 行为（摘要） | OpenAPI / IA |
|----|------|--------------|--------------|
| **FR-MC509** | 运营 | **套餐 / Capability SKU / 映射矩阵**配置与审计（双签 **同窗** **`FR-MC502` 纪律**） | `…/commerce/capability-catalog` · [`config.md`](config.md) |
| **FR-MC510** | 运营 | **按用户协查**：订阅期、配额消耗、加购包余额、**与 `executionId` join** | `…/commerce/users/{userId}/overview` |
| **FR-MC511** | 财务 | **加购包/订阅收入**导出字段模板（与 **FR-MC508** **同窗或扩展 MR**） | `…/commerce/revenue-export-template` |
| **FR-MC512** | 运营 | **配额用尽 / 阻断**类事件健康看板（与 **FR-MC501** **同屏或子卡**） | `…/commerce/quota-blocked-summary` · **Admin 原型** **计费总览 Commerce 卡** |

### 5.3 SC-B（商业层 · 规划主题）

| 编号 | Given | When | Then |
|------|--------|------|------|
| **SC-B20** | 同一 **`executionId`** 已分配且 **S5** **须核销轨 B** | 结算重试或多路回调 **触发** **`ENTITLEMENT_DEBIT`** | **`idempotencyKey`** **`{executionId}:rail-b:entitlement-debit`**（[`commerce-model` §5.1](commerce-model.md)）；**至多一条成功核销**；**重复键** **安全重放** **得等价 `billingTraceId`/状态**；**`INSUFFICIENT`** **终止** **不得** **扣 Token** |
| **SC-B21** | 用户某 **Capability** **剩余额度为 0**（**或** **无有效订阅/包**） | 发起 **须消耗该 Capability** 的 **可计费/写路径** | **S2** **（或 accepted 前最后一道门禁）** **阻断**；**不得** **产生** **新的** **该 Capability ** **成功写**；**`FR-T05`** **引导升级/买包** |

---

## 6. 邻域自检

| 邻域 | 核对 |
|------|------|
| **exchange-agent** | **FR-T01 / T02 / T03 / T04**、`executionId`、**`BILLING_BLOCKED`** |
| **access-control** | 欠费 Pause **不等价于**合规封禁（[`access-control/rules.md`](../access-control/rules.md) 与 billing 分域展示） |
| **agent-management** | **`AGENT_BILLING_BLOCKED`、`lastProductBlockReason`** |
| **telegram** | Billing Deeplink、**FR-T05** |
| **observability · 模块八** | **事件 SSOT**：[`observability/overview` §2](../../../observability/overview.md)；**控制台计费 join**：[`observability-management/overview` §5](../observability-management/overview.md) **M2**、[functions §2](../observability-management/functions.md)、**`SC-OM-01`** |
| **design/api** | **轨 B 主链**：[`internal/billing-entitlements`](../../../../openapi/internal/billing-entitlements.yaml) **·** [`user/commerce-me`](../../../../openapi/user/commerce-me.yaml) **·** **`contract-closure` §8**；**轨 A Token 三线** **对读**（**非 Agent S5 关单**） |

---

**文档版本**：0.3.4 · **维护**：产品 + 账务 + 后台 owner · **本版**：**§1/§4/§5.0 轨 B 主链**、**FR-MC503 核销协查**。**承** **0.3.3**。
