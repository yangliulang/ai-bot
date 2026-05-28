# 测试用例（API）

> 测试 Agent 在 `backend_done` 后执行。实现前由 product.contract 定稿。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | Admin defaults | `PATCH …/admin/ai/defaults` body `{ telegramLlmNarrate: { readMarketTicker: true } }` → `GET` | GET 返回 `telegramLlmNarrate.readMarketTicker: true`；其它 narrate 字段仍为 false；If-Match 与存量一致 | P0 |
| TC-02 | AC-2 | ticker LLM 成功 | defaults `readMarketTicker: true`（env false）；mock `invoke_llm_chat_for_telegram` 返回正文；模拟 TG 已绑定 **read.market.ticker** 成功路由 | 出站含 LLM 文本；时间线含 `llm.read.market.ticker` outcome=success | P0 |
| TC-03 | AC-3 | ticker LLM 回落 | 启用 narrate；mock LLM 返回 None/失败 | `sendMessage` 仍成功；正文为确定性 ticker 行；时间线 narrate outcome=failure；HTTP webhook **200** | P0 |
| TC-04 | AC-4 | ticker 关闭 | defaults 与 env 均为 false；不 mock LLM | 仅确定性 ticker 行；**不**调用 `invoke_llm_chat_for_telegram` | P0 |
| TC-05 | AC-5 | env 覆盖 | defaults `readMarketTicker: false`；env `TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER=true`；mock LLM 成功 | 进入 narrate 分支；与 TC-02 类似 | P0 |
| TC-06 | AC-6 | 多场景 effective | ① defaults `readMarketDepth: true` → depth 成功路由 mock LLM；② defaults `spotFlashConfirm: true` → Type-A 闪兑 mock preamble | 两场景均进入对应 LLM helper；字段映射与 brief 表一致 | P0 |
| TC-07 | AC-7 | timeline payload | TC-02/03 后查 execution timeline | payload 含 `effectiveTelegramLlmNarrateEnabled: true`（尝试分支）；TC-04 无 narrate 事件或 false | P0 |
| TC-08 | AC-8 | 部分 PATCH | GET 基线 → PATCH 仅 `{ telegramLlmNarrate: { readMarketDepth: true } }` → GET | `readMarketDepth: true`；`readMarketTicker` 等其它键保持 PATCH 前状态 | P0 |
| TC-09 | AC-1 | 缺字段默认 | 新库或缺 `telegramLlmNarrate` 合并后 GET | 9 字段均为 false | P1 |

## 契约测试

- [ ] `telegramLlmNarrate` 嵌套对象出现在 OpenAPI schema 与 GET 示例
- [ ] PATCH 深度合并不 wipe 未提交 narrate 键

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| TC-09 | 旧库无 telegramLlmNarrate | 合并后全 false |
| TC-10 | PATCH 非法 narrate 键 | 422 或 strip（与 patch_gateway_defaults 校验策略一致） | P1 |
