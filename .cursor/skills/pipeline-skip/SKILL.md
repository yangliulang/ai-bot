---
name: pipeline-skip
description: Skip pipeline steps declared in status.yaml skips (e.g. API-only features without frontend/E2E/designer).
disable-model-invocation: true
---

# pipeline-skip

Parse **功能 ID** from the user message.

1. Task: `pipeline.skip` in `handoff/pipeline/tasks.yaml`
2. Run `./scripts/pipeline-skip-check.sh {{feature_dir}}` first; if exit 0, run `./scripts/pipeline-skip.sh {{feature_dir}}`

Execute `pipeline.skip` now.
