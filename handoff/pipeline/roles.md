# 岗位与 Agent 对照

> **给人看**：市面岗位、擅长解决什么问题、与 [agency-agents](https://github.com/msitarzewski/agency-agents) 的对应关系。  
> **给 Agent 用**：角色边界仍只由 `.cursor/rules/*-agent.mdc` + `tasks.yaml` 决定；本文件的「借鉴能力」须在门禁内发挥，**不得**因能力列表越权改 phase 或他人目录。

## 文档放哪里？（结论）

| 内容 | 放哪里 | 不放哪里 |
|------|--------|----------|
| 岗位画像、擅长/不擅长、agency 对照 | **`roles.md`（本文件）** | `tasks.yaml` |
| 可执行步骤与 status 推进 | `tasks.yaml` | `roles.md` |
| 编码/测试写法 | `handoff/conventions/*.md` | `roles.md` 长文示例 |
| agency 完整人格与 144 个角色原文 | 链到上游仓库 | 勿整包拷贝进本仓库 |

若借鉴条目继续增多，可拆附录：`handoff/pipeline/agency-reference.md`；主表仍保留在本文件。

---

## 一览表（本仓库 Agent）

| Agent ID | 市面岗位 | 擅长解决什么问题 | 本仓库主要产出 | 典型 Skill |
|----------|----------|------------------|----------------|------------|
| `product-agent` | PM / PO | scope、AC、排期、签收 | `roadmap/`、`brief.md`、`api.openapi.yaml` | `pipeline-product-*` |
| `backend-agent` | 后端 / 架构（实现侧） | 契约落地、API、联调说明 | `apps/api/`、`backend/notes.md` | `pipeline-backend` |
| `test-agent` | QA / 质量工程师 | 用例、门禁、缺陷指派 | `test/*` | `pipeline-test-*` |
| `frontend-agent` | 前端工程师 | 页面、联调、返工 | `apps/web/`、`frontend/integration.md` | `pipeline-frontend-*` |
| `designer-agent` | UI/UX（走查） | 视觉/交互一致性、放行设计 | `design/ui-review.md` | `pipeline-designer-*` |

指挥官 ≈ **Tech Lead / 发布负责人**：`status.yaml` + `COMMANDER.md` + `/pipeline-next`。

---

## 与 agency-agents 的对照（与本流水线相关）

上游按 **12 个 Division** 组织约 144 个角色；本仓库 **5 个 Agent** 只覆盖「软件交付主路径」。下表为 **主要映射**（一对多）；未列入的 Division 见文末「暂不纳入」。

| 本仓库 Agent | agency-agents Division | 主要对应的 Specialist（上游文件名） | 在本流水线中的用法 |
|--------------|------------------------|-------------------------------------|-------------------|
| `product-agent` | **Product** | Product Manager、Sprint Prioritizer、Feedback Synthesizer、Trend Researcher | 规划 backlog、写 brief/AC、定稿契约、最终验收 |
| `product-agent` | **Project Management**（部分） | Senior Project Manager、Project Shepherd | 阶段节奏、依赖顺序（写入 roadmap，不替代 status 机） |
| `backend-agent` | **Engineering** | Backend Architect、Senior Developer（实现）、API 相关 | 实现 OpenAPI；**不**默认承担 DevOps/SRE/安全审计全流程 |
| `frontend-agent` | **Engineering** | Frontend Developer、Rapid Prototyper（MVP 页面） | 页面与联调；快速原型仅 `frontend.mock` 可选 |
| `test-agent` | **Testing** | API Tester、Test Results Analyzer、Evidence Collector、Reality Checker | API/E2E 与报告；Reality Checker 精神用于 **可否推进 phase** |
| `test-agent` | **Testing**（可选深化） | Accessibility Auditor、Performance Benchmarker | P1：a11y/性能写入报告，不单独占 Agent |
| `designer-agent` | **Design** | UI Designer、UX Researcher、UX Architect、Brand Guardian（一致性） | E2E 通过后的 **ui-review**；不做全套品牌战役 |
| `designer-agent` | **Design**（不默认） | Whimsy Injector、Image Prompt Engineer | 仅当 brief 明确要求趣味/插画时作 P1 建议 |

**一对多说明**：agency 角色是「人格化专家库」；本仓库是「状态机 + 文件交接」。借鉴的是 **能力域与交付物类型**，不是把 144 个角色都接进流水线。

---

## 分角色：职责 + 借鉴能力（已按本仓库协同规范裁剪）

### product-agent

**市面岗位**：产品经理、产品负责人。

**擅长**

- 阶段 backlog、功能优先级与依赖
- 用户故事、**可测试 AC**、本期包含/不包含
- API 契约初稿、验收闭环

**从 agency-agents 借鉴的能力**（在 `contract_ready` / `ui_reviewed` 门禁内）

| 上游角色 | 借鉴点 | 在本仓库的落点 |
|----------|--------|----------------|
| Product Manager | 全生命周期：发现 → PRD 级叙述 → 结果度量 | `brief.md` 用户故事与 AC |
| Sprint Prioritizer | 优先级、资源取舍 | `roadmap/phase-N.md` backlog 排序 |
| Feedback Synthesizer | 反馈归纳为用户洞察 | brief「待确认」、AC 修订（不改 status 越权） |
| Trend Researcher | 市场/竞品扫一眼 | 模式 1 规划时的 backlog 备注，不写长篇研报 |
| Senior Project Manager |  realistic scope | 单功能定稿，**一次一个** `contract_ready` |

**不做**：实现代码、测试执行、UI 像素走查。

**何时喊**：`planned` → 定稿；`ui_reviewed` → 验收。

---

### backend-agent

**市面岗位**：后端工程师、服务端开发（实现侧）。

**擅长**

- OpenAPI 落地、统一响应、错误码、CORS
- `backend/notes.md`（curl、启动、差异说明）

**从 agency-agents 借鉴的能力**

| 上游角色 | 借鉴点 | 在本仓库的落点 |
|----------|--------|----------------|
| Backend Architect | API/数据模型意图、可扩展接口形状 | 实现与 `api.openapi.yaml` 一致 |
| Senior Developer | 复杂边界、清晰实现 | `apps/api/` 可读实现 |
| Technical Writer（工程向） | 可复制的调用说明 | `backend/notes.md` |
| Code Reviewer（自检） | 提交前自查安全/可维护 | 自测通过再 `backend_done` |

**默认不纳入本 Agent**（需另开 Chat / 未来 Agent）：DevOps Automator、SRE、Security Engineer 专职审计、Database Optimizer 专职调优。

**何时喊**：`next: backend-agent`。

---

### test-agent

**市面岗位**：QA、测试开发、质量工程师。

**擅长**

- `test/cases.md`、`test/e2e-cases.md` 与 AC 对齐
- P0 门禁、`test/report.md` / `test/e2e-report.md`
- 失败 → `blockers` + 正确 `next`

**从 agency-agents 借鉴的能力**

| 上游角色 | 借鉴点 | 在本仓库的落点 |
|----------|--------|----------------|
| API Tester | 契约与集成验证 | `test.api`、schema 对照 OpenAPI |
| Test Results Analyzer | 指标化结论、覆盖说明 | 报告「结果汇总」表 |
| Evidence Collector | 可复现证据（请求/截图/步骤） | 报告「实际」列、失败明细 |
| Reality Checker | 证据够才放行 | 未全 P0 通过 **禁止** `tested` / `e2e_verified` |
| Accessibility Auditor | WCAG 粗查 | E2E 时 P1 记入 `e2e-report` |
| Performance Benchmarker | 关键路径耗时 | P1 备注，不阻塞试跑主路径 |

**不做**：改 brief 范围、代替设计定稿。

**何时喊**：`backend_done`（API）、`frontend_done`（E2E）。

---

### frontend-agent

**市面岗位**：前端工程师、Web 客户端开发。

**擅长**

- 路由、表单、loading/错误态
- Mock → 真实 API 联调
- 测试/设计返工

**从 agency-agents 借鉴的能力**

| 上游角色 | 借鉴点 | 在本仓库的落点 |
|----------|--------|----------------|
| Frontend Developer | React/Vue 实现、性能与可访问性基础 | `apps/web/`、`conventions/frontend.md` |
| Rapid Prototyper | 快速页面验证想法 | `frontend.mock`（不改 status） |
| UX Architect（实现侧） | 与 brief 一致的交互结构 | `frontend/integration.md` |

**不做**：修改已定稿 OpenAPI（发现问题交 product/backend）。

**何时喊**：`tested` 联调；`frontend.fix-*` 返工。

---

### designer-agent

**市面岗位**：UI 设计师、UX 设计师（**实现后走查**，非纯视觉稿阶段）。

**擅长**

- 对照 brief 走查已上线页面
- P0/P1/P2、`design/ui-review.md`
- 阻塞或 `ui_reviewed`

**从 agency-agents 借鉴的能力**

| 上游角色 | 借鉴点 | 在本仓库的落点 |
|----------|--------|----------------|
| UI Designer | 组件层次、视觉一致性 | `ui-review` 检查项 |
| UX Researcher | 任务路径是否顺畅 | 对照 brief 主流程 |
| UX Architect | 状态是否完整（loading/错误） | 与 E2E 互补，偏视觉与反馈 |
| Brand Guardian | 文案语气、品牌一致 | brief 未覆盖时的 P1 |
| Whimsy Injector | 适度趣味 | 仅 P2，不阻塞发布 |

**不做**：默认不改 `apps/web/`；不改 AC/API。

**何时喊**：`e2e_verified` 且 `next: designer-agent`。

---

## agency-agents 暂不纳入本流水线（供扩展）

以下 Division 与当前 **功能包 + apps/api + apps/web** 主路径无直接 `status.yaml` 交接，**不要**强行塞进现有 5 个 Agent；若未来需要，应 **新增 Agent + tasks + Skill**，而不是写进 `backend.implement` 的 steps：

- Marketing、Paid Media、Sales、Finance、Support（运营/财报）
- Game Development、Spatial Computing、Academic
- Engineering 中的 DevOps / AI Engineer / 嵌入式 / 区块链等垂直岗
- Specialized 中的 Agents Orchestrator（本仓库由 **指挥官 + pipeline-next** 承担编排）

需要时可在 [agency-agents 仓库](https://github.com/msitarzewski/agency-agents) 查阅完整角色表，再单独立项映射。

---

## 与仓库其它文档的分工

| 文档 | 写什么 |
|------|--------|
| **本文件** | Who、解决什么问题、agency 能力借鉴（边界内） |
| `tasks.yaml` | 可执行步骤、phase 目标 |
| `COMMANDER.md` | 你怎么调用 |
| `WORKFLOW.md` | 状态机 |
| `conventions/*.md` | 代码怎么写 |
| `*-agent.mdc` | 门禁 + 链接本文件 |

---

## 扩展与引用

- 新增本仓库 Agent：先更新本表与 agency 映射，再 `tasks.yaml` + Skill。
- 上游项目：[msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)（MIT）。借鉴理念与角色分工，执行仍以本仓库 `status.yaml` 为准。
- 一人多岗：分 Chat、分 Skill，不按人头合并 phase。
