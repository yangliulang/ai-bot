# 指挥官手册 — 一步一步指挥各 Agent

你是**指挥官**：新开 Chat、选规则或 Skill、**只填功能 ID**（如 `2026-05-25--greeting`），其余由任务表与 Agent 规则自动展开。

**不要**再复制大段 Prompt。项目路径与 PRD 见根目录 **`pipeline.project.yaml`**（勿写死 `apps/api` 等）。

---

## 0. 各角色对应什么岗位？

市面岗位、擅长解决什么问题：见 **[roles.md](roles.md)**。  
指挥官只需记住：每个 Chat 扮演一个 Agent，用对应 `/pipeline-*` + 功能 ID。

**唤起后各层如何协作？** 总览图 **[overview-diagram.md](overview-diagram.md)** · 详解 **[invoke-flow.md](invoke-flow.md)**。

---

## 0.1 第一次使用前

确认仓库内已有（一般已提交）：

```text
pipeline.project.yaml
.cursor/rules/*-agent.mdc
.cursor/rules/project.mdc
handoff/pipeline/tasks.yaml
```

若修改了 `apps.backend.path` / `apps.frontend.path`，运行一次：

```bash
./scripts/sync-project-rules.sh
```

可选：在 Cursor 设置里能看到项目 Skills（`.cursor/skills/pipeline-*`）。

---

## 1. 你只记两样东西

| 你要给的 | 示例 |
|----------|------|
| **功能 ID** | `2026-05-25--greeting` |
| **任务**（二选一） | 见下方「方式 A / B」 |

功能包路径固定为：`handoff/features/2026-05-25--greeting/`（Agent 会自动拼）。

---

## 2. 两种调用方式（任选其一）

### 方式 A：Skill（推荐，最接近 `/命令`）

在 Chat 输入框用 **`/`** 搜索 Skill 名，选中后**在同一句话里写上 功能 ID**：

```text
/pipeline-backend 2026-05-25--greeting
```

| 你想做的事 | 输入 |
|------------|------|
| 不知道下一步，自动跟 status | `/pipeline-next 2026-05-25--greeting` |
| 产品：规划 roadmap | `/pipeline-product-plan`（可不写功能 ID） |
| 产品：建包定稿 | `/pipeline-product-contract 2026-05-25--greeting` |
| 后端：实现 API | `/pipeline-backend 2026-05-25--greeting` |
| 测试：API | `/pipeline-test-api 2026-05-25--greeting` |
| 测试：E2E | `/pipeline-test-e2e 2026-05-25--greeting` |
| 前端：联调 | `/pipeline-frontend-integrate 2026-05-25--greeting` |
| 前端：E2E 返工 | `/pipeline-frontend-fix-e2e 2026-05-25--greeting` |
| 前端：UI 返工 | `/pipeline-frontend-fix-ui 2026-05-25--greeting` |
| 设计：UI 走查 | `/pipeline-designer-review 2026-05-25--greeting` |
| 产品：验收 | `/pipeline-product-accept 2026-05-25--greeting` |
| 产品：阶段收束 | `/pipeline-product-phase-close` |
| 产品：清除规划 / 重规划前重置 | `/pipeline-product-plan-reset` |
| 产品：指定 phase 对齐文档 / 返工规划 | `/pipeline-product-phase-realign phase-N` |

可选：`/pipeline-frontend-mock`、`/pipeline-test-prepare`、`/pipeline-designer-rereview`、`/pipeline-test-e2e-retest`。

### 方式 B：`@` 规则 + 功能 ID（不装 Skill 时）

```text
@backend-agent.mdc 2026-05-25--greeting
```

Agent 会读 `handoff/pipeline/tasks.yaml`，按 `status.yaml` 的 `phase` / `next` 匹配默认任务并执行。  
若 phase 与角色不符，应**只汇报**当前该谁做，不擅自改代码。

更稳的写法（多 @ 一个状态文件）：

```text
@backend-agent.mdc @handoff/features/2026-05-25--greeting/status.yaml
```

---

## 3. 标准流水线（按顺序开 7 个 Chat）

每个功能从 **planned → done** 的主路径如下。每步**新开一个 Chat**（或清空上下文），避免混聊。

| 步 | 看谁 | 调用（方式 A） | 预期 `status.yaml` |
|----|------|----------------|---------------------|
| 1 | 产品 | `/pipeline-product-contract 2026-05-25--xxx` | `contract_ready`，`next: backend-agent` |
| 2 | 后端 | `/pipeline-backend 2026-05-25--xxx` | `backend_done`，`next: test-agent` |
| 3 | 测试 | `/pipeline-test-api 2026-05-25--xxx` | `tested`，`next: frontend-agent` |
| 4 | 前端 | `/pipeline-frontend-integrate 2026-05-25--xxx` | `frontend_done`，`next: test-agent` |
| 5 | 测试 | `/pipeline-test-e2e 2026-05-25--xxx` | `e2e_verified`，`next: designer-agent` |
| 6 | 设计 | `/pipeline-designer-review 2026-05-25--xxx` | `ui_reviewed`，`next: product-agent` |
| 7 | 产品 | `/pipeline-product-accept 2026-05-25--xxx` | `done`，`next: null` |

**开始前**先看一眼：

```bash
cat handoff/features/2026-05-25--xxx/status.yaml
```

确认 `next` 与上表一致再开对应 Chat。

### API-only / 无页面（skips）

定稿时在 `status.yaml` 声明（`test/coverage.md` 含页面=否 时 product.contract 写入）：

```yaml
skips: [frontend.integrate, test.e2e, designer.review]
```

路径：**backend → test.api → `/pipeline-skip` → product.accept**。Hook 在 API 测完后提醒勿开 frontend Chat。

---

## 4. 返工分支（失败时再开 Chat）

| 现象 | 调用 |
|------|------|
| API 测试失败 | 修后端 → 再 `/pipeline-test-api 2026-05-25--xxx` |
| E2E 失败 | `/pipeline-frontend-fix-e2e 2026-05-25--xxx` → 再 `/pipeline-test-e2e-retest 2026-05-25--xxx` |
| UI 走查 P0 | `/pipeline-frontend-fix-ui 2026-05-25--xxx` → 再 `/pipeline-designer-rereview 2026-05-25--xxx` |

---

## 5. 偷懒一招：`pipeline-next`

不确定该叫谁时，**只开这一个 Chat**：

```text
/pipeline-next 2026-05-25--greeting
```

Skill 会读 `status.yaml` 的 `phase` + `next`，从 `tasks.yaml` 的 `next_task_map` 选任务并执行。  
若你更想手动指定步骤，仍用第 3 节表格里的具体 Skill。

---

## 6. 阶段规划（与单个功能包无关）

| 目标 | 调用 |
|------|------|
| 从 PRD 拆 Phase 1 backlog | `/pipeline-product-plan` + 附上 PRD 或 `@你的PRD.md`（`mode: greenfield`） |
| **存量首次接入** | `mode: brownfield` → inventory → `./scripts/seed-backlog-from-inventory.sh` → plan |
| **续写下一迭代** | 改 `backlog.yaml` 优先级 → phase 全 done → `/pipeline-product-phase-close` |
| **roadmap 变更、废弃未交付规划** | `/pipeline-product-plan-reset`（soft）→ `/pipeline-product-plan` |
| **指定 phase 对齐 PRD / 含返工** | `/pipeline-product-phase-realign phase-N` + `@product-doc/product/roadmap.md` |
| **整阶段推倒重规划** | `/pipeline-product-plan-reset --mode full` → `/pipeline-product-plan` |
| 试跑极简功能 | 先 product-plan，再对功能 ID 走第 3 节 7 步 |

### 阶段收束门禁（phase 全 done 后必做）

当前 `roadmap/phase-N.md` backlog **全部为 `done`** 时（最后一个功能验收后 Hook 也会提醒）：

1. **先** `/pipeline-product-phase-close`（或 `./scripts/advance-phase.sh`）— 把本阶段 done 项**追加**到 `inventory.md` §2，切片下一批到 §4，生成 `phase-(N+1).md`
2. **再** `/pipeline-product-plan` 审 diff（会 **sync-backlog**），或 `/pipeline-product-contract <首个 ID>`（若 phase 已由 advance-phase 生成）

**勿**在收束前直接 plan：未写入 inventory §2 的已完成能力会被 PRD（`product-doc/product/roadmap.md`）再次排进 backlog。自检：`./scripts/check-phase-close-ready.sh`（退出码 0 = 可收束）。

---

## 7. 质量门禁（规划与定稿）

| 节点 | 清单 / 脚本 | 说明 |
|------|-------------|------|
| `product.plan` 后 | [checklists/product-plan.md](checklists/product-plan.md) | 指挥官确认后再 `product.contract` |
| `product.contract` 前 | [checklists/contract-test-coverage.md](checklists/contract-test-coverage.md) | 含 `test/coverage.md` 与用例 |
| 定稿自动化 | `./scripts/check-test-coverage.sh handoff/features/<功能ID>` | 退出码 0 才可 `contract_ready` |

索引：[checklists/README.md](checklists/README.md)

### Hook 下一步提醒

保存 `handoff/features/*/status.yaml` 后，项目 Hook 会注入下一条 `/pipeline-*` 命令（见 [hooks.md](hooks.md)）。  
策略由 **`pipeline.project.yaml` → `pipeline.hooks`** 控制（本仓 `require_new_chat: false` 时文案不强调新开 Chat，但仍不自动推进门禁）。  
功能 `phase: done` 时：若当前 roadmap 阶段**尚未**全部 done，Hook 通常不跟下一条；若**已全部 done**，会提醒 `/pipeline-product-phase-close`（勿直接 plan）。  
Hook 不代替 `status.yaml` 门禁核对。

---

## 8. 并行（可选）

| 时机 | 可并行 |
|------|--------|
| `contract_ready` 后 | `/pipeline-frontend-mock 2026-05-25--xxx`（不改 status） |
| `contract_ready` 后 | `/pipeline-test-prepare 2026-05-25--xxx`（复审用例矩阵，不改 status） |

主路径仍须：**后端 API 测过 → 前端联调 → E2E → 设计走查 → 产品验收**。

---

## 9. 自检清单（每步完成后）

- [ ] `status.yaml` 的 `phase` / `next` 已更新
- [ ] `history` 多了一条记录
- [ ] 该步交付物已写（如 `test/report.md`、`design/ui-review.md`）
- [ ] roadmap 里该行状态与功能包一致（产品定稿/验收时会改）
- [ ] **定稿步**：`check-test-coverage.sh` 已退出码 0（见 §7）

---

## 10. 任务键速查

完整定义在 [tasks.yaml](tasks.yaml)。与 Skill 对应关系：

| 任务键 | Skill |
|--------|-------|
| `product.plan` | `pipeline-product-plan` |
| `product.plan-reset` | `pipeline-product-plan-reset` |
| `product.phase-realign` | `pipeline-product-phase-realign` |
| `product.phase-close` | `pipeline-product-phase-close` |
| `product.contract` | `pipeline-product-contract` |
| `backend.implement` | `pipeline-backend` |
| `test.api` | `pipeline-test-api` |
| `test.e2e` | `pipeline-test-e2e` |
| `frontend.integrate` | `pipeline-frontend-integrate` |
| `designer.review` | `pipeline-designer-review` |
| `product.accept` | `pipeline-product-accept` |

更多键见 `tasks.yaml` 与 [PROMPTS.md](../PROMPTS.md)（索引表）。

---

## 11. 常见问题

**Q：只写 `2026-05-25--greeting` 不写路径可以吗？**  
可以。规则与 Skill 都会解析为 `handoff/features/2026-05-25--greeting/`。

**Q：Agent 说 phase 不对怎么办？**  
不要强行推进。用 `cat status.yaml` 看 `next`，改开上表对应步的 Chat，或 `/pipeline-next`。

**Q：roadmap 变了，想删掉上次 plan 里还没做的项，重新规划？**  
用 `/pipeline-product-plan-reset`（或 `./scripts/plan-reset.sh`）。**soft** 只删 `planned` 等待办、保留 `done`；**full** 整阶段清空（done 写入 inventory §2）。然后 `/pipeline-product-plan` @`product-doc/product/roadmap.md`。  
与 **phase-close** 不同：phase-close 是阶段**全部 done** 后收束进下一 phase；plan-reset 是阶段**还没做完**或 **roadmap 变更** 时废弃未交付规划。

**Q：产品文档改了，某一 phase 要对齐并规划返工？**  
用 `/pipeline-product-phase-realign phase-N`，附上 roadmap 与变更说明。会先 `./scripts/phase-realign-prepare.sh` 快照并切换 `active_phase`；Agent 重写 phase 表并加 `## 对齐说明`。已 done 项默认**新建返工 ID**；若要 reopen 原包：`./scripts/feature-reopen.sh --feature <ID> --phase N`。

**Q：想改 Prompt 措辞？**  
只改 `handoff/pipeline/tasks.yaml` 里对应 `tasks.*.steps`，不要改七份 Skill 正文（Skill 只指向该文件）。
