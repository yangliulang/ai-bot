# 域需求：计费（Billing — 分层商业 · Token 清算与演进）

| 项 | 内容 |
|----|------|
| **产品** | ChainUp AI Agent（Coobit 单所） |
| **文档** | `specs/requirements/domains/admin/billing-management/overview.md`（全文 **`billing.md`**） |
| **状态** | **Agent 消耗主链** **OpenAPI** [`internal/billing-entitlements`](../../../../openapi/internal/billing-entitlements.yaml)、[`user/commerce-me`](../../../../openapi/user/commerce-me.yaml)、**admin · `commerce_phase2`**（**§12**）；**本仓原型** **§0**。**历史** [`billing-me`](../../../../openapi/user/billing-me.yaml) 等 **仅契约归档**。**商业 SSOT** [`commerce-model.md`](commerce-model.md) **v0.3.0** — **生产闭环** **`contract-closure` §8** |
| **策略** | **Agent 消耗计费（默认）**：**仅轨 B** — **S2 Capability 额度门禁** + **S5 `ENTITLEMENT_DEBIT`**；**配额用尽即停**，**续用仅** **升级/加购包** — [`commerce-model.md`](commerce-model.md)。**子账户 USDT** **仍** **承担交易/理财消耗**（**§7.4.1** **仅交易侧**）。与 **PRD 模块五**、[`consume-and-bill.md`](../../../flows/consume-and-bill.md)、**`contract-closure` §8** 对签；[**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) |
| **互引** | [`commerce-model.md`](commerce-model.md)；[`management-console-v1-prd.md`](../management-console-v1-prd.md)；[`../../web/agent-billing.md`](../../web/agent-billing.md)（**`/subaccount/billing` · FR-WEB07～11**）；[`../../web/admin-console-web-billing-reconciliation.md`](../../web/admin-console-web-billing-reconciliation.md) **§0**；[`admin-console-billing-pages-reconciliation.md`](admin-console-billing-pages-reconciliation.md) **§0**；[`design/api.md`](../../../../design/api.md) |

---

## 0. 本仓原型与 OpenAPI 归档（2026-05-27）

| 层 | Agent 消耗（唯一对客主链） | 历史 Token/USDT 流水（`me/billing` 等） |
|----|---------------------------|----------------------------------------|
| **用户 H5** | **`/subaccount/billing`** · **`me/commerce`** — [`web-billing-reconciliation` §0](../../web/admin-console-web-billing-reconciliation.md) | **`src/Web` 不实现** |
| **Admin Demo** | 商业运营 + **执行核销** — [`admin-console-billing-pages-reconciliation` §0](admin-console-billing-pages-reconciliation.md) | **不实现** Token 扣费/退款 UI |
| **OpenAPI YAML** | [`commerce-me`](../../../../openapi/user/commerce-me.yaml)、[`billing-entitlements`](../../../../openapi/internal/billing-entitlements.yaml) | [`billing-me`](../../../../openapi/user/billing-me.yaml)、[`billing-token`](../../../../openapi/internal/billing-token.yaml) — **CC-P0-03** **量产 MR** |

下文 **§12** 仍索引 **历史包**；**读 FR/关单** 时以 **上表「Agent 消耗」列** 与 **reconciliation §0** 为准。

---

### 小团队落地边界（[`LITE-MODE.md`](../../../LITE-MODE.md)）

- **OpenAPI 同窗 ≠ 生产 Hosted / 网关首填 / 财务关单已齐**：**CC-P0-03**（**历史 Token 三线 · OpenAPI 归档**）、**CC-P0-04**、**CC-P0-05**、**Agent 消耗主链**（**`contract-closure` §8**）— **未关单前** **不** 宣称「计费生产已收口」。

---

## 1. 目的（摘要）

在 **Agent 专用子账户就绪** 后，将 **单次可计费执行** 的 **结算/扣减**做成 **可追溯、幂等、可协查**：与 **`exchange-agent` FR-T01～T05、`agentState`、`lastProductBlockReason`**、**运营台模块五**、**用户侧 Billing（主站/H5）** **语义一致**。

**商业主轴（2026-05-26）**：对客以 **Capability / 订阅档位 / 加购包** 表达价值；**`executionId`** 为 **运行与账务统一锚**；**Token** 为 **Metering 维**，**非对客扣款单元**。**Agent 消耗 S5 仅 `ENTITLEMENT_DEBIT`**；**配额用尽即停** — [`commerce-model.md`](commerce-model.md)。**对客与 Demo**：**`me/commerce` + `/subaccount/billing`**（**`contract-closure` §8**）。

---

## 2. Agent 消耗清算主体（SSOT）

- **S5 落账**：**`POST …/billing/entitlements/debit`** → **`ENTITLEMENT_DEBIT`**（**`SC-B20`**）；**绑定** **`executionId`、`capabilitySkuId`**。  
- **禁止**：**Agent 消耗 S5** **fallback** **子账户 Token/USDT 扣费**（**`FR-B21`**）；**`INSUFFICIENT`** **即终止**。  
- **子账户 USDT**：**仅** **交易/理财等交易所侧消耗**（**§7.4.1**）；**与 Agent 消耗计费分域**。

**追溯键下限**（与 [`runtime`](../../agent/exchange-agent/overview.md) 对签）：**`executionId`**、**`idempotencyKey`**（必含与 **`executionId`** **字节级一致**之段）、**`billingTraceId`**；与 **`observability`** **可 join**。  
**Capability / 订阅 / 包** 的商业键（如 **`capabilitySkuId`、`subscriptionPeriodId`、`packGrantId`**）**须在** **`design`/OpenAPI MR** **与** **`executionId`** **可 join** — **Phase 2**。

### 2.1 商业模型与分层（同窗）

**Capability → 映射/聚合 → Execution → Metering → Pricing → Settlement** 全栈与 **用尽即停 / 仅加购包** 规则 — **SSOT** [`commerce-model.md`](commerce-model.md)。

---

## 3. 同名 §7.4（防串号）

- **`billing.md` §7.4（本文件）**：**结算策略 SSOT**（**`BILLING_SETTLE_POLICY=ENTITLEMENT_ONLY`**、**`PER_EXECUTION_FINAL` 与 token 封印** 等）；**§7.4.1** **交易侧 USDT 可用**（**写路径 · 非 Agent S5 扣 Token**）。  
- **`management-console-v1-prd` 附录 A §7.4**：**运营协查 UI / 计费流水 CSV 导出**（**≠** 结算策略）。

---

## 4. 本域包含 / 不包含（V1 · 与演进）

| 判定 | 内容 |
|------|------|
| **包含（V1 目标 · 运营/对读）** | **Token 费率/最小扣费** **配置与展示**（**Metering/协查**）；**平台级流水查询/导出**（**轨 A 历史面**）；**退款/冲正**；**月度账单**；**§7～§8、`billCode`**；**`FR-MC501～508`**、**`FR-B02`～`FR-B16`**、**`SC-B01`～`SC-B15`**。 |
| **包含（产品主链 · Phase 2）** | **订阅与 Capability 配额**、**加购包**、**S2/S5 轨 B**、**用尽阻断**、**`me/commerce`** — **FR/SC** [`functions.md` §5](functions.md)；**宿主小样** **已链**；**生产 Hosted** **须** **`contract-closure` §8**。 |
| **不包含** | 将 **Coin 撮合手续费** 与 **本 Agent 计费账单** 混算；**主账户非 Agent** 交易账单；完整 **税务/开票**（**延后 ADR**）。 |

---

## 5. 文档索引（阅读顺序）

| 顺序 | 文档 | 说明 |
|:----:|------|------|
| 0 | [`commerce-model.md`](commerce-model.md) | **商业分层、仅轨 B 清算、用尽即停** — **先读** |
| 0b | [`admin-console-billing-pages-reconciliation.md`](admin-console-billing-pages-reconciliation.md) | **运营台三项 + 商业运营五 Tab**（总览 / 商业运营 / 执行核销）**§0 对齐快照** |
| 1 | [`functions.md`](functions.md) | **FR-MC501～508**、**FR-B / SC-B** 规划表 **+ §5 Phase 2** |
| 2 | [`rules.md`](rules.md) | **`PER_EXECUTION_FINAL`、幂等、权限**、流水 **ledger** 扩展 |
| 3 | [`flow.md`](flow.md) | 资格、**权益/包**、尝试、失败、冲正、导出 |
| 4 | [`config.md`](config.md) | **`BILLING_MODE`、IA 骨架** |
| 5 | 本文 **§7～§10** | 与 [`consume-and-bill.md`](../../../flows/consume-and-bill.md)、**`exchange-agent`** **既有互引锚点** |

---

## 6. 规划里程碑（非排期）

| 阶段 | 交付物 |
|------|--------|
| **M1 · 账务 HTTP** | **`design/api` 登记**：**Agent 主链** **`internal/billing/entitlements/*`** + **`me/commerce`** + **`admin/billing/commerce/*`**（**`contract-closure` §8**）；**历史** **`me/billing` / `internal/billing/charges`** — **CC-P0-03** |
| **M2 · 运营可查因** | 模块五 **协查**（`executionId` / `billingTraceId` / `userId`）与 **附录 A §7.4** 导出 **权限/审计**一致 |
| **M3 · 对账** | **`D-12`** 首填、账期异步导出、**`SC-B*`** 与 **`config.md` §9.3** **联表闭合** |
| **M4 · 商业轨（Phase 2）** | **权益/订阅/加购包 `OpenAPI` + `design/api` 登记**；[`commerce-model.md`](commerce-model.md) **S2/S5 仅轨 B**、**`SC-B20/B21`**；**`contract-closure` §8** **关单** |

---

## 7. 结算与用户可见语义（锚点）

### 7.1 计费尝试与终局

单次 **扣费边界**：**`PER_EXECUTION_FINAL`**（见 [`rules.md`](rules.md)）。**幂等**：**同一 `executionId`** **至多一条成功 `ENTITLEMENT_DEBIT`**（**`SC-B20`**）。

### 7.2 最小扣费单位 `effectiveMinChargeUsdt`

**配置真源**：[`keys` §5](../trading-agent-config/keys.md)；**展示** **FR-MC501**（平台）与 **FR-B02**（用户侧 **当前生效值**）。低于 **最小可划转/记账单位** 时 **跳过单笔扣费或滚存至满足阈值** — 与 **`BILLING_SETTLE_POLICY`、账务 HTTP**、[consume-and-bill S5](../../../flows/consume-and-bill.md) **同窗**。**若 **编辑入口 **挂在 **全局配置 Tab** **而非模块五，`ADR`** **单行** **划界**。

### 7.3 `billCode` 与用户可见语义

**下限**与 **`FR-T05`、[`flow`](../../agent/exchange-agent/trade-assistance.md) product 码列、`config.md` §9.3** 一致；含 **`INSUFFICIENT_BALANCE`、`CHARGE_GATEWAY_ERROR`、`CANCELLED`（独立文案）** 等。**详表** **`OpenAPI` MR** 回填。

### 7.3.1 理财矩阵写 vs 计费

**`wealth.subscribe` / `wealth.redeem`**：**504/UNKNOWN** 时 **用户可见成交结论** 与 **S5 核销评估** **解耦** — **`§10.5`**；流程见 [`wealth-via-agent.md`](../../../flows/wealth-via-agent.md)、[`consume-and-bill.md`](../../../flows/consume-and-bill.md)。

### 7.4（本文件）结算策略 `BILLING_SETTLE_POLICY`

**何时**触发 **S5 权益核销 HTTP**、**`BLOCK_NEW`** **解除**、**失败重试策略** — **默认 `BILLING_SETTLE_POLICY=ENTITLEMENT_ONLY`**；**`SC-B20`、`CC-P0-05`**、**`consume-and-bill` S5** **会签回填**。

#### 7.4.1 子账户 USDT 共用可用（资金顺序 · 交易/理财侧）

**结构事实**：**Agent 专用子账户 · 现货 · USDT 可用** **承担交易下单、理财等交易所侧消耗**。**Agent 消耗计费** **不** **在 S5 扣该池 Token 费** — **见** [`commerce-model.md`](commerce-model.md)。**写路径** **仍须** 在 **S2** 判定 **交易侧 USDT 可用** 是否满足 **保证金/下单需求**（与 **Capability 额度门禁** **并列**）。

**主策略（写路径 · 交易消耗）**：

1. **执行前门禁（必选）**：在 **消费主路径 S2**（凡 **须交易写** 的路径）判定：**当前可用** 能覆盖 **本笔交易/理财的保守下界**（**`design` 冻结** 预估与缓冲键）。**不满足** → **阻断**，用户可见与 **`FR-T03`** 一致。

2. **待结算预留（可选增强）**：对 **交易写** **占位/冻结** 预估 USDT，至 **成交终局** 或 **释放**。

3. **最低留存缓冲（可选）**：配置 **子账户 USDT 可用不得低于** 某阈值 **方允许** 新的 **交易写**。

**互引**：[`consume-and-bill`](../../../flows/consume-and-bill.md) **S2**；[`../../agent/exchange-agent/overview.md`](../../agent/exchange-agent/overview.md) **`FR-T02`～`FR-T04`**。

### 7.5 Token 费率 `BILLING_TOKEN_RATE`

**定义**：input/output Token（粒度如「每 1k tokens」，**OpenAPI/`design`** 冻结）折算 **USDT** 的单价或阶梯；可选按 **`modelId`/场景** 分档。**配置**：**FR-MC502**、[`keys` §5](../trading-agent-config/keys.md)；运行时须与结算服务 **同版本快照**；变更须 **审计**，与 **`effectiveMinChargeUsdt`、`BILLING_SETTLE_POLICY`** 同窗评审。

## 8. 用户侧消耗与 Billing（主站/H5）

**主链（Phase 2 · 轨 B）**：**FR-B17～B20** — **订阅/Capability 配额摘要**（**`me/commerce/entitlements/summary`**）+ **消耗明细/月度**（**主列 Capability/SKU**、**核销状态**）；**用尽阻断** **FR-B19** — [`commerce-model.md`](commerce-model.md) **§5.3**（**`executionId` ↔ `billingTraceId` join**）。

**用户 H5（Agent 消耗 · 本仓已实现）**：**FR-WEB07～11**、**FR-B17～B20** — [`web/agent-billing.md`](../../web/agent-billing.md)、[`web-billing-reconciliation` §0](../../web/admin-console-web-billing-reconciliation.md)（**`/subaccount/billing`** · **`me/commerce`**）。**历史 FR-B12～B16（`me/billing` Token 流水）**：**OpenAPI 归档 · CC-P0-03** — **本仓 `src/Web` / Admin Demo 不实现**（见 **§0**）。

**用户级流水** **≠** **平台级**：用户 **不可** **`userId`** **枚举**他人；详见 [`rules` §8](rules.md)。

---

## 9. 产品级 FR-B / SC-B（占位索引）

| FR | 语义方向 |
|----|----------|
| **FR-B02** | 计费说明：**Token 费率**（读者安全子集）+ **`effectiveMinChargeUsdt`** 生效说明 |
| **FR-B05** | **`idempotencyKey` 与 `executionId` 绑定** |
| **FR-B07** | **`FAILED_INSUFFICIENT` / `INSUFFICIENT_BALANCE` / `BLOCK_NEW`** |
| **FR-B11 / FR-B14** | **（轨 A 对读）** 子账户 USDT 扣减 + 收入专户入账 |
| **FR-B12 / FR-B14 / FR-B15** | **用户级**明细：**列表 / 详情 / CSV** |
| **FR-B13** | **平台级**导出（附录 A **§7.4** 语义；与 **FR-MC507** 同窗） |
| **FR-B16** | **用户级月度账单**：汇总 + 下载 |
| **FR-B17～B21** | **Phase 2 商业层**：配额摘要、用尽阻断、Capability 归因、**禁止套餐外按量后付** — **详** [`functions` §5](functions.md) |

| SC | 语义方向 |
|----|----------|
| **SC-B01** | **`PER_EXECUTION_FINAL` 与核销终态一致** |
| **SC-B02** | **配额/余额族 E2E 与 `billCode`/stableReason 对齐**（**核销 INSUFFICIENT** **与** **交易 USDT 不足** **分族**） |
| **SC-B08** | **轨 A 对读**：单 `executionId` 至多一条 **`CHARGE` SUCCESS**（**非 Agent S5 默认**） |
| **SC-B13** | **用户账单分页上界（如 ≤200）** |
| **SC-B14** | **月度账单** 与 **当月明细 rollup** 可对（容差 **`design` 定**） |
| **SC-B15** | **退款** **幂等**、**账务**可追溯 |
| **SC-B20 / SC-B21** | **Phase 2**：**轨 B 核销幂等**；**配额用尽 S2 阻断** — [`functions` §5.3](functions.md) |

**详表**：[`functions` §3](functions.md)。**Phase 2 商业层**：[`functions` §5](functions.md)。**产品与 FR 收口矩阵**：[`functions` §4](functions.md)。

---

## 10. 开放决策与设计交界（节选）

### 10.1 `D-2` · 默认终局：成功结束 + token 封印

**可计费**路径 **业务终局** **默认**先 **封印计量**再 **评估权益核销（S5 · 轨 B）**（与 [`boundaries.md`](../../agent/exchange-agent/boundaries.md) **PER_EXECUTION_FINAL + UNKNOWN** 脚注一致）。

### 10.2 `D-1` · 余额不足时在途

**(A)** 完成原子步 **vs (B)** 强中止 — **[`config.md` §11 `D-1`](../management-console-v1-prd.md)**、**`FR-T04`**、[`architecture.md`](../../../../design/architecture.md) **对签**。

**V1 需求默认（与 §7.4.1 配套 · 分域）**：

1. **Agent 消耗核销（轨 B · 主链）**：若 **S5** **`ENTITLEMENT_DEBIT`** **返回 `INSUFFICIENT`**（**含 S2 已放行但并发耗尽**）：**不得** **fallback 扣 Token**；**记** **核销失败/跳过**、**`FR-T05`** **升级/买包** 或 **运营处置** — **同窗** **`FR-B19`/`FR-B21`/`SC-B20`**。**不** **因核销失败** **自动回滚** **已不可逆** **之** **交易侧事实**（**与下条并列**）。

2. **交易侧 USDT（§7.4.1）**：若 **交易 / 理财写** 等副作用 **已不可逆**（典型 **成交已发生**），而 **交易门禁** **事后** 发现 **子账户 USDT 不足**：**默认采纳 (A)** — **不**自动回滚成交；**阻断** **新交易写**、**`FR-T03`** **充值引导** — **同窗** **`D-1`**、**`FR-T04`**。**须** **`contract-closure` + `design`** **同窗冻结** **最终实现布尔**。

### 10.3 `D-5` / `D-7`

**`D-5`**：**`traceKey`** **运营展示字段** **与** **`billingTraceId`** **同值语义** — **SSOT** [`observability/overview.md`](../../../observability/overview.md) **（`traceKey`）**；**控制台协查** **同窗** [`management-console-v1-prd` §11 `D-5`](../management-console-v1-prd.md)。**`D-7`**：**未知终局（UNKNOWN/504）与计费评估/扣减耦合同步** — **不得** **口头分叉**；**主路径** [`consume-and-bill.md`](../../../flows/consume-and-bill.md)、[`design/architecture.md`](../../../../design/architecture.md)。**收口** **见** [`contract-closure.md`](../../../contract-closure.md) **CC-P0-05**。

**需求闭合（2026-05-09）**：**附录 A §11** **`D-5`/`D-7`** **权威展开** **已锚** 本文 **§10.3** **与** [`observability/overview.md`](../../../observability/overview.md) — **实现** **须** **三处同窗** **单一语义**；**争议** **以** **`contract-closure` CC-P0-05** **DoD** **勾选** **关闭**。

#### 10.3.1 `D-5` / `D-7` · 实现与观测对签检查单（**CC-P0-05**）

**用途**：关闭 **未知终局（UNKNOWN/504）与计费** **口头条目分叉** — **须** **同一 MR/工单** **勾选** **并** **链** **`executionId`** **样例**（**或** **台账 id**）。

1. **`D-5`（`traceKey`）**：**运营 UI / 协查 API** **展示** **`traceKey`** **与** **账务** **`billingTraceId`** **同窗同值**（**`billing-schemas`**、**OpenAPI 同窗**）；**抽样** **≥1** **`executionId`** **可** **从** **观测时间线** **join** **至** **账务流水/对账导出**（**`FR-MC508`** **或** **同窗字段**）。  
2. **`D-7`（未知终局 × 计费）**：**写路径** **遇** **504/UNKNOWN** **首条** **交易所事件** **`exchangeOutcome`** **`unknown`** **（** **`SC-OBS03`** **可对账** **）**；**计费评估/封印** **不得** **与** **[`consume-and-bill.md`](../../../flows/consume-and-bill.md)** **及** **[`architecture.md`](../../../../design/architecture.md)** **叙事** **静默矛盾** — **须** **载明** **「UNKNOWN 下是否推迟扣费/如何对账」** **实现策略** **与 Runbook** **一句** **链** **本条 MR**。  
3. **PRD §13**：**发布清单** **对应** **`[ ]`** **项** **在** **全流程关闭** **时** **勾选** **并** **互引** **本条** **序号 1～2**。  
4. **闭环纪律（2026-05-09）**：**未** **合并** **实现 MR** **并** **在工单中勾选 1～2** **前**，**`management-console-v1-prd` §13 `D-5`/`D-7`** **须** **保持 `[ ]`** — **见** [`contract-closure.md`](../../../contract-closure.md) **§2 · CC-P0-05**。  
5. **仓库回填**：关单 **`contract-closure`** **[§2.1](../../../contract-closure.md#cc-p0-signoff-register)** **`CC-P0-05`** **行** **须** **与** **本条** **序号 1～2** **同窗** **填入** **MR/样例链**。

**当前**：**文档检查单** **已冻结**；**PRD 勾选** **绑定** **实现** **终裁**。

### 10.6 `D-12` · Agent 收入专户引用（`BILLING_AGENT_REVENUE_ACCOUNT_REF` / **CC-P0-04**）

- **配置键 SSOT**：[`keys.md` §5 `BILLING_*`](../trading-agent-config/keys.md) · [`management-console-v1-prd.md` 附录 A §5.1](../management-console-v1-prd.md)。  
- **值格式**：**下文 §10.6.1** **为** **V1 需求文档冻结范式**（**财务/所内** **仍须** **书面会签** **选用** **A/B** **或** **同窗 JSON**）；**OpenAPI** **`revenueAccountRef`** **同窗** [`billing-schemas.yaml`](../../../../openapi/components/billing-schemas.yaml)。  
- **语义**：Token 扣减自 **§2** **扣减主体** **等额** **入** **本专户**（[`overview` §2 · FR-B11/B14](overview.md)）；**禁止** 默认从 **主账户母账本** 扣 **Token 费** 却 **误记** **收入** **至** **非 Agent 收入科目**。  
- **DoD**：**生产** **`BILLING_AGENT_REVENUE_ACCOUNT_REF`** **模板落地 + 配置首填** — **见** [`contract-closure.md`](../../../contract-closure.md) **CC-P0-04**；**未闭合** **不得** 标 **PRD §13 生产已冻结**。

#### 10.6.1 V1 值格式范式（文档冻结 · **CC-P0-04** 需求子集）

**目的**：在 **财务/账务** **口头/工单** **终裁** **前**，仓库内先固定 **可解析、可审计** 的 **字符串范式**，与 **`InternalChargeRequest.revenueAccountRef`** **快照** **同窗对签**（**非** **生产真实 id** **占位**）。

**干系人确认（评审纪要 2026-05-09）**：**V1 默认可采用简化形态** — **`BILLING_AGENT_REVENUE_ACCOUNT_REF`**（或 [`keys` §5](../trading-agent-config/keys.md) **同窗键名**）**直接配置收入专户 UID**（**所内账户体系下可解析的一节 id**），**不强制** **上表 A/B 管道语法**。**A/B** **仍保留** 供 **需多段语义 / 台账码表** 的所内选用；**运行时快照** **须** 与 **配置真源** **一致**。**CC-P0-04** **关闭** **仍建议** **财务书面会签 + 首填审计**（**见** **下方检查单**），**豁免** **须** **`contract-closure` §8** **登记风险**。

| 范式 | 语法（示意） | 说明 |
|------|----------------|------|
| **A · 管道分隔** | `MA:{masterUid}\|SA:{agentSubAccountId}\|REV:{internalLedgerCode}` | **三段非空**；`internalLedgerCode` **为** Coobit/账务 **冻结词表**（所内可替换为真实码表值） |
| **B · 单行内部 id** | `ACCT:{coobitInternalRevenueAccountId}` | **单 id** **须** **在财务台账** **可反查** **至** **Agent Token 收入专户** |
| **C · UID 直配（V1 简化默认）** | `{revenueAccountUid}` | **单行** **收入专户 UID**，**与** **部署/运营配置** **同窗**；**反查与科目** **所内财务台账** **约束** |

**首填 MR / 工单检查单**（**关闭 CC-P0-04** **时** **逐项勾选** **并** **链** **审计 id**）：

1. **财务 + 账务** **书面选用** **范式 A、B、C 之一**（或 **经 ADR 的同窗 JSON**），**与** **本条表** **无静默分歧**（**选用 C** **时** **仍须** **确认 UID** **对应** **Agent Token 收入专户** **科目**）。  
2. **沙箱/生产** **配置源** **首值** **已写入** **`BILLING_AGENT_REVENUE_ACCOUNT_REF`** **并** **`admin.audit`**（或 **等价审计**）。  
3. **运行时** **`revenueAccountRef`（若有）** **与** **配置真源** **一致** **策略** **已载** **实现设计** / Runbook。  
4. **`FR-MC508`** **对账导出** **含** **本引用** **或** **可稳定 join** **字段**。
5. **财务书面会签（关闭 CC-P0-04 必填）**：**工单号** ______；**会签日期** ______；**与** **上文范式 A/B** **选用结论** **一致** **（禁止** **口头偏离** **）**。  
6. **仓库回填**：关单 **`contract-closure`** **[§2.1](../../../contract-closure.md#cc-p0-signoff-register)** **`CC-P0-04`** **行** **须** **与** **本条** **序号 1～5** **同窗** **填入** **工单号/日期/MR/审计 id**。

### 10.4 `D-9` · Context 与计费

**压缩/工具回填** 是否影响 **`inputTokens`** 的计费口径：**运行时** 以 [`../../agent/agent-context/overview.md`](../../agent/agent-context/overview.md) 为准；**账务终裁** **`D-9`** 须 **`billing`/`observability`/`design` 同窗 MR**。

### 10.5 UNKNOWN / 504

**不对用户断言已成交**；**S5 权益核销评估** **不因 UNKNOWN 单独整条推迟** — [`design/architecture.md`](../../../../design/architecture.md)、[`consume-and-bill.md`](../../../flows/consume-and-bill.md)。

---

## 11. `configKey` 与控制台

**`BILLING_*`、`effectiveMinChargeUsdt`、`BILLING_AGENT_REVENUE_ACCOUNT_REF`** 真源：[**`keys.md` §5**](../trading-agent-config/keys.md)（及附录 A §5.1）；**模块五写入口** vs **全局配置 Tab** **划界**（**审计、乐观锁**见 **`design/api`**）。

---

## 12. OpenAPI 同窗（**Agent 主链 + 历史包归档** · 需求终裁索引）

| 面 | 仓库内 Spec | 域条文（验收锚） |
|----|-------------|------------------|
| **内部 · 轨 B（Agent S5 主链）** | [`internal/billing-entitlements.yaml`](../../../../openapi/internal/billing-entitlements.yaml) | **`FR-B17～B21`、`SC-B20`、`SC-B21`**、**§5.3 执行 join** — [`commerce-model.md`](commerce-model.md) |
| 用户 **`me/commerce*`** | [`user/commerce-me.yaml`](../../../../openapi/user/commerce-me.yaml) | **FR-B17** · 配额/消耗摘要 |
| 运营 **`admin/billing/commerce*`** | [`admin/billing-admin.yaml`](../../../../openapi/admin/billing-admin.yaml) | **FR-MC509～512** |
| 用户 **`me/billing*`**（**历史 · 归档**） | [`user/billing-me.yaml`](../../../../openapi/user/billing-me.yaml) | **FR-B12～B16** — **非本仓 Demo** |
| 运营 **`admin/billing*`**（**含 commerce_phase2 + 历史 paths**） | [`admin/billing-admin.yaml`](../../../../openapi/admin/billing-admin.yaml) | **FR-MC501～512**；**Token 退款等历史 path** **无 Demo UI** |
| 内部 **`internal/billing/charges`**（**历史 · 归档**） | [`internal/billing-token.yaml`](../../../../openapi/internal/billing-token.yaml) | **非 Agent S5** |
| 同窗组件 | [`components/billing-schemas.yaml`](../../../../openapi/components/billing-schemas.yaml) | **`BillingTraceId`/`traceKey`（D-5）** · **Entitlement / Commercial schemas** |

### 12.1 仓库内 OpenAPI PATH 同窗（**CC-P0-03** · **示意 = spec paths**）

**说明**：下列 **HTTP path** **与** **仓库** **`specs/openapi`** **三线 YAML** **`paths`** **键** **一致**；**`design/api.md`** **专节** **「`/api/v1/...` 或所内等价」** **在需求侧** **默认** **与** **本同窗** **无分歧**，直至 **生产 BFF** **显式改名** — **须** **`contract-closure` §4 + §7** **同窗 MR**。**`servers.url`** **仍为** **占位**（**OpenAPI 片段不承载部署 host 真值**）。

**干系人确认（评审纪要 2026-05-09）**：**账务三线对外 base URL** **不** **在** **规格内** **拆分** 「测试/生产」**多套叙事**；**各环境** **各自** **在配置文件 / 部署参数** 中填写 **可访问的 baseUrl** 即可（**与** **OpenAPI `servers`** **在实现侧拼装** **同窗**）。**关闭 CC-P0-03（全流程）** **时** **仍须** **MR** **证明** **三线 host** **与** **登记表 / 实现** **一致** — **证据链** **见** [`contract-closure` §2.1](../../../contract-closure.md#cc-p0-signoff-register) **与** **§5.2**。

| 面 | Spec | PATH 键（节选） |
|----|------|-----------------|
| **`internal/billing*`（轨 A）** | [`internal/billing-token.yaml`](../../../../openapi/internal/billing-token.yaml) | `/api/v1/internal/billing/charges`、`.../by-idempotency`、`.../refunds/apply` |
| **`internal/billing* · internal/commerce*`**（**轨 B · spec**） | [`internal/billing-entitlements.yaml`](../../../../openapi/internal/billing-entitlements.yaml) | `.../billing/entitlements/debit`、`.../billing/entitlements/balance`、`.../commerce/pack-grants/apply` |
| **`me/billing*`** | [`user/billing-me.yaml`](../../../../openapi/user/billing-me.yaml) | `/api/v1/me/billing/charges`、`.../{billingTraceId}`、`.../statements`、`.../statements/{periodId}/export`、`.../charges/export` |
| **`me/commerce*`**（**Phase 2**） | [`user/commerce-me.yaml`](../../../../openapi/user/commerce-me.yaml) | `/api/v1/me/commerce/entitlements/summary` |
| **`admin/billing*`**（**含 `commerce_phase2`**） | [`admin/billing-admin.yaml`](../../../../openapi/admin/billing-admin.yaml) | **轨 A**：`summary`、`pricing`、`traces`、`charges`、`refunds`、… **／轨 B**：`.../billing/commerce/capability-catalog`、`.../commerce/users/{userId}/overview`、…（**详见 spec**） |

**`servers` / 网关 baseUrl（随环境配置，不强制本文件维护分环境空表）**：

- **需求默认**：**internal / me / admin** **三条线的可解析 base URL** **由** **运行环境配置**（**同一键族、不同取值**）**提供**；**本域** **不** **强制** **维护** **dev / staging / prod** **并列登记表**。**首填与对签** **仍** **落在** **实现 MR +** [`contract-closure` §2.1](../../../contract-closure.md#cc-p0-signoff-register) **`CC-P0-03`** **行**（**host** **与** **登记表第三列** **同窗**）。
- **OpenAPI**：**`servers.url` 占位** **直至** **同窗 MR** **替换** **或与** **BFF 网关规则** **对齐** — **不因** **省略上表** **削弱** **DoD**。

**实现/生产对签**：**Agent 消耗**：**FR-B17～B21**、**SC-B20/B21**、**§5.3 执行 join** — **`contract-closure` §8**。**历史 Token 包**：**FR-MC501～508**、**SC-B08/B13/B15** — **CC-P0-03**（**非本仓 Demo**）。**观测 D-5** **须** **与** **`billingTraceId`** **同窗**。

**登记表**：[`design/api.md`](../../../../design/api.md) **账务/`me`/模块五 + 轨 B 行**。**轨 B YAML** **`internal/billing-entitlements` / `user/commerce-me` / `admin` · `commerce_phase2`** **已链** — **对外闭环宣称** **仍** **须** **`contract-closure` §8 + 实现 MR**。**字段级变更** **须** **同窗 MR** **更新** **上表 + 本域 FR/SC**。

---

**文档版本**：0.3.4 · **维护**：产品 + 账务域 owner · **本版**：**§12 轨 B 主链索引**、**§3/§7/§10 核销语义**。**承** **0.3.3**。
