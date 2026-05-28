# pipeline.project.yaml — 项目绑定

流水线**框架**（`handoff/pipeline/`、Skills、任务表）与**本仓库应用**（代码路径、URL、PRD）分离。绑定信息写在本文件。

## 字段说明

| 路径 | 用途 |
|------|------|
| `project.prd.primary` | 默认 PRD 路径（product.plan 对齐） |
| `project.onboarding.commander` | 指挥官手册（通常固定） |
| `project.onboarding.mode` | `greenfield` / `brownfield` / `continuing` |
| `product.inventory` | 存量切口 inventory 路径 |
| `product.backlog` | 全量待办队列 backlog.yaml |
| `features.root` | 功能包根目录 |
| `roadmap.default_phase_file` | product.contract 默认读的 roadmap |
| `roadmap.active_phase` | 当前阶段号（advance-phase 维护） |
| `roadmap.phase_capacity` | 每阶段从 backlog 切片条数上限（0=不限） |
| `apps.backend.path` | 后端代码根 |
| `apps.backend.dev.base_url` | OpenAPI servers、curl、联调 |
| `apps.backend.dev.cors_origin` | 后端 CORS（写入 api-dev 规则） |
| `apps.frontend.path` | 前端代码根 |
| `apps.frontend.dev.base_url` | 前端 dev、E2E 环境说明 |
| `pipeline.hooks.enabled` | 是否启用 status 变更 Hook 提醒（默认 `true`） |
| `pipeline.hooks.remind_on_write` | Agent Write/StrReplace `status.yaml` 后是否注入提醒 |
| `pipeline.hooks.stop_followup` | Agent 结束时是否自动续聊（默认 `false`） |
| `pipeline.hooks.require_new_chat` | 文案强调「确认后新开 Chat」 |

模式与 backlog 闭环见 [onboarding-modes.md](onboarding-modes.md)。

## Hook 策略示例

```yaml
pipeline:
  hooks:
    enabled: true
    remind_on_write: true
    stop_followup: false
    require_new_chat: true
```

## 接入模式示例

```yaml
project:
  onboarding:
    mode: greenfield   # 从 0：PRD → plan；存量首次 brownfield；续写 continuing

product:
  inventory: handoff/product/inventory.md
  backlog: handoff/product/backlog.yaml
```

## 常用命令

```bash
source scripts/lib/read-pipeline-project.sh && pp_print_context
./scripts/sync-project-rules.sh
./scripts/check-phase-close-ready.sh          # phase 是否可收束（退出码 0）
./scripts/sync-backlog-from-phase.sh       # product.plan 后
./scripts/plan-reset.sh                    # roadmap 变更：清除未交付规划 / 整阶段重置
./scripts/phase-realign-prepare.sh --phase N  # phase 对齐前快照
./scripts/feature-reopen.sh --feature ID   # 返工 reopen 原功能包
./scripts/seed-backlog-from-inventory.sh   # brownfield
./scripts/advance-phase.sh                  # phase 全 done 后
```

## 迁移到新项目

1. 复制 `pipeline.project.yaml.example` → `pipeline.project.yaml`
2. 设置 `project.onboarding.mode` 与 `apps.*.path`
3. 运行 `./scripts/sync-project-rules.sh`
4. 将 PRD 放到 `project.prd.primary` 所指路径

勿在 `tasks.yaml`、Agent 规则中写死本仓库路径；执行时用 manifest 或 `tasks.yaml` 头注释中的占位符默认值。
