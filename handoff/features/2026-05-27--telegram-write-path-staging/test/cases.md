# 测试用例（API + Staging）

> **STG-xx** = staging 手工（门禁 P0）；**TC-xx** = 可自动化或文档审查。  
> test-agent 在 `backend_done` 后：pytest 回归 **+** 审查 `staging/evidence-log.md` 是否满足 STG。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | 环境登记 | 打开 `staging/evidence-log.md` §1 | 环境名、SHA、日期、执行人、Mock 声明已填；**非** 未批准的生产用户 | P0 |
| TC-02 | AC-2 | 主轴 TG 走读 | staging 跑 `trade.spot.limit_order` 类型 A 全回合；填 §2 `executionId`；勾选 walkthrough §2.1～2.10 | **≥80%** 勾选；`executionId` 非空 | P0 |
| STG-01 | AC-2, AC-3 | 走读与导出 | 同 TC-02；Admin 或 API 导出时间线 | 附件或 §2.1 四项勾选完成 | P0 |
| TC-03 | AC-3 | 时间线序 | 对 §2 `executionId` 调用 `GET …/timeline`（staging token）**或** 附 JSON 导出；本地代理：`pytest test_write_path_pipeline.py::test_http_limit_order_write_path_timeline` | **`agent.skill.spec_read`** 早于确认早于首条 **`trading.exchange_private`** | P0 |
| TC-04 | AC-4 | Eval 正例 | 所内跑 `eval.runtime.pipeline_write_order` §2；链入 evidence §2.2 | **通过**；有日志/MR 链接 | P0 |
| TC-05 | AC-5 | 依赖包 | 核对 `runtime-write-path-pipeline` **done** 与 §1 SHA | evidence §2.3 已填；SHA 一致或说明差异 | P0 |
| TC-06 | AC-6 | 负例快检 | 执行 checklist §3 **N1～N4** 之一 | **拒写/契约失败**；evidence §4 有摘要 | P0 |
| TC-07 | AC-7 | 扩展走读 | evidence §3 增 1 行（如 amend / 条件单撤） | 行内 `executionId` + 结论 | P1 |
| TC-08 | AC-8 | 关单回填 | evidence §5 三项勾选 | 可链 closure / product.accept | P0 |

## 契约测试

- [ ] `GET …/timeline` 对 staging `executionId` 返回 **200** 且序正确（STG 审查 + `scripts/verify_timeline_order.py`）
- [x] `pytest tests/test_write_path_pipeline.py` **全通过**（本地代理 · backend 7 passed）

## 自动化映射

| 用例 | pytest / 工具 |
|------|----------------|
| TC-03（代理） | `tests/test_write_path_pipeline.py` · staging：`scripts/verify_timeline_order.py` |
| TC-04 | 所内 Eval runner（手工登记） |
| TC-01～02, TC-05～08, STG-01 | 审查 `staging/evidence-log.md` |
