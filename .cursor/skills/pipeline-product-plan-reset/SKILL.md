---
name: pipeline-product-plan-reset
description: Clear undelivered phase planning (soft) or wipe phase for replan (full) — then run product.plan.
disable-model-invocation: true
---

# pipeline-product-plan-reset

Parse user intent:

- **默认 soft**：删除当前 `active_phase` 中未 `done` 的 backlog 行，保留已交付项；`backlog.yaml` 对应项改回 `queued`。
- **full**（用户说「整阶段重规划」「清空 phase」）：done 行写入 `inventory` §2，phase 重置为空白模板，本阶段 `in_phase` 全部 → `queued`。

1. Task: `product.plan-reset` in `handoff/pipeline/tasks.yaml`
2. Follow `.cursor/rules/product-agent.mdc`

Execute `product.plan-reset` now. After reset, if user wants new backlog, run `product.plan` in a **new** Chat or continue only if they asked to replan in the same message.
