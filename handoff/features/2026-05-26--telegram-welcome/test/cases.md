# 测试用例（API）

> 测试 Agent 在 `backend_done` 后执行。实现前由 product.contract 定稿。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | Admin 欢迎语键 | `PATCH …/bot` 写入三语键 + 遗留键 → `GET` | 回显一致；单键 >4096 → **400** `ADMIN_TELEGRAM_WELCOME_TEXT_TOO_LONG` | P0 |
| TC-02 | AC-2 | 回退链 | 单元测试 `resolve_activation_welcome_text`：各桶空/仅遗留/全空 | 顺序：命中桶→简体→英→繁→遗留→null | P0 |
| TC-03 | AC-3 | 首次 confirm 发送 | 配置模板 + mock `sendMessage`；`POST …/api-binding/confirm` 新 tg_id | **200**；`activationWelcomeSent=true`；`sendMessage` 调用 1 次 | P0 |
| TC-04 | AC-3 | Me 绑定路径 | 同上经 `POST …/me/agent/bindings/trading-api` | 同 TC-03 语义 | P0 |
| TC-05 | AC-4 | 幂等 | 同一 tg_id 第二次 confirm | `activationWelcomeSent=false`；`activationWelcomeSkipReason=already_sent` | P0 |
| TC-06 | AC-5 | 无模板 | 三语+遗留皆空；confirm | **200**；不调用 `sendMessage`；`no_template` | P0 |
| TC-07 | AC-6 | 发送失败 | mock `sendMessage` 抛错/4xx | confirm **200**；`send_failed`；绑定仍成功 | P0 |
| TC-08 | AC-7 | displayName | 模板含 `{displayName}`；telegram 带 first_name / username | 出站正文替换正确；非法占位原样或 strip（与实现对齐） | P0 |
| TC-09 | AC-8 | 三语 PATCH | 一次 PATCH 写入 ZH_CN/ZH_TW/EN 三键 | GET 三键均非空（API 面；UI 见 E2E） | P0 |
| TC-10 | AC-1 | If-Match | PATCH 带过期 `If-Match` | **409**（回归存量） | P1 |

## 契约测试

- [x] `activationWelcomeSent` / `activationWelcomeSkipReason` 与 OpenAPI 一致
- [x] `bindingRowCreated` 在 agent confirm 响应中暴露（与 me 路径对齐）

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| TC-10 | 配置版本冲突 | 409，不丢欢迎语配置 |
