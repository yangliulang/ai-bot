# Skill 契约 Eval staging

> 功能 ID：`2026-05-28--skill-contract-eval-staging`  
> 产品 Agent 定稿 · Phase-3 **P1** · closure **OP-SKILL B** · W3 **SK-B03** · **`eval.skill.*` P0 真跑**

## 背景

Phase-2 / Phase-3 已交付：

- **`2026-05-27--skill-publish-effective`**：**Publish 生效链** · Runtime **`GET …/skill-operation-spec/effective`** 读 DB **PUBLISHED** 全文。
- **`2026-05-27--runtime-write-path-pipeline`**：**read_skill + 五段因果序**（与 **`eval.runtime.pipeline_write_order`** 分工明确）。
- **`2026-05-28--pipeline-eval-orchestration-align`**：**管线 Eval + freeze §3 对拍**（**done**）。

closure **W3** / **SK-B03** 仍要求 **所内可重复** 的 **`eval.skill.*` P0 回归束** 真跑证据（**非** 仅 product-doc Vitest 演示门卫）。规格 SSOT：[`evals/skill-contract.md`](../../../product-doc/specs/requirements/evals/skill-contract.md) **§3 最小回归束**（4 条 **`evalSetId`**）。

本包把 **槽位门禁 / 分流 / 双确认 / 改单序** 固化为 **Python eval 模块 + pytest + 证据模板**，与 **`product-doc/src/admin/src/skillContract/`** Vitest **同窗 fixture**，供 backend/test-agent 回归与 closure **§7.6 B 组** 勾选。

## 用户故事

- 作为 **Runtime/QA**，我希望一条命令跑通 **`eval.skill.*` §3 P0 四条**，输出 **`evalSetId` + `0.1.0`** 可登记结果。
- 作为 **产品/排障**，我希望 **`GET /api/v1/runtime/skill-operation-spec/effective?skillId=`** 对已 Publish 技能返回 **contract-complete 全文**（Eval **Given** §2.1），与槽位门禁 **同窗** 验收。
- 作为 **后端**，我新增 **`eval_skill_contract`** 模块（或等价）**集中** P0 断言，**语义对齐** Vitest **`gates.ts` + `fixtures.ts`**，**不** 替代生产 Orchestration DAG。

## 验收标准

- [x] **AC-1**：新增 **`eval_skill_contract`**（路径见 `backend/notes.md`）暴露 **`EVAL_SKILL_P0_SET_IDS`**（**4** 条，与 [`skill-contract.md` §3](../../../product-doc/specs/requirements/evals/skill-contract.md) 一致）及 **`EVAL_VERSION = "0.1.0"`** 常量。
- [x] **AC-2**：**`assert_eval_skill_missing_qty_no_confirm(skill_id, slots)`**：`skill.spot.limit_order` + **缺 `quantity`/`quoteQty`** → **不得** 进入类型 A（`can_proceed_to_type_a=False`）；**不得** 允许写（`write_allowed=False`）。
- [x] **AC-3**：**`assert_eval_skill_flash_no_limit_price(skill_id, slots)`**：`skill.spot.flash_convert` + **含 `price`** → **拒绝**（与 Vitest **`flash_convert_must_not_carry_limit_price`** 同窗）；**0** 类型 A / **0** 写。
- [x] **AC-4**：**`assert_eval_skill_margin_double_confirm(confirm_count)`**：**`confirm_count < 2`** → **`margin_cross_write_allowed=False`**；**`= 2`** → **`True`**（**SC-CH-TG-MARGIN-01** 方向）。
- [x] **AC-5**：**`assert_eval_skill_amend_cancel_before_order(actions)`**：序列 **须** **`cancel` 索引 < `order` 索引**；否则 **AssertionError**（**runtime-freeze §3.7** · **SC-CH-TG-SPOT-06**）。
- [x] **AC-6**：**`run_eval_skill_p0_fixture(fixture)`**（或等价）：对 **`fixtures.ts` 同窗** 四条 **`SkillEvalFixture`** **不抛错**；若 **`expectTypeA=false`** 则门禁 **ok=False**；若 **`expectWrite=false`** 则写门禁 **False**。
- [x] **AC-7**：**`server/tests/test_eval_skill_contract.py`**（新）覆盖 AC-2～AC-6：**P0 全绿**；含 **至少 1 条 P1** 边界（如 **`margin_cross_write_allowed(0)`** 或 **改单序缺 cancel**）。
- [x] **AC-8**：**`GET /api/v1/runtime/skill-operation-spec/effective?skillId=skill.spot.limit_order`**（seed/import 后）→ **200**，**`bodyMarkdown`** 非空，**`lifecycle`/指针** 为 **PUBLISHED**（Eval **Given** §2.1）。
- [x] **AC-9**：**`eval/evidence/eval-skill-contract-p0.md`** **§1** 已填：**运行命令**、**日期**、**pytest 摘要**；**§2** 链 **四条 `evalSetId` / version**；**§3** 声明依赖 **`skill-publish-effective`** **done** 与 **`pipeline-eval-orchestration-align`** **done**。

## 范围

### 本期包含

- **Eval 模块 + pytest**（AC-1～AC-7）。
- **功能包 `eval/evidence/eval-skill-contract-p0.md`** 模板（AC-9）。
- **OpenAPI**：验收用 **`GET …/runtime/skill-operation-spec/effective`**、**`GET …/agent/scenarios/{scenarioId}`**（只读 · 场景路由对照）。
- **文档**：`backend/notes.md` 引用 **`evals/skill-contract.md`**、**`production-runtime.md` §3**、Vitest **`skillContract/`** 路径。
- **可选**：从 Vitest **`gates.ts`** 抽 **Python 等价**（本包 **须** 行为对齐，**不要求** TS 运行时调用）。

### 本期不包含

- **全量 10 条 `eval.skill.*`** 扩面（仅 §3 P0 四束；其余随矩阵冻结另开）。
- **Telegram 真机 / 编排 DAG 真节点**（所内 BFF · **MR-B4**）。
- **新 Publish / Admin UI**（**skill-publish-effective** 已 **done**）。
- **改 `eval.skill.*` 规范正文**（仅实现对拍）。
- **Gateway / CC-P1-07**（deferred）。

## 界面与交互（无页面）

**含页面：否**。验收 = **pytest + effective 读 API + eval 证据文件**；**不** 新增 Admin 路由。E2E 表 **N/A**。

## 非功能要求

- Eval 模块 **纯函数** 优先，**不** 依赖 Telegram/HTTP 侧效应（输入 = slots / confirm_count / action 序列）。
- **不得** 在 evidence 写入 Secret / 规范全文。
- 与 **`BACKEND_SPEC` §2.1** 一致：时间字段 UTC。

## 实现备注

| 项 | 路径（计划） |
|----|----------------|
| Eval 断言 | `application/eval_skill_contract.py`（新） |
| 槽位门禁（可对齐） | `application/skill_contract_gates.py`（新 · 或合入 eval 模块） |
| Vitest 同窗 | `product-doc/src/admin/src/skillContract/gates.ts` · `fixtures.ts` |
| 测试 | `tests/test_eval_skill_contract.py` |
| Effective 读 | 存量 `runtime_skill_operation_spec.py` · **skill-publish-effective** |
| 规格 SSOT | `product-doc/specs/requirements/evals/skill-contract.md` |
| 依赖包 | `2026-05-27--skill-publish-effective/` **done** · `2026-05-28--pipeline-eval-orchestration-align/` **done** |

## 待确认问题

- [x] Q1：与 **`pipeline-eval-orchestration-align`** 分工 — 本包 **Skill 槽位/确认/改单序**；管线包 **五段因果序**。
- [x] Q2：**含页面：否** → `skips: [frontend.integrate, test.e2e, designer.review]`。
- [ ] Q3：所内 staging **可选** 在 evidence **§4** 追加 **`executionId`**（P1 · 非 AC 阻塞）。
