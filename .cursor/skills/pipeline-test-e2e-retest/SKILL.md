---
name: pipeline-test-e2e-retest
description: Run test.e2e-retest after frontend E2E fixes; advance to e2e_verified when P0 pass.
disable-model-invocation: true
---

# pipeline-test-e2e-retest

Parse **功能 ID** from the user message.

1. Task: `test.e2e-retest` in `handoff/pipeline/tasks.yaml`
2. Follow `.cursor/rules/test-agent.mdc`

Execute `test.e2e-retest` now.
