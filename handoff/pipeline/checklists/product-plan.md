# 阶段规划检查清单（product.plan）

> 对照本清单后再将 backlog 交给 `product.contract`，或由指挥官人工确认。

## A. 与产品目标对齐

- [ ] 已阅读并对齐 PRD（路径见 `pipeline.project.yaml` → `project.prd.primary`；本仓库为 [`product-doc/product/roadmap.md`](../../../product-doc/product/roadmap.md)，并核对 [`closure-completion-matrix.md`](../../../product-doc/specs/requirements/closure-completion-matrix.md) **W1** 硬排序）
- [ ] backlog **优先级列**与 roadmap **P0 / 阶段 A～D** 及 closure **P‑01～P‑08** 对照一致（勿混读 `L1～L7` 分层索引为开发唯一排序）
- [ ] `phase-N.md` 的**阶段目标**用 1～3 句话说明「本阶段要证明什么」
- [ ] **本阶段不做** 已列出，避免 scope creep

## B. Backlog 结构

- [ ] 每个功能一行，功能 ID 格式为 `YYYY-MM-DD--kebab-slug`（日期与 slug 之间为**双横线** `--`）
- [ ] 优先级（P0/P1/P2）与业务价值一致：先无依赖、可独立试跑的能力
- [ ] 状态列仅使用 roadmap 约定：`planned` / `contract_ready` / `in_dev` / `done`
- [ ] 无重复功能（同一能力拆成两个 ID）

## C. 依赖与顺序

- [ ] 依赖关系无环（A 依赖 B、B 依赖 A）
- [ ] 首个 `contract_ready` 候选为 **P0 且无依赖**（本仓库建议：先 `app-info` 类只读能力）
- [ ] 依赖链在 backlog 表或「依赖与顺序」小节中写清（文字或示意均可）
- [ ] 需要登录的能力排在有 token 的功能之后

## D. 可交付性（每个 backlog 项）

- [ ] 能用**一句话**描述用户价值（谁、要什么、为什么）
- [ ] 预估可在**单功能包**内闭环（brief + API + 页面），不混多个 unrelated 主题
- [ ] 非功能共识与 [project.md](../../conventions/project.md) 一致（API/Web 基址、统一响应体）

## E. 验收标准预备（规划阶段）

- [ ] 未在 roadmap 写 API 细节（路径、字段留在功能包 `brief` / OpenAPI）
- [ ] 已标明哪些功能**有页面**（后续定稿需 E2E 追溯）
- [ ] P0 功能数量可控（建议 Phase 1 同时 `in_dev` 不超过 1 个）

## F. 指挥官确认（人工）

- [ ] 指挥官已扫读本清单，同意进入 `product.contract`
- [ ] 下一功能的 功能 ID 已明确（例：`/pipeline-product-contract 2026-05-25--greeting`）

## 不通过时

- 回到 `product.plan` 修订 `handoff/roadmap/phase-N.md`
- **不要** 创建多个 `contract_ready` 功能包
