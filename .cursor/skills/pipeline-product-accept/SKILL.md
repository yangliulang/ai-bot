---
name: pipeline-product-accept
description: Run product.accept — final acceptance when ui_reviewed, advance to done.
disable-model-invocation: true
---

# pipeline-product-accept

Parse **功能 ID** from the user message.

1. Task: `product.accept` in `handoff/pipeline/tasks.yaml`
2. Follow `.cursor/rules/product-agent.mdc`

Execute `product.accept` now. After marking done, run `./scripts/check-phase-close-ready.sh`; if exit 0, prominently tell the commander to run `/pipeline-product-phase-close` before planning the next phase.
