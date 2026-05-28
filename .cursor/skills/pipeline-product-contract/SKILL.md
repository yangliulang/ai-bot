---
name: pipeline-product-contract
description: Run product.contract — brief + OpenAPI, advance to contract_ready.
disable-model-invocation: true
---

# pipeline-product-contract

Parse **功能 ID** from the user message if present; otherwise pick highest-priority `planned` from roadmap.

1. Task: `product.contract` in `handoff/pipeline/tasks.yaml`
2. Follow `.cursor/rules/product-agent.mdc`

Execute `product.contract` now.
