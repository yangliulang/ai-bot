# Milestones（里程碑叙事）

本篇描述 **给人的沟通与对齐用故事线**，**不承载** FR/SC。验收与门禁以 **[`specs/requirements/product.md`](../specs/requirements/product.md)**、各 **`domains/`**（含 **`domains/web/`**：**Agent 绑定 onboarding** UX **与** **交易所站内账单** UX）、**`flows/`**、**`domains/agent/telegram/`** **（条文宿主：**[**`overview.md` §2.5 · 类型 A、§2～§2.6**](../specs/requirements/domains/agent/telegram/overview.md)**）**、**[`contract-closure.md`](../specs/requirements/contract-closure.md)** **及** **[`closure-remaining.md`](../specs/requirements/closure-remaining.md)** **（§7～§7.6 · 关单路径）** 为准。

## 当前交付范围（给人听的版本）

本仓库把 **已在 `specs` 中展开的能力集合** 视为 **同一产品版本下的「当前范围」** — **不**在 `product/` 里维护另一套 FR 清单。**方向与做/不做** 以 **[`product.md`](../specs/requirements/product.md)** 为准；**执行优先级与阶段** 以 **[`roadmap.md`](./roadmap.md)**（P0、A～D）为准；**可对签缺口** 以 **[`contract-closure.md`](../specs/requirements/contract-closure.md)** 为准；**本仓 vs 所内分工、§7.5 闭环路径、§7.6 MR 勾选** 见 [`closure-remaining.md`](../specs/requirements/closure-remaining.md)。

若对外沟通「什么时候能用什么能力」，请 **同时** 对齐：`product.md` **非目标**、`design/api` **矩阵行**、以及相关 **`flows/`** — 避免「故事会承诺了但表上还是 TBD」。**端到端业务与收口鸟瞰**见 **[`roadmap.md`](./roadmap.md)**（章「**端到端业务与项目闭环**」、**篇首 TL;DR · 收口一览 ·「规格体系快照」L1～L7**）与仓库根 **[`flow/e2e-closed-loop.md`](../flow/e2e-closed-loop.md)**（文首 **「架构语言」** → [`architecture`「与通用 Agent 栈之对照」](../specs/design/architecture.md)）；**W1 / Hosted / Skill CI** → [`closure-completion-matrix.md`](../specs/requirements/closure-completion-matrix.md)、[`HOSTED-ROLLOUT-CHECKLIST.md`](../specs/openapi/HOSTED-ROLLOUT-CHECKLIST.md)、[`.github/workflows/skill-contract-consistency.yml`](../.github/workflows/skill-contract-consistency.yml)。

## 规划中（占位）

本篇刻意不写「版本切片」清单：**执行节奏与 P0** 见 [`roadmap.md`](./roadmap.md)；具体里程碑若以工单/backlog 跟踪，请在所内工具维护链接即可。

若需记录 **尚未落入 specs 的缺口** 或 **外链至项目管理 backlog**，请在一处统一维护（例如所内工单或团队笔记），**避免**在规格树里另起多套「版本」事实源。**需求缺口**若以 Git 追踪，须在对应 **`domains/`** / **`flows/`** / **`design/`** 增补或开立 issue，并保持与 **`product.md`** 索引一致。**2026-05 收口叙事**（不写第二套工单）：优先级与工单模板见 **`specs/requirements/closure-completion-matrix.md`**、**`closure-internal-sprint.md`**，与 **`roadmap.md`** 篇首 TL;DR 同窗。

## 相关阅读

- [执行节奏与任务规划](./roadmap.md)（P0、阶段 A～D、例行节奏）
- [产品与边界](./positioning.md)
- [产品概览与范围](./overview.md)
- [路线图维护约定](./roadmap/README.md)

---

**文档版本**：0.1.2 · **维护**：产品与规格 · **2026-05-26**：与 **`roadmap` TL;DR（收口一览）**、**规格体系快照 L1～L7**、**Hosted**、**Skill GHA** 同窗对齐。
