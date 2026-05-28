---
name: pipeline-product-plan
description: Run product.plan — create or update roadmap phase backlog (branches on greenfield/brownfield/continuing mode).
disable-model-invocation: true
---

# pipeline-product-plan

1. Task: `product.plan` in `handoff/pipeline/tasks.yaml`
2. Follow `.cursor/rules/product-agent.mdc`
3. Use any PRD or product doc the user attached. Read `pipeline.project.yaml` → `project.onboarding.mode` first.

Execute `product.plan` now. After updating `handoff/roadmap/phase-N.md`, run `./scripts/sync-backlog-from-phase.sh` (optional `--dry-run` first) to merge the phase backlog table into `handoff/product/backlog.yaml`.
