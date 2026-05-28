# Agent Pipeline 工作流

本仓库采用 **功能包（Feature Package）+ 契约驱动 + 状态机** 的多 Agent 协作方式。  
所有 Agent 通过 `handoff/features/2026-05-25--xxx/` 目录交接，不依赖聊天历史。

## 目录结构

```text
handoff/
├── WORKFLOW.md                 # 本文件：流转约定
├── pipeline/                   # 指挥层：COMMANDER.md + tasks.yaml
├── conventions/                # 各角色开发规范正文（见 conventions/README.md）
├── roadmap/                    # 阶段规划（产品 Agent 维护）
│   └── phase-1.md
├── templates/
│   ├── feature/                # 功能包模板
│   └── roadmap-phase.md        # 阶段规划模板
└── features/
    └── 2026-05-25--xxx/           # 每个功能一个独立目录
        ├── brief.md              # 产品：需求与验收标准
        ├── api.openapi.yaml      # 契约：接口定义（产品初稿，后端定稿）
        ├── status.yaml           # 状态机：当前阶段与下一负责人
        ├── backend/notes.md      # 后端：实现说明
        ├── test/cases.md         # 测试：API 用例
        ├── test/report.md        # 测试：API 报告
        ├── test/e2e-cases.md     # 测试：E2E / 页面验证用例
        ├── test/e2e-report.md    # 测试：E2E 验证报告
        ├── design/ui-review.md   # 设计师：UI 走查报告
        └── frontend/integration.md  # 前端：对接说明
```

## 阶段（phase）定义

| phase | 含义 | 负责 Agent | 完成后 next |
|-------|------|------------|-------------|
| `planned` | 产品已创建功能包，需求梳理中 | product-agent | product-agent |
| `contract_ready` | 需求与 API 契约已定稿 | product-agent → 全员可读 | backend-agent |
| `backend_in_progress` | 后端开发中 | backend-agent | backend-agent |
| `backend_done` | 后端实现完成，可测 | backend-agent | test-agent |
| `tested` | 接口测试通过 | test-agent | frontend-agent |
| `frontend_done` | 前端联调完成，待 E2E | frontend-agent | test-agent |
| `frontend_done` | E2E 未过，待前端返工 | test-agent | frontend-agent |
| `frontend_done` | E2E 返工完成，待复测 | frontend-agent | test-agent |
| `e2e_verified` | E2E 通过，待 UI 走查 | test-agent | designer-agent |
| `e2e_verified` | UI 走查 P0 未过，待前端修 | designer-agent | frontend-agent |
| `e2e_verified` | UI 返工完成，待复走查 | frontend-agent | designer-agent |
| `ui_reviewed` | UI 走查通过 | designer-agent | product-agent |
| `done` | 产品验收通过，功能闭环 | product-agent | — |

## 流转图

```text
planned
  → contract_ready     （产品：brief + api 定稿）
  → backend_in_progress（后端：开始实现）
  → backend_done       （后端：实现完成，交给测试）
  → tested             （测试：API 通过，交给前端）
  → frontend_done      （前端：页面对接完成，next: test-agent → 测试 E2E）
  → frontend_done      （E2E 失败：next: frontend-agent → 前端返工 → next: test-agent 复测）
  → e2e_verified       （测试：页面 E2E 通过，交给设计师）
  → ui_reviewed        （设计师：UI 走查通过，交给产品）
  → done               （产品：验收通过）
```

**并行说明**（契约就绪后）：

- 后端：按 `api.openapi.yaml` 实现接口
- 测试：基于 `brief.md` 写 `test/cases.md`，契约就绪后可写 contract test
- 前端：基于 `api.openapi.yaml` Mock 开发页面（不必等 backend_done）

**主路径交接**：后端 → test（API）→ 前端 → test（E2E）→ **设计师（UI 走查）** → 产品验收。产品仅在 `ui_reviewed` 后验收。

## status.yaml 字段说明

```yaml
feature: 2026-05-25--example        # 功能 ID，与目录名一致
title: 示例功能                   # 功能标题
phase: planned                   # 当前阶段（见上表）
owner: product-agent             # 当前负责 Agent
next: product-agent              # 下一阶段负责人 Agent
artifacts:                       # 关键产物路径（相对本功能目录）
  brief: brief.md
  api: api.openapi.yaml
blockers: []                     # 阻塞项；E2E/API 失败时写入，owner 与 next 对齐
history:                         # 流转记录（每次变更 append）
  - at: "2026-05-25T10:00:00+08:00"
    phase: planned
    by: product-agent
    note: 创建功能包
updated_at: "2026-05-25T10:00:00+08:00"
```

### Agent 名称约定

| Agent ID | 职责 |
|----------|------|
| `product-agent` | 阶段规划（roadmap）、功能包创建、需求定稿、最终验收 |
| `backend-agent` | 接口实现、更新 OpenAPI、backend/notes.md |
| `test-agent` | API 用例与执行、E2E 页面验证、test/report.md、test/e2e-report.md |
| `frontend-agent` | 页面对接、frontend/integration.md |
| `designer-agent` | UI 走查、design/ui-review.md |

市面岗位与各 Agent 擅长问题见 [handoff/pipeline/roles.md](pipeline/roles.md)。

## 阶段规划（roadmap）与功能包

**两层结构**：

| 层级 | 文件 | 职责 |
|------|------|------|
| 阶段 | `handoff/roadmap/phase-N.md` | 本阶段目标、功能 backlog、优先级、依赖 |
| 功能 | `handoff/features/2026-05-25--xxx/` | 单个功能的 brief、契约、状态机 |

**谁创建什么**：

- **roadmap**：产品 Agent 根据产品文档梳理（模式 1）
- **功能包目录**：产品 Agent 通过 `./scripts/new-feature.sh` 创建（模式 2）
- **brief + API 契约**：产品 Agent 定稿至 `contract_ready`（模式 2）
- **roadmap 状态同步**：产品 Agent 在定稿/验收时更新 backlog 表中的状态

**推荐节奏**：先规划 phase → 按优先级逐个建包定稿 → 后端/测试/前端并行开发 → 产品验收 → 下一个功能。

## 开发规范（与流转分离）

| 类型 | 位置 |
|------|------|
| 流转 / 门禁 / status | `.cursor/rules/*-agent.mdc` + 本文件 |
| 编码与测试约定（正文） | `handoff/conventions/*.md` |
| 编辑代码时自动附加 | `.cursor/rules/project.mdc`（全局）、`api-dev.mdc`、`web-dev.mdc`、`test-dev.mdc` |
| 单功能例外 | `handoff/features/2026-05-25--xxx/brief.md` 等 |

索引见 [handoff/conventions/README.md](conventions/README.md)。

## 各阶段交付物

### 产品 Agent（planned → contract_ready）

- [ ] `brief.md`：用户故事、验收标准（可测试表述）、范围边界
- [ ] `api.openapi.yaml`：路径、方法、请求/响应字段（可后续由后端微调）
- [ ] 更新 `status.yaml`：`phase: contract_ready`, `next: backend-agent`

### 后端 Agent（contract_ready → backend_done）

- [ ] 实现与 `api.openapi.yaml` 一致的接口
- [ ] 定稿 `api.openapi.yaml`（如有变更需注明）
- [ ] 填写 `backend/notes.md`：环境、鉴权、错误码、示例 curl
- [ ] 更新 `status.yaml`：`phase: backend_done`, `next: test-agent`

### 测试 Agent — API（backend_done → tested）

- [ ] 完善 `test/cases.md`
- [ ] 执行 API 测试，填写 `test/report.md`（通过/失败/阻塞）
- [ ] 更新 `status.yaml`：`phase: tested`, `next: frontend-agent`

### 前端 Agent（tested → frontend_done）

- [ ] 按 `api.openapi.yaml` 完成页面对接
- [ ] 填写 `frontend/integration.md`：页面路由、组件、接口映射
- [ ] 更新 `status.yaml`：`phase: frontend_done`, `next: test-agent`

### 测试 Agent — E2E（frontend_done → e2e_verified）

- [ ] 触发：`phase: frontend_done` 且 `next: test-agent`（`blockers` 应为空）
- [ ] 完善 `test/e2e-cases.md`（覆盖 brief 界面与 AC）
- [ ] 启动前后端，执行 E2E P0，填写 `test/e2e-report.md`
- [ ] 通过：更新 `status.yaml`：`phase: e2e_verified`, `next: designer-agent`
- [ ] 失败：保持 `frontend_done`，填写 `blockers` 与 `test/e2e-report.md`，**`next: frontend-agent`**（或 `backend-agent`）

### 设计师 Agent（e2e_verified → ui_reviewed）

- [ ] 触发：`phase: e2e_verified` 且 `next: designer-agent`
- [ ] 对照 `brief.md` 与 `frontend/integration.md` 走查页面，填写 `design/ui-review.md`
- [ ] 通过：更新 `status.yaml`：`phase: ui_reviewed`, `next: product-agent`
- [ ] P0 未过：保持 `e2e_verified`，`blockers` + **`next: frontend-agent`**

### 前端 Agent — UI 返工（e2e_verified，next: frontend-agent）

- [ ] 阅读 `design/ui-review.md` 与 `blockers`，修复 P0 视觉/交互问题
- [ ] 清空 `blockers`，保持 `phase: e2e_verified`，**`next: designer-agent`**（若影响 AC，备注需 test-agent 复测 E2E）

### 前端 Agent — E2E 返工（frontend_done，next: frontend-agent）

- [ ] 阅读 `test/e2e-report.md` 与 `blockers`，修复页面/对接
- [ ] 自测失败用例，更新 `frontend/integration.md`
- [ ] 清空 `blockers`，保持 `phase: frontend_done`，**`next: test-agent`**

### 产品 Agent 验收（ui_reviewed → done）

- [ ] 对照 `brief.md` 验收标准确认
- [ ] 更新 `status.yaml`：`phase: done`, `next: null`

## 创建新功能

**推荐（产品 Agent 或你本地执行）**：

```bash
./scripts/new-feature.sh 2026-05-25--user-profile "用户资料查看/编辑"
```

**手动方式**：

```bash
cp -r handoff/templates/feature handoff/features/2026-05-25--your-feature
# 编辑 status.yaml 中的 feature、title
```

### Agent 标准 Prompt

指挥官操作见 [handoff/pipeline/COMMANDER.md](pipeline/COMMANDER.md)；任务索引见 [handoff/PROMPTS.md](PROMPTS.md)。

**产品 Agent — 阶段规划**：

```text
你是 product-agent。阅读 handoff/WORKFLOW.md 与 .cursor/rules/product-agent.mdc。
根据 {产品文档路径或描述}，创建或更新 handoff/roadmap/phase-1.md：
输出本阶段目标、功能 backlog（含 功能 ID、优先级、依赖），暂不写详细 API。
```

**模式 2 — 建包定稿（按 roadmap 优先级）**：

```text
你是 product-agent。阅读 handoff/roadmap/phase-1.md，取优先级最高且状态为 planned 的功能。
若功能包不存在则运行 scripts/new-feature.sh 创建；
完成 brief.md、api.openapi.yaml，更新 status.yaml 至 contract_ready，
并同步更新 roadmap 中的状态。
```

**模式 3 — 验收**：

```text
你是 product-agent。处理 handoff/features/{feature-id}/，phase 为 ui_reviewed。
对照 brief.md 与 design/ui-review.md 验收，通过后 status.yaml 设为 done，并更新 roadmap。
```

然后对产品 Agent 说（单功能，兼容旧流程）：

> 请处理 `handoff/features/2026-05-25--your-feature/`，阅读 status.yaml，完成 planned 阶段的需求梳理，产出 brief.md 和 api.openapi.yaml，完成后更新 status.yaml 进入 contract_ready。

## 给 Agent 的通用指令模板

```text
请处理 handoff/features/{feature-id}/：
1. 读取 status.yaml，确认 phase 与 next 是否匹配你的角色
2. 只修改本功能目录下的文件
3. 完成后更新 status.yaml（phase、owner、next、history、updated_at）
4. 不要依赖聊天历史，以目录内文件为准
```
