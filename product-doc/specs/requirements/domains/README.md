# 域需求（Domains）导航

本目录 **`domains/`** 按目标结构划分为 **`agent/`**（用户侧 AI 业务域）、**`web/`**（**浏览器 UX**：**Agent 产品线绑定 onboarding（`me/agent/*`，不须交易所主站）** · **账单（交易所站内主站/H5）**），与 **`admin/`**（交易所后台管理能力域）。契约级 FR/SC 仍以各文为准；与 [`product.md`](../product.md) 冲突时以 **`product.md`** 仲裁。

**端到端链路**：[`../../../product/README.md`](../../../product/README.md)；主流程 **[`../flows/`](../flows/)**；接口矩阵 **[`../../design/api.md`](../../design/api.md)**；会签闭环 **[`../contract-closure.md`](../contract-closure.md)**；**本仓关单余量 / MR 锚点速查** **[`../closure-remaining.md`](../closure-remaining.md)**（**[§0 速链](../closure-remaining.md#closure-remaining-quicklinks)** · **[§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)** · **[§7 开放项](../closure-remaining.md#cc-remaining-open-items)** · **[§7.5 闭环路径](../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6 MR 执行清单](../closure-remaining.md#cc-closure-exec-checklist)**）。

**鸟瞰图 · 架构语言**：[`flow/e2e-closed-loop.md`](../../../flow/e2e-closed-loop.md) **文首「架构语言」** → [`architecture` §「与通用 Agent 栈之对照」](../../design/architecture.md)。

---

## `agent/` — AI 业务域

| 路径 | 说明 |
|------|------|
| [`agent/README.md`](agent/README.md) | **结构说明**；**[`exchange-agent/`](agent/exchange-agent/)** 为 **业务能力主体**；[`overview.md`](agent/exchange-agent/overview.md) **Capability §1～§3**，[`overview-legacy-migration.md`](agent/exchange-agent/overview-legacy-migration.md) **§10映射**；[`agent-orchestration/`](agent/agent-orchestration/)（**[`overview.md`](agent/agent-orchestration/overview.md)** 索引、**[`routing-engine.md`](agent/agent-orchestration/routing-engine.md)** 寄存器 **等** **九文件**） |
| [`agent/exchange-agent/`](agent/exchange-agent/) | **AI Trading Companion**：入口 [`overview.md`](agent/exchange-agent/overview.md)；分卷 intents / market-intelligence / portfolio-insight / risk-alerts / trade-assistance / monitoring-tasks / boundaries。**对上 Coobit HTTP 实现宿主**：[`integrations/exchange/overview.md`](../integrations/exchange/overview.md)（**`openapi-ai`**） |
| [`agent/agent-orchestration/`](agent/agent-orchestration/) | **九文件**：`routing-engine`/`execution-lifecycle`/`state-machine`/`task-scheduler`/`confirmation-flow`/`retry-policy`/`runtime-freeze`/`boundaries` + **`overview`**；**对客闸 1** **（** **§13.1** **）** **须** **同窗** **`runtime-freeze` §3** **写路径最小编排** **与** **`routing-engine` 文首** **映射** |
| [`agent/runtime/`](agent/runtime/) | **用户侧运行时透镜（索引）**：[`overview.md`](agent/runtime/overview.md)、[`README.md`](agent/runtime/README.md)；横切 **`Runtime/`** 见 [`overview.md`](../Runtime/overview.md)、[`README.md`](../Runtime/README.md) |
| [`agent/onboarding/`](agent/onboarding/) | **开通与绑定**：[**`overview.md`**](agent/onboarding/overview.md)，[**`initialization-flow.md`**](agent/onboarding/initialization-flow.md)，[**`telegram-binding.md`**](agent/onboarding/telegram-binding.md)，[**`agent-account.md`**](agent/onboarding/agent-account.md)，[**`permission-authorization.md`**](agent/onboarding/permission-authorization.md)，[**`runtime-provisioning.md`**](agent/onboarding/runtime-provisioning.md)，[**`activation-policy.md`**](agent/onboarding/activation-policy.md)，[**`boundaries.md`**](agent/onboarding/boundaries.md) |
| [`agent/telegram/`](agent/telegram/) | **Telegram 渠道**：[**`overview.md` §2.5 · 类型 A / §2～§2.6**](agent/telegram/overview.md)、[**`admin-bot-config.md`**](agent/telegram/admin-bot-config.md)（**控制台 Bot 配置项**）、[`README.md`](agent/telegram/README.md) |

---

## `web/` — 浏览器触点（Agent 产品线 onboarding · 交易所站内账单 UX）

| 路径 | 说明 |
|------|------|
| [`web/README.md`](web/README.md) | **索引**；[`overview.md`](web/overview.md) **域边界**、**§4 FR-WEB→CC·`design/api`** |
| [`web/agent-onboarding.md`](web/agent-onboarding.md) | **Trading Agent 绑定页**（**FR-WEB01～06**、**SC-WEB-01～06**、**SC-WEB-12**；同窗 **`me/agent/*`** **产品线 onboarding**，**不须交易所主站**） |
| [`web/agent-billing.md`](web/agent-billing.md) | **交易所站内 Agent 账单 H5**（**FR-WEB07～11**、**SC-WEB-07～11**；**§2.1** **FR-B17～B21**、**SC-WEB-14～15**；**`/subaccount/billing`**） |

**不写**：后台账务契约全文 — 同窗 **[`admin/billing-management/`](admin/billing-management/overview.md) §0**（**`me/commerce` 主链**；**`me/billing` 仅 OpenAPI 归档**）、[`agent/onboarding/`](agent/onboarding/overview.md)。

---

## `admin/` — 后台业务子域（对齐 **[`management-console-v1-prd.md`](admin/management-console-v1-prd.md)** 八大模块）

| 模块 | 目录 | 说明 |
|------|------|------|
| **聚合 / IA** | [`admin/management-console-v1-prd.md`](admin/management-console-v1-prd.md) | 管理后台 V1 产品需求与 **附录 A**（`configKey`、对签字段） |
| **一、Agent Management** | [`admin/agent-management/`](admin/agent-management/)（[`overview.md`](admin/agent-management/overview.md)） | 模板、实例、运行控制 |
| **二、Prompt Management** | [`admin/prompt-management/`](admin/prompt-management/) | 提示词治理（交易所后台语义） |
| **三、Tool Management** | [`admin/tool-management/`](admin/tool-management/)（[`overview.md`](admin/tool-management/overview.md)） | Tool 运营面（矩阵 SSOT 仍在 `design/api` + `trade-assistance`） |
| **四、AI Settings** | [`admin/ai-settings/`](admin/ai-settings/)（[`overview.md`](admin/ai-settings/overview.md)） | Provider / Model / 网关参数 |
| **五、Billing & Settlement** | [`admin/billing-management/`](admin/billing-management/) | 计费与用户侧 Billing |
| **六、Access Control** | [`admin/access-control/`](admin/access-control/)（[`overview.md`](admin/access-control/overview.md)） | 准入、灰度/白名单、封禁、KYC 镜像、VIP；[`functions` SC-AC](admin/access-control/functions.md) |
| **七、Trading Agent Config** | [`admin/trading-agent-config/`](admin/trading-agent-config/)（[`overview.md`](admin/trading-agent-config/overview.md)） | 交易默认值与.symbol/限价等全局策略 |
| **八、Logs & Observability** | [`admin/observability-management/`](admin/observability-management/)（[`overview.md`](admin/observability-management/overview.md)） | 控制台观测与检索入口（字段 SSOT：[`observability/`](../observability/)） |

**非 `admin/` 但常被后台引用的横切**：[`Runtime/overview.md`](../Runtime/overview.md)、[`Runtime/README.md`](../Runtime/README.md)、[`risk/README.md`](../risk/README.md)（含 [`acceptance.md`](../risk/acceptance.md) **`SC-RISK*`**）、[`observability/`](../observability/overview.md)、[`tools/`](../tools/README.md)、[`integrations/`](../integrations/)、[`flows/`](../flows/README.md)、[`metrics/`](../metrics/README.md)。

**标准与落地 playbook**：[`../standards/README.md`](../standards/README.md)、[`../standards/STANDARDS-ADOPTION.md`](../standards/STANDARDS-ADOPTION.md)。
