# Phase 对齐检查清单（product.phase-realign）

> 指定 `phase-N` 对照 PRD / roadmap 变更后，指挥官确认再开 `product.contract`。

## A. 输入与范围

- [ ] 已明确 **目标阶段 N**（`--phase N` 或消息中 `phase-N`）
- [ ] 已附 **变更后的 PRD / roadmap**（或说明变更章节）
- [ ] 已运行 `./scripts/phase-realign-prepare.sh --phase N`（或 Agent 在本任务第 1 步执行）
- [ ] 已阅读快照 `handoff/roadmap/.realign/phase-N-latest.md`

## B. 对齐策略

- [ ] `phase-N.md` 含 **`## 对齐说明`**：文档变更摘要、保留 / 返工 / 新增 / 推迟 对照
- [ ] **已 done 且文档未影响** 的行保持 `done`，未重复新建 ID
- [ ] **文档变更影响已交付**：默认 **新建返工功能 ID**（备注 `返工←原ID`），原行仍 `done`
- [ ] **指挥官指定 reopen 原 ID**：已运行 `./scripts/feature-reopen.sh --feature <ID> --phase N`
- [ ] **in_progress** 项有明确处理（保留继续 / reopen / 等新返工 ID 替代）

## C. Backlog 质量（同 product-plan）

- [ ] 阶段目标 1～3 句；本阶段不做已更新
- [ ] 功能 ID 格式 `YYYY-MM-DD--kebab-slug`；无重复能力两行
- [ ] 依赖无环；首个 contract 候选为 P0 且无依赖
- [ ] 已运行 `./scripts/sync-backlog-from-phase.sh --phase N`

## D. 指挥官确认

- [ ] 返工项清单与优先级已认可
- [ ] 下一命令明确：`/pipeline-product-contract <首个 planned ID>`

## 与 plan-reset / phase-close 的区别

| 操作 | 场景 |
|------|------|
| **phase-realign** | 指定历史或当前 phase，对照**产品文档变更**优化 backlog，含返工规划 |
| **plan-reset** | 仅清除未交付 planned，不读 PRD 写新表 |
| **phase-close** | 阶段**全部 done** 后收束进下一 phase |
