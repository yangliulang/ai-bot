# Eval 证据 · `eval.runtime.pipeline_write_order`

> 对齐 [`product-doc/specs/requirements/evals/pipeline-write-order.md`](../../../../product-doc/specs/requirements/evals/pipeline-write-order.md) · **evalSetId** **`eval.runtime.pipeline_write_order`** · **version `0.1.0`**

## §1 本地运行登记

| 项 | 值 |
|----|-----|
| 运行日期 | 2026-05-28 |
| Git SHA | _（部署时填写）_ |
| 执行人 | backend-agent · test-agent（API 测复核） |
| 命令 | `cd server && uv run pytest tests/test_eval_pipeline_write_order.py tests/test_orchestration_freeze_align.py tests/test_write_path_pipeline.py -q` |
| 结果摘要 | **22 passed**（test-agent · eval 7 + freeze 8 + write_path 7）；backend 自测曾报 29（含 catalog 回归子集） |

## §2 Eval 登记

| 项 | 值 |
|----|-----|
| evalSetId | `eval.runtime.pipeline_write_order` |
| version | `0.1.0` |
| 正例 §2 | `test_eval_positive_synthetic_timeline` · `test_write_path_pipeline_delegates_to_eval_positive` **PASS** |
| 负例 P-N1 | `test_eval_pn1_rejects_write_before_confirm` **PASS** |
| 负例 P-N2 | `test_eval_pn2_rejects_spec_read_after_confirm` **PASS** |

## §3 依赖与 freeze 对拍

| 项 | 值 |
|----|-----|
| 依赖功能包 | `2026-05-27--runtime-write-path-pipeline` → **done** |
| freeze §3 场景 | `trade.spot.limit_order` · `trade.spot.flash_convert` · `trade.spot.amend_limit_order` |
| TC-06 结果 | **PASS**（`test_orchestration_freeze_align.py` · 10 tests） |
| OP-AO3 勾选 | **done**（product.accept · closure §7.6 C 组可勾选） |

## §4 Staging 扩展（P1 · 可选）

| executionId | 环境 | 备注 |
|-------------|------|------|
| _（可链 `telegram-write-path-staging` evidence `exec-3d132b3ad3ad44`）_ | staging | 非本包 AC 阻塞 |
