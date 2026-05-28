# 测试用例（API + Eval pytest）

> test-agent 在 `backend_done` 后：跑 **TC-01～TC-08** pytest + 审查 **TC-11** evidence 模板；**TC-09～TC-10** HTTP。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | P0 evalSetId | 导入 `eval_memory_stm`；读 `EVAL_MEMORY_STM_P0_SET_IDS`、`EVAL_VERSION` | 含 **`eval.memory.session_clear_stm`**、**`eval.memory.stm_vs_ltm_intent`**；**version=`0.1.0`** | P0 |
| TC-02 | AC-2 | L0 追加 | 对 `sessionId=test-stm-1` 追加 **3** 条 L0 message；`get_l0_for_prompt` | **count=3**；preview 含近轮 | P0 |
| TC-03 | AC-3 | STM 清空 | `clear_session_stm("test-stm-1", userId)` | **clearedAt** 非空；L0 **空**；Semantic fixture **未改** | P0 |
| TC-04 | AC-4 | Eval GWT | `assert_eval_memory_session_clear_stm` **Given** 3 轮 + LTM ON fixture **When** 已 clear | **不抛错**；**l0 空**；**semantic 仍在** | P0 |
| TC-05 | AC-5 | 类型 A 作废 | 登记 `waiting_confirmation` → clear | **`pendingTypeAValid=False`** | P0 |
| TC-06 | AC-6 | 观测事件 | `build_session_cleared_event` | **`eventName=agent.memory.session_cleared`**；含 **userId/sessionId/clearedAt** | P0 |
| TC-07 | AC-7 | 意图分流 | `resolve_memory_user_intent("我们重新开始吧")` vs `("清空记忆")` | **`stm_clear`** vs **`ltm_revoke`**；**不得相同** | P0 |
| TC-08 | AC-8 | pytest | `cd server && uv run pytest tests/test_eval_memory_stm.py -q` | **全通过**（含 P1） | P0 |
| TC-09 | AC-9 | POST clear-stm | 先 **GET context** 见 **l0>0** → **POST** `…/clear-stm` body `{userId}` | **200**；**clearedAt**；再 **GET** **l0MessageCount=0** | P0 |
| TC-10 | AC-9 | GET context OFF | `GET …/context?userId=u1`（默认 semantic OFF） | **200**；**semanticNarrativeEnabled=false**；**semanticNarrativeBlock** 空 | P0 |
| TC-11 | AC-10 | 证据 | 打开 `eval/evidence/eval-memory-session-clear-stm.md` §1～§3 | 命令、日期、pytest、evalSetId、依赖 **done** 已填 | P0 |
| TC-12 | AC-3 | P1 负例 | `clear_session_stm` 对 **从未写入** 的 session | **不 500**；**clearedAt** 仍返回或 **404**（与实现一致 · 文档化） | P1 |

## 契约测试

- [ ] TC-08 pytest green
- [ ] TC-09 POST + GET 200 对拍
- [ ] TC-10 LTM 默认 OFF

## 自动化映射

| 用例 | pytest / 文件 |
|------|----------------|
| TC-01～TC-08, TC-12 | `tests/test_eval_memory_stm.py` |
| TC-09～TC-10 | `tests/test_eval_memory_stm.py`（TestClient）或 `tests/test_runtime_memory_api.py` |
| TC-11 | `eval/evidence/eval-memory-session-clear-stm.md`（审查） |
