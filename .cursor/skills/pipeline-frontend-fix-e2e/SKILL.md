---
name: pipeline-frontend-fix-e2e
description: Run frontend.fix-e2e after failed E2E; clear blockers and set next test-agent.
disable-model-invocation: true
---

# pipeline-frontend-fix-e2e

Parse **功能 ID** from the user message.

1. Task: `frontend.fix-e2e` in `handoff/pipeline/tasks.yaml`
2. Follow `.cursor/rules/frontend-agent.mdc`

Execute `frontend.fix-e2e` now.
