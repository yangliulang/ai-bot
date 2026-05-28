---
name: pipeline-product-phase-close
description: Run product.phase-close — rollover done phase items to inventory and slice next backlog into the next phase.
disable-model-invocation: true
---

# pipeline-product-phase-close

1. Task: `product.phase-close` in `handoff/pipeline/tasks.yaml`
2. Follow `.cursor/rules/product-agent.mdc` and `handoff/conventions/onboarding-modes.md`
3. Prerequisite: current `handoff/roadmap/phase-N.md` backlog rows are all `done`

Execute `product.phase-close` now (runs `./scripts/advance-phase.sh`).
