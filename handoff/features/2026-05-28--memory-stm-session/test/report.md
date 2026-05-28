# 测试报告（API）

> 测试 Agent 在 backend_done 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-27
- 执行人：test-agent
- 环境：本地 `server/` · `uv run pytest` · API health `http://127.0.0.1:8080/health` → 200
- 结论：✅ 通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 11（P0）+ 1（P1） | 12 | 0 | 0 | 0 |

自动化：

```bash
cd server && uv run pytest tests/test_eval_memory_stm.py -v
```

→ **10 passed**（TC-01～TC-08、TC-09～TC-10 经 TestClient；TC-12 P1 含在内）。

## 用例执行明细

| ID | 优先级 | 结果 | 自动化 / 说明 |
|----|--------|------|----------------|
| TC-01 | P0 | 通过 | `test_eval_memory_stm_p0_constants` — `EVAL_VERSION=0.1.0`；P0 set 含 `session_clear_stm`、`stm_vs_ltm_intent` |
| TC-02 | P0 | 通过 | `test_append_l0_and_get_for_prompt` — 3 条 L0，`l0MessageCount=3` |
| TC-03 | P0 | 通过 | `test_clear_session_stm_clears_l0_preserves_semantic` — L0 空；semantic fixture 仍在 |
| TC-04 | P0 | 通过 | `test_session_clear_stm_gwt` — `assert_eval_memory_session_clear_stm` 不抛错 |
| TC-05 | P0 | 通过 | `test_pending_type_a_invalidated_on_clear` — `pendingTypeAValid=False` |
| TC-06 | P0 | 通过 | `test_build_session_cleared_event` — `eventName=agent.memory.session_cleared` |
| TC-07 | P0 | 通过 | `test_stm_vs_ltm_intent_routing` — `stm_clear` vs `ltm_revoke` |
| TC-08 | P0 | 通过 | 全套件 pytest green |
| TC-09 | P0 | 通过 | `test_runtime_post_clear_stm_and_get_context` + live curl — POST 200 `clearedAt`；GET `l0MessageCount=0`、`sessionClearedAt` |
| TC-10 | P0 | 通过 | `test_runtime_get_context_ltm_off_by_default` + live curl — `semanticNarrativeEnabled=false`，block 为 null |
| TC-11 | P0 | 通过 | 审查 `eval/evidence/eval-memory-session-clear-stm.md` §1～§3 已填（命令、日期、pytest 摘要、evalSetId、依赖 done） |
| TC-12 | P1 | 通过 | `test_clear_never_written_session_p1` — 幂等返回 `clearedAt`，不 500 |

## 契约抽查

- [x] `POST …/clear-stm` 200 体含 `sessionId`、`userId`、`clearedAt`、`eventName`（camelCase）
- [x] `GET …/context` 200 体含 `l0MessageCount`、`memoryContext.sessionClearedAt`、`semanticNarrativeEnabled`
- [x] LTM 默认 OFF：`semanticNarrativeBlock=null`（TC-10）

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- **无页面**（`test/coverage.md` 含页面：否）。`status.yaml` 已设 `skips: [frontend.integrate, test.e2e, designer.review]`。
- **勿开 frontend Chat** — 下一步请指挥官执行 **`/pipeline-skip 2026-05-28--memory-stm-session`**，再 **`/pipeline-product-accept 2026-05-28--memory-stm-session`**。
