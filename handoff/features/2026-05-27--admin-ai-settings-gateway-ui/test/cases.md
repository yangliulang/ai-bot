# 测试用例（API）

> 后端字段已由前序包实现；本包 TC 以 **defaults 回归** + **FE 联调前置** 为主。test-agent 可复跑前序 pytest。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1, AC-2, AC-6, AC-8 | GET defaults 含网关字段 | 1. Admin Bearer<br>2. `GET /api/v1/admin/ai/defaults` | **200**；`intentNluUseLlm` 为 boolean；`telegramLlmNarrate` 含 9 键且均为 boolean | P0 |
| TC-02 | AC-3 | PATCH intentNluUseLlm | 1. 记录 GET 当前值<br>2. `PATCH` Body `{ "intentNluUseLlm": !cur }`<br>3. 再 GET | **200**；GET 与 PATCH 响应一致 | P0 |
| TC-03 | AC-4 | PATCH narrate 部分合并 | 1. GET `telegramLlmNarrate`<br>2. `PATCH` 仅 `{ "telegramLlmNarrate": { "readMarketDepth": true } }`<br>3. GET | **200**；`readMarketDepth=true`；**其它 8 键** 与步骤 1 相同 | P0 |
| TC-04 | AC-5 | PATCH 非法 narrate 键 | 1. `PATCH` `{ "telegramLlmNarrate": { "notAField": true } }` | **422**；`code`/message 指明未知字段（与存量校验一致） | P1 |
| TC-05 | AC-7 | 存量 scenario 模型 PATCH | 1. 确保 catalog 有启用模型<br>2. `PATCH` `{ "scenarioChatModel": "<validModelId>" }` | **200**；GET 回显该字段 | P0 |

## 契约测试

- [ ] `intentNluUseLlm` / `telegramLlmNarrate.*` camelCase 与 `api.openapi.yaml` 一致
- [ ] 错误体含 `code` + `message`（非信封 `code:0`）

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| TC-04 | 未知 narrate 字段 | **422**，不写库 |
