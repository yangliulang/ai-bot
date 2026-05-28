# 测试报告（API）

> 测试 Agent 在 backend_done 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-26
- 执行人：test-agent
- 环境：`server/` · pytest ASGITransport · SQLite 隔离库 · `CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET` 默认空（TC-07 单独覆盖）
- 结论：**通过**

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 6 | 5 | 0 | 1 | 0 |

（P0 共 6 条：TC-01～TC-06；TC-06 为纯前端，API 阶段记 **跳过**。）

## P0 明细

| 用例 ID | 关联 AC | 结果 | 证据 |
|---------|---------|------|------|
| TC-01 | AC-1 | 通过 | `test_admin_p1_ops.py::test_observability_tool_calls_and_llm` — tool-calls 200，`items≥1`，`invocationState=SUCCESS` |
| TC-02 | AC-2 | 通过 | `test_admin_observability_pipeline_p0.py::test_observability_execution_not_found_tc02` — 404 ×2，`AGENT_ADMIN_EXECUTION_NOT_FOUND` |
| TC-03 | AC-3 | 通过 | `test_observability_tool_calls_and_llm` — llm 200，`calls≥1`，`eventName=llm.chat.faq`；响应无 messages 字段 |
| TC-04 | AC-4 | 通过 | `test_observability_tool_calls_schema_tc04` — `invocationState`、`summary` 对象存在 |
| TC-05 | AC-5 | 通过 | `test_observability_llm_empty_calls_tc05` — 无 LLM 事件时 `calls=[]` |
| TC-06 | AC-6 | 跳过（API） | 不适用 HTTP；交 **E2E-03**（`frontend_done` 后） |

## P1 明细

| 用例 ID | 关联 AC | 结果 | 证据 |
|---------|---------|------|------|
| TC-07 | AC-1 | 通过 | `test_observability_admin_auth_required_tc07` — 配置 JWT Secret 后无 Bearer → 401 `ADMIN_CONSOLE_AUTH_REQUIRED` |

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 自动化命令

```bash
cd server && uv run pytest \
  tests/test_admin_p1_ops.py::test_observability_tool_calls_and_llm \
  tests/test_admin_observability_pipeline_p0.py -q
```

## 备注

- 新增回归文件：`server/tests/test_admin_observability_pipeline_p0.py`（TC-02/04/05/07）。
- 下一棒：**frontend-agent** 对接 `/observability?tab=tool|llm`（见 `admin/FE_HANDOFF.md` 2026-05-25）。
