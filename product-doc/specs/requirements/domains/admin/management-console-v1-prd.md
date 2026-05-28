# AI Trading Agent — 管理后台产品需求（V1 · MVP）

| 项 | 内容 |
|----|------|
| **文档** | `specs/requirements/domains/admin/management-console-v1-prd.md` |
| **状态** | Draft |
| **互引** | [`product.md`](../../product.md)；[`billing-management/overview.md`](billing-management/overview.md)；[`prompt-management/overview.md`](prompt-management/overview.md)；[`observability/overview.md`](../../observability/overview.md)；[`contract-closure.md`](../../contract-closure.md)；[`closure-remaining` §0](../../closure-remaining.md#closure-remaining-quicklinks) · [§6/§6.4](../../closure-remaining.md#cc-exec-solve-path)；[`Runtime/overview.md`](../../Runtime/overview.md)、[`Runtime/README.md`](../../Runtime/README.md) |

---

## 3. 管理后台信息架构（V1）

**与各业务子域**（`domains/admin/<子域>/overview.md`）对齐：

| 模块 | 子域 |
|------|------|
| 一 · Agent Management | [`agent-management/overview.md`](agent-management/overview.md) |
| 二 · Prompt Management | [`prompt-management/overview.md`](prompt-management/overview.md) |
| 三 · Tool Management | [`tool-management/overview.md`](tool-management/overview.md) |
| 四 · AI Settings | [`ai-settings/overview.md`](ai-settings/overview.md) |
| 五 · Billing & Settlement | [`billing-management/overview.md`](billing-management/overview.md) |
| 六 · Access Control | [`access-control/overview.md`](access-control/overview.md) |
| 七 · Trading Agent Config | [`trading-agent-config/overview.md`](trading-agent-config/overview.md) |
| 八 · Logs & Observability | [`observability-management/overview.md`](observability-management/overview.md)（事件下限 [`observability/overview.md`](../../observability/overview.md)；**主态边** **§2.4 · `transitionTrigger`**） |

详述见下文 §4～§11；**附录 A** 保留 **`configKey` / `agentState` / 会签** 等实现口径。

---

## 1. 产品定位（V1）

基于交易所能力、**AI Trading Agent**、**订阅 · Capability · 加购包（用尽即停 · S5 仅轨 B 核销）**、**子账户隔离**、**平台统一模型与 Prompt**、**MVP**；目标 **可控 · 可停 · 可观测 · 可计费 · 可配置 · 可风控**。**商业分层 SSOT**：[`billing-management/commerce-model.md`](billing-management/commerce-model.md)。

### 1.1 与 Prompt / 终端的划界

- **Prompt**：**模块二** + [`prompt-management/overview.md`](prompt-management/overview.md)。  
- **Telegram**：[`domains/agent/telegram/`](../agent/telegram/)；渠道闸见 **附录 A · §5.1** `CHANNEL_*`。

---

## 2. 设计原则

| # | 原则 |
|---|------|
| P1 | 可调能力须有后台审计 |
| P2 | 全局/用户/Runtime 停服路径独立存在 |
| P3 | 观测与账务可 join（`executionId`、trace 等） |
| P4 | 交易写与用户确认闸门对签（ADR-001） |

---

## 4. 模块一 — Agent Management

模板（Template）、用户实例（Instance）、Runtime 控制（**Start·Pause·Resume·Stop**、**批量 Pause/Stop** 与状态摘要）、实例维度的 **Agent Logs** 控制台入口（对话 / Tool / Runtime 错误，事件字段下限与 **`observability`** 对签）、**全局门禁只读横幅（G01）**、**模板克隆（T09）**、**模板草稿删除（T10）**与 **实例列表导出（I08）**。**FR-MC101～114** 的 **可测子项** 以 **FR-AM-*** 为 SSOT，见 **§4.1** 与本节互引的 [`agent-management/functions.md`](agent-management/functions.md)。编排仍以 **`executionId`+`scenarioId`** 为准；**控制台与交易确认闸门**的端到端闭环见 [`contract-closure.md`](../../contract-closure.md)。

### 4.1 FR-MC101～114 · 与 FR-AM 对照（验收归因）

| FR-MC | 覆盖 FR-AM（子项） | 验收说明 |
|-------|-------------------|----------|
| **101** | T01 | 模板列表与筛选 |
| **102** | **T02**（创建）· **T03**（编辑/新版本）· **T09**（克隆）· **T10**（**仅草稿**删除/归档） | 每条子项可 **单独建用例**；**T10 不**覆盖已发布模板硬删 |
| **103** | T08 | 启用/停用与存量策略（默认见子域 [`rules.md`](agent-management/rules.md) §6） |
| **104** | T04 | Prompt 绑定与健康 |
| **105** | T05 | Tool 绑定与矩阵校验 |
| **106** | T06 | 默认模型与下线策略 |
| **107** | T07 | 模板风控与全局合并 |
| **108** | G01 | 全局门禁 **只读**横幅；**不改** `GLOBAL_AGENT_SWITCH` 本体 |
| **109** | I01 · I02 · **I08** | 实例列表、创建、**列表 CSV 导出**（各子项独立用例） |
| **110** | I03 · I04 · I05 | 详情、子账户绑定、实例参数 |
| **111** | I06 | 实例删除与在途校验 |
| **112** | I07 | 模板版本钉扎/迁移（无则标 N/A） |
| **113** | **R01～R05**（单实例）· **R06**（批量 Pause/Stop） | **R01～R05** 与 **R06** 分用例；**全局 OFF 下行为**见子域 **G01+R06 冻结规则** |
| **114** | L01 · L02 · L03 | 三类日志 + 查询/详情/导出（导出 **observability-management** SSOT） |

**实现依赖**：日志分页/导出/TRACE **依赖** [`observability/overview.md`](../../observability/overview.md) 与 [`observability-management/overview.md`](observability-management/overview.md) 定稿 API；未定时模块一 **可 UI 占位 + BFF 契约先行**。

---

## 5. 模块二 — Prompt Management

与 [`prompt-management/overview.md`](prompt-management/overview.md)、[`prompt-management/functions.md`](prompt-management/functions.md) **及** **[`prompt-management/runtime-injection.md`](prompt-management/runtime-injection.md)**（**拼装顺序**、**占位符 denylist§2.3**、**Safety 用语闸§7.1**、**会话冻结**、**Tool Schema SSOT**）**对签**。**PRD 条目**：**FR-MC201～207**（细项与验收见 **`functions` §2～§4 · SC-PM**）；**附录 A §1.3**：与 **模块一** **Prompt 绑定** **划界**。**观测 join 键下限**：[`observability/overview.md`](../../observability/overview.md) **§2.3**。

---

## 6. 模块三 — Tool Management

与 [`tool-management/overview.md`](tool-management/overview.md)、[`tool-management/functions.md`](tool-management/functions.md)、[**`tool-management/runtime-contract.md`**](tool-management/runtime-contract.md)**（`invocationState`、风险级、Retry/幂等、Result 信封、运行时权限链、隔离）** **及** [`tool-management/config.md`](tool-management/config.md)（**IA · `FR-TM03` 策略模型 · `toolProfile`/T05**）、[`tool-management/flow.md`](tool-management/flow.md)（**Enable 流程 · §6 Tool Profile / 在飞**）、[`tool-management/rules.md`](tool-management/rules.md) **对签**。**PRD 条目**：**FR-MC301～305**（细项 · **SC-TM-01～12** · **§2～§7**）；**默认**：**缺失可调用的 `FR-TM03` 配置 → 不得 Enable**（**`functions` §7**）；**矩阵真源**：**[`design/api.md`](../../../design/api.md)** + **`trade-assistance` §8**；**观测**：**[`observability/overview.md`](../../observability/overview.md) §2.1 · SC-OBS05**。**验收**：**SC-MCV1-05**（§13）与本域 **SC-TM** **同一「不得假开」口径**。

---

## 7. 模块四 — AI Settings

**叙事与契约锚点**：[`ai-settings/overview.md`](ai-settings/overview.md) **§1～§5**（**后台 Demo** `/ai-settings` 交互摘要见 **§1.1**）；**功能与验收**：[`ai-settings/functions.md`](ai-settings/functions.md)。**OpenAPI / 占位路径**：[`design/api.md`](../../../design/api.md) **登记表「模块四」行**、**「运营侧 AI Settings API（`admin/ai/*`）」** · **`CC-P0-01`**。**密钥仅 `secretRef`**，**不**与 [`keys.md`](trading-agent-config/keys.md) 交易键 **混落明文**。**计费改价** **走** **模块五**。**降级/路由** **同窗** [`integrations/llm/provider-routing.md`](../../integrations/llm/provider-routing.md)、[`Runtime/recovery.md`](../../Runtime/recovery.md)。**观测 `modelId`** **同窗** [`observability/overview.md`](../../observability/overview.md) **§2**、[`observability-management/functions.md`](observability-management/functions.md) **FR-MC804**。

| FR | 主题（规划实施） |
|----|------------------|
| **FR-MC401** | **Provider 台账**：`providerId`、`baseUrl`、`secretRef`、`healthStatus`、启用；**无 Secret 明文回包** |
| **FR-MC402** | **模型目录**：`modelId`、能力/上下文窗、下架语义；**`defaultModelRef` 允许集** **同窗** [`agent-management/config.md`](agent-management/config.md) |
| **FR-MC403** | **Temperature**：默认与 min/max 硬边界 |
| **FR-MC404** | **Max output tokens**：默认与硬顶 |
| **FR-MC405** | **Timeout**：首包/整次或统一 ms（**OpenAPI 终裁**） |
| **FR-MC406** | **Rate limit**：RPM/并发等运营级默认 |
| **FR-MC407** | **Health**：周期/阈值、手动探针、**与 **`Runtime`** **同窗**熔断/降级** |

**验收（占位）**：**SC-AI-01～04** — [`ai-settings/functions.md` §2](ai-settings/functions.md)。

---

## 8. 模块五 — Billing & Settlement

**叙事与契约锚点**：[`billing-management/overview.md`](billing-management/overview.md) **§7～§10**；**商业分层 SSOT** [`billing-management/commerce-model.md`](billing-management/commerce-model.md)（**Agent 消耗 S5 仅轨 B**）；**功能拆分与联考**：[`billing-management/functions.md`](billing-management/functions.md) **§2～§5**（**§5 · Phase 2 商业层**）。**核销主体、追溯键、**`billCode`**、 **`PER_EXECUTION_FINAL`** **须与同文及 **`consume-and-bill.md`** **一致**。**契约闭环**：**轨 B 主链** **`contract-closure` §8** + **`me/commerce`**；**轨 A Token 三线** **OpenAPI 对读**（**非 Agent S5 关单**）。**OpenAPI / 占位路径**：[`design/api.md`](../../../design/api.md) **「模块五」「内部 · 商业轨」「用户侧 `me/commerce`」「运营侧 `admin/billing/commerce/*`」**；**流水枚举下限** [`billing-management/rules.md`](billing-management/rules.md)。

| FR | 主题（规划实施） |
|----|----------------|
| **FR-MC501** | **计费健康**：`BILLING_MODE`、`effectiveMinChargeUsdt`、**`BILLING_TOKEN_RATE`** 摘要 |
| **FR-MC502** | **`BILLING_TOKEN_RATE`（费率）与 `effectiveMinChargeUsdt`（最小扣费）**；**`keys` MR · 双签** |
| **FR-MC503** | **单笔协查**：`userId`、`executionId`、**`billingTraceId`**、`observability` |
| **FR-MC504** | **平台级流水列表**；与 **FR-MC507** **导出同源** |
| **FR-MC505** | **退款/冲正**：工单 · **`refundIdempotencyKey` 幂等** · **双分录 · 审计** |
| **FR-MC506** | **网关/账务错误聚合**（下钻 **FR-MC503**） |
| **FR-MC507** | **平台级异步导出**：流水 CSV · **月度 rollup**（同窗 **FR-B16**）；**`billing-management/rules`** |
| **FR-MC508** | **财务对账**：字段模板 · PSP **映射占位** |
| **FR-MC509** | **（Phase 2）套餐 / Capability SKU / `BILLING_CAPABILITY_MAP` 映射矩阵**；编辑 **双签同窗** **FR-MC502** |
| **FR-MC510** | **（Phase 2）用户权益协查**：订阅期、配额、加购包余额；**join `executionId`** |
| **FR-MC511** | **（Phase 2）订阅/加购包收入导出**（**同窗** **FR-MC508** **或** **扩展列**） |
| **FR-MC512** | **（Phase 2）配额用尽 / 阻断事件**健康卡（**可并入** **FR-MC501** **同屏**） |

**验收（节选）**：**SC-B01、SC-B02、SC-B08、SC-B13、SC-B14、SC-B15** — [`billing-management/functions.md` §3](billing-management/functions.md)；**Phase 2**：**SC-B20、SC-B21** — [`billing-management/functions.md` §5.3](billing-management/functions.md)。

### 8.1 OpenAPI PATH 同窗（Phase 2 · 轨 B · 与 overview §12 一致）

| 面 | Spec | PATH 键（节选） | FR |
|----|------|-----------------|-----|
| **internal · 轨 B** | [`internal/billing-entitlements.yaml`](../../../openapi/internal/billing-entitlements.yaml) | `…/billing/entitlements/debit`、`…/billing/entitlements/balance`、`…/commerce/pack-grants/apply` | **FR-B19**（S2/S5）、**SC-B20** |
| **me · commerce** | [`user/commerce-me.yaml`](../../../openapi/user/commerce-me.yaml) | `/api/v1/me/commerce/entitlements/summary` | **FR-B17** |
| **admin · commerce_phase2** | [`admin/billing-admin.yaml`](../../../openapi/admin/billing-admin.yaml) | `…/billing/commerce/capability-catalog`、`…/commerce/users/{userId}/overview`、… | **FR-MC509～512** |

**同窗组件**：[`billing-schemas.yaml`](../../../openapi/components/billing-schemas.yaml) **Commercial / Entitlement schemas**。**轨 B 生产闭环** **不** **计入 CC-P0-03** — **须** **`contract-closure` §8**。

---

## 9. 模块六 — Access Control

准入、KYC 同步、地域、黑白名单与灰度等。**FR-MC601～607**；验收 **SC-AC** 见 [`access-control/functions.md`](access-control/functions.md) **§3**；[`access-control/overview.md`](access-control/overview.md)。

---

## 10. 模块七 — Trading Agent Config

全局交易默认值与限制；以 **附录 A · §5.1**、[`trading-agent-config/keys.md`](trading-agent-config/keys.md) 及 [`design/api.md`](../../../design/api.md) 冻结为上限。**FR-MC701～711**（含 **Telegram Bot 配置** [`../agent/telegram/admin-bot-config.md`](../agent/telegram/admin-bot-config.md)）。与 [`overview`](trading-agent-config/overview.md)、[`functions`](trading-agent-config/functions.md)、[`keys`](trading-agent-config/keys.md)、[`config`](trading-agent-config/config.md)、[`flow`](trading-agent-config/flow.md)、[`rules`](trading-agent-config/rules.md) 对签；验收 **SC-TAC** 系列见 [`functions` §4](trading-agent-config/functions.md)。

---

## 11. 模块八 — Logs & Observability

控制台检索与审计入口；**字段下限** [`observability/overview.md`](../../observability/overview.md)、**`executionId`/trace** [`observability/tracing.md`](../../observability/tracing.md)。**主态迁移 × 观测**：**`transitionTrigger`** **与** **§2.4** **映射**（**同窗** **[`execution-transition-matrix.md`](../../Runtime/execution-transition-matrix.md) **§2.2**、**`SC-OBS08`/`SC-OM-04`**）**须** **在** **`FR-MC801` 时间线** **上** **可读** **（** **API** **已返回时** **）** — **详** **[`observability-management/functions.md`](observability-management/functions.md) · `FR-MC801`、`SC-OM-04`**。**产品与 IA**：[`observability-management/overview.md`](observability-management/overview.md)、[`config §4`](observability-management/config.md)；**FR-MC801～807、SC-OM**：[`observability-management/functions.md`](observability-management/functions.md)。**HTTP 占位**：[`design/api.md`](../../../design/api.md) **`admin/observability/*`、模块八登记行** · **`CC-P0-01`**。

| FR（摘要） | 主题 |
|------------|------|
| **801～802** | **`executionId` / `userId` 联合协查**与时间线 **（** **含** **`transitionTrigger` / §2.4 等价 `summary` 之可读展示 · `SC-OM-04`** **）** · **实例 L01～L03 深链** |
| **803～804** | **工具 / LLM** 抽样列（**`invocationState`、Token 摘要**） |
| **805** | **SLI** 嵌入或跳转 |
| **806～807** | **`admin.audit` 导出**与水印 **`≈billing.rules §5`** |
| **并联** | **计费三联** **`userId`/`executionId`/`billingTraceId`** **`→` FR-MC503、`billing.entitlement_debit_*` 事件**（**主链** · **`functions` §2**） |

---

## 12. V1 不建议做

Marketplace 级技能市场、多 Agent 协同、用户自定义 Prompt/模型、Workflow Builder、Fine-tuning 平台（与产品共识一致时可调整）。

---

## 13. 验收主题（节选）

SC-MCV1-01～05：IA 可走通、熔断生效、计费可 join、审计可追溯、矩阵未冻结项不可在 Tool 管理「假开」。

---

# 附录 A — 运行时/账务对签（沿用历史 § 引用）

## §1.3 划界

管理台 **不交付** 交易所主站 **Prompt 独立模块**之 CRUD — 见 **`prompt-management`**；实现落位以该文 SSOT 为准。

## §5.1 `configKey`

**枚举真源**：[`domains/admin/trading-agent-config/keys.md`](trading-agent-config/keys.md)（全局闸、`FEATURE_*`、护栏、`BILLING_*` 边界、`configVersion`/快照）。

**本节保留索引（与 [`keys`](trading-agent-config/keys.md) 对齐）**：`GLOBAL_AGENT_SWITCH`、`FEATURE_TRADING`、`FEATURE_ANALYSIS`、`FEATURE_AGENT_SPOT|_MARGIN|_FUTURES|_WEALTH`、`CHANNEL_TELEGRAM`、**`STM_*`/`RESUME_*`/`WARM_EXECUTION_INDEX_TTL_SEC`（Memory · [`keys` §2.1](trading-agent-config/keys.md#21-runtime--memory--stmfr-stm--产品默认-v0)）**、**`TELEGRAM_*`**（**Bot 运行参数、`secretRef`；Webhook 运维 API 见 `keys` §4.4**）、`AGENT_MIN_VIP_TIER`、`SYMBOL_POLICY_*`、`BILLING_*`、`AGENT_PRICE_*` 等。HTTP 写入见 **[`design/api.md`](../../../design/api.md)** 全局配置行 **及** **Telegram Bot / Webhook** 登记行。

## §7.4（运营协查 / 水单导出）

**≠** `billing.md` §7.4（结算策略）；语义见 **`billing-management`** 与 **模块五**。

## §8.2 运营摘要字段（下限）

`vipTier`（**母账号 · `userId` 维度 VIP**，**与 **`AGENT_MIN_VIP_TIER`** 比对**）、`agentMinVipTier`、`agentSubAccountId`、`agentSubAccountStatus`（可选）、`agentTradingApiBindingStatus`、`agentTradingApiKeyId`（可选）、`agentState`、`lastProductBlockReason`。

**管理台展示验收**：控制台宜 **逐项**勾选 **展示 / 脱敏 / 无数据 / 仅 Viewer**，见 **[`agent-management/functions.md` · §9.4](agent-management/functions.md)**。**HTTP 读写契约**（含用户摘要 API）以 **[`design/api.md`](../../../design/api.md)** 登记表与 **OpenAPI** 冻结为 SSOT，并与 **本节字段下限** 及 **§9**（`agentState`）**对签**。

## §9 `agentState`

`NORMAL`、`GLOBAL_OFF`、`OPS_SUSPENDED`、`MEMBERSHIP_BLOCKED`、`AGENT_SUBACCOUNT_BLOCKED`、`BILLING_BLOCKED`（与 `exchange-agent`/`flow` 对签）。

## §11 开放决策（摘录）

**D-1** 在途 (A) 完成原子步 / (B) 强中止 — **SSOT** [`architecture.md`](../../../design/architecture.md) **在途与紧急停止**、[`exchange-agent/overview.md`](../agent/exchange-agent/overview.md) **`FR-T02～T04`**。**V1 默认展开**（不可逆成交 / **交易 USDT 不足** **与** **核销 INSUFFICIENT** **分域**）：[`billing-management/overview.md`](billing-management/overview.md) **§10.2**（**与 §7.4.1 门禁** **配套**）。**D-12** `BILLING_AGENT_REVENUE_ACCOUNT_REF` — **轨 A 对读**；**Agent S5 关单** **见** **`contract-closure` §8**。

**D-5** **（`traceKey` 与 `billingTraceId` 同值 · 运营协查）**：**权威展开** [`observability/overview.md`](../../observability/overview.md)（**`traceKey` 行**）、[`billing-management/overview.md`](billing-management/overview.md) **§10.3** — **实现** **须** **同窗** **对签**（**CC-P0-05 子项**）。

**D-7** **（未知终局与计费耦合）**：**权威展开** [`billing-management/overview.md`](billing-management/overview.md) **§10.3**、[`consume-and-bill.md`](../../flows/consume-and-bill.md) — **UNKNOWN/504** **路径** **与** **S5 权益核销评估** **不得** **口头分叉**（**CC-P0-05 子项**）。

## §6 功能索引

**FR-C01～08**、**FR-M01～07** 映射见各模块与 **§5.1**。

## §14 测试钩子

TC-10、TC-21、TC-26 等见 **`metrics`/`flows`** 互引。

---

<a id="mc-prd-appendix-a-release-checklist"></a>

## §13 发布 / 对齐检查清单

与 [`contract-closure.md`](../../contract-closure.md) **§2～§7**、**[§5.1 升格 gate](../../contract-closure.md#cc-stage4-spec-gate)** 联动；**D-12**、矩阵 **`TBD`**、收入专户未收口 **不得**标 **生产已冻结**。**P0** **会签工单 / 实现 MR 证据** **集中回填** **[`contract-closure` §2.1](../../contract-closure.md#cc-p0-signoff-register)**（**先于** **将下列 `[ ]` 改为 `[x]`**）。**模块三 · Tool / `CC-P1-03`** **闭链** **须** **同窗** **[MR-E](../../contract-closure.md#cc-p1-mr-e)** **实现 MR** **与** **上文 §6**；**§13 ↔ CC** **逐行映射** **[§5.2.1](../../contract-closure.md#cc-521-prd-map)**。

发布前 **至少**核对（与 **§附录 A、`design/api`、域 FR/SC** 同窗 **MR** 或 **可合并窗口**）：

- **[x] Telegram Bot / Webhook · 文档/仓库内 B 子集**：**A**：[`design/api.md`](../../../design/api.md) **专节** **PATH 示意** **已载**。**B（仓库内）**：[`admin/telegram-channels.yaml`](../../../openapi/admin/telegram-channels.yaml) **已链** **登记表**；**Owner** [`OWNERS.md`](../../../openapi/OWNERS.md) **（本仓库** **暂** **统一 DRI**；**规模化** **须** **补** **备** **责任人）**。**仍须（全流程 DoD）**：**Hosted/生产** **与** **密钥**、**`SC-TAC-11～13`、FR-MC709～711** **可对签** — **见** **`CC-P1-06`** **B**（[`contract-closure.md`](../../contract-closure.md) **§3**）；需求 SSOT：**[`telegram/admin-bot-config.md`](../agent/telegram/admin-bot-config.md)**，**`configKey`** [`trading-agent-config/keys.md`](trading-agent-config/keys.md) **§4**。
- **[x] `TELEGRAM_*`（文档 SSOT）**：[`trading-agent-config/keys.md`](trading-agent-config/keys.md) **§4.2** **枚举** **与** **附录 A · §5.1** **`CHANNEL_*`/`TELEGRAM_*` 叙事** **已** **同窗**（[`keys.md`](trading-agent-config/keys.md) **全文** **与** **PRD 附录** **互引**）；**运行时默认值变更** **仍须** **同窗 MR** **+** **审计**（[`flow.md`](trading-agent-config/flow.md)）。
- **[ ] `D-5` / `D-7`（账务 × 观测 × 控制台）**：**需求检查单** [`billing-management/overview.md` §10.3.1](billing-management/overview.md) — **实现关闭** **`contract-closure` CC-P0-05** **时** **逐项勾选** **并** **`SC-OBS03`** **同窗**；**证据** **[§2.1](../../contract-closure.md#cc-p0-signoff-register)**；**未闭合** **不得** **宣称** **账务/协查** **生产终裁一致**。**（2026-05-09·文档轨）** **§10.3.1** **已载** **闭环节奏**；**本条 `[x]`** **仅于** **实现 MR** **勾选检查单 1～2** **后** **人工改为已勾选** — **禁止** **无实现预勾选**。
- **[ ] `D-12` / **`BILLING_AGENT_REVENUE_ACCOUNT_REF`**（收入专户 · **CC-P0-04**）**：**首填与会签检查单** [`billing-management/overview.md` §10.6.1](billing-management/overview.md) — **财务书面会签** **+** **生产配置首填** **+** **审计链** **关闭** **`contract-closure` CC-P0-04** **时** **逐项勾选**；**证据** **[§2.1](../../contract-closure.md#cc-p0-signoff-register)**；**未闭合** **不得** **宣称** **计费收入专户** **生产终裁一致**。**本条 `[x]`** **仅于** **工单/MR** **勾满 §10.6.1（含会签工单号）** **后** **人工改为已勾选** — **禁止** **无会签预勾选**。
- **[ ] `SC-MCV1-05` / Tool Registry SSOT（模块三 · **`CC-P1-03`**）**：**控制台矩阵「不得假开」** **与** **`trade-assistance` §8 · `FR-TS07`** **及** **DB/镜像** **`toolId`/`skillId` 幂等** **须** **同窗** **实现** **MR**（**组织轨** **[MR-E](../../contract-closure.md#cc-p1-mr-e)**）；**叙事** **须** **与** **上文 §6** **FR-MC301～305** **无矛盾**。**本条 `[x]`** **仅于** **`contract-closure` CC-P1-03** **DoD** **（含 §8 登记）** **闭合后**；**禁止** **无实现/无抽检预勾选**。**细则** **见** **[`contract-closure` §5.2.1](../../contract-closure.md#cc-521-prd-map)**（**CC-P1-03** **行**）。

---

**文档版本**：1.0.23-rebuild · **维护**：产品 Owner · **本版**：**互引** **补** **`closure-remaining` §0·§6.4**。**承** 1.0.22-rebuild。
