---
name: pipeline-product-phase-realign
description: Realign a specific phase-N with updated roadmap/PRD — snapshot, replan backlog, schedule rework feature IDs.
disable-model-invocation: true
---

# pipeline-product-phase-realign

Parse **目标阶段** from the user message: `phase-2`, `phase 2`, or `--phase 2` (required).

1. Task: `product.phase-realign` in `handoff/pipeline/tasks.yaml`
2. Follow `.cursor/rules/product-agent.mdc`
3. User should attach updated PRD / roadmap docs and describe what changed.

Execute `product.phase-realign` now.
