# 测试用例（API）

> 测试 Agent 在 backend_done 后执行 P0。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | Runtime 读已发布规范 | 1. 种子/发布 `skill.spot.limit_order`<br>2. `GET …/runtime/skill-operation-spec/effective?skillId=skill.spot.limit_order` | **200**；含 `skillId`、`skillSpecVersion`、`specDigest`、`sections`；无 Secret | P0 |
| TC-02 | AC-2 | TG 限价完整回合 | 1. 绑定用户 + TRADING 开<br>2. 发送限价意图文本<br>3. 点按类型 A 确认<br>4. 拉取 timeline | 存在 `agent.skill.spec_read` 且 `phase=success`（payload 含 skillId/version/digest） | P0 |
| TC-03 | AC-3 | 五段因果序 | 对 TC-02/TC-08 的 `executionId` 取 timeline 事件名序列 | 满足 `execution.dispatched` < `agent.skill.spec_read` < `confirmation.required` < `user.confirmed` < 首条 `trading.exchange_private`（与 `writePathPipelineOrder.ts` 一致） | P0 |
| TC-04 | AC-4 | read.skill 编排步 | TC-02 timeline | 存在 `agent.orchestration.step` 且 `stepKey=read.skill`，时间不晚于 `agent.skill.spec_read` | P0 |
| TC-05 | AC-5 | Admin timeline API | `GET …/admin/observability/executions/{executionId}/timeline`（Bearer） | **200**；`items` 可排序复现 TC-03 | P0 |
| TC-06 | AC-6 | 无效 skill 阻断 | 1. 配置未知 skill 或清空 PUBLISHED<br>2. 发起 TG 限价写 | 类型 A 前终止；**无** 成功 `agent.skill.spec_read`；**无** `trading.exchange_private` 写 | P0 |
| TC-07 | AC-7 | TG 改单路径 | 改单意图 → 类型 A → 确认（mock 交易所） | 同 TC-02/03/04 对 `trade.spot.amend_limit_order` | P0 |
| TC-08 | AC-8 | HTTP 限价写序 | `POST …/agent/trade/spot/limit-order`（绑定用户） | timeline 满足 TC-03 五段序；`source=http_api` | P0 |
| TC-09 | AC-1 | 未知 skillId | `GET effective?skillId=skill.unknown` | **404** 或 **403** + `PROMPT_SKILL_REF_INVALID` | P1 |

## 契约测试

- [x] `GET effective` 响应 schema 与 `api.openapi.yaml` 一致
- [x] timeline `eventName` / `transitionTrigger` 与 observability §2.1 对齐
- [x] 错误体 `code` 与 OpenAPI 示例一致

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| TC-09 | 未知 skill | 不写、不确认 |
