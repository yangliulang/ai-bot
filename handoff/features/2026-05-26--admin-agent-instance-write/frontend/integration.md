# 前端对接说明

> 功能包 `2026-05-26--admin-agent-instance-write` · **frontend_done**（真实 API · Vite proxy `/api` → `127.0.0.1:8080`）

## 页面与路由

| 页面 | 路由 | 说明 |
|------|------|------|
| 实例列表 | `/agents/instances` | **AC-7**「创建实例」Modal；列表刷新 |
| 实例详情 | `/agents/instances/:instanceId` | **AC-8** I05 表单保存；**AC-9** I04 登记/解绑 |

## 接口映射

| 页面/操作 | API | 方法 | 客户端 |
|-----------|-----|------|--------|
| 列表拉取 | `/api/v1/admin/agents/instances` | GET | `listAgentInstances` |
| 创建实例 | `/api/v1/admin/agents/instances` | POST | `createAgentInstance` |
| 详情 | `/api/v1/admin/agents/instances/{instanceId}` | GET | `getAgentInstance` |
| 保存实例参数 | `…/{instanceId}` | PATCH | `patchAgentInstance` · `instanceOverrides` |
| 登记子账户 | `…/{instanceId}/binding` | POST | `bindInstanceSubaccount` |
| 解绑托管 | `…/{instanceId}/binding` | DELETE | `unbindInstanceSubaccount` |
| 删除实例（存量） | `…/{instanceId}` | DELETE | `deleteAgentInstance` |

实现文件：

- `admin/src/shared/api/agent-instances.ts`
- `admin/src/pages/agents/AgentInstancesListPage.vue`
- `admin/src/pages/agents/AgentInstanceDetailPage.vue`

## Mock 切换

- **无 MSW**：读路径与写路径均走 **`httpClient`**（ky + Bearer，与存量 Admin 一致）。
- 开发态 **`vite.config`** proxy：`/api` → `http://127.0.0.1:8080`。
- 错误展示：`formatAgentInstanceWriteError`（含 **422** `code` / `message` / `details.unknownKeys`）。

## 联调结果

- [x] 主流程走通：创建 → 列表可见 → 详情 PATCH overrides → 登记子账户 → 解绑后 `tradingApiBindingStatus=NONE`
- [x] 错误态：重复 tg **422**、非法 overrides 键 **422**（`unknownKeys` 展示）、表单校验（非数字 tg）
- [x] 加载/空态：提交中按钮 loading；详情 **404** 沿用 `loadError` 横幅

**自测**：`npm run build`（admin）通过；后端 pytest `test_admin_p1_ops` 已覆盖 API 契约。

## 遗留问题

- E2E P0 已通过，见 `test/e2e-report.md`（2026-05-26）。
- 本地 API DB **须** `cd server && uv run alembic upgrade head`（含 `0027_agent_instance_overrides`），否则创建/PATCH 可能 **DATABASE_ERROR** / 500。
