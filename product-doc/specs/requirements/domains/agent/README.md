# `domains/agent/` — 用户侧 AI 业务域

**[`exchange-agent/`](exchange-agent/)**（**AI Trading Companion / AI Exchange Agent**）为本树 **业务能力主体**。产品上以 **五种能力域** 为 pillar（见 [`exchange-agent/overview.md`](exchange-agent/overview.md) **§1**）。**分段实施与成熟度表**：[`exchange-agent/README.md`](exchange-agent/README.md)。另 **`intents`** / **`boundaries`** 分卷 **横跨五域**。**`exchange-agent/`** 内含 **能力分卷 + `overview-legacy-migration` 附录**。**编排域**（`scenarioId`/`FR-AO*`/执行面）：[`agent-orchestration/overview.md`](agent-orchestration/overview.md) **索引**；寄存器 [`routing-engine.md`](agent-orchestration/routing-engine.md)；**开发对齐** [`implementation-alignment.md`](agent-orchestration/implementation-alignment.md)（**对客「已支持」三闸** **§13.1**）；**开放项 / 首节派工 / 走读缺口** [**§0 速链**](../../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../../closure-remaining.md#cc-exec-solve-path) · [`closure-remaining` §7](../../closure-remaining.md#cc-remaining-open-items) · **[§7.1](../../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../closure-remaining.md#cc-closure-exec-checklist)**。**[`agent-context/overview.md`](agent-context/overview.md)**：会话上下文与工具链回填 **域入口**。**其余子目录**（`runtime/`、`onboarding/` 等）条文以各 **README / overview** 为准。

**成熟度口径**：**v0.3 分卷** **多指** **叙事骨架**；**能否对客承诺** **以** [`contract-closure.md`](../../contract-closure.md) **§1.2** **与** **`implementation-alignment` §13** **为准**，**不得** **仅凭分卷版本标签** **推断** **生产闭环**。**关单余量首节** → **[§0](../../closure-remaining.md#closure-remaining-quicklinks)** · **[§6 / §6.4](../../closure-remaining.md#cc-exec-solve-path)**（[`closure-remaining`](../../closure-remaining.md)）。

**对上 Coobit**：私网出站默认 **`openapi-ai`**（须 pin）；契约与白名单同窗 [`integrations/exchange/overview.md`](../../integrations/exchange/overview.md)、[`design/api`](../../../design/api.md)。

**端到端鸟瞰 · 架构语言**：[`flow/e2e-closed-loop.md`](../../../../flow/e2e-closed-loop.md) **文首「架构语言」** → [`architecture` §「与通用 Agent 栈之对照」](../../../design/architecture.md)。

## 目录结构

| 子目录 | 用途（规划标签） |
|--------|------------------|
| [`exchange-agent/`](exchange-agent/) | **交易所场景 Agent**：[`overview`](exchange-agent/overview.md) · 路线图 [`README`](exchange-agent/README.md) · 五 pillar 分卷 + 横跨 intents / boundaries |
| [`agent-orchestration/`](agent-orchestration/) | 场景编排、`scenarioId`、步骤语义；**写澄清** [`clarify-session`](agent-orchestration/clarify-session.md) |
| [`goals/`](goals/README.md) | **结构化 `goal_id` 评审范例**（**非** **契约** **直至** **与 `routing-engine` 会签**） |
| [`agent-context/`](agent-context/overview.md) | **会话上下文**预算／压缩／工具回填；链 **`Runtime/context-management`**、**`observability`**、**`trade-assistance` §8.4** |
| [`runtime/`](runtime/) | **用户侧运行时索引**：[`overview`](runtime/overview.md)、[`README`](runtime/README.md)；横切 **[`Runtime`](../../Runtime/overview.md)**（[`README` 短入口](../../Runtime/README.md)） |
| [`onboarding/`](onboarding/) | 用户开通、子账户、绑定与 Deeplink：[`overview`](onboarding/overview.md) 总览 + `initialization-flow` / `telegram-binding` **等** **八文件**；**主站/H5 开通页 UX** [`../web/agent-onboarding.md`](../web/agent-onboarding.md) |
| [`telegram/`](telegram/) | **会话渠道**：[`overview`](telegram/overview.md) **§2.5 · 类型 A / §2～§2.6**、[`admin-bot-config`](telegram/admin-bot-config.md)（**Bot 运维配置项**）、[`mobile-app`](telegram/mobile-app.md)（暂缓） |

**上级导航**：[`../README.md`](../README.md) · [`../../spec.md`](../../spec.md) · [`../../../design/api.md`](../../../design/api.md)
