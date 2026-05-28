# 交易所管理后台 · AI Trading Agent（Demo）

**非生产 · 原型演示**；规格与交互对齐见 `specs/requirements/skill-specs/requirements-closure.md`。**不**承诺生产 BFF/DB（所内见 `MR-B-BFF-IMPLEMENTATION.md`）。

**与本仓库边界**：真机 Runtime / Gateway / 编排服务的 **开发与部署不在本仓库**；`src/admin`（含 `src/admin/src/productionRuntime` 下可对签小函数）仅服务 **控制台 Demo + 契约对签草稿**，量产实现以 **`specs/`**、`specs/openapi/` **及 MR 文档为准**，由专门开发团队落库上线。

- **运营 IA（菜单 / 页面 ID / Runtime 映射）SSOT**：[`specs/requirements/admin-console/README.md`](../../specs/requirements/admin-console/README.md) · **模块/功能/页面命名** [`naming-alignment.md`](../../specs/requirements/admin-console/naming-alignment.md) · 路由全表 [`demo-routing.md`](../../specs/requirements/admin-console/demo-routing.md)
- **PRD 八大模块与 FR 归因**：[`management-console-v1-prd.md`](../../specs/requirements/domains/admin/management-console-v1-prd.md) **§3**；与 IA 对照见 [`prd-ia-alignment.md`](../../specs/requirements/admin-console/prd-ia-alignment.md)

**关单余量（MR 首节）**：[`closure-remaining` §0](../../specs/requirements/closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../specs/requirements/closure-remaining.md#cc-exec-solve-path) · [**§6.4 问题→动作**](../../specs/requirements/closure-remaining.md#cc-problem-to-action)；**主契约** [`contract-closure`](../../specs/requirements/contract-closure.md)

侧栏分组与 **Sitemap** 一致；默认落地 **`/runtime/executions`**（P0）。

## 本地运行

```bash
cd src/admin
npm install
npm run dev
```

默认 <http://localhost:5174>。

**执行记录列表 · 可选接 BFF**：在 `.env.development` 中配置 `VITE_API_BASE_URL`（运营 BFF 根 URL，无尾斜杠）且 `VITE_USE_OBSERVABILITY_API=true` 时，`/runtime/executions` 将调用 OpenAPI **`GET /api/v1/admin/observability/executions`**（`listObservabilityExecutions`）；未开启时继续使用 `src/data/mock.ts`。合并检索框 → API：`u-*`→`userId`、**纯数字 10～19 位**→`executionId`、点分 `a.b.c`→`scenarioId`；显式 `?scenario=` 覆盖 `scenarioId`；支持 **`nextCursor` 加载更多**（`executionId` 规则见 `naming-standard.md` §1）。**详见** [`.env.example`](.env.example)。

## Demo 路由 ↔ 页面 ID ↔ 规格

| 路由 | 页面 ID（见 admin-console） | 主要规格 / 说明 |
|------|------------------------------|-----------------|
| `/runtime/executions` | `runtime.executions` | 对齐 [`runtime-executions-reconciliation`](../../specs/requirements/domains/admin/observability-management/admin-console-runtime-executions-reconciliation.md) §0 |
| `/runtime/executions/:executionId` | `runtime.execution-detail` | **总览**：场景 Skill Scope + Prompt 追溯 + 技能规范 + **Canonical Inspector（演示）**；**时间线** `FR-MC801`；`?tab=` |
| `/runtime/tasks` · `/runtime/events` | （重定向） | → `/runtime/executions`（MVP 不拆独立页；见 `demo-routing.md`） |
| `/agents/config` · `/agents/config/:id` · `/agents/templates` · `/agents/templates/:id` | （重定向） | → **`/agents/instances`**（单租户 Demo；见 `demo-routing.md`、`agent-management/config.md` §1） |
| `/agents/instances` | `ai.agents-instances` | 对齐 [`agent-instances-reconciliation`](../../specs/requirements/domains/admin/agent-management/admin-console-agent-instances-reconciliation.md) §0 |
| `/agents/instances/:id` | `ai.agents-instances` | PRD **一** I03 · 可从列表进入 |
| `/prompts/strategy` | `ai.prompt-strategy` | 对齐 [`prompt-strategy-reconciliation`](../../specs/requirements/domains/admin/prompt-management/admin-console-prompt-strategy-reconciliation.md) §0 |
| `/prompts/safety` | `ai.prompt-safety` | 安全防护（SAFETY 类 Prompt） |
| `/prompts/system` · `/prompts/scenarios` | （重定向） | → `/prompts/strategy`（旧书签） |
| `/ai/tool-registry` | `ai.tool-registry` | **技能与工具** — 对齐 [`admin-console-tool-registry-reconciliation.md`](../../specs/requirements/domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) §0 |
| `/ai/skill-specs` · `/tools/registry` · `/tools` · `/ai/tool-policies` | （重定向） | → **`/ai/tool-registry`**（旧书签；规范已并入 A 类 Tab） |
| `/ai/runtime-orchestration` | `ai.runtime-orchestration` | 场景目录 + **Skill Scope Viewer**（按 `scenarioId` 只读 · `skillScopeForScenario.ts`）+ 执行策略 |
| `/ai-settings` | `ai.settings` | **模型配置**（Demo）：**厂商与模型**（展开维护；厂商表单合并底座与名称）+ **使用策略**（模型下拉引用台账启用模型）；不落库 · 规格见 `specs/requirements/domains/admin/ai-settings/overview.md` §1.1 |
| `/ai/confirmation-rules` | `ai.confirmation-rules` | 占位 · `risk/hitl-and-automation-matrix.md` |
| `/access` | `access.overview` | PRD **六** · `access-control/…`；旧 `/access/eligibility` → `/access`（见 `demo-routing.md`） |
| `/billing/overview` | `billing.overview` | **计费总览**：运行健康 + 商业运营入口（MC501/506/512） |
| `/billing/operations` | `billing.operations` | **商业运营**：Tab 订阅套餐 / 资源管理 / 计费规则 / **订阅订单**（`CommerceOrderDetailDrawer` · §3.2.1）/ 用户消耗 — [`billing-pages-reconciliation` §3.2.1](../../specs/requirements/domains/admin/billing-management/admin-console-billing-pages-reconciliation.md) |
| `/billing/ledger` | `billing.ledger` | **执行核销追踪**（MC503/504） |
| `/billing/pricing` · `/billing/commerce` · 等 | （重定向） | → `/billing/overview` 或 `operations?tab=…` |
| `/billing` | （重定向） | → `/billing/overview` |
| `/system/channels`、`/system/channels/:channelId` | `sys.channels` | **渠道管理**：列表 + 分渠道详情（Demo：IM 渠道如 Telegram）；旧 `/integrations/*` 重定向见 `demo-routing.md` |
| `/system/contract-closure` | （重定向） | → `/runtime/executions`（**无**索引页；契约收口见 [`contract-closure.md`](../../specs/requirements/contract-closure.md)） |
| `/observability/runtime-health` | `obs.health` | **重定向** → `/observability`（**无** 页内 SLI 看板） |
| `/observability` | `obs.traces-logs` | 对齐 [`observability-reconciliation`](../../specs/requirements/domains/admin/observability-management/admin-console-observability-reconciliation.md) §0 |
| `/observability/alerts` | `obs.alerts` | **重定向** → `/observability` |
| `/trading-config` | `sys.trading-config` | PRD **七** · `trading-agent-config/keys.md` |
| `/system/feature-flags` · `/system/global-gate` | （重定向） | → `/runtime/executions`（已移除独立功能开关 / 总闸页） |

## 行为说明

### 技能登记页 · Demo 与需求分工（必读）

**文档 SSOT**：[`admin-console-tool-registry-reconciliation.md`](../../specs/requirements/domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) **§0～§2**（与 [`page-specs` · `ai.tool-registry`](../../specs/requirements/admin-console/page-specs.md) 同窗）。

本预览 **不提供「新建技能」**；A 类 **14** 条来自 [`skillRegistryCatalog.ts`](src/pages/tools/skillRegistryCatalog.ts)（同窗 [`manifest.yaml`](../../specs/requirements/skill-specs/manifest.yaml)）。**运营可用性** 仅 **启用/停用**（`toolRegistryStorage` · **SC-TM-16**）。

| 块 | 实现 |
|----|------|
| **统计** | 可下单已启用 x/14 · 查询+外部已启用 · 变更记录条数 |
| **Tab** | 可帮用户下单（含搜索）· 查询类 · 外部检索 · 变更记录 |
| **抽屉** | 概览 · 对话与下单要求（六分节 + 可选 Git 原文折叠） |
| **无** | Runtime 发布 UI · 页顶 x/11 · **说明就绪**（在运行场景页） |

**SC-TM-17～18** → 所内 MR-B；Vitest `skillPublish/*` 供契约对签，**不对** 运营演示。

**Prompt 治理（Demo UI）**：[`mockPromptData.ts`](src/data/mockPromptData.ts) + [`promptBodyTemplates.ts`](src/data/promptBodyTemplates.ts)（**16** 包：SYSTEM 含 `pp-system-core` / `pp-runtime-clarify` / `pp-runtime-output-contract`；写路径 **TRADING** 按 `scenarioId` 拆；读侧 **仅** `pp-analysis-core` + [`ANALYSIS_CAPABILITY_REGISTRY`](src/data/mockPromptDataCatalog.ts)）；正文统一六段结构，不写 Gateway/Billing/API。  
**可选 BFF**（`VITE_USE_PROMPT_API=true` + `VITE_API_BASE_URL`）：列表走 `/api/v1/admin/prompt-packs`；**远端未返回的治理包** 由 mock **补齐**（`remote+mock-ssot` · 见 [`mergeGovernancePromptPacks.ts`](src/pages/prompt/mergeGovernancePromptPacks.ts)）；接口失败则 **整表回退** mock。

**Commerce 运营 API**（`VITE_USE_BILLING_COMMERCE_API=true` + `VITE_API_BASE_URL`）：商业运营与总览 **MC512** 摘要走 `GET /api/v1/admin/billing/commerce/*`；`npm run dev` 内置 BFF mock（同窗 [`billing-admin.yaml`](../../specs/openapi/admin/billing-admin.yaml)）；失败回退 mock。客户端见 [`billingCommerceClient.ts`](src/api/billingCommerceClient.ts)。**FR-MC509** 目录 **PATCH + 双签抽屉**（[`CommerceCapabilityCatalogEditor.tsx`](src/pages/billing/CommerceCapabilityCatalogEditor.tsx) · **If-Match/409**）。

**Ledger traces API**（`VITE_USE_BILLING_LEDGER_API=true`）：`/billing/ledger` 走 `GET /api/v1/admin/billing/traces`；客户端 [`billingLedgerClient.ts`](src/api/billingLedgerClient.ts)。

**MR-BILL-B1/B2 本地探针**：Dev BFF 提供 `GET/POST /api/v1/internal/billing/entitlements/*`；走读见 [`staging-mr-bill-runbook.md`](../../specs/requirements/domains/admin/billing-management/staging-mr-bill-runbook.md)。**一键脚本**（Vite 已启动）：`ORIGIN=http://localhost:5173 ../../scripts/staging-mr-bill-probe.sh`。

- **`GLOBAL_AGENT_SWITCH` / G01**：`mock.ts` · `globalGateConfigKeys`（Demo 默认 **`false`** 可验 OFF 横幅）；**实例列表 / 详情** 页顶 **Alert** + 「当日不再显示（UTC）」；列表 **Start / Resume** 快捷入口与详情 **启动 / 恢复** 在 OFF 时禁用；**无**独立总闸运营页（`/system/global-gate` 仍重定向）。批量 Pause/Stop（R06）在 OFF 时仍可用。
- **Secret**：绑定区不展示真实密钥，与 specs 一致。
- **ADR-001**：用户「类型 A」确认在 Telegram；本控制台不重复确认流（文案可在产品文档中强调）。

## 构建

```bash
npm run build
```

## 测试（D-5 深链纯函数）

```bash
npm test
```

产出 `dist/`，可挂静态服务器做评审演示。
