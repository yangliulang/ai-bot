# 测试报告（API + Staging 代理）

> 测试 Agent 在 `backend_done` 后执行并填写。

## 概要

- 执行时间：2026-05-28
- 执行人：test-agent
- 环境：本地 `server/` · `uv run pytest` · SQLite 隔离库；**预发 staging 未接入**（`staging/evidence-log.md` 仍为空模板）
- 结论：✅ **有条件通过**（**自动化代理 P0 全通过**；**STG 手工 P0 待所内预发**，不阻塞 `tested` → **`product.accept` 前须填 evidence**）

## 结果汇总

| 类别 | 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|------|
| 自动化代理（TC-03 等） | 1 套件 | 7 tests | 0 | 0 | 0 |
| STG 手工（TC-01/02/04～06/08 · STG-01） | 7 | 0 | 0 | 7 | 0 |
| P1（TC-07） | 1 | 0 | 0 | 1 | 0 |

## 用例执行明细

| ID | 优先级 | 结果 | 说明 |
|----|--------|------|------|
| TC-01 | P0 | 跳过 | `staging/evidence-log.md` §1 未填；需所内 staging 环境登记 |
| TC-02 | P0 | 跳过 | 主轴 TG 走读未执行（无预发 Bot/账号） |
| STG-01 | P0 | 跳过 | 同 TC-02/03 手工导出 |
| TC-03 | P0 | 通过 | `pytest tests/test_write_path_pipeline.py` **7 passed**（含 `test_http_limit_order_write_path_timeline` 等五段序断言） |
| TC-04 | P0 | 跳过 | Eval 正例未在所内 runner 执行；待 evidence §2.2 |
| TC-05 | P0 | 通过 | 依赖 `2026-05-27--runtime-write-path-pipeline` **phase: done**（`status.yaml` 核对） |
| TC-06 | P0 | 跳过 | 负例快检未做；待 evidence §4 |
| TC-07 | P1 | 跳过 | §3 扩展走读未填 |
| TC-08 | P0 | 跳过 | evidence §5 关单回填未勾 |

## 自动化

```bash
cd server && uv run pytest tests/test_write_path_pipeline.py -v
# 7 passed in ~1.4s
```

**未执行**（需 staging `executionId` + 存活 API）：

```bash
cd server && uv run python \
  ../handoff/features/2026-05-27--telegram-write-path-staging/scripts/verify_timeline_order.py \
  --execution-id <from evidence §2> --base-url <staging> --token "$ADMIN_BEARER"
```

本地 `http://127.0.0.1:8080/health` 探测：**不可用**（走查时未起 `chainup-agent-api`）。

## 契约 / 追溯

- [x] pytest 代理与 `runtime-write-path-pipeline` 行为一致（`assert_write_path_pipeline_order`）
- [ ] staging `GET …/timeline` + `verify_timeline_order.py` — **待 evidence §2 有 `executionId` 后补跑**
- [ ] `staging/evidence-log.md` 完整填写 — **`product.accept` 硬门禁**

`./scripts/check-test-coverage.sh handoff/features/2026-05-27--telegram-write-path-staging` → **0**

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| STG 包 | 预发走读证据未登记 | P0（accept 前） | 所内 QA / Runtime · 填 `staging/evidence-log.md` |

## 备注

- **含页面：否**；下一 Chat：**`/pipeline-frontend-integrate`**（空跑）→ E2E N/A。
- **`product.accept` 不得通过** 直至 `staging/evidence-log.md` §1～§5 与 walkthrough **≥80%** 勾选完成（见 `brief.md` AC-1～AC-8）。
