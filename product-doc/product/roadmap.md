# 产品路线图

**维护约定**（按季/主题的拆分文档、`design/api` 与对外承诺边界）：[`roadmap/README.md`](./roadmap/README.md)。

**本篇 TL;DR**：

- **职责**：规格侧 **P0 → 阶段 A～D** 与 **例行节奏**；对齐 **`flow/e2e-closed-loop`**（文首 **「架构语言」** → [`architecture`「与通用 Agent 栈之对照」](../specs/design/architecture.md)）与本文 **端到端主链**，用于团队「先写什么、何时算收口」。
- **边界**：**不**替代各文档内 FR/SC 正文；**不**在此冻结 **[`design/api.md`](../specs/design/api.md)** 矩阵格。**全库需求导航** → 下文 **[「需求全覆盖索引」](#req-full-index)**（链向 `specs/requirements/` **全部域/流/Runtime/设计**）。人力甘特见 **「刻意不做」**。**实质需求变更**：须 **同窗** 更新索引 + TL;DR（[`roadmap/README` · 维护约定](./roadmap/README.md)）。
- **收口执行一览（2026-05 规格批次 · 对齐）**：写路径优先级、W1 动作与 MR 粘贴稿见 **[`closure-completion-matrix.md`](../specs/requirements/closure-completion-matrix.md)** · **[`closure-internal-sprint.md`](../specs/requirements/closure-internal-sprint.md)**；管线走读勾选 **[`Runtime/pipeline-walkthrough-checklist.md`](../specs/requirements/Runtime/pipeline-walkthrough-checklist.md)**；本仓自检 **`./scripts/closure-preflight.sh`**。**不**替代 [`contract-closure.md`](../specs/requirements/contract-closure.md) DoD。
- **鸟瞰 / design 同窗（同批次）**：[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md) **与** **管线走读 · 闭环矩阵** **同窗维护**；MNRA / Memory **注入设计** **真源** **[`design/market-narrative-runtime.md`](../specs/design/market-narrative-runtime.md)** · **[`design/memory-runtime-injection.md`](../specs/design/memory-runtime-injection.md)**（分层细节见下文 **规格体系快照** 与横切表）。
- **横切 · 计费商业模型（2026-05-26）**：**订阅 + Capability + 加购包（用尽即停）** · **Agent 消耗仅轨 B** — **SSOT** [`billing-management/commerce-model.md`](../specs/requirements/domains/admin/billing-management/commerce-model.md) **v0.3** · **执行记录 join** **§5.3**（**`billingTraceId` + 核销状态**）；**Phase 2 FR/SC** [`functions` §5](../specs/requirements/domains/admin/billing-management/functions.md)、[`flow` S5 轨 B](../specs/requirements/domains/admin/billing-management/flow.md)、[`web/agent-billing` §2.1](../specs/requirements/domains/web/agent-billing.md)；**轨 B 契约骨架** + **`productionRuntime` S2/S5 + `runWritePathConsumeAndBill`** **已入库**；**Admin `/billing/overview` · Commerce 演示卡**（**FR-MC512** 同窗）。**关单余量** → [`closure-remaining` §7 · OP-BILL](../specs/requirements/closure-remaining.md#cc-remaining-open-items) · **派工** [`closure-internal-sprint` · MR-BILL](../specs/requirements/closure-internal-sprint.md)。**生产闭环** **`contract-closure` §8**。
- **横切 · `design/api` 计费轨 B（2026-05-26）**：[`design/api.md`](../specs/design/api.md) **登记表 · 内部专节 · 运营 `commerce/*` 小节** 与 [`commerce-model.md`](../specs/requirements/domains/admin/billing-management/commerce-model.md)、**PRD 模块五 · `FR-MC509～512`** **及** **上列 OpenAPI** 同窗。
- **横切 · 文档对齐（2026-05-26 → 05-27 清扫）**：**`product.md`**、**`web/overview`**、**`billing/overview` §0**、**Telegram Deeplink**、**`flows/*`**、**`openapi/README`** — **统一** **`me/commerce` + `/subaccount/billing` + join §5.3**；**`me/billing` / Token 扣费 UI** **仅 OpenAPI 归档（CC-P0-03）** — **本仓原型不实现**（**取代** 05-26「轨 A 对读」表述）。
- **横切 · Web 用户账单 IA（2026-05-27）**：[`admin-console-web-billing-reconciliation` §0](../specs/requirements/domains/web/admin-console-web-billing-reconciliation.md) — **`me/commerce` only**；TG **`?start=ab`**（[`commerce-deeplink` §3](../specs/requirements/domains/web/commerce-deeplink.md)）；**SC-WEB-14/15**；**`staging-mr-bill-probe`**（`WEB_ORIGIN`）。
- **横切 · Admin 计费 IA（2026-05-27）**：[`admin-console-billing-pages-reconciliation` §0](../specs/requirements/domains/admin/billing-management/admin-console-billing-pages-reconciliation.md) — **总览 / 商业运营 / 执行核销**；**纯数字 `executionId`**；**无** Token 退款/对读 UI。
- **横切 · Planner 输出契约（2026-05-27）**：[`Runtime/planner-contract.md`](../specs/requirements/Runtime/planner-contract.md) **§5～§8** — **`PlannerPlanEnvelope`/`PlannerPlanStep`**、**V1 线性计划**、**禁嵌套条件 DAG**（**`emit_nested_conditional_plan`** · [`execution-lifecycle` §5.2](../specs/requirements/domains/agent/agent-orchestration/execution-lifecycle.md)）；**OpenAPI 类型** = **B 阶段** **专项 MR**。
- **横切 · 记忆四原则与配置默认（2026-05-27）**：[`memory-runtime` §14～§16](../specs/requirements/Runtime/memory-runtime.md) **v1.8** · **默认 stale + Resume 门控**（**idle/TTL 先达 · 温索引最近 episode · `RESUME_CLASSIFIER_MIN_CONFIDENCE=0.75`**）· [`keys` §2.1](../specs/requirements/domains/admin/trading-agent-config/keys.md) · [`design/memory-runtime-injection` §2.4](../specs/design/memory-runtime-injection.md) **v0.4** · **P0 eval** **`idle_default_stale` / `resume_classifier_gate` / `resume_classifier_multi_episode` / `stm_governance_regression`**
- **横切 · 澄清需求闭环（2026-05-27）**：[`clarify-user-visible` §0～§7](../specs/requirements/prompts/shared/clarify-user-visible.md) · [`clarify-session.md`](../specs/requirements/domains/agent/agent-orchestration/clarify-session.md) **v1.6**（**§1.1 类型A×stale · §2.5 去重 · §2.3 重意图 · Telegram §2.6.1 幂等**）· [`evals/clarify-telegram` §12～§13](../specs/requirements/evals/clarify-telegram.md) · **OpenAPI **`MemoryRuntimeConfigSnapshot`** · **[`memory-runtime-injection` v0.5](../specs/design/memory-runtime-injection.md)**
- **横切 · 会话并发 P0（2026-05-27）**：[`session-concurrency-policy.md`](../specs/requirements/domains/agent/agent-orchestration/session-concurrency-policy.md) **v1.0** · **`FR-AO07`/`SC-AO-09～10`** · [`keys` §2.2](../specs/requirements/domains/admin/trading-agent-config/keys.md) **`SESSION_*`** · [`evals/session-concurrency.md`](../specs/requirements/evals/session-concurrency.md)
- **横切 · 只读澄清 P1（2026-05-27）**：[`read-clarify-session.md`](../specs/requirements/domains/agent/agent-orchestration/read-clarify-session.md) **v1.0** · **`FR-AO08`/`SC-READ-CLARIFY-*`** · **`rc:*`** · [`keys` §2.3](../specs/requirements/domains/admin/trading-agent-config/keys.md) · [`evals/read-clarify-telegram.md`](../specs/requirements/evals/read-clarify-telegram.md)
- **横切 · Fallback/Retry 决策树 P1（2026-05-27）**：[`fallback-policy.md`](../specs/requirements/Runtime/fallback-policy.md) **v0.4** **§2 场景表** · **`SC-RT-FB-01～07`** · [`evals/fallback-retry-decision-tree.md`](../specs/requirements/evals/fallback-retry-decision-tree.md)
- **横切 · UNKNOWN 追问状态机 P1（2026-05-27）**：[`unknown-stall-policy.md`](../specs/requirements/risk/unknown-stall-policy.md) **v0.2** **§2** · **`SC-RISK-07*`** · [`keys` §2.4](../specs/requirements/domains/admin/trading-agent-config/keys.md) **`UNKNOWN_*`** · [`evals/unknown-followup-telegram.md`](../specs/requirements/evals/unknown-followup-telegram.md)
- **横切 · Prompt 治理 IA + 正文（2026-05-27）**：[`admin-console-prompt-strategy-reconciliation` §0](../specs/requirements/domains/admin/prompt-management/admin-console-prompt-strategy-reconciliation.md)、[`governance-map`](../specs/requirements/prompts/governance-map.md)、[`promptBodyTemplates.ts`](../src/admin/src/data/promptBodyTemplates.ts)、[`prompt-governance-checklist`](./prompt-governance-checklist.md) — **16 包 · SC-PM-21～22**；执行详情 **Skill Scope / 拼装追溯 / Canonical Inspector**。
- **横切 · 运营台 IA 对账（2026-05-27 · 原型 §0 索引）**：[`tool-registry-reconciliation` §0](../specs/requirements/domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) · [`runtime-executions-reconciliation` §0](../specs/requirements/domains/admin/observability-management/admin-console-runtime-executions-reconciliation.md) · [`observability-reconciliation` §0](../specs/requirements/domains/admin/observability-management/admin-console-observability-reconciliation.md) · [`agent-instances-reconciliation` §0](../specs/requirements/domains/admin/agent-management/admin-console-agent-instances-reconciliation.md)。
- **横切 · 技能登记 Demo（2026-05-26）**：**`src/admin`** **启用/停用** + Git 登记册 · [`PUBLISH` §7.1](../specs/requirements/skill-specs/PUBLISH.md#71-admin-原型--交付边界srcadmin) · [`src/admin/README`](../src/admin/README.md)（**SC-TM-17～18** → 所内 MR-B）。
- **入口**：**[`product.md`](../specs/requirements/product.md)**（范围 SSOT）→ **[需求全覆盖索引](#req-full-index)** → **L1～L7 快照** → [`product/README` · 文档地图](./README.md)、[`release-notes.md`](./release-notes.md)。

### 规格体系快照（2026-05 批次 · 分层索引）

与本仓 **[`closure-completion-matrix`](../specs/requirements/closure-completion-matrix.md)**（主链 **P‑01～P‑08**、横切 **OP-***）及 **[`skill-specs/requirements-closure.md`](../specs/requirements/skill-specs/requirements-closure.md)**（**§3 · 需求层 DoD**）**同窗**；**下文不复制 FR**。**推荐阅读顺序**：**`Runtime/overview` + `domain-model`** → **PRS（`prompt-runtime`）** → **Skill / Tool 运营 · Publish** → **Memory / MNRA · Eval** → **收口 preflight · GHA**。

| 层 | 定位（与执行态分界线） | 权威入口 |
|----|--------------------------|----------|
| **L1 · Runtime 执行态** | **`executionId` 十步管线、Risk、上下文栈、Timeline、Recovery、真源映射** · **Planner 输出契约** [`planner-contract` §5～§6](../specs/requirements/Runtime/planner-contract.md) · **≠ 模型拼装（PRS）** | **[`Runtime/README.md`](../specs/requirements/Runtime/README.md)** · [`overview`](../specs/requirements/Runtime/overview.md)、[`domain-model`](../specs/requirements/Runtime/domain-model.md)、[`execution`](../specs/requirements/Runtime/execution.md)、[`planner-contract`](../specs/requirements/Runtime/planner-contract.md)、[`context-management`](../specs/requirements/Runtime/context-management.md)、[`memory-runtime`](../specs/requirements/Runtime/memory-runtime.md)、[`recovery`](../specs/requirements/Runtime/recovery.md)、[`runtime-truth-source-map`](../specs/requirements/Runtime/runtime-truth-source-map.md)、[`pipeline-walkthrough-checklist`](../specs/requirements/Runtime/pipeline-walkthrough-checklist.md) |
| **L2 · PRS** | **Prompt Runtime Spec：模型调用前拼装**（`prompts/` · `prompt-management/runtime-injection` **同窗**）；**≠** **`Runtime/` 执行truth** | [`prompt-runtime/README.md`](../specs/requirements/prompt-runtime/README.md)（[`§4 · 改什么去哪`](../specs/requirements/prompt-runtime/README.md#prs-where-to-edit)）、[`prompt-management/runtime-injection.md`](../specs/requirements/domains/admin/prompt-management/runtime-injection.md)、[`prompts/README.md`](../specs/requirements/prompts/README.md) |
| **L3 · Skill 契约 · Publish · Tool** | **L0 Markdown `skill-specs`、manifest、bundle、`read_skill` 前编排** · **后台模块三 Tool 登记与「技能与工具」页镜像** · **≠ 交易所写实现** | [`skill-specs/README`](../specs/requirements/skill-specs/README.md)、[`skill-specs/PUBLISH`](../specs/requirements/skill-specs/PUBLISH.md)、[`skill-specs/production-runtime`](../specs/requirements/skill-specs/production-runtime.md)、[`domains/admin/tool-management/overview`](../specs/requirements/domains/admin/tool-management/overview.md)、[`tools/tool-registry`](../specs/requirements/tools/tool-registry.md)、[`admin-console/page-specs.md`](../specs/requirements/admin-console/page-specs.md)、[`openapi/components/skill-operation-spec-schemas.yaml`](../specs/openapi/components/skill-operation-spec-schemas.yaml) |
| **L4 · Memory（STM / LTM / 装配闸）** | **跨会话 Semantic、会话内上下文、清空、话术与门禁** · **idle/TTL 默认 stale + Resume** · **同窗 Telegram / 澄清 session** | [`Runtime/memory-runtime.md`](../specs/requirements/Runtime/memory-runtime.md)、[`clarify-session.md`](../specs/requirements/domains/agent/agent-orchestration/clarify-session.md)、[`design/memory-runtime-injection.md`](../specs/design/memory-runtime-injection.md)、[`openapi/components/memory-runtime-schemas.yaml`](../specs/openapi/components/memory-runtime-schemas.yaml)、[`evals/memory-runtime.md`](../specs/requirements/evals/memory-runtime.md)、[`telegram/overview.md`](../specs/requirements/domains/agent/telegram/overview.md)、[`interaction-flow-standard.md`](../specs/requirements/standards/interaction-flow-standard.md)、[`trading-agent-config/keys.md`](../specs/requirements/domains/admin/trading-agent-config/keys.md) |
| **L5 · Market MNRA** | **行情叙事宿主、Facts、phase、hints · 需求 + design + OpenAPI 组件同窗** | [`market-narrative-runtime/README.md`](../specs/requirements/market-narrative-runtime/README.md)、[`market-intelligence.md`](../specs/requirements/domains/agent/exchange-agent/market-intelligence.md)、[`design/market-narrative-runtime.md`](../specs/design/market-narrative-runtime.md)、[`market-runtime-schemas.yaml`](../specs/openapi/components/market-runtime-schemas.yaml)、[`evals/market-narrative.md`](../specs/requirements/evals/market-narrative.md) |
| **L6 · Eval（专卷 · 不保代域验收）** | **写序、Skill 契约、Memory/Market/Clarify fixture**；总索引 **`evals/README`**、**`evals/scenarios`** | [`evals/README.md`](../specs/requirements/evals/README.md)、[`evals/scenarios.md`](../specs/requirements/evals/scenarios.md)、[`evals/pipeline-write-order.md`](../specs/requirements/evals/pipeline-write-order.md)、[`evals/skill-contract.md`](../specs/requirements/evals/skill-contract.md)、[`evals/memory-runtime.md`](../specs/requirements/evals/memory-runtime.md)、[`evals/clarify-telegram.md`](../specs/requirements/evals/clarify-telegram.md)、[`evals/idle-default-stale.md`](../specs/requirements/evals/idle-default-stale.md)、[`evals/resume-classifier-gate.md`](../specs/requirements/evals/resume-classifier-gate.md) |
| **L7 · 收口与本仓 CI** | **一览表 · 冲刺工单 · evidence · preflight · Skill/registry 一致性** | [`closure-completion-matrix`](../specs/requirements/closure-completion-matrix.md)、[`closure-internal-sprint`](../specs/requirements/closure-internal-sprint.md)、`./scripts/closure-preflight.sh`、[`.github/workflows/skill-contract-consistency.yml`](../.github/workflows/skill-contract-consistency.yml)；**Hosted** → [`HOSTED-ROLLOUT-CHECKLIST`](../specs/openapi/HOSTED-ROLLOUT-CHECKLIST.md) |

<a id="req-full-index"></a>

## 需求全覆盖索引（契约导航）

**用途**：Roadmap **须覆盖当前项目全部需求正文** — 本节为 **可检索总表**（**索引层**），与 [`product.md`](../specs/requirements/product.md) **§范围**、[`domains/README.md`](../specs/requirements/domains/README.md) **同窗**。**FR/SC 条文** **只** 在各链接文档内维护；**未列路径** = 遗漏，应补链或补文档。

### A. 治理、聚合与收口

| 类 | 文档 |
|----|------|
| **产品范围 SSOT** | [`product.md`](../specs/requirements/product.md)、[`spec.md`](../specs/requirements/spec.md) |
| **小团队日常** | [`LITE-MODE.md`](../specs/requirements/LITE-MODE.md)、[`release-notes.md`](./release-notes.md) |
| **关单 / 余量 / 冲刺** | [`contract-closure.md`](../specs/requirements/contract-closure.md)、[`closure-remaining.md`](../specs/requirements/closure-remaining.md)、[`closure-internal-sprint.md`](../specs/requirements/closure-internal-sprint.md)、[`closure-completion-matrix.md`](../specs/requirements/closure-completion-matrix.md)、[`closure-staging-evidence-log.md`](../specs/requirements/closure-staging-evidence-log.md) |
| **书写规范** | [`standards/README.md`](../specs/requirements/standards/README.md)、[`STANDARDS-ADOPTION.md`](../specs/requirements/standards/STANDARDS-ADOPTION.md)、[`Log.md`](../specs/requirements/standards/Log.md) |
| **业务薄索引** | [`business/README.md`](../specs/requirements/business/README.md) |
| **需求总目录** | [`requirements/README.md`](../specs/requirements/README.md) |

### B. 产品范围 ↔ 需求入口（`product.md` §范围）

| `product.md` 包含项 | 权威需求入口 |
|---------------------|--------------|
| 子账户 · API · 交易路由 | [`exchange-agent/overview`](../specs/requirements/domains/agent/exchange-agent/overview.md)、[`onboarding/`](../specs/requirements/domains/agent/onboarding/overview.md) |
| 用户接入与绑定 | [`onboarding/`](../specs/requirements/domains/agent/onboarding/overview.md)、[`web/agent-onboarding`](../specs/requirements/domains/web/agent-onboarding.md) |
| Exchange Agent 能力主体 | [`exchange-agent/`](../specs/requirements/domains/agent/exchange-agent/README.md)（**分卷见 §C**） |
| 计费 · 商业分层 | [`billing-management/`](../specs/requirements/domains/admin/billing-management/overview.md)、[`commerce-model`](../specs/requirements/domains/admin/billing-management/commerce-model.md)、[`web/agent-billing`](../specs/requirements/domains/web/agent-billing.md)、[`consume-and-bill`](../specs/requirements/flows/consume-and-bill.md) |
| 会员准入 · VIP | [`access-control/`](../specs/requirements/domains/admin/access-control/overview.md)、[`eligibility-runtime`](../specs/requirements/domains/admin/access-control/eligibility-runtime.md) |
| 运营后台八大模块 | [`management-console-v1-prd`](../specs/requirements/domains/admin/management-console-v1-prd.md)、**§E** |
| 观测与审计 | [`observability/`](../specs/requirements/observability/overview.md) |
| 主流程 | **§G** [`flows/README`](../specs/requirements/flows/README.md) |
| Telegram 渠道 | [`telegram/overview`](../specs/requirements/domains/agent/telegram/overview.md)、[`admin-bot-config`](../specs/requirements/domains/agent/telegram/admin-bot-config.md) |
| Prompt 治理（后台） | [`prompt-management/`](../specs/requirements/domains/admin/prompt-management/overview.md)、[`prompts/`](../specs/requirements/prompts/README.md) |
| 场景编排 | [`agent-orchestration/`](../specs/requirements/domains/agent/agent-orchestration/overview.md) |
| 上下文控制 | [`agent-context/overview`](../specs/requirements/domains/agent/agent-context/overview.md) |
| 契约收口 | [`contract-closure`](../specs/requirements/contract-closure.md) |
| 交易技能化 · `FR-T11` | [`trade-assistance`](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)、[`skill-specs/`](../specs/requirements/skill-specs/README.md) |

### C. `domains/agent/` — AI 业务域

| 子域 | 入口与分卷 |
|------|------------|
| **导航** | [`agent/README.md`](../specs/requirements/domains/agent/README.md) |
| **exchange-agent** | [`overview`](../specs/requirements/domains/agent/exchange-agent/overview.md)、[`intents`](../specs/requirements/domains/agent/exchange-agent/intents.md)、[`market-intelligence`](../specs/requirements/domains/agent/exchange-agent/market-intelligence.md)、[`market-runtime-payload`](../specs/requirements/domains/agent/exchange-agent/market-runtime-payload.md)、[`portfolio-insight`](../specs/requirements/domains/agent/exchange-agent/portfolio-insight.md)、[`risk-alerts`](../specs/requirements/domains/agent/exchange-agent/risk-alerts.md)、[`trade-assistance`](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)、[`monitoring-tasks`](../specs/requirements/domains/agent/exchange-agent/monitoring-tasks.md)、[`boundaries`](../specs/requirements/domains/agent/exchange-agent/boundaries.md)、[`overview-legacy-migration`](../specs/requirements/domains/agent/exchange-agent/overview-legacy-migration.md) |
| **agent-orchestration** | [`overview`](../specs/requirements/domains/agent/agent-orchestration/overview.md)、[`routing-engine`](../specs/requirements/domains/agent/agent-orchestration/routing-engine.md)、[`runtime-freeze`](../specs/requirements/domains/agent/agent-orchestration/runtime-freeze.md)、[`execution-lifecycle`](../specs/requirements/domains/agent/agent-orchestration/execution-lifecycle.md)、[`implementation-alignment`](../specs/requirements/domains/agent/agent-orchestration/implementation-alignment.md)、[`confirmation-flow`](../specs/requirements/domains/agent/agent-orchestration/confirmation-flow.md)、[`clarify-session`](../specs/requirements/domains/agent/agent-orchestration/clarify-session.md)、[`read-clarify-session`](../specs/requirements/domains/agent/agent-orchestration/read-clarify-session.md)、[`session-concurrency-policy`](../specs/requirements/domains/agent/agent-orchestration/session-concurrency-policy.md)、[`state-machine`](../specs/requirements/domains/agent/agent-orchestration/state-machine.md)、[`retry-policy`](../specs/requirements/domains/agent/agent-orchestration/retry-policy.md)、[`task-scheduler`](../specs/requirements/domains/agent/agent-orchestration/task-scheduler.md)、[`boundaries`](../specs/requirements/domains/agent/agent-orchestration/boundaries.md)、[`goal-and-execution-paths`](../specs/requirements/domains/agent/agent-orchestration/goal-and-execution-paths.md) |
| **onboarding** | [`overview`](../specs/requirements/domains/agent/onboarding/overview.md)、[`initialization-flow`](../specs/requirements/domains/agent/onboarding/initialization-flow.md)、[`telegram-binding`](../specs/requirements/domains/agent/onboarding/telegram-binding.md)、[`agent-account`](../specs/requirements/domains/agent/onboarding/agent-account.md)、[`permission-authorization`](../specs/requirements/domains/agent/onboarding/permission-authorization.md)、[`runtime-provisioning`](../specs/requirements/domains/agent/onboarding/runtime-provisioning.md)、[`activation-policy`](../specs/requirements/domains/agent/onboarding/activation-policy.md)、[`boundaries`](../specs/requirements/domains/agent/onboarding/boundaries.md) |
| **telegram** | [`overview`](../specs/requirements/domains/agent/telegram/overview.md)、[`admin-bot-config`](../specs/requirements/domains/agent/telegram/admin-bot-config.md)、[`mobile-app`](../specs/requirements/domains/agent/telegram/mobile-app.md)（**非目标**） |
| **runtime（透镜）** | [`runtime/overview`](../specs/requirements/domains/agent/runtime/overview.md) |
| **agent-context** | [`agent-context/overview`](../specs/requirements/domains/agent/agent-context/overview.md) |
| **goals** | [`goals/README`](../specs/requirements/domains/agent/goals/README.md) |

### D. `domains/web/` — 浏览器触点

| 文档 | 说明 |
|------|------|
| [`README`](../specs/requirements/domains/web/README.md)、[`overview`](../specs/requirements/domains/web/overview.md) | 域边界 · **FR-WEB→CC §4** |
| [`agent-onboarding`](../specs/requirements/domains/web/agent-onboarding.md) | 产品线绑定 · **`me/agent/*`** |
| [`agent-billing`](../specs/requirements/domains/web/agent-billing.md) | **`/subaccount/billing`** · **FR-WEB07～11 / SC-WEB-14～15** |
| [`commerce-deeplink`](../specs/requirements/domains/web/commerce-deeplink.md) | TG **`?start=ab*`** |
| [`admin-console-web-billing-reconciliation` §0](../specs/requirements/domains/web/admin-console-web-billing-reconciliation.md) | **原型 ↔ 规格 SSOT** |
| [`staging-me-commerce-runbook`](../specs/requirements/domains/web/staging-me-commerce-runbook.md) | Staging 探针 |

### E. `domains/admin/` — 运营后台八大模块

| 模块 | 需求入口 | 原型对账（若有） |
|------|----------|------------------|
| **聚合 PRD** | [`management-console-v1-prd`](../specs/requirements/domains/admin/management-console-v1-prd.md) | — |
| **一 · Agent Management** | [`agent-management/overview`](../specs/requirements/domains/admin/agent-management/overview.md) | [`agent-instances-reconciliation` §0](../specs/requirements/domains/admin/agent-management/admin-console-agent-instances-reconciliation.md) |
| **二 · Prompt Management** | [`prompt-management/overview`](../specs/requirements/domains/admin/prompt-management/overview.md)、[`config`](../specs/requirements/domains/admin/prompt-management/config.md)、[`runtime-injection`](../specs/requirements/domains/admin/prompt-management/runtime-injection.md) | [`prompt-strategy-reconciliation` §0](../specs/requirements/domains/admin/prompt-management/admin-console-prompt-strategy-reconciliation.md) |
| **三 · Tool Management** | [`tool-management/overview`](../specs/requirements/domains/admin/tool-management/overview.md) | [`tool-registry-reconciliation` §0](../specs/requirements/domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) |
| **四 · AI Settings** | [`ai-settings/overview`](../specs/requirements/domains/admin/ai-settings/overview.md) | — |
| **五 · Billing** | [`billing-management/overview`](../specs/requirements/domains/admin/billing-management/overview.md) **§0**、[`commerce-model`](../specs/requirements/domains/admin/billing-management/commerce-model.md)、[`functions`](../specs/requirements/domains/admin/billing-management/functions.md)、[`flow`](../specs/requirements/domains/admin/billing-management/flow.md)、[`rules`](../specs/requirements/domains/admin/billing-management/rules.md)、[`bff-worker-wiring`](../specs/requirements/domains/admin/billing-management/bff-worker-wiring.md) | [`billing-pages-reconciliation` §0](../specs/requirements/domains/admin/billing-management/admin-console-billing-pages-reconciliation.md) |
| **六 · Access Control** | [`access-control/overview`](../specs/requirements/domains/admin/access-control/overview.md)、[`functions`](../specs/requirements/domains/admin/access-control/functions.md)、[`eligibility-runtime`](../specs/requirements/domains/admin/access-control/eligibility-runtime.md) | — |
| **七 · Trading Agent Config** | [`trading-agent-config/overview`](../specs/requirements/domains/admin/trading-agent-config/overview.md)、[`keys`](../specs/requirements/domains/admin/trading-agent-config/keys.md) | — |
| **八 · Observability** | [`observability-management/overview`](../specs/requirements/domains/admin/observability-management/overview.md) | [`runtime-executions-reconciliation` §0](../specs/requirements/domains/admin/observability-management/admin-console-runtime-executions-reconciliation.md)、[`observability-reconciliation` §0](../specs/requirements/domains/admin/observability-management/admin-console-observability-reconciliation.md) |

### F. `admin-console/` — 后台 IA（视图层 · 非 Domain FR）

[`README`](../specs/requirements/admin-console/README.md)、[`naming-alignment`](../specs/requirements/admin-console/naming-alignment.md)、[`sitemap`](../specs/requirements/admin-console/sitemap.md)、[`page-specs`](../specs/requirements/admin-console/page-specs.md)、[`runtime-to-ui-mapping`](../specs/requirements/admin-console/runtime-to-ui-mapping.md)、[`demo-routing`](../specs/requirements/admin-console/demo-routing.md)、[`api-surface`](../specs/requirements/admin-console/api-surface.md)、[`delivery-plan`](../specs/requirements/admin-console/delivery-plan.md)、[`prd-ia-alignment`](../specs/requirements/admin-console/prd-ia-alignment.md)

### G. `flows/` — 业务主流程

[`flows/README`](../specs/requirements/flows/README.md) · [`activate-trading-agent`](../specs/requirements/flows/activate-trading-agent.md) · [`trade-via-agent`](../specs/requirements/flows/trade-via-agent.md) · [`read-analyze-and-search-via-agent`](../specs/requirements/flows/read-analyze-and-search-via-agent.md) · [`consume-and-bill`](../specs/requirements/flows/consume-and-bill.md) · [`wealth-via-agent`](../specs/requirements/flows/wealth-via-agent.md) · [`automation-alerts`](../specs/requirements/flows/automation-alerts.md)

### H. `Runtime/` — 执行态（全分卷）

[`Runtime/README`](../specs/requirements/Runtime/README.md)、[`overview`](../specs/requirements/Runtime/overview.md)、[`domain-model`](../specs/requirements/Runtime/domain-model.md)、[`execution`](../specs/requirements/Runtime/execution.md)、[`runtime-state-machine`](../specs/requirements/Runtime/runtime-state-machine.md)、[`execution-transition-matrix`](../specs/requirements/Runtime/execution-transition-matrix.md)、[`context-management`](../specs/requirements/Runtime/context-management.md)、[`memory-runtime`](../specs/requirements/Runtime/memory-runtime.md)、[`recovery`](../specs/requirements/Runtime/recovery.md)、[`unknown-state`](../specs/requirements/Runtime/unknown-state.md)、[`reconciliation`](../specs/requirements/Runtime/reconciliation.md)、[`failure-matrix`](../specs/requirements/Runtime/failure-matrix.md)、[`runtime-error-taxonomy`](../specs/requirements/Runtime/runtime-error-taxonomy.md)、[`runtime-invariants`](../specs/requirements/Runtime/runtime-invariants.md)、[`runtime-truth-source-map`](../specs/requirements/Runtime/runtime-truth-source-map.md)、[`planner-contract`](../specs/requirements/Runtime/planner-contract.md)、[`pipeline-walkthrough-checklist`](../specs/requirements/Runtime/pipeline-walkthrough-checklist.md)、[`boundaries`](../specs/requirements/Runtime/boundaries.md) · 其余：[`error-normalization`](../specs/requirements/Runtime/error-normalization.md)、[`persistence`](../specs/requirements/Runtime/persistence.md)、[`locking`](../specs/requirements/Runtime/locking.md)、[`sessions`](../specs/requirements/Runtime/sessions.md)、[`event-storage`](../specs/requirements/Runtime/event-storage.md)、[`freeze-policy`](../specs/requirements/Runtime/freeze-policy.md)、[`fallback-policy`](../specs/requirements/Runtime/fallback-policy.md)、[`runtime-consistency`](../specs/requirements/Runtime/runtime-consistency.md)、[`runtime-state`](../specs/requirements/Runtime/runtime-state.md)

### I. PRS · Prompt · Skill · MNRA

| 类 | 入口 |
|----|------|
| **PRS** | [`prompt-runtime/README`](../specs/requirements/prompt-runtime/README.md) |
| **L1 提示词库** | [`prompts/README`](../specs/requirements/prompts/README.md)、[`governance-map`](../specs/requirements/prompts/governance-map.md)、[`prompts/shared/clarify-user-visible.md`](../specs/requirements/prompts/shared/clarify-user-visible.md)、[`prompts/library/`](../specs/requirements/prompts/library/README.md) |
| **Skill L0** | [`skill-specs/README`](../specs/requirements/skill-specs/README.md)、[`PUBLISH`](../specs/requirements/skill-specs/PUBLISH.md)、[`production-runtime`](../specs/requirements/skill-specs/production-runtime.md)、[`requirements-closure`](../specs/requirements/skill-specs/requirements-closure.md) |
| **Tool 登记** | [`tools/README`](../specs/requirements/tools/README.md)、[`tool-registry`](../specs/requirements/tools/tool-registry.md) |
| **MNRA** | [`market-narrative-runtime/README`](../specs/requirements/market-narrative-runtime/README.md) |

### J. 横切：观测 · 风险 · 集成 · 评测 · 指标

| 类 | 入口 |
|----|------|
| **观测** | [`observability/overview`](../specs/requirements/observability/overview.md)、[`tracing`](../specs/requirements/observability/tracing.md)、[`metrics`](../specs/requirements/observability/metrics.md)、[`audit-log`](../specs/requirements/observability/audit-log.md)、[`hallucination`](../specs/requirements/observability/hallucination.md)、[`runtime-monitor`](../specs/requirements/observability/runtime-monitor.md) |
| **风险** | [`risk/README`](../specs/requirements/risk/README.md)、[`acceptance`](../specs/requirements/risk/acceptance.md)、[`hitl-and-automation-matrix`](../specs/requirements/risk/hitl-and-automation-matrix.md) |
| **集成** | [`integrations/README`](../specs/requirements/integrations/README.md)、[`exchange/overview`](../specs/requirements/integrations/exchange/overview.md)、[`agent-coobit-api-allowlist`](../specs/requirements/integrations/exchange/agent-coobit-api-allowlist.md)、[`telegram/`](../specs/requirements/integrations/telegram/bot-api.md)、[`llm/`](../specs/requirements/integrations/llm/provider-routing.md)、[`notifications/`](../specs/requirements/integrations/notifications/push-delivery.md) |
| **评测** | [`evals/README`](../specs/requirements/evals/README.md)、[`scenarios`](../specs/requirements/evals/scenarios.md)、[`pipeline-write-order`](../specs/requirements/evals/pipeline-write-order.md)、[`skill-contract`](../specs/requirements/evals/skill-contract.md)、[`memory-runtime`](../specs/requirements/evals/memory-runtime.md)、[`clarify-telegram`](../specs/requirements/evals/clarify-telegram.md)、[`idle-default-stale`](../specs/requirements/evals/idle-default-stale.md)、[`resume-classifier-gate`](../specs/requirements/evals/resume-classifier-gate.md) |
| **指标导航** | [`metrics/README`](../specs/requirements/metrics/README.md)、[`trading-metrics`](../specs/requirements/metrics/trading-metrics.md) |

### K. `design/` · `openapi/` · 契约

| 类 | 入口 |
|----|------|
| **设计总览** | [`design/README`](../specs/design/README.md)、[`architecture`](../specs/design/architecture.md)、[`runtime-architecture`](../specs/design/runtime-architecture.md)、[`deployment`](../specs/design/deployment.md) |
| **API 矩阵** | [`design/api.md`](../specs/design/api.md) |
| **Canonical / 工具序** | [`canonical-trading-model`](../specs/design/canonical-trading-model.md)、[`tool-calling-sequence`](../specs/design/tool-calling-sequence.md)、[`sub-account-isolation`](../specs/design/sub-account-isolation.md) |
| **注入设计** | [`market-narrative-runtime`](../specs/design/market-narrative-runtime.md)、[`memory-runtime-injection`](../specs/design/memory-runtime-injection.md) |
| **ADR** | [`adr/README`](../specs/design/adr/README.md)（**001～004**） |
| **OpenAPI** | [`openapi/README`](../specs/openapi/README.md)、[`OWNERS`](../specs/openapi/OWNERS.md) |

### L. 人类叙事与鸟瞰（非 FR SSOT）

[`product/README`](./README.md)、[`flows.md`](./flows.md)、[`end-to-end-guide.md`](./end-to-end-guide.md)、[`journey-validation.md`](./journey-validation.md)、[`telegram-and-cards.md`](./telegram-and-cards.md)、[`requirements-spec-human.md`](./requirements-spec-human.md)、[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md)、[`e2e-closed-loop.html`](../flow/e2e-closed-loop.html)

### M. 本仓原型（实现对照 · 非需求正文）

| 路径 | 说明 |
|------|------|
| [`src/admin/README`](../src/admin/README.md) | 运营台 Demo · **对账见 §E/F** |
| [`src/Web/README`](../src/Web/README.md) | 用户 H5 · **对账见 §D** |
| [`src/admin/src/productionRuntime/README`](../src/admin/src/productionRuntime/README.md) | S2/S5 计费小样 |

**索引维护**：新增 **`specs/requirements/**` 域/流/Runtime 分卷** 时，**须** 在本节 **补一行链**；**仅改 FR 编号** 可 **N/A**（若路径未变）。

### 优先级与编号对照（读法 SSOT）

避免 **路线图 `P0` · 矩阵 `P-01` · 契约 `CC-P0` · 快照 `L1～L7` · 冲刺 `W1`** **混读**。**不**另起 **人力甘特**；本节只 **对齐符号**。

| 记号 | 所在文档（锚） | 含义 | 怎么用 |
|------|----------------|------|--------|
| **`P0` · 阶段 A～D** | **本文** · **§当前最应该做的三件事** · **§分阶段节奏** | 产品对内 **阶段优先** | 「长期先稳住什么底盘」 |
| **`L1～L7`** | **本文** · **规格体系快照** | **分层阅读 / MR 条文自检顺序** | **自顶向下对拍** · **≠** **本周开发唯一排序** |
| **`P‑01～P‑08`** | [`closure-completion-matrix` §1](../specs/requirements/closure-completion-matrix.md) | **端到端写路径** **块** · **色块=闭合度** | **跟 Gateway、Publish 等主链卡点** |
| **`CC‑P0` · `CC‑P1`** | [`closure-completion-matrix` §2](../specs/requirements/closure-completion-matrix.md)、[`contract-closure`](../specs/requirements/contract-closure.md) | **契约关单** · **红黄=对外承诺边界** | **MR 勾选 · 会签** |
| **`W1` · **W1～W4** | [`closure-completion-matrix` §0 · §5](../specs/requirements/closure-completion-matrix.md) | **冲刺周** · **谁先做什么** | **派工第一依据** · 同窗 [`closure-internal-sprint`](../specs/requirements/closure-internal-sprint.md) |

**当周硬排序**：以 **`closure-completion-matrix` §0 · W1 五步** + **`closure-internal-sprint`** **为准**。**`L4` / `L5` 互不默认锁死先后顺序** — 除非 **工单/MR** 显式捆绑。

---

以下 **执行节奏与任务规划** 与 specs 对齐；若与 [`specs/requirements/product.md`](../specs/requirements/product.md) 冲突，以 specs 为准并回写本文。**路演 / 对外承诺**：须 **`product.md`**（范围）、[`design/api.md`](../specs/design/api.md)（矩阵）、[`contract-closure.md`](../specs/requirements/contract-closure.md)（收口）**同屏对读**；**未关闭项排期 / MR 勾选路径** [`closure-remaining` §7.5](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path) · [§7.6](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)；**不得以** 仅 **`product/`** 叙事或 **本文** **代替契约裁定**。

---

## 执行节奏与任务规划（specs / 产品对齐）

本文说明 **当前最应优先做的事** 与 **分阶段节奏**，用于团队对齐「先写什么、后写什么、何时算收口」。**契约与验收 SSOT** 仍以 [`specs/requirements/product.md`](../specs/requirements/product.md)、各 [`domains/`](../specs/requirements/domains/)（含 **[`domains/web/`](../specs/requirements/domains/web/README.md)** · **绑定 onboarding（可外置）** **与** **账单（交易所站内）** **FR-WEB**）、[`flows/`](../specs/requirements/flows/)、[`domains/agent/telegram/`](../specs/requirements/domains/agent/telegram/README.md)、[`specs/design/`](../specs/design/) 为准。

### Roadmap 与「完整项目」：读者分工（消解歧义）

| 你要回答的问题 | 先打开的权威 | 与本文关系 |
|----------------|--------------|------------|
| **做不做 / 非目标 / 术语** | [`product.md`](../specs/requirements/product.md) | 与域条文冲突 → **`product.md`** 裁 |
| **用户故事 / 汇报话术** | [`product/README`](./README.md)、[`flows.md`](./flows.md)、[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md)、[`requirements-spec-human.md`](./requirements-spec-human.md) | **不得单独**当作「已承诺能力」；**对内系统工程叙事** [`architecture`「与通用 Agent 栈之对照」](../specs/design/architecture.md)；**对外半页纸** → [`release-notes.md`](./release-notes.md)、[`LITE-MODE`](../specs/requirements/LITE-MODE.md) |
| **PATH 冻结与否 / 能否宣称上线** | [`design/api.md`](../specs/design/api.md)、[`contract-closure.md`](../specs/requirements/contract-closure.md) | **本文不冻结矩阵格** |
| **FR/SC / 步骤门禁** | [`domains/README.md`](../specs/requirements/domains/README.md)、[`flows/README.md`](../specs/requirements/flows/README.md) | Roadmap **未逐条枚举 ≠** 范围不包含 |
| **聚合契约索引 / 业务薄索引** | [`spec.md`](../specs/requirements/spec.md)、[`business/README.md`](../specs/requirements/business/README.md) | **`spec`** **不**取代 **`domains`** SSOT；**`business/`** **只**指路 |

**缺省**：若 **「优先级 / 编号混读」** → **上文「优先级与编号对照」**；若 **「Roadmap 里怎么没写 X？」** → **篇首「规格体系快照」（L1～L7）** → **「横切主题」表** → **[`requirements/README.md`](../specs/requirements/README.md)** / **[`spec.md`](../specs/requirements/spec.md)**。

---

## 端到端业务与项目闭环

**要不要写「端到端业务」？** **要。** 路线图若只有排期没有 **用户侧一条路**，会与 **`product.md` / `flows`** 脱节。本条同时承载两件事：

| 层 | 含义 | 读者问的是 |
|----|------|------------|
| **端到端业务（对客）** | 用户在 **Coobit + Telegram** 场景能否走完 **开通 → 资金/会员就绪 → 会话与执行 →（可选）确认后下单或理财 → 配额/订阅门禁 → 权益核销（`ENTITLEMENT_DEBIT`）→ 交易所站内 `/subaccount/billing`（`me/commerce`）→ 异常时说法可信 → 运营调参后下一轮会话仍一致** | 「客户完整用起来要经过什么？」 |
| **端到端项目闭环（对内）** | **规格 → 设计矩阵 → 实现 MR → 观测协查 → 收口 (`contract-closure`) → 再发布**；阶段 **A3** 要求 **`e2e`** 图上每一段 **可条文追溯** | 「团队怎样才算文档与契约对齐？」 |

**鸟瞰 SSOT**：仍以 **[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md)**（技术鸟瞰图；文首 **「架构语言」** → [`architecture`「与通用 Agent 栈之对照」](../specs/design/architecture.md)）与 **[`product/flows.md`](./flows.md)**（同人话七章）为 **业务叙事主轴**；**不做第二套 FR**，条文 **`domains/` / `flows/` / `design/`**。

| 入口 | 说明 |
|------|------|
| **[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md)** | **端到端闭环总览**（Mermaid：Telegram → 门禁 → 意图 → 交易四轨 / 理财 / 问答 / 自动化 → 类型 A → 执行 → 计费 → 交易所站内 Billing·H5 → 观测 → 运营控制台回流）；文首摘要 **「架构语言」** → [`architecture`「与通用 Agent 栈之对照」](../specs/design/architecture.md)；文末 **按主题权威流程表** 链向各 **`flows/`** 与域 SSOT |
| **[`product/flows.md`](./flows.md)** | 同人话 **七章**（开户 → 会话 → 卡片确认 → 计费与 Billing → 504 → 纯分析 → 自动化），与上表 **同窗**

### 端到端业务：用户与运行时主链（对客）

下列顺序 **不等于** 单次请求的代码调用栈，而是 **产品级「一条路走通」** 的约定叙事：

1. **开通与绑定**：**Telegram** 首触实例门禁 → **产品线 Deeplink → Agent 绑定页（`me/agent/*` · Agent 项目承载，不须交易所主站）**（**保存** **`POST .../bindings/trading-api`** · **§1.2 下限**（**UID≡`subUid`** · [**`FR-WEB06`**](../specs/requirements/domains/web/agent-onboarding.md) · **`TradingApiBindRejectCode`**）→ **通过后** **实例创建与绑定**）（[`activate-trading-agent.md`](../specs/requirements/flows/activate-trading-agent.md)、[`onboarding/overview.md`](../specs/requirements/domains/agent/onboarding/overview.md)；触点 UX [**`domains/web/agent-onboarding.md`**](../specs/requirements/domains/web/agent-onboarding.md)）→ **Telegram** 会话与用户映射（[`telegram-binding.md`](../specs/requirements/domains/agent/onboarding/telegram-binding.md)、[`telegram/overview.md`](../specs/requirements/domains/agent/telegram/overview.md) **§2.5 · 类型 A；总则 §2～§2.6**）。
2. **资金与会员**：子账户 **币币 USDT** 就绪、**母账号 VIP** 下限（[`billing.md` §2](../specs/requirements/domains/admin/billing-management/overview.md)、[`exchange-agent/overview.md`](../specs/requirements/domains/agent/exchange-agent/overview.md) **FR-T02/T03**；[`eligibility-runtime.md`](../specs/requirements/domains/admin/access-control/eligibility-runtime.md) **§1 · VIP**）。
3. **会话与编排**：单次 **`executionId`** 管线 — **门禁快照** → **意图 / `scenarioId`**（[`agent-orchestration/`](../specs/requirements/domains/agent/agent-orchestration/overview.md)、[`Runtime/overview.md`](../specs/requirements/Runtime/overview.md)）→ **工具链 / Prompt**（[`trade-assistance` §8](../specs/requirements/domains/agent/exchange-agent/trade-assistance.md)、[`prompts/`](../specs/requirements/prompts/README.md)）。
4. **写路径**：凡落 **交易所私有写**，**须** **Telegram 类型 A**（或同窗理财确认）**先于** API（[`ADR-001`](../specs/design/adr/001-telegram-confirm-before-coobit-write.md)、[`trade-via-agent.md`](../specs/requirements/flows/trade-via-agent.md)、[`wealth-via-agent.md`](../specs/requirements/flows/wealth-via-agent.md)）。
5. **计费与用户回看**：可计费执行终局 → **`consume-and-bill` S5 权益核销** → **交易所站内** **`/subaccount/billing`（`me/commerce`）**（[`consume-and-bill.md`](../specs/requirements/flows/consume-and-bill.md)、[`billing-management/overview` §0](../specs/requirements/domains/admin/billing-management/overview.md)、[**`web/agent-billing.md`**](../specs/requirements/domains/web/agent-billing.md)）。
6. **异常与信任**：**504 / UNKNOWN** → 查单与对账话术 — **不得假构成终态**（[`architecture.md`](../specs/design/architecture.md)、[`exchange-agent/boundaries.md`](../specs/requirements/domains/agent/exchange-agent/boundaries.md)、[`Runtime/recovery.md`](../specs/requirements/Runtime/recovery.md)）。
7. **只读与其它轨**：问答/检索（[`read-analyze-and-search-via-agent.md`](../specs/requirements/flows/read-analyze-and-search-via-agent.md)）、**自动化 / Pull**（[`automation-alerts.md`](../specs/requirements/flows/automation-alerts.md)）— **矩阵未冻结路径不得对外承诺闭环**（同窗 **`design/api`**、[`contract-closure.md`](../specs/requirements/contract-closure.md)）。
8. **运营回流**：观测与模块八检索 → **Prompt / Tool / Bot / 准入 / I02** 等配置变更 — **有效 `configVersion`** 再进入下一轮会话（[`observability/overview.md`](../specs/requirements/observability/overview.md)、[`admin-console/runtime-to-ui-mapping.md`](../specs/requirements/admin-console/runtime-to-ui-mapping.md)、[`management-console-v1-prd.md`](../specs/requirements/domains/admin/management-console-v1-prd.md)）。

### 端到端项目闭环：规格 — 交付 — 收口（对内）

| 环节 | 做什么 | 锚点 |
|------|--------|------|
| **方向与范围** | 产品做/不做、术语 | [`product.md`](../specs/requirements/product.md)、[`product/README.md`](./README.md) |
| **域与流程** | FR/SC、步骤级 `flows` | [`domains/README.md`](../specs/requirements/domains/README.md)、[`flows/README.md`](../specs/requirements/flows/README.md) |
| **设计与契约** | 子账户矩阵、`me/internal/admin` billing、ADR；**部署 / 拓扑**见 **`deployment`** | [`design/api.md`](../specs/design/api.md)、[`design/adr/`](../specs/design/adr/README.md)、[`deployment.md`](../specs/design/deployment.md) |
| **实现与会签** | P0/P1 CC、MR §9 六款、PRD §13 / 附录 A | [`contract-closure.md`](../specs/requirements/contract-closure.md)、[`closure-remaining.md`](../specs/requirements/closure-remaining.md)（**[§7](../specs/requirements/closure-remaining.md#cc-remaining-open-items)** · **[§7.5](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)**） |
| **升格与对外承诺** | 「契约冻结」叙事门槛 | [`contract-closure.md` §5.1](../specs/requirements/contract-closure.md)、[`spec.md`](../specs/requirements/spec.md) Status |

### 与下文 P0、阶段 A～D 的对应（不致第二套排期）

| 路线图块 | 在闭环中的位置 |
|----------|----------------|
| **P0-1** | 压实 **端到端业务** 主链 **1～2**（开通·资金）与 **`product`/`onboarding`/`billing`/`domains/web`** **叙事同窗** |
| **P0-2** | 任意闭环节点 **可查权威文档**（含 **`domains/web` §4→CC**） |
| **P0-3** | **规格—交付—收口** 表 **下半截**：矩阵、`contract-closure`、`design/api` |
| **阶段 A** | **对内闭环** 的设计/资金/权限底盘 + **矩阵** 与 PRD 附录对齐；**须完成 A3**（**`e2e`** **分段走读可追溯**） |
| **阶段 B** | **可读性与薄索引**，含 **主站/H5 FR-WEB** 与 **`src/Web`** 原型对照 |
| **阶段 C / D** | 能力切片与资产工程化 — **不改变** 上文 **端到端业务主链** **顺序 SSOT** |

---

### 当前最应该做的三件事（P0）

| 顺序 | 事项 | 为何优先 | 产出 / 完成判据 |
|------|------|----------|-----------------|
| **1** | **统一「产品事实」**（子账户、资金就绪、扣费主体、**后台（PRD · 八大模块）**与 **Telegram** 分工） | 避免 `onboarding` / `billing` / `exchange-agent` / `product` 叙事分叉，后续一切文档与实现都建在这之上 | [`product.md`](../specs/requirements/product.md) 与 [`onboarding/overview.md`](../specs/requirements/domains/agent/onboarding/overview.md)、[`billing` 概览](../specs/requirements/domains/admin/billing-management/overview.md)、[**`domains/web`**](../specs/requirements/domains/web/README.md) **同窗** 对 **开户 → 划转/余额 → 可用交易 Agent → H5 回看流水** 的描述 **无矛盾**；必要时在 [`flows/`](../specs/requirements/flows/) 补一条「资金就绪」主路径 |
| **2** | **补「域导航」** | **管理后台八大模块**（[`management-console-v1-prd.md`](../specs/requirements/domains/admin/management-console-v1-prd.md)）+ **Telegram** + **[`domains/web`](../specs/requirements/domains/web/README.md)**（触点）；新人应按 **[`domains/README`](../specs/requirements/domains/README.md)** 进 **业务域子目录**，避免平铺混杂 | **[`domains/README.md`](../specs/requirements/domains/README.md)**：**业务域一览**（含 **`web/`**）+ 「后台模块 ↔ 文档」映射 + 端到端链；横切 **观测 / Runtime / 指标** 见文内表（**非**虚假 `admin/*-management/` 目录）。主站/H5 **FR-WEB→CC** 映射见 [`web/overview §4`](../specs/requirements/domains/web/overview.md) |
| **3** | **跑通「可对外承诺」闭环** | 能力上限由矩阵决定，未收口则研发与对客都不可控 | 按 [`contract-closure.md`](../specs/requirements/contract-closure.md) 核对 [`design/api.md`](../specs/design/api.md)：**TBD 有 owner 与目标日期**；与 **[附录 A · 发布 / 对齐检查清单](../specs/requirements/domains/admin/management-console-v1-prd.md#mc-prd-appendix-a-release-checklist)**（若适用）一致 |

完成 **1～3** 后，团队已能 **稳定迭代** specs 与产品叙事。

**P0 自检（可选）**

- [ ] **P0-1**：[`product.md`](../specs/requirements/product.md)、[`onboarding/overview.md`](../specs/requirements/domains/agent/onboarding/overview.md)、[`billing` 概览](../specs/requirements/domains/admin/billing-management/overview.md)、[**`domains/web`**](../specs/requirements/domains/web/README.md) **同窗**：开户 → 资金就绪 → 回看流水 **叙事无矛盾**
- [ ] **P0-2**：端到端闭环节点 **均有可追溯条文**（含 [`web/overview` §4→CC](../specs/requirements/domains/web/overview.md)）
- [ ] **P0-3**：[`design/api.md`](../specs/design/api.md) **TBD** **均有 owner / 目标日期**；与 [`contract-closure.md`](../specs/requirements/contract-closure.md)、[**附录 A · 发布 / 对齐检查清单**](../specs/requirements/domains/admin/management-console-v1-prd.md#mc-prd-appendix-a-release-checklist)（若适用）**同窗**

---

### 分阶段节奏（建议）

#### 阶段 A — 对齐与冻结（约 1～2 个迭代周期，视会签速度）

- **A0（建议第一步）**：**管理后台 V1 IA 与技术对签走查** — 以 **[`management-console-v1-prd.md`](../specs/requirements/domains/admin/management-console-v1-prd.md)** 为 **产品与模块 SSOT**：核对 **八大模块边界**、`design/api` **矩阵对齐**、[ **`contract-closure.md`](../specs/requirements/contract-closure.md)** **CC-P0-04/CC-P0-05**。输出：**采纳 / 有条件通过** 纪要 + **须回填的附录 A（对签小节）或邻域条目**列表。
- **A1** 产品 / 后端 / 所内账户与计费 owner 会同：子账户、API 绑定、**主→子资金路径**（自动 / 手动 / 混合）、Token 扣减账户。
- **A2** **`design/api`** 矩阵与 ADR-001（确认闸门）无歧义；与 **`trade-via-agent`** 等流程交叉引用检查。
- **A3（端到端分段验收）**：按 **[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md)** 图 **及** 本文上文「**端到端业务：用户与运行时主链（对客）**」**逐段走读**：每一段须在 **`domains/`**、**`flows/`** 或 **`design/api`**（含 OpenAPI 登记表）中有 **可追溯条文**；**仍为 `TBD`/书面延期** 的能力须在纪要中 **显式登记**，**禁止**在路演材料中写成「已闭环」。产出：**走读纪要 + 缺口清单**（建议粘贴 [`closure-remaining` §7.1](../specs/requirements/closure-remaining.md#cc-remaining-gap-paste) **或** **互链** **[`closure-remaining` §7](../specs/requirements/closure-remaining.md#cc-remaining-open-items)** · **[§7.5 闭环路径](../specs/requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6 MR 执行清单](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)** / 工单）。**补充（2026-05）**：可与 **[`closure-completion-matrix`](../specs/requirements/closure-completion-matrix.md)** 状态列 **及** **[`Runtime/pipeline-walkthrough-checklist`](../specs/requirements/Runtime/pipeline-walkthrough-checklist.md)** **同窗走读**（**不**替代上文缺口粘贴义务）。

**出口**：

- 「资金与权限故事」能从 **`product` 一句说到 `flows` 一步」。
- **A3** 已完成：**`e2e`** 全图 **无「画了却无条文锚点」的静默段**；已知延期与 **`design/api` 矩阵备注** **同窗**。

**阶段 A 自检（评审 / MR 纪要建议勾选）**

- [ ] **A0**：八大模块走查与 **CC-P0-04/CC-P0-05** / 附录 A 所需回填 **已登记**
- [ ] **A1**：子账户、API、主→子资金、Token 扣减 **叙事同窗**
- [ ] **A2**：矩阵与 **ADR-001**、核心 **`flows`** **交叉引用已核对**
- [ ] **A3**：**`e2e-closed-loop`** **分段 → 条文映射**已产出（或等价：该文「按主题权威流程」表 **全覆盖走读**）；缺口 **已列入** 纪要或 **`closure-remaining`**

#### 阶段 B — 可导航与薄索引（低成本，可持续）

- **B1** **`domains/README`**（已具备）+ **[`standards/STANDARDS-ADOPTION.md`](../specs/requirements/standards/STANDARDS-ADOPTION.md)**：按 Wave D 给域 PR **`prd-standard §6` 自检**。
- **B2** **[`business/README.md`](../specs/requirements/business/README.md)**：**交付形态**（现有后台 **Agent 能力** + **Telegram**）**已载篇首**；本步 **核对索引完备**：索引须 **可点到** [`domains/README.md`](../specs/requirements/domains/README.md)、[**`telegram/overview.md` §2.5 · 类型 A；§2～§2.6**](../specs/requirements/domains/agent/telegram/overview.md)、[`management-console-v1-prd.md`](../specs/requirements/domains/admin/management-console-v1-prd.md)、[`domains/web/README.md`](../specs/requirements/domains/web/README.md)（或等价入口）；**缺则补链**，**不**再造第二套 SSOT 正文。
- **B2.1**（可选）**`domains/web` 触点**：[`domains/web/`](../specs/requirements/domains/web/README.md) 与 **`onboarding`/`billing`** **同窗**迭代时，核对 **`design/api`** **`user/onboarding.yaml`、`user/commerce-me.yaml`**（**绑定=产品线 `me/agent/*`**；**账单=`/subaccount/billing` · `me/commerce`**）；**`user/billing-me.yaml`** **仅 CC-P0-03 归档** — **本仓 `src/Web` 不实现**。工程原型 **`src/Web/README.md`**（**非**生产 SSOT）。
- **B3** 维护约定：**改 `domains` / `flows` 牵动叙事时**，同步 **`product/`** 对应篇或至少 [`README.md`](./README.md) 索引。

**出口**：新同学 **15 分钟内**能找到「**后台八大模块**（[`domains/README.md`](../specs/requirements/domains/README.md) 摘要）+ Bot + **`domains/web`（Agent 产品线绑定 + 交易所站内 Billing UX）**」各自权威文档。

**阶段 B 自检（可选）**

- [ ] **B1**：域 PR 对照 **[`STANDARDS-ADOPTION.md`](../specs/requirements/standards/STANDARDS-ADOPTION.md)**、**`prd-standard §6`**
- [ ] **B2**：[`business/README.md`](../specs/requirements/business/README.md) **交付形态与** **`domains/README`、`telegram`、`PRD`、`domains/web`** **导航链完整**（**只补缺链**，不重写交付叙事）
- [ ] **B3**：近迭代 **`domains` / `flows` 牵动叙事** **已同步** **`product/`**（篇或 [`README`](./README.md) 索引）

#### 阶段 C — 能力条款结构化（按需，不一步到位）

仅在 **`domains/agent/exchange-agent/overview.md`** 或其它单文件 **难以并行编辑** 时再拆：

- 将 **意图 / 参数补全 / 规划 / 执行 / 工具 / 风控** 在文内用大标题锚定清楚，或在 **`domains/agent/exchange-agent/`** 内 **增补切片 `.md`**（**不复制**计费/观测条款，只链）。
- **风控**：优先落在 **`exchange-agent`** / **`trade-assistance`** / **管理后台 PRD** / **`flows`**；全局 **`requirements/risk/`** 仅存 **横向索引或补充**，避免与域内条文 **双 SSOT**。

**出口**：研发排期可 **按章节 / 文件** 切分 ownership。

#### 阶段 D — 资产与工程化（有流水线再上）

- **`prompts/*.yaml`**：仅当 Git 即为下发源且 **[`domains/admin/prompt-management/overview.md`](../specs/requirements/domains/admin/prompt-management/overview.md)** 写明与后台的关系时再引入。
- **`tools/schemas`**：仍以 **`design/api`** 为主；避免与矩阵并行维护两份契约。

**出口**：无刻意的 **Git 与实际运行配置** 双源。

**阶段 C / D 自检（可选）**

- [ ] **C**：仅在 **`exchange-agent`**（或邻域）单文件 **难以并行编辑** 时再切片；全局 **`requirements/risk/`** **不作**与域内的 **双 SSOT**
- [ ] **D**：**`prompts`/YAML、`tools/schemas`** **未**与 **`design/api`** **并行维护两份契约**

---

### 例行节奏建议

| 频率 | 动作 |
|------|------|
| **每次合入 specs** | MR 勾选 **[`review-and-change-standard`](../specs/requirements/standards/review-and-change-standard.md) §2**；描述贴 **同文件 §3 变更摘要模板**；按需对照 **[`STANDARDS-ADOPTION`](../specs/requirements/standards/STANDARDS-ADOPTION.md)**；改 **`standards/`** 须写 [`Log.md`](../specs/requirements/standards/Log.md) |
| **大包 Runtime / Skill / Eval 批次合入后（可选）** | 本地 **`./scripts/closure-preflight.sh`**；状态列对照 **[`closure-completion-matrix`](../specs/requirements/closure-completion-matrix.md)**；PR **须绿** **[`.github/workflows/skill-contract-consistency.yml`](../.github/workflows/skill-contract-consistency.yml)**（与矩阵 **§4** 同窗） |
| **双周（或迭代末）** | 过一遍 **`contract-closure`**：`api` **TBD** 是否减少；是否与 **`product`** 范围矛盾 |
| **版本/路演前** | **`product.md`** + **`design/api`** + **`contract-closure`** **与** **`product/`** **同窗校对**；对外材料 **不超前于** 矩阵已冻结能力 |

---

### 横切主题（完整工程相关 · 路线图不单列 FR）

下列主题 **多为长期邻域**（准入、集成、风险、观测 …）。**2026‑05 批次「Runtime → PRS → Skill/Tool → Memory → MNRA → Eval → 收口」主轴** 已收束于篇首 **「规格体系快照」L1～L7**；**先查快照，再下表**。

| 主题 | 与端到端的关系 | 入口 |
|------|------------------|------|
| **准入 / VIP / 灰度 / 封禁 / KYC 镜像** | 同窗 **主链门禁**（[`exchange-agent` FR-T02](../specs/requirements/domains/agent/exchange-agent/overview.md)）与 **运营控制台** | [`access-control/overview.md`](../specs/requirements/domains/admin/access-control/overview.md)、[`eligibility-runtime.md`](../specs/requirements/domains/admin/access-control/eligibility-runtime.md) |
| **外部集成**（交所 · Telegram · LLM 等） | **网关 / 渠道上游契约**；Coobit 私网 HTTP **allowlist 摘要** **同窗** | [`integrations/README.md`](../specs/requirements/integrations/README.md)、[`integrations/exchange/agent-coobit-api-allowlist.md`](../specs/requirements/integrations/exchange/agent-coobit-api-allowlist.md) |
| **全局风险与 HITL** | **类型 A**、自动化边界同窗 **`risk`** | [`risk/README.md`](../specs/requirements/risk/README.md)、[`risk/acceptance.md`](../specs/requirements/risk/acceptance.md)、[`hitl-and-automation-matrix.md`](../specs/requirements/risk/hitl-and-automation-matrix.md) |
| **评测 / 指标** | **快照 L6**（**`pipeline-write-order` / `skill-contract` / `market-narrative` / `memory-runtime` / `clarify-telegram` / `idle-default-stale` / `resume-classifier-gate`** 等专卷）；**总索引** | [`evals/README.md`](../specs/requirements/evals/README.md)、[`evals/scenarios.md`](../specs/requirements/evals/scenarios.md)、[`metrics/README.md`](../specs/requirements/metrics/README.md) |
| **观测 / 审计 / 追踪** | **504 / UNKNOWN**、运营回流、查单协查同窗 **`observability`** | [`observability/overview.md`](../specs/requirements/observability/overview.md)、[`observability/tracing.md`](../specs/requirements/observability/tracing.md) |
| **OpenAPI 分包（YAML）** | PATH 仍以 **`design/api`** 矩阵登记为准；YAML 分包见 **`specs/openapi`** · **Hosted rollout** · **批次组件** **`skill-operation-spec` / `market-runtime` / `memory-runtime` schemas** **见快照 L3～L5** | [`openapi/README.md`](../specs/openapi/README.md)、[`openapi/HOSTED-ROLLOUT-CHECKLIST.md`](../specs/openapi/HOSTED-ROLLOUT-CHECKLIST.md)、[`design/api.md`](../specs/design/api.md) |
| **环境与部署拓扑** | 上线与分层 **非** `requirements` 正文职责 | [`deployment.md`](../specs/design/deployment.md)、[`architecture.md`](../specs/design/architecture.md) |
| **Runtime · PRS · Memory · MNRA（批次核心链）** | **篇首 L1～L2、L4～L5**；执行态 **`executionId`** 管线 **≠** **PRS 拼装** | [`Runtime/README.md`](../specs/requirements/Runtime/README.md)、[`prompt-runtime/README.md`](../specs/requirements/prompt-runtime/README.md) |
| **Skill / Tool / Publish · Admin 镜像** | **篇首 L3**；**`read_skill` · 「技能与工具」页 · GHA** | [`skill-specs/README.md`](../specs/requirements/skill-specs/README.md)、[`admin-console/runtime-to-ui-mapping.md`](../specs/requirements/admin-console/runtime-to-ui-mapping.md)、[`.github/workflows/skill-contract-consistency.yml`](../.github/workflows/skill-contract-consistency.yml) |
| **闭环完成度与 preflight（本仓）** | **快照 L7** · **一览表 + 工单/证据模板** · **与 `contract-closure` 分工** | [`closure-completion-matrix.md`](../specs/requirements/closure-completion-matrix.md)、[`closure-internal-sprint.md`](../specs/requirements/closure-internal-sprint.md)、[`closure-work-item-templates.md`](../specs/requirements/closure-work-item-templates.md)、[`closure-staging-evidence-log.md`](../specs/requirements/closure-staging-evidence-log.md)；仓库根 **`scripts/closure-preflight.sh`** |
| **Agent 目标与缺口自检** | **能力 / Memory / Prompt 与 Runtime 同窗** — **不写第二套验收** | [`domains/agent/goals/README.md`](../specs/requirements/domains/agent/goals/README.md) |
| **小团队日常管控** | **Optional** 相对 **`contract-closure` 全文** | [`LITE-MODE.md`](../specs/requirements/LITE-MODE.md)、[`product/release-notes.md`](./release-notes.md) |
| **需求全覆盖索引** | **Roadmap 总导航** — **链向全库 `specs/requirements`** | 本文 **[§需求全覆盖索引](#req-full-index)** |

---

### 刻意不做（防范围膨胀）

- **不做**再行「无命名约定」地把需求堆进 **`domains/` 根目录**（新 FR/SC **须**落入 **`domains/<业务域>/`**）；不大搬 **`design/`**，除非 **`design`** owner 立项。
- **不恢复** **`mvp/v1/v2`** 目录；范围变更走 **`product.md` + domains**。
- **不在 `requirements`** 堆实现细节、排期、技术栈选型（归 **`design/`** 或实现仓库）。
- **不写进本仓 specs / 路线图正文**：**客服 SLA / 工单流水线**、**地域合规细则（所内文书 SSOT）**、**人力甘特与 capacity** —— 归 **PM / 所内工单**；如需对齐，**外链或工单编号** 引用即可。

---

### 与 [`roadmap/`](./roadmap/) 子目录、`milestones` 的关系

- 按季/主题的 **路线图正文**：在 [`roadmap/`](./roadmap/) 追加 `YYYY-Qx.md` 等；**粒度更细的执行清单**可走项目管理工具，本文只做 **规格侧节奏**。
- [`milestones.md`](./milestones.md)：阶段叙事入口，应与本文 **无二义冲突**。

*维护：产品与规格 owner；修订时请注明日期。（**2026-05-11**：对齐 **`domains/web`**、**FR-WEB→CC** [`overview §4`](../specs/requirements/domains/web/overview.md)；**增补** 「**端到端业务与项目闭环**」、`flow/e2e-closed-loop`、`milestones`、`roadmap/README`；阶段 **A · A3**。章名显式区分 **对客业务** 与 **对内收口**。**后续修订**：PRD **八大模块** 用词统一；增 **横切主题** 表（access-control / integrations / risk / evals / deployment / LITE）。**同日**：增 **「Roadmap 读者分工」**；**B2** 改为 **`business/README` 索引核对**；**刻意不做** 扩至客服/合规文书/人力甘特；路演行前 **三件套同窗**。**同日二次**：篇首 **TL;DR**；**读者分工** 增 **`spec`/`business`** 行；**P0·B～D 可选自检**；横切增 **observability**、**OpenAPI 分包**。**2026-05-26**：**计费商业模型（轨 B / 权益核销）** — `commerce-model`、OpenAPI 轨 B、`productionRuntime` S2/S5、`design/api` 登记表；篇首 TL;DR 增 **收口执行一览**、**规格体系快照 L1～L7**；横切 **Runtime / Skill / 闭环矩阵** 等。**2026-05-27**：**计费 + Admin/Web IA 对齐原型**（reconciliation §0）、**叙事清扫**（移除 `me/billing` 原型/BFF）、**Prompt 治理 IA + 16 包正文**、**执行/实例/工具登记 IA**；`e2e` HTML 账单节点；**B2.1** 改 **`commerce-me` 主链**；[`release-notes`](./release-notes.md) **同日三节**。**2026-05-27 末**：**`src/Web` / `src/admin` 构建绿灯**。**2026-05-27 续**：新增 **[「需求全覆盖索引」](#req-full-index)**（**A～M** · 链向 `specs/requirements` 全库 + 原型）。**2026-05-27 澄清+记忆**：**`clarify-session` v1.5** · **`memory-runtime` §14.6 v1.8**（**idle/TTL 先达 stale · Resume 置信阈值**）· **索引补链** **L4/L6/C/I/J** · [`release-notes`](./release-notes.md) **新节**。）*
