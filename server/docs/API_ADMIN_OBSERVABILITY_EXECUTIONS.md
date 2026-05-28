# Admin Observability · 持久化执行接口契约

> **Phase1** · 数据源：表 **`agent_execution`**（迁移 **`0005_exec`**，`0011_exec_prompt_meta` 增补 **`prompt_pack_version` / `resolved_prompt_binding`**）；执行时间线 **`agent_execution_event`**（迁移 **`0007_exec_event`**）  
> **实现**：`chainup_agent/api/routers/admin_observability.py` · DTO：`api/schemas/admin_agent_executions.py`、`api/schemas/admin_observability_timeline.py` · 查询：`application/admin_agent_executions.py`、`application/agent_execution_events.py`

产品与 **`openapi/admin/observability.yaml`** 对齐；**已实现**：**`agent_execution` 行级** **列表**、**详情**、**删除**、**`GET …/timeline`**、**`GET …/tool-calls`**（**FR-MC803**）、**`GET …/llm`**（**FR-MC804**）、执行详情内嵌 **`GET …/queue`** / **`…/events`** / **`…/retries`** / **`…/recovery`**。**尚未实现**：联合 **`/search`**、审计导出等。路径前缀：**`/api/v1/admin/observability`**。

---

## 1. 通用约定

| 项 | 约定 |
|----|------|
| **Base** | 与 Admin SPA 同源：`/api` 代理至 Agent API（见 **`API_INTEGRATION_GUIDE`**） |
| **鉴权** | 与控制台其它 **`/api/v1/admin/*`** 一致；当前 **`access_token`** 校验策略见 **`BACKEND_SPEC` §3.1**（生产可由网关承接） |
| **响应 JSON** | **camelCase**（**`204`** **无 Body** 除外；Pydantic **`populate_by_name`**） |
| **错误体** | **`ErrorBody`**：**`code`**、**`message`**、**`request_id`**、可选 **`details`**（见 **`BACKEND_SPEC` §4） |
| **筛选逻辑** | 列表接口：各 Query 条件之间为 **AND**；**`keyword`** 单独一条 **OR（三列任一匹配）**，再与其它条件 **AND** |

---

## 2. `GET /api/v1/admin/observability/executions`

### 2.1 用途

分页返回 **`agent_execution`** 行，按 **`created_at` 降序**（最新在前）。

### 2.2 Query 参数

| 参数 | 类型 | 默认 | 约束 | 说明 |
|------|------|------|------|------|
| **`limit`** | integer | `50` | 1～200 | 每页条数 |
| **`offset`** | integer | `0` | ≥ 0 | 跳过条数（偏移分页，非 cursor） |
| **`executionId`** | string | — | trim 非空才生效 | **`execution_id`** **精确**相等 |
| **`userId`** | string | — | 同上 | **`user_id`** **精确**相等 |
| **`channel`** | string | — | 同上 | **`channel`** **精确**相等 |
| **`scenarioId`** | string | — | 同上 | **`scenario_id`** **精确**相等 |
| **`state`** | string | — | 大小写不敏感，规整为大写 | 仅允许 **`ACCEPTED`**、**`SUCCEEDED`**、**`FAILED`**、**`CANCELLED`**；其它 → **422** **`VALIDATION_ERROR`** |
| **`keyword`** | string | — | 最长 256（校验由 FastAPI **`max_length`**） | **子串**匹配：**`execution_id`** **或** **`user_id`** **或** **`scenario_id`**（SQL **`LIKE %keyword%`**）；数据库默认校对规则下大小写行为依赖引擎 |
| **`createdAfter`** | string (`date-time`) | — | RFC 3339 / ISO 8601 | **`created_at`** ≥ 解析后的时刻 |
| **`createdBefore`** | string (`date-time`) | — | 同上 | **`created_at`** ≤ 解析后的时刻 |

**分页语义**：**`total`** 为 **当前筛选条件下** 的全表计数；**`items`** 为 **`[offset, offset + limit)`** 窗口。

### 2.3 响应 **`200`**

```json
{
  "items": [
    {
      "executionId": "exec-a1b2c3d4e5f6789",
      "userId": "123456789",
      "scenarioId": "chat.faq",
      "channel": "telegram",
      "state": "SUCCEEDED",
      "source": "telegram_webhook",
      "idempotencyKey": null,
      "note": null,
      "createdAt": "2026-05-13T08:12:34.567890Z",
      "updatedAt": "2026-05-13T08:12:35.123456Z"
    }
  ],
  "total": 42
}
```

### 2.4 字段说明（`items[]`）

| JSON 字段 | 对应列 | 说明 |
|-----------|--------|------|
| **`executionId`** | `execution_id` | 主键；服务端生成前缀 **`exec-`** |
| **`userId`** | `user_id` | Phase1 Telegram 锚点为 **`tg_id`** 数值串 |
| **`scenarioId`** | `scenario_id` | 可为 **`null`**（accept 时未带场景） |
| **`channel`** | `channel` | 如 **`telegram`** |
| **`state`** | `state` | **`ACCEPTED`** → 成功 **`SUCCEEDED`** / 失败 **`FAILED`** / **`CANCELLED`**（finalize 映射见运行时 **`execution/finalize`**） |
| **`source`** | `source` | 如 **`telegram_webhook`**、**`http_api`** |
| **`idempotencyKey`** | `idempotency_key` | 可选 |
| **`note`** | `note` | finalize 可选 note（Phase1 较少使用） |
| **`promptPackVersion`** | `prompt_pack_version` | **可选**；存在已发布 **Prompt 包**且 **accept** 时未手填时由服务端写入 |
| **`resolvedPromptBinding`** | `resolved_prompt_binding` | **可选** JSON；与 **`GET …/internal/prompts/effective`** **`resolvedPromptBinding`** 同形摘要；无包时为 **`null`** |
| **`createdAt`** | `created_at` | 带时区 |
| **`updatedAt`** | `updated_at` | 带时区 |

---

## 3. `GET /api/v1/admin/observability/executions/{executionId}`

### 3.1 用途

按主键读取单行；响应体与列表 **`items[]` 元素** 相同 schema。

### 3.2 Path

| 参数 | 说明 |
|------|------|
| **`executionId`** | **`execution_id`** 原样（区分大小写取决于 DB collation；本项目 ID 为服务端生成小写十六进制片段） |

### 3.3 响应

| HTTP | `code` | 说明 |
|------|--------|------|
| **200** | — | **`AdminAgentExecutionItem`** |
| **404** | **`AGENT_ADMIN_EXECUTION_NOT_FOUND`** | 不存在 |
| **422** | **`VALIDATION_ERROR`** | Path/校验异常（少见） |

---

## 4. `DELETE /api/v1/admin/observability/executions/{executionId}`

### 4.1 用途

**硬删除**表 **`agent_execution`** 对应主键行（Phase1：**联调清理 / 运维**，无软删）。**对已删除或不存在的 id 再次调用** → **404**（与 **`GET` 详情** 一致；**非**「静默 **204**」幂等删除）。

### 4.2 Path

与 **`§3.2`** 相同。

### 4.3 响应

| HTTP | `code` | 说明 |
|------|--------|------|
| **204** | — | **无 Body**；删除成功 |
| **404** | **`AGENT_ADMIN_EXECUTION_NOT_FOUND`** | 该行不存在 |

---

## 5. 执行时间线（协查）

### 5.1 端点

**`GET`** **`/api/v1/admin/observability/executions/{executionId}/timeline`**

**用途**：按 **`executionId`** 拉取可观测事件时间线（工单协查）；与产品 **`ObservabilityTimelineEvent`** 形状对齐。详见 **`BACKEND_SPEC.md`**（Admin 可观测性 / 产品 **`flow.md` FR-MC801**）。

**治理事件（2026-05-26）**

| `eventName` | `summary` 关键字段 |
|-------------|-------------------|
| **`agent.prompt.binding_resolved`** | **`resolvedPromptBinding`**（完整 SC-PM-22 形）+ 镜像 **`promptBindingResolved`** |
| **`agent.skill.spec_read`** | **`skillId` / `skillSpecVersion` / `specDigest`** + 镜像 **`skillSpecRead`** |
| **`prompt.snapshot`** / **`trading_write`** | 含 **`resolvedPromptBinding`**（写路径 AC-5） |

**`execution/accept`** 后在 **`execution.dispatched`** 之后自动写入 **`agent.prompt.binding_resolved`**（幂等一次）。

### 5.1b 场景 Skill 范围（治理面板）

**`GET`** **`/api/v1/admin/observability/scenarios/{scenarioId}/skill-scope`**

只读；返回 **`mode`**（`write_skill` / `read_only` / `unmapped_write`）、**`skills[]`**、**`promptStrategyPackId`**、**`promptSkillScopeRef`**、**`narrative`**。对齐产品原型 **`ExecutionScenarioSkillScope`**（5176 Demo 仍可用 mock 合并，生产 **`admin/`** 应接本接口）。

### 5.2 响应（示例，200）

根字段为 **`items[]`**（非 OpenAPI 占位草稿里的 **`events[]`**）。**`summary`** 为 **JSON 对象**（由 `payload_json` 与列 **`step_kind` / `outcome`** 合并），可含产品 §2.4 建议之 **`transitionTrigger`**。

```json
{
  "items": [
    {
      "eventName": "agent.execution.step",
      "ts": "2026-05-13T12:34:56.789000Z",
      "executionId": "exec-a1b2c3d4e5f6789",
      "userId": "123456789",
      "summary": {
        "stepKind": "quote",
        "outcome": "success",
        "venue": "coobit",
        "canonicalOp": "place_order",
        "scenarioId": "trade.spot.flash_convert",
        "lastPrice": "65000.1",
        "transitionTrigger": "flash.quote.public_ticker"
      }
    },
    {
      "eventName": "trading.exchange_private",
      "ts": "2026-05-13T12:34:56.900000Z",
      "executionId": "exec-a1b2c3d4e5f6789",
      "userId": "123456789",
      "summary": {
        "stepKind": "submit_order",
        "outcome": "success",
        "venue": "coobit",
        "canonicalOp": "place_order",
        "methodPathSummary": "POST /sapi/v2/order",
        "exchangeOutcome": "success",
        "httpStatus": 200,
        "orderRequest": {
          "path": "POST /sapi/v2/order",
          "symbol": "BTC/USDT",
          "side": "BUY",
          "type": "MARKET",
          "volume": 500.0,
          "newClientOrderId": "cu_agent_abc123",
          "flashMarketMeta": {
            "baseQtyUserRequested": "0.01",
            "userVolumeInput": "0.01",
            "volumeSemantics": "market_buy_quote_amount",
            "quoteAmountOnWire": 500.0,
            "lastPriceUsed": "50000"
          }
        },
        "exchangeResponsePreview": {
          "orderIdString": "499890200602846976",
          "clientOrderId": "cu_agent_abc123",
          "status": "0",
          "symbol": "BTCUSDT",
          "side": "BUY",
          "type": "MARKET"
        }
      }
    }
  ]
}
```

**说明**：**`trading.exchange_private`** 行继承与 **`agent.execution.step`（submit_order）** 同窗的 **`stepKind`**（便于 SQL 落库），UI 宜按 **`eventName`** 区分逐步展示。现货下单相关步骤的 **`summary`** 另含 **`venue`**（V1 **`coobit`**）与 **`canonicalOp`**（**`place_order`**），与产品 **ADR-004** 观测建议一致。

### 5.2.1 现货闪兑（`trade.spot.flash_convert`）事件次序（典型）

| 次序 | `eventName` | `summary.stepKind`（典型） | 说明 |
|------|-------------|------------------------------|------|
| 1 | **`agent.execution.step`** | **`quote`** | 公开 **`GET /sapi/v2/ticker`** 摘要（Telegram Type-A 发按钮前；HTTP **`POST …/flash-convert`** 内在 **BUY** 路径再记一条 **quote**） |
| 2 | **`agent.execution.step`** | **`confirm_prompt`** | 仅 Telegram Type-A：Inline 二次确认已展示 |
| 3 | **`agent.execution.step`** | **`confirm_accept`** | 用户点「确认下单」callback（若复用当轮 **`executionId`**，随后 **不再** 重复 **quote**） |
| 4 | **`agent.execution.step`** | **`submit_order`** | 摘要侧业务步：数量、**`orderId`** 等 |
| 5 | **`trading.exchange_private`** | **`submit_order`** | **`POST /sapi/v2/order`**：**`methodPathSummary`**、**`exchangeOutcome`**、**`httpStatus`**、**`clientOrderRef`**；脱敏 **`orderRequest`**；**`exchangeResponsePreview`**：成功时为订单 ACK 白名单字段；**拒单 / 业务错误**时为对端 JSON 之 **`code`/`msg`**（及白名单内其它字段）。**超时、传输错误、非 JSON** 一般无 **`exchangeResponsePreview`** |

HTTP 直连闪兑：**`quote` → `submit_order` → `trading.exchange_private`**（**3** 条，无 confirm）。旧 pending 无 **`executionId`** 时 Telegram callback 仍可能 **新开** **`agent_execution`**（**`source=telegram_callback`**），时间线从 **confirm_accept** 起。

### 5.2.2 Phase1 · 只读路由（`POST /api/v1/agent/routing/execute` 与 Telegram **`read.*`**）

| 次序 | `eventName` | `summary.stepKind`（典型） | 说明 |
|------|-------------|------------------------------|------|
| 1 | **`trading.exchange_public`** 或 **`trading.exchange_private`** | **`exchange_read`** | 成功：**`methodPathSummary`**、**`exchangeReadPreviewSummary`**、**`transitionTrigger`**（**`routing.read.public_ticker`** / **`routing.read.public_depth`** / **`routing.read.public_trades`** / **`routing.read.private_account`**） |
| 1（失败） | **`agent.execution.step`** | **`exchange_read`** | **`routing.read.failed`**：**`appErrorCode`** / **`httpStatus`** |

### 5.2.3 Telegram 闲聊（**`ROUTE_CHAT_FAQ`**）

| 次序 | `eventName` | `summary.stepKind`（典型） | 说明 |
|------|-------------|------------------------------|------|
| 1 | **`prompt.snapshot`** | **`intent_nlu`** | 意图 NLU 包（**`scenarioId`**=`agent.runtime.intent_nlu`）：**`promptPackVersion`** / **`resolvedPromptBinding`**，及 **`nluSource`**、**`intentNluLlmEnabled`**、**`planNextStep`** 等 |
| 2 | **`llm.chat.faq`** | **`chat_faq`** | 闲聊 LLM 调用 + **`chat.faq`** 有效包快照；**`gatewayModelId`** / **`gatewayProviderId`** / **`useArkProtocol`**；**`outcome`** **success** / **failure**；失败时可有 **`userVisibleError`** |

### 5.3 错误

| HTTP | `code` | 说明 |
|------|--------|------|
| **404** | **`AGENT_ADMIN_EXECUTION_NOT_FOUND`** | **`executionId`** 对应的 **`agent_execution`** 不存在 |

---

## 6. 执行详情内嵌 Tab（`runtime.execution-detail`）

与产品 **`page-specs.md`** **任务队列 / 运行事件 / Retries / Recovery** 对齐；数据源均为 **`agent_execution_event`**（及 **`trading_reconcile`** 推断），**非**独立队列表。

| Method | Path | 响应 | 说明 |
|--------|------|------|------|
| **`GET`** | **`…/executions/{executionId}/queue`** | **`{ items: ExecutionTaskQueueItem[] }`** | 未完成编排步（**`orchestration_flow_catalog`** + **`agent.orchestration.step`**）及未完成 **`agent.execution.step`**；**`state`**：`PENDING` \| `RUNNING` \| `BLOCKED` |
| **`GET`** | **`…/executions/{executionId}/events`** | **`{ items: ExecutionRuntimeEventItem[] }`** | 运行域摘录（**`tool.*` / `trading.*` / `llm.*` / `agent.execution.*`** 等）；**排除** **`agent.orchestration.step`**（与 **Timeline** 分工） |
| **`GET`** | **`…/executions/{executionId}/retries`** | **`{ retryCount, items[] }`** | **`retry.*` / `trading.reconcile` / exchange `unknown`** 等时间线条目；**`reason`** 中文摘要 |
| **`GET`** | **`…/executions/{executionId}/recovery`** | **`ExecutionRecoveryResponse`** | **`stillUnknown` / `caseKind` / `resolutionStatus`**（复用 Agent 对账推断）；**`observabilitySearchPath`**、**`reconcileApiHint`** 供 FE 深链 |

**`ExecutionTaskQueueItem`**（camelCase）：**`taskId`**、**`executionId`**、**`state`**、**`scheduledAt`**、可选 **`stepKey`** / **`stepLabelZh`**。

**`ExecutionRuntimeEventItem`**：**`at`**、**`eventType`**（持久化 **`event_type`**）、**`summary`**（单行可读）、可选 **`seq`**。

**`ExecutionRetryItem`**：**`attempt`**（1-based）、**`at`**、**`reason`**、可选 **`eventType`** / **`seq`**。

**`ExecutionRecoveryResponse`** 另含 **`recoveryTitle`** / **`recoveryBody`**（与 **`opsPanelHints.EXECUTION_DETAIL`** 一致）、**`manualRetrySupported`**（Phase1 恒 **`false`**）。

### 6.1 错误

与 **`§5.3`** 相同：**404** **`AGENT_ADMIN_EXECUTION_NOT_FOUND`**。

---

## 7. 错误码汇总

| HTTP | `code` | 典型场景 |
|------|--------|----------|
| **422** | **`VALIDATION_ERROR`** | **`state`** 非法；或其它 FastAPI 校验失败 |
| **404** | **`AGENT_ADMIN_EXECUTION_NOT_FOUND`** | **`GET` 详情**、**`GET …/timeline`** 或 **`DELETE`** 时 id 不存在 |

---

## 8. 数据从哪里来（与 Bot / Runtime 对齐）

| 写入路径 | `source` / `channel` | 说明 |
|----------|----------------------|------|
| Telegram 已绑定且门禁通过 | **`telegram_webhook`** · **`telegram`** | **`run_telegram_turn_execution`**：**accept → 生成回复**；常规路径 **`finalize SUCCESS`**。**Type-A 闪兑** 出确认按钮后轮次 **`leave_accepted`**，行保持 **`ACCEPTED`** 直至 callback **finalize** |
| Telegram 闪兑 **`callback_query` 确认** | 复用：`source` 不变；新开：**`telegram_callback`** | 优先复用 **`pending.executionId`**；时间线追加 **confirm_accept**、下单步与 **`trading.exchange_private`** |
| **`POST /api/v1/agent/trade/spot/flash-convert`** | **`http_api`** · **`http`** | 路由内 **`execution_accept → spot_flash_convert_for_bound_user（写时间线）→ finalize`**；**`commit`** 后与 Admin 时间线对齐 |
| **`POST /api/v1/agent/routing/execute`** | **`http_api`** · Body **`channel`** 默认 **`http`** | **`execution_accept` → Phase1 路由（只读 / orchestration / 占位 **`note`）→ `agent_execution_event` → `execution_finalize`**；**200** 含 **`executionId`**；**业务错误**（如 **403**）`**finalize FAILED**` 后仍抛 **`AppError`** |
| **`POST /api/v1/agent/execution/accept`**（HTTP） | **`http_api`**（accept 时传入） | 探针 / 集成 |

**门禁拒绝**：**不**插入 **`agent_execution`**。

---

## 9. 与公开 Runtime API 的关系

| 能力 | 路径 | 说明 |
|------|------|------|
| 创建 / 终结（写） | **`POST …/agent/execution/accept`**、**`POST …/agent/execution/finalize`** | 运行时契约 |
| 查询（读） | **`GET …/agent/execution/{executionId}`** | 与 Admin 详情 **同一表** |
| 删除（Admin） | **`DELETE …/admin/observability/executions/{executionId}`** | **仅运营控制台**；公开 Runtime **无** delete |

---

## 10. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-05-27 | §6：执行详情 **`/queue`**、**`/events`**、**`/retries`**、**`/recovery`** |
| 2026-05-18 | §5.2.3：**Telegram `ROUTE_CHAT_FAQ`** — **`prompt.snapshot`**（**`intent_nlu`**）与 **`llm.chat.faq`**（**`chat_faq`**） |
| 2026-05-15 | §5.2：**`summary`** 示例与说明增补 **`venue`**（**`coobit`**）、**`canonicalOp`**（**`place_order`**）（现货闪兑/限价下单时间线，ADR-004 观测） |
| 2026-05-14 | §5.2 示例：**`orderRequest.flashMarketMeta`** 标明 **MARKET BUY** 时 **`volume`**=计价 **amount**（与 **`baseQtyUserRequested`×`lastPriceUsed`** 一致）；**SELL** 为 **`market_sell_base_qty`** |
| 2026-05-14 | §5.2 / §5.2.1：**`trading.exchange_private`**：**`orderRequest`**；**`exchangeResponsePreview`**（**成功**与 **可对端 JSON 协查之失败**；超时/非 JSON 等除外） |
| 2026-05-14 | §7：**`POST /routing/execute`** 写入 **`agent_execution` + timeline**；**`transitionTrigger`** 增 **`routing.read.*`** / **`routing.read.failed`** |
| 2026-05-13 | **`DELETE …/executions/{executionId}`**（硬删除，**204** / **404**） |
| 2026-05-13 | 初版：列表 + 详情字段级契约与筛选语义 |
