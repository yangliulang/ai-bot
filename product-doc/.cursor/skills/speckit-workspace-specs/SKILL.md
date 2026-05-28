---
name: speckit-workspace-specs
description: >-
  Aligns work with this repo’s Speckit FEATURE_DIR and specs layout (requirements vs design,
  product SSOT, domains/flows/agent-telegram, contract closure) for a crypto exchange AI product—
  knowing where exchange-agent, risk, tools schemas, OpenAPI exchange packs, and admin-console IA live.
  Use when editing or reviewing specs/requirements, running Speckit, mentioning FEATURE_DIR,
  product.md, domains/, contract-closure, or asking whether docs match repository conventions.
---

# Speckit 与本仓库 specs 协作

## 先读这些（按顺序）

1. [`specs/README.md`](../../../specs/README.md) — 需求与设计的目录职责、事实源关系。
2. [`.specify/memory/workspace-layout.md`](../../../.specify/memory/workspace-layout.md) — **路径约定**（FEATURE_DIR、`product.md`、`domains/`、`flows/`、`Runtime/`、`domains/agent/telegram/`、**PRS**（`prompt-runtime` · `prompts` · MNRA · `skill-specs`）、**`business`/`metrics`/`evals`/`tools` 索引**、`design/`）。
3. [`.specify/feature.json`](../../../.specify/feature.json) — **`feature_directory`** 当前为 `specs/requirements`。
4. 人类可读叙事（非契约 SSOT）：[`product/README.md`](../../../product/README.md)；冲突以 `specs/requirements` 与 `specs/design` 正文为准并回写 `product/`。
5. PRD / 交互 / 业务流程书写规范：[`specs/requirements/standards/README.md`](../../../specs/requirements/standards/README.md)；MR 勾选与变更摘要见 [`review-and-change-standard.md`](../../../specs/requirements/standards/review-and-change-standard.md)；**改 `standards/` 须更新 [`Log.md`](../../../specs/requirements/standards/Log.md)**。

## 路径角色（必须遵守）

| 角色 | 路径 |
|------|------|
| Speckit / 特性根目录 | `specs/requirements/` |
| 聚合索引（兼容 `spec.md`） | `specs/requirements/spec.md` → 指向 `product.md` 与各域 |
| 产品方向 SSOT | `specs/requirements/product.md` |
| 域需求 | `specs/requirements/domains/<业务域>/`（[`domains/README`](../../../specs/requirements/domains/README.md)） |
| 后台 IA（Sitemap、Runtime→UI） | **`specs/requirements/admin-console/`** — [`README`](../../../specs/requirements/admin-console/README.md)；**不**替代 `domains/admin` FR |
| 主流程 | `specs/requirements/flows/` |
| **Runtime（横切运行时需求）** | **`specs/requirements/Runtime/`** — **主链** **[`overview.md`](../../../specs/requirements/Runtime/overview.md)** **§1**；短入口 **[`README.md`](../../../specs/requirements/Runtime/README.md)** · **不替代**域 FR/SC |
| 渠道 | `specs/requirements/domains/agent/telegram/` |
| 业务索引 | `specs/requirements/business/`（链向 `product/` 与各域） |
| 指标体系索引 | `specs/requirements/metrics/` |
| **评测素材索引** | [`specs/requirements/evals/README.md`](../../../specs/requirements/evals/README.md) — 与 `metrics/` **分工**，**不**替代域 FR/SC |
| 全局风险横切 | [`specs/requirements/risk/README.md`](../../../specs/requirements/risk/README.md) — **分层 + 分卷**；域内边界 SSOT：**[`exchange-agent/boundaries`](../../../specs/requirements/domains/agent/exchange-agent/boundaries.md)** |
| **PRS**（单一体系名） | [`specs/requirements/prompt-runtime/README.md`](../../../specs/requirements/prompt-runtime/README.md) — **总入口** + **[§4 改什么去哪](../../../specs/requirements/prompt-runtime/README.md#prs-where-to-edit)**；L1 `prompts/` · 读侧 MNRA `market-narrative-runtime/` · L0 `skill-specs/` · Publish `prompt-management` · 拼装 `runtime-injection`（**≠** `Runtime/` 执行态） |
| Tools 索引 | `specs/requirements/tools/`（契约 SSOT：`design/api.md`） |
| 外部集成（交所 / Telegram / LLM / 通知） | **`specs/requirements/integrations/`** — [`README`](../../../specs/requirements/integrations/README.md) |
| 契约收口索引 | `specs/requirements/contract-closure.md` |
| 设计（接口、架构、ADR） | `specs/design/` — **不与需求混写** |

临时切换特性目录时可设环境变量 **`SPECIFY_FEATURE_DIRECTORY`**（见 workspace-layout 说明）。

## 行业相关规格落点（加密货币 / CEX / Web3 邻域）

编辑或评审时优先识别 **事实源**，避免把 **链上叙事** 写进 **所内 API** 条文（除非 `integrations`/`design` 已定义跨链场景）：

| 主题 | 主要落点 |
|------|-----------|
| 交易与账户能力、工具矩阵 | **[`domains/agent/exchange-agent/`](../../../specs/requirements/domains/agent/exchange-agent/overview.md)**、**[`tools/`](../../../specs/requirements/tools/README.md)**（JSON schema）、**[`specs/openapi/exchange/`](../../../specs/openapi/exchange/coobit-spot.yaml)** 等分包 |
| 风控、确认、Kill switch、合规 | **[`risk/`](../../../specs/requirements/risk/README.md)**、**[`hitl-and-automation-matrix`](../../../specs/requirements/risk/hitl-and-automation-matrix.md)** |
| 运行时、幂等、对账、未知态 | **[`Runtime/`](../../../specs/requirements/Runtime/overview.md)** |
| 计费与用户 Billing FR | **[`domains/admin/billing-management/`](../../../specs/requirements/domains/admin/billing-management/overview.md)** |
| 外部所、Bot、LLM 边界 | **[`integrations/`](../../../specs/requirements/integrations/README.md)** |
| 交易向评测素材 | **[`evals/`](../../../specs/requirements/evals/README.md)**（不替代域 FR/SC） |
| 管理后台 IA（非 domains SSOT） | **[`admin-console/`](../../../specs/requirements/admin-console/README.md)** |

## 执行任务时的习惯

- **改需求条目**：落在对应 `domains/<业务域>/`、`flows/`、`domains/agent/telegram/`；**`Runtime/`** 仅存 **横切叙事**（分卷见 **`Runtime/overview.md` §1**），新 FR/SC **默认仍归** **`domains/<业务域>/`**；跨域引用保持与 `spec.md` / `product.md` 索引一致。若仅增导航，可更新 `business/`、`metrics/`、**`evals/`**、`prompts/`、`tools/`、**`Runtime/overview`/`README`** 的链向，**不**替代域/设计正文。
- **改「能否对外承诺」闭环**：同步核对 `contract-closure.md`、`design/api.md` 矩阵与相关域 FR/SC。
- **工具仍解析旧路径 `10-domains/...`**：以 workspace-layout 为准并迁移工具配置（与 `.cursor/rules/specify-rules.mdc` 一致）。

## 不要做

- 把实现细节、技术栈、排期写进 `specs/requirements/`（应落在 `specs/design/` 或实现仓库）。
- 在 FEATURE_DIR 外另造一套「规格 SSOT」而不改 `product.md` / `spec.md` 索引。

## 完整域列表（README 简版可能不全）

以磁盘与 **`spec.md`** 为准，当前域包括但不限于：**[`management-console-v1-prd.md`](../../../specs/requirements/domains/admin/management-console-v1-prd.md)**（后台 V1）、`billing`、**`exchange-agent`**（分卷 **`trade-assistance`** 承继原 **`trading-skills`**）、`observability`、**`domains/agent/onboarding`**、**[`domains/web/`](../../../specs/requirements/domains/web/README.md)**（主站/H5 **开通 · Agent 账单** UX）、`prompt-management`、`agent-orchestration`、`agent-context`。
