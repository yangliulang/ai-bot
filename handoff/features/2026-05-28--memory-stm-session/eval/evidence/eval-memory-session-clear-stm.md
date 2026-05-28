# Eval 证据 · `eval.memory.*` STM P0

> 对齐 [`product-doc/specs/requirements/evals/memory-runtime.md`](../../../../product-doc/specs/requirements/evals/memory-runtime.md) **§4** · **version `0.1.0`**

## §1 本地运行登记

| 项 | 值 |
|----|-----|
| 运行日期 | 2026-05-27 |
| Git SHA | _（部署时填写）_ |
| 执行人 | backend-agent |
| 命令 | `cd server && uv run pytest tests/test_eval_memory_stm.py -q` |
| 结果摘要 | **10 passed** |

## §2 Eval 登记（P0 二束）

| evalSetId | version | pytest / 断言 | 结果 |
|-----------|---------|---------------|------|
| `eval.memory.session_clear_stm` | `0.1.0` | `test_session_clear_stm_gwt` | PASS |
| `eval.memory.stm_vs_ltm_intent` | `0.1.0` | `test_stm_vs_ltm_intent_routing` | PASS |

## §3 依赖与 Given

| 项 | 值 |
|----|-----|
| 依赖功能包 | `2026-05-28--prompt-runtime-assembly-write` → **done** |
| Skill / 管线 | `2026-05-28--skill-contract-eval-staging` → **done** |
| Runtime API | `POST …/memory/sessions/{sessionId}/clear-stm` · `GET …/context` |
| LTM 默认 | **OFF**（**SC-MEM01**）；**SC-STM02** 用 **query/fixture ON** |
| OP-MEM | **done**（`2026-05-28--memory-stm-session` · product.accept 2026-05-27） |

## §4 最小回归束链（P1 · 可选）

| 序号 | evalSetId | 本包 |
|------|-----------|------|
| 1 | `eval.memory.session_clear_stm` | **本包 AC** |
| 2 | `eval.context.session_execution_tool_bind` | 另包 |
| 3 | `eval.memory.budget_trim` | 另包 |

## §5 Staging 扩展（P1 · 可选）

| sessionId | 环境 | 备注 |
|-----------|------|------|
| _tg:{chatId}_ | staging | Telegram §2.8 真机 · 非 AC 阻塞 |
