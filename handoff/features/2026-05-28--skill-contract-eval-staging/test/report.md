# 测试报告（API）

> test-agent · `backend_done` → `tested` · 2026-05-28

## 概要

- 执行时间：2026-05-28T17:00:00+0800
- 执行人：test-agent
- 环境：本地 pytest（`httpx` ASGI client + DB seed from `runtime-bundle.json`）；Base URL `http://127.0.0.1:8080`
- 结论：✅ **通过**

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 9 (P0) | 9 | 0 | 0 | 0 |

| ID | AC | 场景 | 结果 | 备注 |
|----|-----|------|------|------|
| TC-01 | AC-1 | P0 evalSetId 列表 | ✅ | `EVAL_SKILL_P0_SET_IDS` 4 条 · `EVAL_VERSION=0.1.0` · `test_eval_skill_p0_constants` |
| TC-02 | AC-2 | 缺数量 | ✅ | `test_missing_qty_no_confirm` · Type A / write 均阻断 |
| TC-03 | AC-3 | 闪兑带价 | ✅ | `test_flash_no_limit_price` · reason=`flash_convert_must_not_carry_limit_price` |
| TC-04 | AC-4 | 双确认 | ✅ | `test_margin_double_confirm` · count=1→False · count=2→True |
| TC-05 | AC-5 | 改单序 | ✅ | `test_amend_cancel_before_order_valid` / `_invalid` |
| TC-06 | AC-6 | P0 fixtures | ✅ | 4× `test_run_eval_skill_p0_fixture[…]` **PASS**（同窗 `fixtures.ts`） |
| TC-07 | AC-7 | pytest 套件 | ✅ | **14 passed** · `tests/test_eval_skill_contract.py` |
| TC-08 | AC-8 | effective Given | ✅ | `test_runtime_effective_given_skill_spot_limit_order` · **200** · `lifecycle=PUBLISHED` · sections 非空 |
| TC-09 | AC-9 | 证据模板 | ✅ | `eval/evidence/eval-skill-contract-p0.md` §1～§3 已填；test-agent 复核通过 |

### P1（可选）

| ID | 结果 | 备注 |
|----|------|------|
| TC-10 | ✅ | `test_margin_cross_write_allowed_zero_p1` · `test_amend_sequence_missing_cancel_p1` |

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | 无 | — | — |

## 备注

- TC-08 响应为存量 API 形状（`sections[].bodyMarkdown`），非顶层 `bodyMarkdown`；与 `runtime_skill.py` 一致，内容非空已断言。
- TC-06 附加：`test_agent_scenario_p0_fixture_ids` 四场景 **200**。
- 本包 `skips` 含 `frontend.integrate` / `test.e2e` / `designer.review`（API-only）；推进 **`tested`** 后请指挥官执行 **`/pipeline-skip 2026-05-28--skill-contract-eval-staging`**，勿开前端 Chat。
