# Phase 3 对齐快照

> 生成: 2026-05-27T15:12:36+08:00 · `./scripts/phase-realign-prepare.sh --phase 3`
> PRD: `product-doc/product/roadmap.md` · inventory: `handoff/product/inventory.md` · backlog: `handoff/product/backlog.yaml`

## 指挥官变更说明

realign vs product roadmap and inventory

## 状态摘要

| 类别 | 数量 | 说明 |
|------|------|------|
| done | 5 | 已交付；若文档变更影响，应对齐任务**新增返工功能 ID**，勿改原行 done |
| in_progress | 0 | 开发/定稿中；对齐时默认保留，或指挥官指定 reopen |
| planned | 0 | 未交付；prepare 后 soft reset 会 demote 到 backlog queued |

## done（保留对照，返工请新建 ID）

| 功能 ID | 功能名 | 备注 |
|---------|--------|------|
| 2026-05-28--pipeline-eval-orchestration-align | 管线 Eval + 编排 freeze 对拍 | **OP-AO3** · `eval.runtime.pipeline_write_order` · `runtime-freeze` §3 · W2 Eval；**含页面：否** |
| 2026-05-28--prompt-runtime-assembly-write | Prompt Runtime 写路径拼装链 | **CC-P1-04** · **OP-PR** · AC-09a～f · 写路径 TRADING 扩面；**含页面：否** |
| 2026-05-28--skill-contract-eval-staging | Skill 契约 Eval staging | **OP-SKILL B** · W3 **SK-B03** · `eval.skill.*` P0 真跑；**含页面：否** |
| 2026-05-28--registry-tool-idempotency | Registry toolId/skillId 幂等 | **CC-P1-03** · MR-E · `SC-MCV1-05` / `SC-OBS01`；**含页面：否** |
| 2026-05-28--memory-stm-session | Memory STM 会话基线 | **OP-MEM** · `eval.memory.session_clear_stm` · LTM 默认 OFF；**含页面：否** |

## in_progress（对齐时注意 blockers）

| 功能 ID | roadmap 状态 | 包 phase | 备注 |
|---------|--------------|----------|------|
| — | — | — | — |

## planned（reset 后将 demote）

| 功能 ID | 功能名 | 备注 |
|---------|--------|------|
| — | — | — |

## Agent 对齐产出要求

1. 重写 `handoff/roadmap/phase-3.md`：阶段目标、backlog 表、依赖、本阶段不做
2. 新增 **`## 对齐说明`**：文档变更摘要、保留 / 返工 / 新增 / 推迟 对照表
3. **返工**：文档变更影响已 done 能力时，**新建** `YYYY-MM-DD--slug`（可加 `-v2`），状态 `planned`，备注 `返工←原ID`；**勿**把原 done 行改回 planned
4. 运行 `./scripts/sync-backlog-from-phase.sh --phase 3`
5. 对照 `handoff/pipeline/checklists/phase-realign.md`
