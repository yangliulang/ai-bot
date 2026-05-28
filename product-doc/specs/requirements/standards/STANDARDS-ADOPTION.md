# 标准落地 · 存量对齐（PRD / 业务流程 / 交互）

本文说明 **如何把 `standards/` 三本规范与评审规范用起来**，并把现有 **`domains/`、`flows/`、`domains/agent/telegram/`** 与 **`Runtime/`**（**主链** [`overview.md`](../Runtime/overview.md) **§1 分卷**；短入口 [`README.md`](../Runtime/README.md)）分波对齐。**不复制**条文全文；自检项以 **[`prd-standard.md`](prd-standard.md) §6**、**[`business-process-standard.md`](business-process-standard.md) §6**、**[`interaction-flow-standard.md`](interaction-flow-standard.md) §8** 为准。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 1. 每次改需求的固定动作（用起来）

| 步骤 | 动作 |
|------|------|
| 1 | MR 描述粘贴 **[`review-and-change-standard.md`](review-and-change-standard.md) §3 变更摘要模板** |
| 2 | 勾选 **[`review-and-change-standard.md`](review-and-change-standard.md) §2** 中与本次范围相关的条目 |
| 3 | **`domains`**：改动后对照 **`prd-standard.md` §6** PRD 质量门禁 |
| 4 | **`flows`**：改动后对照 **`business-process-standard.md` §6** |
| 5 | **`Runtime/`**（若动）：**叙事与域 FR 不打架**；新 FR/SC **仍须**落在 **`domains/<业务域>/`**，除非你方已单独约定 **横切 REQ ID**（见 [`Runtime/overview.md`](../Runtime/overview.md)、[`Runtime/README.md`](../Runtime/README.md)） |
| 6 | **`domains/agent/telegram/overview.md`**：改动后对照 **`interaction-flow-standard.md` §8** |
| 7 | 若动 **`design/api`** 矩阵：执行 **[`contract-closure.md`](../contract-closure.md) §4** MR 核对 |
| 8 | **改任一 `standards/` 条文**：**必须**在同一 MR 追加 **[`Log.md`](Log.md)** 履历 |

---

## 2. 对齐批次（ Waves ）

以下 **≠ 优先级排序实现**，而是 **文档形态对齐顺序**建议；勾选进度由团队在 MR 或看板自建。

### Wave F — **`flows/`**（已为示范或需补同款「文首摘要 + `S{n}`」）

| 文件 | 目标形态 | 状态 |
|------|-----------|------|
| [`flows/activate-trading-agent.md`](../flows/activate-trading-agent.md) | **`business-process` §2 文首摘要表**；主路径 **`S1`～`Sn`**（§3 模板） | **已对示范** |
| [`flows/consume-and-bill.md`](../flows/consume-and-bill.md) | 同上 | **已对示范** |
| [`flows/trade-via-agent.md`](../flows/trade-via-agent.md) | **文首摘要表**；概要 **`S1`～`S10`**；挂单类 **扩展 `S11`～`S17`**；合约/全仓 **专节「第一步～第八步」** **为子路径号**（文内声明 **≠ `S11`～`S17`**） | **已对示范** |
| [`flows/read-analyze-and-search-via-agent.md`](../flows/read-analyze-and-search-via-agent.md) | **文首摘要表**；主路径 **`S1`～`S7`**（§3 模板） | **已对示范** |
| [`flows/wealth-via-agent.md`](../flows/wealth-via-agent.md) | **文首摘要表**；理财主链 **`S1`～`S8`**（门禁段 + 分段标题） | **已对示范** |
| [`flows/automation-alerts.md`](../flows/automation-alerts.md) | **文首摘要表**；主路径 **`S1`～`S7`**（§3 模板） | **已对示范** |

### Wave D — **`domains/`**（按域 PR **`prd-standard.md` §6 + §3 章节结构补缺）

| 域文件 | 建议 |
|--------|------|
| [`management-console-v1-prd.md`](../domains/admin/management-console-v1-prd.md) | **`roadmap.md` A0**；八模块 IA 与 **附录 A（对签）**；链 **contract-closure** |
| [`management-console-v1-prd.md`](../domains/admin/management-console-v1-prd.md) | 文首§1～§13 / 附录 **A**；结案 **§11 D-x**；**§13** 逐项勾选可追溯 |
| [`billing.md`](../domains/admin/billing-management/overview.md) | 长文：增补 **§0 目录**（若尚无）；FR 条目核对 **§4 触发/行为/边界** |
| [`overview.md`](../domains/agent/exchange-agent/overview.md) | 同上；大范围改 FR 时必须 **flows + telegram** 联评 |
| [`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md)、[`agent-orchestration/overview.md`](../domains/agent/agent-orchestration/overview.md) | **`toolId`/`scenarioId`** 与 **`design/api`、`contract-closure`** 单行可追溯 |
| [`onboarding/overview.md`](../domains/agent/onboarding/overview.md) | 与 **`activate-trading-agent`**、`domains/agent/telegram` Deeplink **无冲突** |
| [`observability.md`](../observability/overview.md)、[`agent-context/overview.md`](../domains/agent/agent-context/overview.md) | 权威边界表穷尽 **计费/会话/编排**依赖 |
| [`overview.md`](../domains/admin/prompt-management/overview.md) | **草案结案** ↔ **CC-P1-04** |

### Wave CH — **`domains/agent/telegram/`**

| 文件 | 目标 |
|------|------|
| [`overview.md`](../domains/agent/telegram/overview.md) | 文末「自检 · 用起来」链 **`interaction-flow-standard` §8**；卡片变更 **必填 § 锚点** |
| [`README.md`](../domains/agent/telegram/README.md) | Billing / Deeplink **与 `billing`、`overview.md`** 单行 SSOT |

### Wave R — **`Runtime/`**（横切运行时叙事，**不替代**域 SSOT）

| 文件 | 目标 |
|------|------|
| [`Runtime/overview.md`](../Runtime/overview.md)、[`README.md`](../Runtime/README.md) | **主链**：`overview` **总览 · §1 分卷**；**`README`** **短入口**；新增分卷 **须**脚注 **`domains` FR/§** |
| [`Runtime/boundaries.md`](../Runtime/boundaries.md)、[`execution.md`](../Runtime/execution.md)、[`sessions.md`](../Runtime/sessions.md)、[`runtime-state.md`](../Runtime/runtime-state.md)、[`context-management.md`](../Runtime/context-management.md)、[`persistence.md`](../Runtime/persistence.md)、[`freeze-policy.md`](../Runtime/freeze-policy.md)、[`locking.md`](../Runtime/locking.md)、[`recovery.md`](../Runtime/recovery.md)、[`event-storage.md`](../Runtime/event-storage.md) | **按主题分卷**；与 **Wave D** 域正文 **无 FR 冲突** |

## 3. 拆分 vs 增补（避免过度拆）

按 **[`prd-standard.md`](prd-standard.md) §1 拆分原则**：

| 情形 | 动作 |
|------|------|
| 步骤跨 **≥2 系统或多域**，且常被引用 | 条文在 **`domains`**，叙事链在 **`flows`**（已实现） |
| 仅会话形态与字段 | **`domains/agent/telegram/`**；**不写第二套字段表进 `flows`** |
| **运行时横切叙事**（编排/上下文/会话链，多域串联） | **`Runtime/`** + **`domains` FR/§** 脚注；实现细节只在 **`design/`** |
| **`exchange-agent/overview.md`（或任一 `exchange-agent/*.md`）超长** | **优先**：文内目录 + FR 锚点；**再**考虑在 **`domains/agent/exchange-agent/`** 内增删切片或 **`Runtime/`** 叙事（单次 MR **只拆一章**并联更新 `spec.md` / [`domains/README`](../domains/README.md)） |

---

## 4. 完成定义（本条文档的 Done）

- Wave F：**七条 `flows`** 均已具备 **`business-process` §2 文首摘要表**  
- Wave F：**主线两条**（开通、扣费）与 **`trade-via-agent` 概要 + 七段扩展（`S1`～`S17`）** 主路径已为 **`S{n}`** 或 **显式 `S*`**；**其余** **flows** **见** Wave F 表状态列  
- 每个打开的域 PR：**§2 MR 勾选 + §3 摘要 + `prd-standard` §6 自检（可贴在 MR）**

---

## 5. 与仓库其它入口的关系

| 文档 | 关系 |
|------|------|
| [`../README.md`](../README.md) | FEATURE_DIR **布局一览** |
| [`../domains/README.md`](../domains/README.md) | 后台模块映射、**admin-backend-coverage-checklist** |
| [`../../../product/roadmap.md`](../../../product/roadmap.md) | P0～阶段 A：**先事实、后收口**；本文 **负责「书写与 MR 的形态」** |
| [`../contract-closure.md`](../contract-closure.md) | **可对签**；与标准 **叠加** |

*维护：规格 owner；大改 `standards/` 时同步更新本文 Wave 表状态列（或改由看板管理状态）。*
