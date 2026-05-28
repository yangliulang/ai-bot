# Phase 2 对齐快照

> 生成: 2026-05-27T15:14:30+08:00 · `./scripts/phase-realign-prepare.sh --phase 2`
> PRD: `product-doc/product/roadmap.md` · inventory: `handoff/product/inventory.md` · backlog: `handoff/product/backlog.yaml`

## 指挥官变更说明

Realign Phase-2 vs product-doc/product/roadmap.md and inventory S2/S6 ChainUp P-04-P-08 W1

## 状态摘要

| 类别 | 数量 | 说明 |
|------|------|------|
| done | 7 | 已交付；若文档变更影响，应对齐任务**新增返工功能 ID**，勿改原行 done |
| in_progress | 0 | 开发/定稿中；对齐时默认保留，或指挥官指定 reopen |
| planned | 0 | 未交付；prepare 后 soft reset 会 demote 到 backlog queued |

## done（保留对照，返工请新建 ID）

| 功能 ID | 功能名 | 备注 |
|---------|--------|------|
| 2026-05-27--runtime-write-path-pipeline | 写路径管线（read_skill + 事件序） | **P‑04** · **P‑05** · W1 **MR-RT-B4**；含 TG/时间线；**含页面：否** · 2026-05-27 收口 |
| 2026-05-27--skill-publish-effective | Skill Publish 生效链 | **P‑07** · W1 **SK-B1～B3/B5**；**含页面：是** · 2026-05-26 收口 |
| 2026-05-27--admin-ai-settings-gateway-ui | Admin AI 网关开关 UI | Phase-1 FE 债 · `/ai-settings?tab=runtime` 网关策略 · 2026-05-27 收口 |
| 2026-05-26--trading-reconcile | 504 对账契约收口 | **P‑03** / Recovery；**含页面：否** · 2026-05-26 收口 |
| 2026-05-26--condition-order-list-cancel | 条件单查撤契约收口 | Step 2.5 · **含页面：否** · 2026-05-28 收口 |
| 2026-05-26--futures-cancel | 合约撤单契约收口 | Step 2.3 · **含页面：否** · 2026-05-28 收口 |
| 2026-05-27--telegram-write-path-staging | 主链 TG 写路径 staging 证据 | **P‑08** · `exec-3d132b3ad3ad44` · evidence 已填 · 2026-05-26 收口 |

## in_progress（对齐时注意 blockers）

| 功能 ID | roadmap 状态 | 包 phase | 备注 |
|---------|--------------|----------|------|
| — | — | — | — |

## planned（reset 后将 demote）

| 功能 ID | 功能名 | 备注 |
|---------|--------|------|
| — | — | — |

## Agent 对齐产出要求

1. 重写 `handoff/roadmap/phase-2.md`：阶段目标、backlog 表、依赖、本阶段不做
2. 新增 **`## 对齐说明`**：文档变更摘要、保留 / 返工 / 新增 / 推迟 对照表
3. **返工**：文档变更影响已 done 能力时，**新建** `YYYY-MM-DD--slug`（可加 `-v2`），状态 `planned`，备注 `返工←原ID`；**勿**把原 done 行改回 planned
4. 运行 `./scripts/sync-backlog-from-phase.sh --phase 2`
5. 对照 `handoff/pipeline/checklists/phase-realign.md`
