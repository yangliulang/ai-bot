# 后端说明 — 2026-05-27--runtime-write-path-pipeline

> MR-RT-B4 · write path pipeline · `backend_done`

## 启动与环境

| 项 | 值 |
|----|-----|
| 启动 | `cd server && uv run chainup-agent-api` |
| Base URL | http://127.0.0.1:8080 |
| 机器可读契约 | http://127.0.0.1:8080/openapi.json |
| 功能包 OpenAPI | `handoff/features/2026-05-27--runtime-write-path-pipeline/api.openapi.yaml` |

## 实现位置

| 层 | 模块 |
|----|------|
| Runtime 读规范 | `application/runtime_skill_operation_spec.py` |
| 时间线五段序 | `application/write_path_pipeline.py` |
| Router | `api/routers/v1/runtime_skill.py` |
| 起票 | `application/agent_execution_memory.py` → `execution.dispatched` |
| TG 类型 A 前 | `application/telegram_bound_reply.py` |
| TG 确认回调 | `application/telegram_callback_handler.py` |
| HTTP 限价写 | `api/routers/v1/agent_trade_spot.py` |
| PUBLISHED 快照 | `chainup_agent/data/skill_specs/runtime-bundle.json`（源自 product-doc published bundle） |

## 路由

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/v1/runtime/skill-operation-spec/effective` | Query `skillId`（必填）、`scenarioId`（可选） |
| GET | `/api/v1/admin/observability/executions/{executionId}/timeline` | 验收事件序（存量） |
| POST | `/api/v1/agent/trade/spot/limit-order` | HTTP 写路径代表；增量五段序事件 |

Telegram 写路径无独立 HTTP path；见 `test/cases.md`。

## 时间线事件序（写路径）

同一 `executionId` 须满足（与 Admin `writePathPipelineOrder.ts` / `eval.runtime.pipeline_write_order` 一致）：

1. `execution.dispatched`
2. `agent.skill.spec_read`（`phase=success`，payload 含 `skillId` / `skillSpecVersion` / `specDigest`，**无** 全文）
3. `agent.orchestration.step` · `stepKey=read.skill`
4. `confirmation.required`
5. `user.confirmed`
6. 首条 `trading.exchange_private`（写类）

Callback 若 pending 无前置 turn 事件，回调内会 **补发** `spec_read` / `confirmation.required`（`ensure_write_path_skill_spec_read_if_missing`）。

## curl 示例

```bash
# AC-1 · 已发布规范
curl -s 'http://127.0.0.1:8080/api/v1/runtime/skill-operation-spec/effective?skillId=skill.spot.limit_order'

# AC-5 · 时间线（需 Admin Bearer，若已配置 JWT）
curl -s -H 'Authorization: Bearer YOUR_TOKEN' \
  'http://127.0.0.1:8080/api/v1/admin/observability/executions/exec-XXXXXXXXXXXXXX/timeline'
```

## 自测（pytest）

```bash
cd server && uv run pytest tests/test_write_path_pipeline.py -q
```

2026-05-27 本地：**4 passed**。

## 与功能包 OpenAPI 差异

| 项 | 说明 |
|----|------|
| 无 | 路径、字段、错误码与 `api.openapi.yaml` 一致 |

## 关联文档

- `product-doc/specs/requirements/evals/pipeline-write-order.md`
- `product-doc/specs/requirements/skill-specs/production-runtime.md`
- `server/docs/BACKEND_SPEC.md`（Observability 时间线）
