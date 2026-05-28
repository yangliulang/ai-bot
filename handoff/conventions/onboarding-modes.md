# 项目接入模式（greenfield / brownfield / continuing）

> 由 `pipeline.project.yaml` → `project.onboarding.mode` 定义。脚本与 `product.plan` / `product.phase-close` 据此分支。

## 三种模式

| 模式 | 适用 | 优先级 SSOT | 典型流程 |
|------|------|-------------|----------|
| **`greenfield`** | 从 0 新项目 | PRD + `product.plan` 直接写 `phase-1.md` | `/pipeline-product-plan` @PRD → contract → 7 步 |
| **`brownfield`** | 存量项目**首次**接入流水线 | 先 `inventory.md` §4，再 `seed-backlog` → `backlog.yaml` | 填 inventory → seed-backlog → plan → 7 步 |
| **`continuing`** | 已接入，**续写下一迭代** | `handoff/product/backlog.yaml` 队列顺序 | plan 对齐 PRD/roadmap 并 **sync-backlog** → contract；或改 backlog 优先级 → phase-close 切片 |

## manifest 字段

```yaml
project:
  onboarding:
    mode: greenfield   # greenfield | brownfield | continuing

product:
  inventory: handoff/product/inventory.md
  backlog: handoff/product/backlog.yaml

roadmap:
  glob: handoff/roadmap/phase-*.md
  default_phase_file: handoff/roadmap/phase-1.md
  active_phase: 1
  phase_capacity: 0    # 0 = 不限制；>0 每阶段最多切片条数
```

## 模式切换（闭环）

```text
greenfield ──(phase 全部 done + phase-close)──► continuing
brownfield ──(phase 全部 done + phase-close)──► continuing

continuing ──(product.plan + sync-backlog)──► phase-N 与 backlog 对齐 ──► contract
continuing ──(改 backlog.yaml 优先级)──► advance-phase / phase-close ──► 下一 phase-N.md
continuing ──(plan-reset soft/full)──► 清除未交付 / 整阶段重置 ──► product.plan 重规划
continuing ──(phase-realign phase-N)──► 对照 PRD 对齐指定阶段 + 返工 ID ──► contract
```

- **首次** `phase-close`：把当前 phase 的 `done` 行写入 `inventory` §2，并初始化/更新 `backlog.yaml`。
- **continuing** 下：`advance-phase.sh` 从 `backlog.yaml` 的 `queued` 按优先级切片；**`product.plan` 后**运行 `sync-backlog-from-phase.sh` 将 phase 表写回 backlog（planned → `in_phase`）。

## 命令速查

| 命令 | 模式 |
|------|------|
| `./scripts/seed-backlog-from-inventory.sh` | brownfield（inventory §4 → backlog.yaml） |
| `./scripts/sync-backlog-from-phase.sh` | plan 后（phase 表 → backlog.yaml） |
| `./scripts/check-phase-close-ready.sh` | 任意（当前 phase 是否全部 done；退出码 0 = 可 phase-close） |
| `./scripts/advance-phase.sh` | continuing（或 phase 已全 done 的 brownfield） |
| `/pipeline-product-phase-close` | 同上（Agent 执行 phase-close 任务） |
| `./scripts/plan-reset.sh` | roadmap 变更：清除未交付规划（`--mode soft`）或整阶段重置（`--mode full`） |
| `/pipeline-product-plan-reset` | 同上（Agent 执行 plan-reset 任务） |
| `./scripts/phase-realign-prepare.sh` | 指定 phase 对齐前：快照 + 切换 active_phase + soft reset planned |
| `/pipeline-product-phase-realign` | 对照 PRD/roadmap 重写 phase-N（含返工规划） |
| `./scripts/feature-reopen.sh` | 显式 reopen 原功能 ID → planned |
| `/pipeline-product-plan` | 三模式均可；完成后 **sync-backlog**；continuing 读 backlog + inventory 对齐 |

## 仍建议人工维护

- `inventory` §1 切口说明、§5 本阶段不做、§6 PRD 章节映射
- `backlog.yaml` 增删 **`deferred`**、调未进当前 phase 的 **`queued`** 优先级（plan 已 sync 本阶段行）
- `product.plan` 后指挥官确认 diff

详见 [product.md](product.md)、[../product/inventory.md](../product/inventory.md)。
