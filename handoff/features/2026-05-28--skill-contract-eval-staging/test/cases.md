# 测试用例（API + Eval pytest）

> test-agent 在 `backend_done` 后：跑 **TC-01～TC-07** pytest + 审查 **TC-09** evidence 模板。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | P0 evalSetId 列表 | 导入 `eval_skill_contract`；读取 `EVAL_SKILL_P0_SET_IDS`、`EVAL_VERSION` | **4** 条 id 与 `skill-contract.md` §3 一致；**version=`0.1.0`** | P0 |
| TC-02 | AC-2 | 缺数量 | 对 `skill.spot.limit_order` + slots `{symbol, side, price}`（无 qty）调 `assert_eval_skill_missing_qty_no_confirm` | **不抛错**；`can_proceed_to_type_a=False`；`write_allowed=False` | P0 |
| TC-03 | AC-3 | 闪兑带价 | 对 `skill.spot.flash_convert` + slots 含 `price` 调 `assert_eval_skill_flash_no_limit_price` | **不抛错**；门禁 **拒绝**（reason 含 flash/limit） | P0 |
| TC-04 | AC-4 | 双确认 | `assert_eval_skill_margin_double_confirm(1)` 与 `(2)` | **1** → `margin_cross_write_allowed=False`；**2** → **True** | P0 |
| TC-05 | AC-5 | 改单序 | `assert_eval_skill_amend_cancel_before_order(["order","cancel"])` | **AssertionError**；`["cancel","order"]` **不抛错** | P0 |
| TC-06 | AC-6 | P0 fixtures | 对 `fixtures.ts` 同窗四条 fixture 各调 `run_eval_skill_p0_fixture` | **全不抛错**；`expectTypeA`/`expectWrite` 与断言一致 | P0 |
| TC-07 | AC-7 | pytest 套件 | `cd server && uv run pytest tests/test_eval_skill_contract.py -q` | **全通过**（含 P1 边界） | P0 |
| TC-08 | AC-8 | effective Given | `GET /api/v1/runtime/skill-operation-spec/effective?skillId=skill.spot.limit_order` | **200**；`bodyMarkdown` 非空；已 **PUBLISHED** | P0 |
| TC-09 | AC-9 | 证据模板 | 打开 `eval/evidence/eval-skill-contract-p0.md` §1～§3 | 命令、日期、pytest 摘要、四条 evalSetId、依赖包 **done** 已填 | P0 |
| TC-10 | AC-4 | 边界 P1 | `margin_cross_write_allowed(0)` | **False** | P1 |

## 契约测试

- [x] TC-07 pytest green
- [x] TC-08 effective 200 + 全文
- [x] TC-06 四 P0 fixture 同窗

## 自动化映射

| 用例 | pytest / 文件 |
|------|----------------|
| TC-01～TC-07, TC-10 | `tests/test_eval_skill_contract.py` |
| TC-08 | `tests/test_eval_skill_contract.py` 或 `tests/test_runtime_skill_operation_spec.py` |
| TC-09 | `eval/evidence/eval-skill-contract-p0.md`（审查） |
