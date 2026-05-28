# Roadmap（路线图子目录）

本目录用于放置 **按时间轴或主题轴** 拆分的路线图正文（例如按季度增补 `2026-Q2.md` 等），**属于 `product/` 叙事**，**不是** FR/SC 契约 SSOT。

## 维护约定

- **需求变更须同步路线图（必选）**：凡合并请求 **新增或实质修改** **[`specs/requirements/product.md`](../../specs/requirements/product.md)**、**[`domains/`](../../specs/requirements/domains/README.md)**、**[`flows/`](../../specs/requirements/flows/README.md)**、**[`domains/agent/telegram/`](../../specs/requirements/domains/agent/telegram/README.md)**，或 **横切需求专卷**（例：**[`Runtime/`](../../specs/requirements/Runtime/overview.md)**、**[`skill-specs/`](../../specs/requirements/skill-specs/README.md)**、**[`evals/`](../../specs/requirements/evals/README.md)**、**[`closure-completion-matrix.md`](../../specs/requirements/closure-completion-matrix.md)** 等与 **P0／阶段／横切主题** **直接相关的闭合或排期条文**），**须**在同一 MR **择要** 更新 **[`../roadmap.md`](../roadmap.md)**：**篇首 TL;DR**、**「规格体系快照」（L1～L7）**、**[「需求全覆盖索引」](../roadmap.md#req-full-index)**（**新增/移动需求文档路径时须补链**）、**横切主题表**、**阶段 A～D／例行节奏／P0**，或 **文末维护沿革** 中至少一处。**豁免**：纯错别字、标点、不重读产品含义的链接修正 — MR 勾选 **Roadmap · N/A** 并说明。
- **方向与范围仲裁**仍以 **[`specs/requirements/product.md`](../../specs/requirements/product.md)** 为准；路线图若与 specs 冲突，以 specs 正文为准并回写 `product/`。
- **可对外承诺的能力**须与 **[`specs/design/api.md`](../../specs/design/api.md)** 矩阵及 **[`specs/requirements/contract-closure.md`](../../specs/requirements/contract-closure.md)** 一致；**关单余量 / MR 勾选** **同窗** [`closure-remaining.md`](../../specs/requirements/closure-remaining.md)（**[§7.5](../../specs/requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)**）；不得在此承诺矩阵中 **TBD** 或未覆盖项。
- **实现排期、人力、技术栈**不属于本仓库 specs 职责，可链到项目管理工具；此处只保留 **产品向** 的里程碑叙事（如需）。
- **P0、阶段 A～D、例行节奏与规格侧「刻意不做」** 已统一写在 **[`../roadmap.md`](../roadmap.md)**，请勿在子目录再造第二套「执行规划」正文。

## 入口

- **路线图主文件**：[`../roadmap.md`](../roadmap.md) — **篇首 TL;DR** + **「规格体系快照」L1～L7（Runtime / PRS / Skill·Tool / Memory / MNRA / Eval / 收口）** · **横切主题**（邻域并排）；含 **端到端业务 / 收口**、`flow/e2e-closed-loop` · **P0 / 阶段 A～D**。篇内 **「读者分工」** 说明 **`product.md` / `design/api`+`contract-closure`**（Roadmap **不承担 FR/SC**）。**2026-05 收口一览** → [`closure-completion-matrix.md`](../../specs/requirements/closure-completion-matrix.md)。
- **端到端闭环图（仓库根）**：[`flow/e2e-closed-loop.md`](../../flow/e2e-closed-loop.md) — 文首 **「架构语言」** → [`architecture`「与通用 Agent 栈之对照」](../../specs/design/architecture.md)
- **阶段叙事总览**：[`../milestones.md`](../milestones.md)
- **需求与设计事实源**：[`specs/requirements/product.md`](../../specs/requirements/product.md)、[`specs/requirements/README.md`](../../specs/requirements/README.md)；**域导航**：[`specs/requirements/domains/README.md`](../../specs/requirements/domains/README.md)（含 **[`domains/web/`](../../specs/requirements/domains/web/README.md)** · **FR-WEB**）
