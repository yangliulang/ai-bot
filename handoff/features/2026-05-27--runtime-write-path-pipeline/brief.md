# 写路径管线（read_skill + 事件序）

> 功能 ID：`2026-05-27--runtime-write-path-pipeline`  
> 产品 Agent 定稿 · 对齐 closure **P‑04** / **P‑05** · W1 **MR-RT-B4**

## 背景

产品规格要求 **A 类写** 在 **类型 A 确认之前** 完成 **`read_skill_operation_spec`**（**FR-T11 / FR-AO04**），且 **同一 `executionId` 时间线** 须满足 **`eval.runtime.pipeline_write_order`** 五段因果序（**`execution.dispatched` → `agent.skill.spec_read` → `confirmation.required` → `user.confirmed` → 首条私域写**）。

当前 **`server/`** 已有 **`orchestration_flow_catalog`** 对 **`trade.spot.limit_order`** / **`trade.spot.amend_limit_order`** 登记 **`read.skill`** 步骤，但 **运行时未** 发射 **`agent.skill.spec_read`**，TG/HTTP 写路径 **未** 接线 **`read_skill_operation_spec`**，时间线 **不满足** Admin **`writePathPipelineOrder`** 断言。

本包交付 **生产 Runtime 编排接线 + 观测事件**，**不** 重复 **Skill Publish Admin API**（见 **`2026-05-27--skill-publish-effective`**）。

## 用户故事

- 作为 **交易员（Telegram）**，在限价下单前，系统应已读取 **已发布** 技能规范并展示类型 A 确认，避免未读规范即承诺下单。
- 作为 **运营/排障**，我能在 Admin **Observability 执行详情** 时间线看到 **`agent.skill.spec_read`** 且其 **早于** 确认与 **`trading.exchange_private`**，以便对拍走查清单。
- 作为 **后端/测试**，我希望 **`GET …/runtime/skill-operation-spec/effective`** 与 pytest **可断言** 事件序，与 **`product-doc`** **`pipeline-write-order`** 一致。

## 验收标准

- [x] **AC-1**：**`GET /api/v1/runtime/skill-operation-spec/effective?skillId=`**（可选 **`scenarioId`**）对 **已种子/已发布** 的 **`skill.spot.limit_order`** 返回 **200**，JSON 含 **`skillId`**、**`skillSpecVersion`**、**`specDigest`**、**`sections`**（§1～§6 摘要或全文指针），**不含** Secret；未发布/未知 skill 返回 **`403`** 或 **`404`**，**`code=PROMPT_SKILL_REF_INVALID`**（或文档约定的 **`AppError`** 码）。
- [x] **AC-2**：**Telegram** **`trade.spot.limit_order`** 完整回合（意图 → 类型 A Inline 确认 → 成交/拒单）在 **`executionId`** 时间线写入 **`agent.skill.spec_read`**，**`phase=success`**，payload 含 **`skillId`**、**`skillSpecVersion`**、**`specDigest`**（**禁止** 写入规范全文）。
- [x] **AC-3**：AC-2 同一时间线满足因果序：**`execution.dispatched`**（或 **`execution_accept` 等价起票事件**）**早于** **`agent.skill.spec_read`** **早于** **`confirmation.required`**（或 **`agent.orchestration.step`/`agent.execution.step` 含 `confirmKind=type_a*`** 之最早一条）**早于** **`user.confirmed`** **早于** 首条 **`trading.exchange_private`**（写类 **`exchangeOutcome`** 不限 success/fail）。
- [x] **AC-4**：AC-2 时间线含 **`agent.orchestration.step`**，**`stepKey=read.skill`**，且其 **时间不晚于** **`agent.skill.spec_read`**（允许同序紧邻）。
- [x] **AC-5**：**`GET /api/v1/admin/observability/executions/{executionId}/timeline`** 对 AC-2 的 **`executionId`** 返回 **200**，**`items[]`** 可按 **`createdAt`** 排序复现 AC-3（字段 **camelCase**，与 Admin 存量契约一致）。
- [x] **AC-6**：当 Runtime **无法解析有效 PUBLISHED 规范**（未知 **`skillId`** 或版本）时，**Telegram 写路径** 在 **类型 A 之前** 终止，**不** 产生 **`trading.exchange_private` 写**；用户可见 **FR-T05** 类拒答话术；时间线 **无** 成功 **`agent.skill.spec_read`**。
- [x] **AC-7**：**`trade.spot.amend_limit_order`** Telegram 改单确认路径同样满足 AC-2～AC-4（**`read.skill`** 已登记于 catalog）。
- [x] **AC-8**：**`POST /api/v1/agent/trade/spot/limit-order`**（HTTP 写，绑定用户）在成功/交易所拒单前，时间线 **同样** 满足 AC-3 五段序（**`source=http_api`**）。

## 范围

### 本期包含

- **`GET /api/v1/runtime/skill-operation-spec/effective`**（读 **PUBLISHED** 快照；首版可来自 **Alembic 种子 / 仓内 `runtime-bundle` 等**，与 Publish 包解耦）。
- **编排接线**：TG **`trade.spot.limit_order`**、**`trade.spot.amend_limit_order`**；HTTP **`POST …/limit-order`** 代表写路径。
- **时间线事件**：**`agent.skill.spec_read`**、规范化 **`confirmation.required`** / **`user.confirmed`**（与存量 **`agent.execution.step`** 对齐或映射，**须** 满足 Admin **`assertWritePathPipelineOrder`**）。
- **`agent.orchestration.step`**：**`read.skill`** 在写路径 emit。
- **测试**：pytest（Runtime 读 + TG/HTTP 写路径时间线序）；功能包 OpenAPI + **`test/*`** 追溯。
- **文档**：`backend/notes.md` 引用 **`BACKEND_SPEC`**、**`eval.runtime.pipeline_write_order`**。

### 本期不包含

- **Admin Publish API / 「技能与工具」页**（**`2026-05-27--skill-publish-effective`**）。
- **全量 A 类写场景** 一次性扩面（合约/条件单/杠杆等 **后续** 按 catalog 迭代；本包 **至少** 覆盖 AC-2/7/8 所列场景）。
- **改 `eval.runtime.pipeline_write_order` 规范本身**（仅实现对拍）。
- **TG 一键对账 / 504 UNKNOWN**（已 **`done`** 包覆盖）。

## 界面与交互（无页面）

**含页面：否**。验收依赖 **Admin Observability 存量执行详情页**（读时间线 API）；**不** 新增 Admin 路由。E2E 可为 **API + 时间线断言** 或 test-agent 标注 **N/A**（与契约收口包一致）。

## 非功能要求

- **不得** 在时间线/日志写入 API Secret、规范全文（仅 **`specDigest`** + 版本元数据）。
- **read_skill** 失败 **不得** 继续类型 A 或交易所写（**SC-OBS11**）。
- 与 **`BACKEND_SPEC` §2.1** 一致：时间字段 UTC。

## 实现备注

| 层 | 路径（计划） |
|----|----------------|
| Runtime 读 | `application/runtime_skill_operation_spec.py`（新）· router `api/routers/v1/runtime_skill.py` |
| 编排 / TG | `telegram_bound_reply.py` · `telegram_callback_handler.py` · `orchestration_steps.py` |
| 观测 | `agent_execution_events.py` · Admin `admin_observability.py`（只读验收） |
| Catalog | `orchestration_flow_catalog.py`（已含 `read.skill`） |
| 参考断言 | `product-doc/src/admin/.../writePathPipelineOrder.ts` |

## 待确认问题

- [x] Q1：首版 **PUBLISHED** 来源 — **DB 种子或 bundled JSON**，不阻塞 **`skill-publish-effective`** 后续切换指针。
- [x] Q2：**`confirmation.required` / `user.confirmed`** 可与存量 **`agent.execution.step`** **并存**，但 **eventName/transitionTrigger** **须** 满足 Admin 五段序断言（见 AC-3）。
