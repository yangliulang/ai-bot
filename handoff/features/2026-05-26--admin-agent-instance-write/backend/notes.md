# 后端实现说明

> 功能包 `2026-05-26--admin-agent-instance-write` · **backend_done**（存量实现核对 + pytest 映射 AC-1～AC-6）

## 环境

- **Base URL**：`http://127.0.0.1:8080`
- **启动方式**：
  ```bash
  cd server && uv run chainup-agent-api
  ```
- **健康检查**：`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/health` → **200**
- **OpenAPI**：`http://127.0.0.1:8080/openapi.json`（路径含 `admin-agent-instances` 标签）

## 鉴权

- Admin 控制台 **Bearer JWT**（`Authorization: Bearer <token>`）。
- 环境变量 **`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`** 非空时，未带有效 Bearer 的 Admin 路由返回 **401**。
- 本地 pytest 默认清空该 secret（见 `server/tests/conftest.py`），无需 Token。

## 已实现接口

| 方法 | 路径 | 说明 | 实现位置 |
|------|------|------|----------|
| POST | `/api/v1/admin/agents/instances` | **I02** 创建实例 | `api/routers/admin_agent_instances.py` · `application/admin_agent_instance_write.py` |
| PATCH | `/api/v1/admin/agents/instances/{instanceId}` | **I05** `instanceOverrides` 白名单 + 可选 `runtimeState` | 同上 |
| POST | `/api/v1/admin/agents/instances/{instanceId}/binding` | **I04** 登记 `exchangeSubAccountUserId` / `subAccountId` | 同上 |
| DELETE | `/api/v1/admin/agents/instances/{instanceId}/binding` | **I04** 解绑托管行（保留 `agent_instance`） | 同上 |
| GET | `/api/v1/admin/agents/instances` | **I01** 列表（联调读路径） | `application/admin_agent_instances.py` |
| GET | `/api/v1/admin/agents/instances/{instanceId}` | **I03** 详情 | 同上 |

**DB**：`agent_instance.instance_overrides_json`（迁移 `0027_agent_instance_overrides`）。

## 错误码约定

| HTTP | code | 含义 |
|------|------|------|
| 201 | — | I02 创建成功 |
| 200 | — | PATCH / POST binding 成功 |
| 204 | — | DELETE binding 成功 |
| 404 | `AGENT_ADMIN_INSTANCE_NOT_FOUND` | 实例不存在 |
| 422 | `AGENT_QUOTA_EXCEEDED` | 同一 `telegramUserId` 已有实例（AC-2） |
| 422 | `AGENT_GLOBAL_OFF` | `CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED=true`（AC-6） |
| 422 | `AGENT_OPS_SUSPENDED` | 运维全局暂停时禁止新建 |
| 422 | `AGENT_ROLLOUT_BLOCKED` | 灰度白名单未包含用户 |
| 422 | `VALIDATION_ERROR` | 非法 `telegramUserId`、空 binding body、**I05 未知键**（`details.unknownKeys`） |
| 422 | — | 封禁相关码（`ban_envelope_code`） |

## 示例请求

```bash
# 创建实例 I02（替换 TOKEN；本地无 JWT secret 时可省略 -H）
curl -sS -X POST http://127.0.0.1:8080/api/v1/admin/agents/instances \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"telegramUserId":"88001001","templateId":"tmpl_test"}'

# PATCH instanceOverrides I05
curl -sS -X PATCH "http://127.0.0.1:8080/api/v1/admin/agents/instances/inst_XXX" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"instanceOverrides":{"preferredLanguage":"zh-Hans"}}'

# 登记子账户 I04
curl -sS -X POST "http://127.0.0.1:8080/api/v1/admin/agents/instances/inst_XXX/binding" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"exchangeSubAccountUserId":"sub_01"}'

# 解绑 I04
curl -sS -X DELETE "http://127.0.0.1:8080/api/v1/admin/agents/instances/inst_XXX/binding" \
  -H "Authorization: Bearer $TOKEN" -w "\nHTTP %{http_code}\n"
```

## 自动化测试

```bash
cd server && uv run pytest tests/test_admin_p1_ops.py::test_admin_instance_i02_i04_i05 tests/test_admin_p1_ops.py::test_admin_instance_i02_global_off -q
```

映射 **brief AC-1～AC-6** / `test/cases.md` TC-01～TC-08。

## 与 OpenAPI 的差异（如有）

无。功能包 `api.openapi.yaml` 与 `server/chainup_agent/api/routers/admin_agent_instances.py` 一致；PATCH 可选 `runtimeState` 与 SSOT 一致，本包验收以 `instanceOverrides` 为主。

## 已知问题 / 技术债

- **Admin FE**（AC-7～AC-9）未在本阶段交付，见 `admin/FE_HANDOFF.md`，由 **frontend-agent** 接续。
- 计费 `AGENT_BILLING_BLOCKED`、模板 `AGENT_TEMPLATE_DISABLED` 全矩阵见 brief P1 范围外。
