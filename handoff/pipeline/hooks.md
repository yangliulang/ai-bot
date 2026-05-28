# 流水线下一步 Hook 提醒

项目级配置：`.cursor/hooks.json` + `.cursor/hooks/pipeline-status-reminder.sh`

## 触发时机

| 事件 | 行为 |
|------|------|
| `postToolUse`（`Write` / `StrReplace`） | **仅当**工具路径为某功能包 `status.yaml` 时，注入 `additional_context`（可由 `pipeline.hooks.remind_on_write` 关闭） |
| `stop` | **仅当** `pipeline.hooks.stop_followup: true` 时，对 3 分钟内改过的 `status.yaml` 输出 `followup_message`（默认 `false`，避免同 Chat 反复自动续聊） |

策略：**fail-open**（脚本异常不阻断保存或结束会话）。**项目策略**在根目录 `pipeline.project.yaml` → `pipeline.hooks`（脚本运行时读取；`hooks.json` 路径不变）。

### pipeline.hooks 开关

| 字段 | 默认 | 说明 |
|------|------|------|
| `enabled` | `true` | `false` 时脚本直接退出，等同关闭 Hook |
| `remind_on_write` | `true` | `false` 时不向当前 Chat 注入 `additional_context` |
| `stop_followup` | `false` | `true` 时在 `stop` 事件输出 `followup_message`（更半自动） |
| `require_new_chat` | `true` | 文案强调「指挥官确认后新开 Chat，勿在本会话自动推进门禁」 |

**推荐（需用户确认再下一步）**：保持默认即可——写入时有提醒，`stop` 不自动续聊。

**更自动**：`stop_followup: true`（仍不会自动执行 Skill，仅可能在本 Chat 多跟一句）。

**完全静默**：`enabled: false`。

### 为何有时「状态变了却没有提醒」？

1. **Hooks 未启用**：在 Cursor **Settings → Hooks** 确认项目 `hooks.json` 已加载；改配置后建议重启 Cursor。
2. **手动改文件**：若用外部编辑器改 `status.yaml` 且未经过 Agent 工具，默认**不会**注入提醒（`stop_followup: false`）。请指挥官确认后**新开 Chat** 执行 `/pipeline-next` 或对应 Skill。
3. **`remind_on_write: false`**：写入 `status.yaml` 也不注入，仅依赖 `stop_followup: true` 时在会话结束跟一条（更自动，也更容易在同 Chat 内连发）。

### 为何曾出现「同一句提醒反复自动对话」？

1. **脚本误触发（已修复）**：旧版在 `stop` 之外的事件、或 stdin 任意字段提到 `status.yaml` 时也会注入 `additional_context`；Agent 每轮结束又回复「本回合不推进门禁」，形成空转。
2. **`stop_followup: true` + `loop_limit: null`**：每轮结束都跟一条 `followup_message`；与 `require_new_chat: true` 同时存在时，Agent 仍无法在本 Chat 推进，容易刷屏。**推荐**保持 `stop_followup: false`，写入时提醒一次即可。

## 提示内容

脚本读取 `status.yaml` 的 `feature`、`phase`、`next`（及 `blockers`），对照 `handoff/pipeline/tasks.yaml` 的 `next_task_map`，映射为指挥官 Skill，例如：

```text
/pipeline-backend 2026-05-25--greeting
```

- 若 `status.yaml` 的 `skips` 含下一正向步骤 → 提醒 `/pipeline-skip <功能ID>`，**勿**建议已跳过的角色 Skill
- 功能 `phase: done` 且 roadmap 阶段全部 done → 提醒 `/pipeline-product-phase-close`
- `contract_ready` + `backend-agent` → 额外提示可选 `test-prepare`、`frontend-mock`
- 无法映射 → 建议 `/pipeline-next <功能ID>`

## 本地自测

```bash
chmod +x .cursor/hooks/pipeline-status-reminder.sh

# 模拟 afterFileEdit（无 JSON 路径时脚本会读仓库内 status 文件）
./.cursor/hooks/pipeline-status-reminder.sh < /dev/null

# 已 done / next: null → 无输出
echo '{"hook_event_name":"postToolUse","tool_name":"Write","tool_input":{"path":"handoff/features/2026-05-25--greeting/status.yaml"}}' | \
  ./.cursor/hooks/pipeline-status-reminder.sh

# 进行中（next 非空）→ 有 additional_context；用任意 phase≠done 且 next 有值的 status.yaml 测试
```

在 Cursor **Settings → Hooks** 或 **Hooks 输出通道** 确认已加载；修改 `hooks.json` 后若未生效可重启 Cursor。

## 与指挥官手册关系

Hook 为**半自动提醒**，不代替门禁。指挥官仍应在开 Chat 前 `cat handoff/features/<id>/status.yaml` 核对 `phase` / `next`（见 [COMMANDER.md](COMMANDER.md) §9）。
