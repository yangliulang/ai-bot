# 管线 Eval + 编排 freeze 对拍

> 功能 ID：`2026-05-28--pipeline-eval-orchestration-align`  
> 产品 Agent 定稿 · Phase-3 **P0** · closure **OP-AO3** · W2 **`eval.runtime.pipeline_write_order`**

## 背景

Phase-2 已交付：

- **`2026-05-27--runtime-write-path-pipeline`**：Runtime **read_skill + 五段因果序**（pytest + Admin 断言）。
- **`2026-05-27--telegram-write-path-staging`**：**P-08** staging 走读证据（手工 **`executionId`** 登记）。

closure **W2** 仍要求 **所内可重复** 的 **`eval.runtime.pipeline_write_order`** 正/负例 runner，以及 **`runtime-freeze` §3** 与 **`orchestration_flow_catalog` / `GET …/agent/scenarios`** **自动化对拍**（**OP-AO3**），**不** 再重复 staging 手工填表为主交付。

本包把 **Eval GWT + freeze §3 编排下限** 固化为 **可执行模块 + pytest + 证据模板**，供 backend/test-agent 回归与 closure §7.6 **C 组** 勾选。

## 用户故事

- 作为 **Runtime/QA**，我希望一条命令跑通 **`eval.runtime.pipeline_write_order` §2 正例** 与 **§3 P-N1/P-N2 负例**，输出 **evalSetId `0.1.0`** 可登记结果。
- 作为 **产品/排障**，我希望 **`GET /api/v1/agent/scenarios/{scenarioId}`** 的 **`executionSteps`** **可静态断言** 满足 **`runtime-freeze` §3.1/3.2**（**`read.skill` 早于确认/写**）。
- 作为 **后端**，我新增 **`eval_pipeline_write_order`** 模块（或等价）**集中** 五段序断言，**复用** 于 `test_write_path_pipeline.py` 与 Admin Vitest 同源语义。

## 验收标准

- [x] **AC-1**：**`trade.spot.limit_order`**、**`trade.spot.flash_convert`**、**`trade.spot.amend_limit_order`** 的 **`GET /api/v1/agent/scenarios/{scenarioId}`** 返回 **200**；**`executionSteps[]`** 中 **`read.skill`** 的 **`order`** **严格小于** 首个含 **`confirm`** 或 **`write`** 语义之 **`stepKey`**（**`confirm.type_a`** / **`write.submit`** 等，见 catalog 真源）。
- [x] **AC-2**：新增 **`eval_pipeline_write_order`**（路径见 `backend/notes.md`）提供 **`assert_eval_pipeline_write_order_positive(events)`**，对符合 **`evals/pipeline-write-order.md` §2** 的 timeline **不抛错**；**`evalSetId=eval.runtime.pipeline_write_order`**、**`version=0.1.0`** 常量可导入。
- [x] **AC-3**：同一模块 **`assert_eval_pipeline_write_order_negative_pn1(events)`**（或等价）：timeline 在 **`user.confirmed` 之前** 出现 **`trading.exchange_private` 写类** → **AssertionError**（**SC-TA01** 方向）。
- [x] **AC-4**：同一模块 **`assert_eval_pipeline_write_order_negative_pn2(events)`**：**`agent.skill.spec_read` 时间不早于** **`confirmation.required`** → **AssertionError**（**SC-OBS11**）。
- [x] **AC-5**：**`server/tests/test_eval_pipeline_write_order.py`**（新）覆盖 AC-2～AC-4：**正例 synthetic timeline** + **两条负例** **P0 全绿**。
- [x] **AC-6**：**`server/tests/test_orchestration_freeze_align.py`**（新）或扩展现有 catalog 测试：对 AC-1 三 **`scenarioId`** **静态断言** catalog/API **stepKey 序** 与 **`runtime-freeze` §3.1/3.2** 一致（**read.skill → validate → … → confirm → write** 子序列存在）。
- [x] **AC-7**：**`eval/evidence/eval-pipeline-write-order.md`** **§1** 已填：**运行命令**、**日期**、**pytest 摘要**（pass/fail 计数）；**§2** 链 **`evalSetId` / version**；**§3** 声明依赖 **`runtime-write-path-pipeline`** **done**。
- [x] **AC-8**：**`GET /api/v1/admin/orchestration/policy`** 的 **`engineeringSpecRefs[]`** **含** 指向 **`runtime-freeze` §3**（或 **`specs/requirements/domains/agent/agent-orchestration/runtime-freeze.md` §3** 等价 URI/锚文本）；若存量已满足则测试 **文档化** 不断言回归破坏。

## 范围

### 本期包含

- **Eval 模块 + pytest**（AC-2～AC-6、AC-5）。
- **功能包 `eval/evidence/eval-pipeline-write-order.md`** 模板（AC-7）。
- **OpenAPI**：验收用 **`GET …/agent/scenarios/{scenarioId}`**、**`GET …/admin/orchestration/policy`**、**`GET …/timeline`**（只读 · 与 runtime 包一致）。
- **重构（可选）**：`write_path_pipeline.assert_write_path_pipeline_order` **委托** eval 模块，**行为不变**。
- **文档**：`backend/notes.md` 引用 **`evals/pipeline-write-order.md`**、**`runtime-freeze` §3**、**`pipeline-walkthrough-checklist` §2.10**。

### 本期不包含

- **staging 手工走读填表**（属 **`telegram-write-path-staging`**，已 **done**）。
- **新 Runtime 写行为**（read_skill 接线已 **done**）。
- **Gateway / CC-P1-07** 实现（所内工程仓 · **deferred**）。
- **全量 A 类写场景** catalog 扩面（仅 AC-1 三场景 + 可扩展测试 helper）。
- **改 `eval.runtime.pipeline_write_order` 规范正文**（仅实现对拍）。

## 界面与交互（无页面）

**含页面：否**。验收 = **pytest + scenarios API + eval 证据文件**；**不** 新增 Admin 路由。E2E 表 **N/A**。

## 非功能要求

- Eval 模块 **纯函数** 优先，**不** 依赖 Telegram/HTTP 侧效应（输入 = timeline 事件列表）。
- **不得** 在 evidence 写入 Secret / 规范全文。
- 与 **`BACKEND_SPEC` §2.1** 一致：时间字段 UTC。

## 实现备注

| 项 | 路径（计划） |
|----|----------------|
| Eval 断言 | `application/eval_pipeline_write_order.py`（新） |
| 既有五段序 | `application/write_path_pipeline.py` · `assert_write_path_pipeline_order` |
| Catalog | `application/orchestration_flow_catalog.py` |
| 测试 | `tests/test_eval_pipeline_write_order.py` · `tests/test_orchestration_freeze_align.py` |
| 规格 SSOT | `product-doc/specs/requirements/evals/pipeline-write-order.md` |
| Freeze SSOT | `product-doc/.../runtime-freeze.md` **§3.1～3.2** |
| 依赖包 | `handoff/features/2026-05-27--runtime-write-path-pipeline/` **done** |

## 待确认问题

- [x] Q1：与 **`telegram-write-path-staging`** 分工 — 本包 **自动化 Eval + freeze 对拍**；staging 包 **手工 evidence**。
- [x] Q2：**含页面：否** → `skips: [frontend.integrate, test.e2e, designer.review]`。
- [ ] Q3：所内 staging **可选** 在 evidence **§4** 追加 `executionId`（P1 · 非 AC 阻塞）。
