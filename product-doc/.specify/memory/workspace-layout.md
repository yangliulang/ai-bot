# Workspace layout（本仓库）

本仓库采用 **产品层 `product/` + 规格 `specs/`**；**Speckit FEATURE_DIR** = `specs/requirements/`。

## 顶层

| 路径 | 说明 |
|------|------|
| **`product/`** | **人类可读**：`overview.md`、`roadmap.md`、`roadmap/README.md`（按季拆分约定）、`milestones.md`、`user-scenarios.md`、`positioning.md`、`requirements-review.md`（评审入口）等；**目录与 specs 对照表**见 **`product/README.md` · 文档地图**（非 FR/SC SSOT） |
| **`flow/`** | **端到端鸟瞰图**（如 Mermaid）：[`flow/README.md`](../../flow/README.md)；[`e2e-closed-loop`](../../flow/e2e-closed-loop.md) **文首「架构语言」** **同窗** **[`architecture`「与通用 Agent 栈之对照」](../../specs/design/architecture.md)**；步骤级 SSOT 仍为 **`specs/requirements/flows/`** |
| **`specs/requirements/`** | 需求：域、流程、运行时、工具、风险横切、观测、**`evals/`**、**`integrations/`**、标准 |
| **`specs/requirements/admin-console/`** | 管理后台 **信息架构**（视图层，**非** Runtime Domain）：[`README`](../../specs/requirements/admin-console/README.md)、[`sitemap`](../../specs/requirements/admin-console/sitemap.md)、[`Runtime→UI 映射`](../../specs/requirements/admin-console/runtime-to-ui-mapping.md)（与 **`domains/admin` 业务能力**分层，对上 **`src/admin/`**） |
| **`specs/design/`** | 设计：**[`overview.md`](../../specs/design/overview.md)**（入口重定向）；**[`architecture.md`](../../specs/design/architecture.md)**（C4、504、数据流 · **「与通用 Agent 栈之对照」**）；**[`canonical-trading-model.md`](../../specs/design/canonical-trading-model.md)**（Intent→Canonical→Gateway；**ADR-004**）；**[`deployment.md`](../../specs/design/deployment.md)**、**[`api.md`](../../specs/design/api.md)**、**[`adr/`](../../specs/design/adr/README.md)**、**[`runtime-architecture.md`](../../specs/design/runtime-architecture.md)**（**组件级挂载点**；**充实**须与 **`architecture`/`Runtime`/`exchange-agent`** 对签）等 |
| **`src/`** | **`admin/`**：交易所 **管理后台 Demo**（Vite+React，IA 对齐 `management-console-v1-prd` §3）；见 [`src/admin/README.md`](../../src/admin/README.md) |

## `specs/requirements/` 内

| 路径 | 说明 |
|------|------|
| **`domains/agent/`** | **AI 业务域**：`exchange-agent/`、`agent-orchestration/`、`runtime/`、`onboarding/` + 根 **`README.md`**（**布局**：[`domains/agent/README.md`](../../specs/requirements/domains/agent/README.md)） |
| **`domains/web/`** | **主站 / H5 用户触点**：Trading Agent **开通页**、**Agent 账单** UX（**FR-WEB\***）；[`domains/web/README.md`](../../specs/requirements/domains/web/README.md)、[`overview.md` §4 映射](../../specs/requirements/domains/web/overview.md) |
| **`domains/admin/`** | **后台模块**（按需建档）：详见 [`domains/README.md`](../../specs/requirements/domains/README.md)（**PRD · 八大模块与子域**）；运维观测 / 运行时横切 / 经营指标见同级 **`observability/`**、**`Runtime/`**、**`metrics/`** |
| **`flows/`** | 主流程（步骤级） |
| **`Runtime/`** | **主链** **[`Runtime/overview.md`](../../specs/requirements/Runtime/overview.md)**（执行、会话、状态、上下文、持久化、冻结、锁、恢复、事件、`boundaries`）；短入口 **[`Runtime/README.md`](../../specs/requirements/Runtime/README.md)** · **与** `exchange-agent` **互引** |
| **PRS**（**`prompt-runtime/`**） | **模型调用前拼装子系统**（**≠** `Runtime/` 执行态）— **总入口** [`prompt-runtime/README`](../../specs/requirements/prompt-runtime/README.md)（**[改什么去哪 §4](../../specs/requirements/prompt-runtime/README.md#prs-where-to-edit)**）；**L1** `prompts/`（七目录 + `library/`）；**读侧块 5** `market-narrative-runtime/`（MNRA · [`scenario-matrix`](../../specs/requirements/market-narrative-runtime/scenario-matrix.md)）；**L0** `skill-specs/`；Publish / 拼装 → `domains/admin/prompt-management/` · `runtime-injection` |
| **`tools/`** | Tool 注册与 schema 片段 |
| **`risk/`** | 全局风险横切：[`README`](../../specs/requirements/risk/README.md) **索引** + **薄切片** + [`acceptance`](../../specs/requirements/risk/acceptance.md)（**`SC-RISK*`**）；**域内边界 SSOT** **[`exchange-agent/boundaries`](../../specs/requirements/domains/agent/exchange-agent/boundaries.md)** |
| **`observability/`** | AI 观测（tracing、审计、幻觉类等）— **正文入口** `overview.md` |
| **`integrations/`** | 外部系统（交所 / Telegram / LLM / 通知等）— **[`README`](../../specs/requirements/integrations/README.md)** |
| **`standards/`** | 书写与评审规范 |
| **`metrics/`** | 指标体系 **索引** |
| **`evals/`** | **评测素材 / 场景集 / 数据集版本** 登记 — **[`README`](../../specs/requirements/evals/README.md)** |
| **`business/`** | 业务叙事索引 |
| **`product.md`** / **`spec.md`** | 产品 SSOT 与聚合索引 |
| **`contract-closure.md`** | 契约收口（DoD 主表） |
| **`closure-remaining.md`** | **关单余量 / §7.5 路径 / §7.6 MR 勾选**（**不**替代 `contract-closure`）：[`../../specs/requirements/closure-remaining.md`](../../specs/requirements/closure-remaining.md) **[§0 速链](../../specs/requirements/closure-remaining.md#closure-remaining-quicklinks)** · **[§7.5](../../specs/requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)** |

**Telegram 等渠道**：**以本仓库现网路径为准** — 需求与脚本互引中出现的路径（常含 **`domains/agent/telegram/`**、**`design/api`** **「Telegram Bot API」专节**、**`product/`** 卡片叙事）**即** **有效入口**；**不必**另假固定录。

若工具仍按旧路径（`channels/`、`domains/trading-agent/` 无 `agent/` 前缀等）解析，请以 **本篇** 为准并迁移工具配置。
