# 测试报告（API）

> 测试 Agent 在 backend_done 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- **执行时间**：2026-05-26T15:09:00+0800
- **执行人**：test-agent
- **环境**：pytest + ASGITransport（`server/tests/conftest.py` 隔离 SQLite）；命令见下
- **结论**：✅ **通过**（P0 全绿）

```bash
cd server && uv run pytest \
  tests/test_admin_p1_ops.py::test_admin_instance_i02_i04_i05 \
  tests/test_admin_p1_ops.py::test_admin_instance_i02_global_off -v
```

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 8 (P0) | 8 | 0 | 0 | 0 |
| 2 (P1) | 1 | 0 | 1 | 0 |

## P0 用例明细

| 用例 ID | AC | 结果 | 证据 |
|---------|-----|------|------|
| TC-01 | AC-1 | ✅ | `test_admin_instance_i02_i04_i05`：POST **201**；`instanceId` 前缀 `inst_`；含 `templateId` |
| TC-02 | AC-2 | ✅ | 同测：重复 POST **422** `AGENT_QUOTA_EXCEEDED` |
| TC-03 | AC-3 | ✅ | PATCH `preferredLanguage` **200** 回显；响应体为 `AdminAgentInstanceItem`（与 GET 同源投影） |
| TC-04 | AC-3 | ✅ | PATCH `secretApiKey` **422** `VALIDATION_ERROR`；`details.unknownKeys` 含 `secretApiKey` |
| TC-05 | AC-4 | ✅ | POST binding `{ subAccountId }` **200**；`exchangeSubAccountUserId` 更新 |
| TC-06 | AC-4 | ✅ | DELETE binding **204** |
| TC-07 | AC-5 | ✅ | `bindings/trading-api` mock 成功 → GET **BOUND** → DELETE binding → GET **NONE**；`instanceId` 不变 |
| TC-08 | AC-6 | ✅ | `test_admin_instance_i02_global_off`：`AGENT_RUNTIME_GLOBAL_DISABLED` → **422** `AGENT_GLOBAL_OFF` |

## P1 用例

| 用例 ID | 结果 | 备注 |
|---------|------|------|
| TC-09 | ✅ | 手工 ASGI：`telegramUserId=not-a-number` → **422** `VALIDATION_ERROR` |
| TC-10 | ⏭ 跳过 | 未单独 pytest；GET 未知实例 **404** 见 `tests/test_api.py::test_admin_agent_instances_list_and_get`；PATCH 同 `get_agent_instance_joined_admin` 404 路径 |

## 契约测试

- [x] 创建响应字段与 OpenAPI `AdminAgentInstanceCreatedResponse` 一致（`instanceId`、`userId`、`templateId`、`runtimeInstanceState`）
- [x] `instanceOverrides` 仅接受四白名单键（TC-04 `unknownKeys`）

## 失败与阻塞项

无。

## 备注

- `./scripts/check-test-coverage.sh handoff/features/2026-05-26--admin-agent-instance-write` 退出码 **0**。
- **AC-7～AC-9**（Admin UI）留 **frontend-agent** + E2E 阶段验收。
- 本地常驻 API（`127.0.0.1:8080`）若 DB 未跑迁移 `0027`，PATCH 可能 500；pytest 使用 `create_all` 无此问题。联调前请 `cd server && uv run alembic upgrade head`。
