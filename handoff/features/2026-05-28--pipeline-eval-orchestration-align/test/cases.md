# 测试用例（API + Eval pytest）

> test-agent 在 `backend_done` 后：跑 **TC-02～TC-06** pytest + 审查 **TC-07** evidence 模板。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | 三场景 catalog 序 | 对 `trade.spot.limit_order`、`trade.spot.flash_convert`、`trade.spot.amend_limit_order` 各调 `GET /api/v1/agent/scenarios/{id}` | **200**；`read.skill` 的 `order` **<** 首个 confirm/write 相关 `stepKey` 的 `order` | P0 |
| TC-02 | AC-2 | Eval 正例 | 调用 `assert_eval_pipeline_write_order_positive` 传入 synthetic 五段序 timeline（见 `test_eval_pipeline_write_order.py`） | **不抛错**；模块暴露 `EVAL_SET_ID` / `EVAL_VERSION` | P0 |
| TC-03 | AC-3 | P-N1 负例 | 传入 timeline：`trading.exchange_private` 在 `user.confirmed` 之前 | **AssertionError**（或封装异常码） | P0 |
| TC-04 | AC-4 | P-N2 负例 | 传入 timeline：`confirmation.required` 早于 `agent.skill.spec_read` | **AssertionError** | P0 |
| TC-05 | AC-5 | pytest 套件 | `cd server && uv run pytest tests/test_eval_pipeline_write_order.py -q` | **全通过** | P0 |
| TC-06 | AC-6 | freeze 对拍 | `uv run pytest tests/test_orchestration_freeze_align.py -q` | **全通过**；三场景 step 子序列满足 §3.1/3.2 | P0 |
| TC-07 | AC-7 | 证据模板 | 打开 `eval/evidence/eval-pipeline-write-order.md` §1～§3 | 命令、日期、pytest 摘要、依赖包 **done** 已填（backend 或 test-agent） | P0 |
| TC-08 | AC-8 | policy refs | `GET /api/v1/admin/orchestration/policy`（Admin JWT） | **200**；`engineeringSpecRefs` **含** runtime-freeze §3 锚 | P0 |
| TC-09 | AC-2 | 回归代理 | `uv run pytest tests/test_write_path_pipeline.py -q`（可选 P1） | **仍通过**（eval 模块委托后无行为回归） | P1 |

## 契约测试

- [ ] TC-01 三场景 API 200 + step 序
- [ ] TC-05 + TC-06 pytest green
- [ ] TC-08 policy refs 含 freeze §3

## 自动化映射

| 用例 | pytest / 文件 |
|------|----------------|
| TC-02～TC-05 | `tests/test_eval_pipeline_write_order.py` |
| TC-01, TC-06 | `tests/test_orchestration_freeze_align.py` |
| TC-08 | `tests/test_orchestration_flow_catalog.py` 或 freeze align 文件 |
| TC-07 | `eval/evidence/eval-pipeline-write-order.md`（审查） |
