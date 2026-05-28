---
name: pipeline-test-api
description: Run test.api for a feature package — execute API P0 cases, advance to tested.
disable-model-invocation: true
---

# pipeline-test-api

Parse **功能 ID** from the user message.

1. Task: `test.api` in `handoff/pipeline/tasks.yaml`
2. `{{feature_dir}}` = `handoff/features/{{feat}}/`
3. Follow `.cursor/rules/test-agent.mdc`

Execute `test.api` now.
