---
name: pipeline-next
description: >-
  Auto-run the pipeline task for a feature package based on status.yaml phase and next.
  Use when the commander says pipeline-next or does not know which step to run.
disable-model-invocation: true
---

# pipeline-next

The user message contains a **功能 ID** (e.g. `2026-05-25--greeting`) or path under `handoff/features/`.

## Instructions

1. Resolve `{{feat}}` from the user message (slug like `YYYY-MM-DD--slug`).
2. Read `handoff/features/{{feat}}/status.yaml`.
3. Open `handoff/pipeline/tasks.yaml` → `next_task_map` → use `next` and `phase` to pick the task key.
4. If no mapping, report current `phase`, `next`, and suggest the matching Skill from `handoff/pipeline/COMMANDER.md` §3.
5. Execute that task's `steps` from `tasks.yaml` (replace `{{feat}}`, `{{feature_dir}}`).
6. Follow `.cursor/rules/{agent}-agent.mdc` for the task's `agent` field.

Do not skip status.yaml gates unless the user explicitly exempts in the same message.
