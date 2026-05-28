# 测试用例（API）

> 测试 Agent 在 `backend_done` 后执行。实现前由 product.contract 定稿。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | I02 创建 | `POST …/instances` body `{ telegramUserId, templateId?, exchangeSubAccountUserId? }` | **201**；`instanceId` 以 `inst_` 开头；含 `userId`、`templateId` | P0 |
| TC-02 | AC-2 | 配额 | 同一 `telegramUserId` 再次 POST | **422** `code=AGENT_QUOTA_EXCEEDED` | P0 |
| TC-03 | AC-3 | I05 合法 | PATCH `{ instanceOverrides: { preferredLanguage: "zh-Hans" } }` → GET 详情 | **200**；详情 `instanceOverrides.preferredLanguage=zh-Hans` | P0 |
| TC-04 | AC-3 | I05 非法键 | PATCH `{ instanceOverrides: { secretApiKey: "x" } }` | **422** `VALIDATION_ERROR`；`details.unknownKeys` 含 `secretApiKey` | P0 |
| TC-05 | AC-4 | I04 登记 | POST `…/binding` `{ subAccountId: "sub_x" }` | **200**；`exchangeSubAccountUserId=sub_x` | P0 |
| TC-06 | AC-4 | I04 解绑 | DELETE `…/binding` | **204** | P0 |
| TC-07 | AC-5 | 绑定态 | POST `…/me/agent/bindings/trading-api`（mock 探测成功）→ GET 详情 → DELETE binding → GET | 先 **BOUND** 后 **NONE**；`instanceId` 不变 | P0 |
| TC-08 | AC-6 | G01 | env `CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED=true` → POST 创建 | **422** `AGENT_GLOBAL_OFF` | P0 |
| TC-09 | AC-1 | 非法 tg | POST `{ telegramUserId: "not-a-number" }` | **422** `VALIDATION_ERROR` | P1 |

## 契约测试

- [ ] 创建响应字段与 OpenAPI `AdminAgentInstanceCreatedResponse` 一致
- [ ] `instanceOverrides` 仅接受四白名单键（OpenAPI `additionalProperties: false`）

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| TC-09 | 非数值 telegramUserId | 422 |
| TC-10 | PATCH 未知 instanceId | 404 `AGENT_ADMIN_INSTANCE_NOT_FOUND` | P1 |
