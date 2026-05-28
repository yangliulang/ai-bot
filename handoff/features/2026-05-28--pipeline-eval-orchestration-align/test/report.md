# 测试报告（API）

> test-agent · `backend_done` → `tested` · 2026-05-28

## 概要

- 执行时间：2026-05-28T14:30:00+0800
- 执行人：test-agent
- 环境：本地 `http://127.0.0.1:8080`（`cd server && uv run chainup-agent-api` 已运行）；Admin JWT 已配置（`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`）
- 结论：✅ **通过**

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 8 (P0) | 8 | 0 | 0 | 0 |

| ID | AC | 场景 | 结果 | 备注 |
|----|-----|------|------|------|
| TC-01 | AC-1 | 三场景 catalog 序 | ✅ | `limit_order` / `flash_convert` / `amend_limit_order` 均 **200**；`read.skill` order=2 < 首个 confirm/write order=5 |
| TC-02 | AC-2 | Eval 正例 | ✅ | `test_eval_pipeline_write_order.py` · synthetic timeline 不抛错；`EVAL_SET_ID` / `EVAL_VERSION` 可导入 |
| TC-03 | AC-3 | P-N1 负例 | ✅ | `test_eval_pn1_rejects_write_before_confirm` **PASS** |
| TC-04 | AC-4 | P-N2 负例 | ✅ | `test_eval_pn2_rejects_spec_read_after_confirm` **PASS** |
| TC-05 | AC-5 | pytest eval 套件 | ✅ | **7 passed** · `tests/test_eval_pipeline_write_order.py` |
| TC-06 | AC-6 | freeze 对拍 | ✅ | **8 passed** · `tests/test_orchestration_freeze_align.py`（含 catalog + API 子序列断言） |
| TC-07 | AC-7 | 证据模板 | ✅ | `eval/evidence/eval-pipeline-write-order.md` §1～§3 已填；test-agent 复核通过 |
| TC-08 | AC-8 | policy refs | ✅ | **200** + Bearer；`engineeringSpecRefs[0]` 含 `runtime-freeze.md §3` |

### P1（可选）

| ID | 结果 | 备注 |
|----|------|------|
| TC-09 | ✅ | `test_write_path_pipeline.py` **7 passed**（eval 委托后无回归） |

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | 无 | — | — |

## 备注

- TC-08 需 Admin Bearer（本地 `.env` 控制台账号）；pytest 用例在无 JWT secret 时匿名 **200**，与 live curl 行为一致于契约。
- 本包 `skips` 含 `frontend.integrate` / `test.e2e` / `designer.review`（API-only）；推进 **`tested`** 后请指挥官执行 **`/pipeline-skip 2026-05-28--pipeline-eval-orchestration-align`**，勿开前端 Chat。
