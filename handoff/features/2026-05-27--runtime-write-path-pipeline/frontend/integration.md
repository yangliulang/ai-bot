# 前端对接

> **含页面：否** — 无 `admin/` / `deeplink/` 变更。`frontend.integrate` 空跑完成。

## 联调结论

| 项 | 值 |
|----|-----|
| 路由 | 无（brief 明确无页面） |
| 关键文件 | 无 |
| API 客户端 | 无；Runtime/TG/HTTP 直连后端 |
| Mock → 真实 API | 不适用（未建 Mock 页） |
| 联调日期 | 2026-05-27 |
| 后端 Base URL | http://127.0.0.1:8080（见 `backend/notes.md`） |

## 存量 Observability（只读对齐）

| 项 | 说明 |
|----|------|
| 页面 | Admin Observability 执行详情 · Timeline 表 |
| API | `GET /api/v1/admin/observability/executions/{executionId}/timeline` |
| 展示 | `eventName` 列通用渲染；**`agent.skill.spec_read`** 等新事件会以原始事件名出现在表中，无专用文案/图标（本包不改 UI） |
| 五段序 | 产品验收以 pytest `assert_write_path_pipeline_order` + Admin `writePathPipelineOrder.ts` 逻辑为准，非本阶段 FE 实现 |

## 接口映射（供调用方参考，非 Admin 实现）

| 场景 | Method | Path | 说明 |
|------|--------|------|------|
| Runtime 读规范 | GET | `/api/v1/runtime/skill-operation-spec/effective` | Query `skillId`（必填）；200 camelCase |
| HTTP 限价写 | POST | `/api/v1/agent/trade/spot/limit-order` | 绑定用户；timeline 五段序 |
| 时间线验收 | GET | `/api/v1/admin/observability/executions/{executionId}/timeline` | Bearer；`items[].eventName` |
| TG 写路径 | — | `POST /webhook/telegram/{token}` | 无 OpenAPI path；见 `test/cases.md` |

错误态（403/404/422）见 `api.openapi.yaml` 与 `backend/notes.md`。

## 联调自检

- [x] **主流程**：无 FE 路由；API P0 已由 test-agent 在 `test/report.md` 覆盖（pytest 7 passed）
- [x] **错误态**：同上（含 `PROMPT_SKILL_REF_INVALID`）；无页面级错误 UI
- [x] **加载态**：不适用
- [x] **Observability**：存量 Timeline 可列出 `execution.dispatched` / `agent.skill.spec_read` / `confirmation.required` / `user.confirmed` / `trading.exchange_private`（字段名直出，无 gap 阻断本包收口）

## 代码变更

无。`admin/`、`deeplink/` 未检出本功能包范围内的对接或 Mock 页面。

## 备注

- 用户触达：Telegram 限价/改单、HTTP limit-order、Runtime effective 读规范；契约见功能包 `api.openapi.yaml`。
- 可选增强（**非本包**）：Observability 对 `agent.skill.spec_read` 做摘要展示 → 交后续 Admin 包或 `/fe`。
- 下一步：test-agent 执行 `test.e2e`，在 `test/e2e-report.md` 标 **N/A** 后推进 `e2e_verified`。
