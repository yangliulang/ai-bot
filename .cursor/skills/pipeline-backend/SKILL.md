---
name: pipeline-backend
description: Run backend.implement for a feature package — implement OpenAPI in apps/api, advance to backend_done.
disable-model-invocation: true
---

# pipeline-backend

Parse **功能 ID** from the user message.

1. Task: `backend.implement` in `handoff/pipeline/tasks.yaml`
2. Substitute `{{feat}}`, `{{feature_dir}}` = `handoff/features/{{feat}}/`
3. Follow `.cursor/rules/backend-agent.mdc`

Execute `backend.implement` now.
