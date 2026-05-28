# Eval 证据 · `eval.skill.*` P0 回归束

> 对齐 [`product-doc/specs/requirements/evals/skill-contract.md`](../../../../product-doc/specs/requirements/evals/skill-contract.md) **§3** · **version `0.1.0`**

## §1 本地运行登记

| 项 | 值 |
|----|-----|
| 运行日期 | 2026-05-28 |
| Git SHA | _（部署时填写）_ |
| 执行人 | backend-agent · test-agent（API 测复核） |
| 命令 | `cd server && uv run pytest tests/test_eval_skill_contract.py -q` |
| 结果摘要 | **14 passed** |

## §2 Eval 登记（P0 四束）

| evalSetId | version | pytest / 断言 | 结果 |
|-----------|---------|---------------|------|
| `eval.skill.missing_qty_no_confirm` | `0.1.0` | `test_missing_qty_no_confirm` | PASS |
| `eval.skill.flash_no_limit_price` | `0.1.0` | `test_flash_no_limit_price` | PASS |
| `eval.skill.margin_double_confirm` | `0.1.0` | `test_margin_double_confirm` | PASS |
| `eval.skill.amend_cancel_before_order` | `0.1.0` | `test_amend_cancel_before_order_valid` | PASS |

## §3 依赖与 Given

| 项 | 值 |
|----|-----|
| 依赖功能包 | `2026-05-27--skill-publish-effective` → **done** |
| 管线 Eval | `2026-05-28--pipeline-eval-orchestration-align` → **done** |
| Effective Given | `GET …/runtime/skill-operation-spec/effective?skillId=skill.spot.limit_order` → **200** |
| Vitest 同窗 | `product-doc/src/admin/src/skillContract/skillContract.contract.test.ts`（演示门卫 · 非阻塞） |
| OP-SKILL B / SK-B03 | **done**（product.accept · closure §7.6 B 组可勾选） |

## §4 Staging 扩展（P1 · 可选）

| executionId | 环境 | 备注 |
|-------------|------|------|
| _（可链 Observability 写路径 demo）_ | staging | 非本包 AC 阻塞 |
