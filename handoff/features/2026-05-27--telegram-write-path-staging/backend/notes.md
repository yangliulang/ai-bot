# 后端说明 — 2026-05-27--telegram-write-path-staging

> P‑08 staging 证据 · **backend_done** · **无生产代码变更**

## 启动与环境

| 项 | 值 |
|----|-----|
| 本地 API（代理回归） | `cd server && uv run chainup-agent-api` → http://127.0.0.1:8080 |
| Staging Base URL | 填 `staging/evidence-log.md` §1（所内预发） |
| 功能包 OpenAPI | `handoff/features/2026-05-27--telegram-write-path-staging/api.openapi.yaml` |
| 依赖功能包 | `2026-05-27--runtime-write-path-pipeline` → **done** |

## 实现位置（存量，本包不改动）

| 层 | 模块 |
|----|------|
| 五段序断言 | `chainup_agent/application/write_path_pipeline.py` · `assert_write_path_pipeline_order` |
| Admin 时间线 | `api/routers/v1/admin_observability.py` · `GET …/executions/{executionId}/timeline` |
| TG / HTTP 写路径 | `telegram_bound_reply.py` · `telegram_callback_handler.py` · `agent_trade_spot.py` |
| 本地回归 | `server/tests/test_write_path_pipeline.py` |

## Staging 验收工具（本包新增）

对 evidence §2 登记的 **`executionId`**，在所内 staging 拉时间线并校验序：

```bash
cd server && uv run python \
  ../handoff/features/2026-05-27--telegram-write-path-staging/scripts/verify_timeline_order.py \
  --execution-id exec-XXXXXXXXXXXXXX \
  --base-url https://YOUR-STAGING-HOST \
  --token "$ADMIN_BEARER" \
  --pretty
```

成功 → exit **0** 且 stdout 含 `OK: write-path pipeline order verified`。

## 本地 pytest 代理（不替代 staging 真跑）

```bash
cd server && uv run pytest tests/test_write_path_pipeline.py -q
```

2026-05-28：**7 passed**（TC-03 代理；映射 `test/cases.md`）。

| TC | 说明 |
|----|------|
| TC-01～02, TC-04～08 | 审查 `staging/evidence-log.md`（STG 手工） |
| TC-03 | staging `verify_timeline_order.py` **或** 时间线导出 + 上列 pytest 代理 |

## curl（staging 对拍）

```bash
curl -s -H "Authorization: Bearer $ADMIN_BEARER" \
  "$STAGING_BASE/api/v1/admin/observability/executions/$EXECUTION_ID/timeline"
```

## 与功能包 OpenAPI 差异

| 项 | 说明 |
|----|------|
| — | **无** — `GET …/timeline` 与存量 Admin 契约一致 |

## Staging 填写责任

- **`staging/evidence-log.md`** §1～§5 由 **所内 staging 走读** 填写（QA/test-agent 审查）；backend **不** 用生产/伪造数据预填。
- 走读步骤：`staging/walkthrough.md` · 勾选 SSOT：`product-doc/.../pipeline-walkthrough-checklist.md` §2。

## 关联文档

- `product-doc/specs/requirements/closure-staging-evidence-log.md`
- `product-doc/specs/requirements/evals/pipeline-write-order.md`
