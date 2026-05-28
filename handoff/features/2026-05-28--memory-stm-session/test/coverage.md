# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-28--memory-stm-session` |
| 含页面（需 E2E） | 否（STM eval pytest + Runtime memory API；E2E N/A） |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | evalSetId 常量 | TC-01 | — | `eval_memory_stm` 模块 |
| AC-2 | L0/L1 session store | TC-02 | — | `memory_session_store` |
| AC-3 | clear_session_stm | TC-03 | — | `clear_session_stm` |
| AC-4 | session_clear_stm GWT | TC-04 | — | `assert_eval_memory_session_clear_stm` |
| AC-5 | 作废类型 A | TC-05 | — | `invalidate_pending_type_a_on_stm_clear` |
| AC-6 | session_cleared 事件 | TC-06 | — | `build_session_cleared_event` |
| AC-7 | STM vs LTM 意图 | TC-07 | — | `resolve_memory_user_intent` |
| AC-8 | pytest 套件 | TC-08 | — | `test_eval_memory_stm.py` |
| AC-9 | Runtime clear/context API | TC-09, TC-10 | — | POST/GET memory sessions |
| AC-10 | 证据模板 | TC-11 | — | `eval/evidence/eval-memory-session-clear-stm.md` |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| POST | /api/v1/runtime/memory/sessions/{sessionId}/clear-stm | TC-09 |
| GET | /api/v1/runtime/memory/sessions/{sessionId}/context | TC-10 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 含页面：否；E2E 列留空
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-28--memory-stm-session` 退出码 0
