# Agent Pipeline 在本仓快速上手

> 拷贝自 [agent-workflow](https://github.com/yangliulang/agent-workflow) 框架，已按 ChainUp 单体仓调整路径。

## 已拷贝内容

| 路径 | 作用 |
|------|------|
| `handoff/` | 流水线、模板、规范、inventory、roadmap |
| `scripts/` | `new-feature.sh`、`sync-project-rules.sh`、`check-test-coverage.sh`、`check-phase-close-ready.sh`、`sync-backlog-from-phase.sh`、`advance-phase.sh`、`plan-reset.sh`、`phase-realign-prepare.sh`、`feature-reopen.sh` |
| `.cursor/rules/*-agent.mdc`、`pipeline-project.mdc` | Agent 规则 |
| `.cursor/skills/pipeline-*` | `/pipeline-*` 指挥官命令 |
| `.cursor/hooks.json` | status 保存后下一步提醒 |
| `pipeline.project.yaml` | 项目绑定（`server` / `admin`） |

**保留不动**：`.cursor/rules/monorepo-role-scopes.mdc`、现有 `deploy-jenkins` / `fe` 等 skills。

---

## 第 0 步：一次性检查

```bash
cd /path/to/chainup-exchange-ai-bot
chmod +x scripts/*.sh scripts/lib/*.sh .cursor/hooks/pipeline-status-reminder.sh
./scripts/sync-project-rules.sh
export PIPELINE_PROJECT_ROOT="$PWD"
bash -c 'source scripts/lib/read-pipeline-project.sh && pp_print_context'
```

确认输出里 `backend_path=server`、`frontend_path=admin`。

**Hook 已启用时**：`pipeline.project.yaml` → `pipeline.hooks`（本仓 `stop_followup: false`；`require_new_chat` 可按团队习惯调整）。status 变更会**提示**下一条命令；当前阶段**全部 done** 时会提醒 `/pipeline-product-phase-close`。自检：`./scripts/check-phase-close-ready.sh`。

---

## Hook 策略（可选调整）

编辑根目录 `pipeline.project.yaml`：

```yaml
pipeline:
  hooks:
    enabled: true
    remind_on_write: true
    stop_followup: false      # false = 需指挥官新开 Chat（推荐）
    require_new_chat: true
```

改 YAML 即生效，无需 sync。完整说明：[handoff/pipeline/hooks.md](pipeline/hooks.md)。

---

## 第 1 步：对齐存量切口（产品 / 指挥官）

1. 编辑 **`handoff/product/inventory.md`**（§2 已实现、§4 本阶段要做、第一个 contract 候选）。
2. 与 PM 核对 **`product-doc/product/roadmap.md`**（**P0** · 阶段节奏 · **优先级与编号对照**）及 **`closure-completion-matrix.md`**（**W1** 硬排序）。

---

## 第 2 步：规划 roadmap（新开 Chat）

```text
/pipeline-product-plan
@handoff/product/inventory.md
@product-doc/product/roadmap.md
@product-doc/specs/requirements/closure-completion-matrix.md

请更新 handoff/roadmap/phase-1.md：backlog 优先级对齐 roadmap 内 P0/P1 与 closure 矩阵 W1；不写 API 细节。
```

或复制 `handoff/product/brownfield-product-plan-prompt.md` 全文。

### 产品文档变更：指定 phase 对齐 / 返工

当 `product-doc/product/roadmap.md` 或 specs 变更影响**某一历史阶段**（含已 done 需返工）：

```text
/pipeline-product-phase-realign phase-2

变更：user-login 响应字段调整，需返工
@product-doc/product/roadmap.md
@handoff/product/inventory.md
```

- 默认：已 done 项**新建返工功能 ID**（原 ID 保持 done）
- 若要 reopen 原包：`./scripts/feature-reopen.sh --feature 2026-05-26--user-login --phase 2`

仅废弃未交付 planned（不对照 PRD 写新表）：`/pipeline-product-plan-reset` → `/pipeline-product-plan`。

---

## 第 3 步：第一个功能包定稿（新开 Chat）

```text
/pipeline-product-contract 2026-05-26--condition-order-list-cancel
```

（换成 roadmap 里第一个 `planned` 且 P0 的 ID。）

产物：`handoff/features/<ID>/brief.md`、`api.openapi.yaml`、`test/*`、`status.yaml` → `contract_ready`。

---

## 第 4 步：按流水线推进（每步新开 Chat）

| 步 | Skill | 说明 |
|----|-------|------|
| 后端 | `/pipeline-backend <功能ID>` | 只改 `server/` |
| API 测 | `/pipeline-test-api <功能ID>` | |
| 前端 | `/pipeline-frontend-integrate <功能ID>` | 默认 `admin/`；deeplink 写在 integration.md |
| E2E | `/pipeline-test-e2e <功能ID>` | |
| 设计 | `/pipeline-designer-review <功能ID>` | |
| 验收 | `/pipeline-product-accept <功能ID>` | |

偷懒：`/pipeline-next <功能ID>`（读 `status.yaml` 自动选任务）。

每步前：`cat handoff/features/<ID>/status.yaml`

---

## 第 5 步：日常命令

```bash
# 新建功能包目录
./scripts/new-feature.sh 2026-05-26--my-feature "功能标题"

# 定稿前检查测试追溯
./scripts/check-test-coverage.sh handoff/features/2026-05-26--my-feature
```

---

## 多前端注意

- **manifest 默认前端** = `admin/`（运营控制台）。
- **deeplink** / **official-website**：在功能包 `brief.md` 写清路由；`frontend/integration.md` 列出页面与 API。
- 与 `/fe` 规则并存：frontend-agent 仍只改 brief 范围内的前端目录。

---

## 文档索引

- 指挥官：`handoff/pipeline/COMMANDER.md`
- Hook 提醒配置：`handoff/pipeline/hooks.md`
- 单体仓对照：`handoff/conventions/chainup-monorepo.md`
- 后端 SSOT：`server/docs/BACKEND_SPEC.md`
- 前端接入：`server/docs/API_INTEGRATION_GUIDE.md`、`admin/FE_HANDOFF.md`
