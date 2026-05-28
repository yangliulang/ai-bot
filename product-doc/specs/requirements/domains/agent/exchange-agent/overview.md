# Exchange Agent · 域内总览（AI Trading Companion / AI Exchange Agent）

**路径**：`specs/requirements/domains/agent/exchange-agent/overview.md`。

**实施路线与成熟度**：[`README.md`](README.md)。

**定位**：**交易所场景下的 AI Agent 能力中枢**。产品叙事上 **能力与用户价值** 归为 **五种能力域（§1）**；递进链路可作理解用：**市场洞察** → **资产/持仓理解** → **风险提醒** → **交易辅助** → **条件监控（含提醒与必要时执行）**。**交易辅助** 仅为其中一类。

**横跨层（不计入五种 pillar）**：[`intents.md`](intents.md)（**用户意图语义** · 歧义分流）、[`boundaries.md`](boundaries.md)（边界与主站回退）。**编排键 `scenarioId`、执行面（归因 / 告警投递 / `taskId` 生命周期）**：[`../agent-orchestration/overview.md`](../agent-orchestration/overview.md) **文档地图第 1 节** — **有意与本文分层**，避免 Capability 文档 **Runtime 化**。**交易所调用之后的平台 Runtime（UNKNOWN、REST↔WS 对账、错误归一化）**：[`../../../Runtime/reconciliation.md`](../../../Runtime/reconciliation.md)、[`../../../Runtime/unknown-state.md`](../../../Runtime/unknown-state.md)、[`../../../Runtime/recovery.md`](../../../Runtime/recovery.md)（**UNKNOWN 收口与退避宿主**）、[`../../../Runtime/error-normalization.md`](../../../Runtime/error-normalization.md)；**上游本体**：[`../../../integrations/exchange/overview.md`](../../../integrations/exchange/overview.md)。

本文 **不写**可复制进 OpenAPI 的字段表（以 [`../../../../design/api.md`](../../../../design/api.md) **矩阵**为准）。

**对上 Coobit 私网 HTTP**：出站默认 **`openapi-ai`**（Skill 宿主），制品须 pin；PATH 与 [`design/api`](../../../../design/api.md) 矩阵、[`agent-coobit-api-allowlist`](../../../integrations/exchange/agent-coobit-api-allowlist.md) 同窗 [`integrations/exchange/overview`](../../../integrations/exchange/overview.md)。**不改变** 平台侧计费、`executionId`、UNKNOWN / 504 等对账语义（同窗 [`Runtime/overview`](../../../Runtime/overview.md)）。**执行链语义分层**（Intent → Canonical → Gateway → Adapter）见 [**`canonical-trading-model`**](../../../../design/canonical-trading-model.md)、[**ADR-004**](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance`](trade-assistance.md) **§2.6**、契约 [**CC-P1-07**](../../../contract-closure.md#cc-p1-07)；**人类评审速查** [`requirements-review` §7.5](../../../../../product/requirements-review.md#cc-adr004-review-checklist)。

**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

**端到端鸟瞰 · 架构语言**：[`flow/e2e-closed-loop.md`](../../../../../flow/e2e-closed-loop.md) **文首「架构语言」** → [`architecture` §「与通用 Agent 栈之对照」](../../../../design/architecture.md)。

**旧稿回迁、§10.x 外链对读**：[`overview-legacy-migration.md`](overview-legacy-migration.md)（**非能力 SSOT**）。

---
## 1. 五类能力域（产品 pillar）

| 能力域（英文档名对齐） | 说明 |
|------------------------|------|
| **Market Intelligence** | 行情、资金费率、波动率、热点叙事、市场摘要 |
| **Portfolio Insight** | 余额、持仓、敞口、盈亏、风险偏好 |
| **Risk Alerts** | 爆仓风险、异常波动、仓位过大、价格触发 |
| **Trade Assistance** | 下单辅助、撤单、持仓调整建议、用户确认后执行 |
| **Monitoring Tasks** | 条件监控、价格提醒、事件提醒、定时任务 |

**与分卷对应**：Market Intelligence → [`market-intelligence.md`](market-intelligence.md)；Portfolio Insight → [`portfolio-insight.md`](portfolio-insight.md)；Risk Alerts → [`risk-alerts.md`](risk-alerts.md)；Trade Assistance → [`trade-assistance.md`](trade-assistance.md)；Monitoring Tasks → [`monitoring-tasks.md`](monitoring-tasks.md)。

---

## 2. 术语：`skillId`（技能）与 `toolId`（工具）

| 术语 | 含义（摘要） | 权威 |
|------|----------------|------|
| **`skillId`** | **A 类**：经用户 **类型 A** 后的 **Coobit 私有写**（`call_exchange_write`）之 **登记名**（常见前缀 **`skill.*`**）。 | [`trade-assistance.md`](trade-assistance.md) **§3·§4·§8.1～§8.2** |
| **`toolId`** | **B 类**（所内只读）或 **C 类**（外网等）之 **稳定名**（常见前缀 **`tool.*`**）。 | [`trade-assistance.md`](trade-assistance.md) **§3·§5·§8.1·§8.3～§8.4** |
| **A / B / C 类** | **能力分型**：写 vs 只读 vs 外网；**是否须类型 A** **以 §8.1 表为准**。 | [`trade-assistance.md`](trade-assistance.md) **§8.1** |
| **观测名 `agent.tool.call`** | **工具调用归因**之 **事件总称**；**可涵盖 A/B/C 编排路径**，**不**表示业务语义上「仅为 `toolId`」。 | [`trade-assistance.md`](trade-assistance.md) **职责段**；[`execution-lifecycle.md`](../agent-orchestration/execution-lifecycle.md) |
| **Coobit 官方 openapi-ai Skill** | **对上 Coobit HTTP** **的优选实现宿主**（`skills/*/SKILL.md`/CLI/MCP，`design`/`allowlist`/Runtime **不变**）。 | [`trade-assistance.md`](trade-assistance.md) **文首宿主段**；[`integrations/exchange/overview.md`](../../../integrations/exchange/overview.md)；**≠** **`skillId`/Cursor「Skill」。** |
| **Cursor「Skill」** | **`.cursor/skills/`** 等 **IDE 指引**，**非** **`skillId`** **亦非** **`openapi-ai`。** | [`../../../standards/README.md`](../../../standards/README.md) |

**登记表逻辑 SSOT**：[`ADR-002`](../../../../design/adr/002-tool-skill-registry-ssot.md)；**PATH/`operationId` 终裁**：[`design/api.md`](../../../../design/api.md)。

---

## 3. 分卷索引（含横跨层）

| 文件 | 主题 |
|------|------|
| [`intents.md`](intents.md) | **意图语义**：话术簇、目标、歧义分流（**不**承担 `scenarioId` 寄存器） |
| [`market-intelligence.md`](market-intelligence.md) | **市场洞察**：可读能力条目与产品下限 |
| [`portfolio-insight.md`](portfolio-insight.md) | **资产/持仓理解**：叙事与只读聚合口径 |
| [`risk-alerts.md`](risk-alerts.md) | **风险提醒**：类型、分级、话术与能力边界 |
| [`trade-assistance.md`](trade-assistance.md) | **交易辅助**：确认链、写边界、**`skillId`/`toolId`** **能力登记**（**§3·§8**） |
| [`monitoring-tasks.md`](monitoring-tasks.md) | **条件监控**：用户可订阅的任务形态与用户价值 |
| [`boundaries.md`](boundaries.md) | **边界（横跨）**：主站回退、Deeplink、不做清单 |
| [`overview-legacy-migration.md`](overview-legacy-migration.md) | **附录**：回迁表 + 旧 **`§10.x`** 映射 |

---

## 4. Product boundary（简述）

| 条目 | 说明 |
|------|------|
| **矩阵终裁** | **`design/api` 未冻结 PATH** → **不对外承诺闭环**；拒答话术 **`FR-T05` 族** — 流程与条文见 [`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md)、[`trade-assistance.md`](trade-assistance.md)、[`boundaries.md`](boundaries.md)。 |
| **契约收口 · WS+REST 视图** | **若**某能力 **依赖私有 WS** **刷新订单/余额** **且** **对外承诺 REST 兜底闭合**：**须** **同窗** [`../../../contract-closure.md`](../../../contract-closure.md) **§1·第 6 款** — **`trade-assistance` §2.5**、**`design/api`「REST ↔ WebSocket 对账」**、**`Runtime/reconciliation`**、**`observability` §2/`SC-OBS06`**。 |
| **写须确认** | **每笔** **`call_exchange_write`** 前 **类型 A** — [`../../../../design/adr/001-telegram-confirm-before-coobit-write.md`](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)。 |
| **非投顾** | 收益/风险叙事须 **Disclaimer**；**详见** [`boundaries.md`](boundaries.md)。 |
| **子账户内多账本归集** | **全仓杠杆下单** **前**，若 **币币可调拨** **且** **矩阵模板已纳入** → **须在对话内** **完成「现货→cross」** **类型 A** **后代发划转并衔接下单** — **流程** [`../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 第四步**；**禁静默** **见** [`boundaries.md`](boundaries.md) **§8.4**。 |
| **UNKNOWN / `unknown_pending` 无进展策略（域内登记）** | **`504`/UNKNOWN** **致** **主态** **`unknown_pending`** **停留** **时**：**本域须** 与 [`../../../Runtime/unknown-state.md`](../../../Runtime/unknown-state.md) **「收口与无进展（产品下限）」**、[`../../../Runtime/recovery.md`](../../../Runtime/recovery.md) **「UNKNOWN 收口（与 SLA 宿主）」**、[`../../../risk/unknown-stall-policy.md`](../../../risk/unknown-stall-policy.md)（**阈值/查单有界** **`risk` 条文聚合**）**对签** — **在** **`design` / `ai-settings` / `keys` / `eval`** **专项 MR** **登记** **可观测阈值、查单·退避·最大轮次、超时后终局或人工处置路径**（**配置键名与默认值以 OpenAPI / 控制台键 SSOT 为准**）。**验收**：[`unknown-state.md`](../../../Runtime/unknown-state.md) **收口检查** **末项**；**横切抽检** **`SC-RISK-06`** [`../../../risk/acceptance.md`](../../../risk/acceptance.md)。**用户触达** **须** **与** **`FR-T05` 族** **无矛盾**（**不** **假终局成交**、**不** **无限无解释重试**）。**协议矩阵与查单 PATH** **仍** **`design/api`「REST ↔ WebSocket 对账」** **与** **`trade-assistance` §2.5**。 |

**邻域导航**（Runtime / onboarding / flows 总表）：[`../README.md`](../README.md)。

---

**文档版本**：0.4.10 · **维护**：产品 + Agent Runtime owner · **本版**：篇首 **补** **`e2e`↔`architecture` §对照（架构语言）**。**承** 0.4.9。
