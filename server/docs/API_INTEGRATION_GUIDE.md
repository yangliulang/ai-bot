# 分阶段开发说明 · 第一阶段 API 与前端接入

> **读者**：前端（`admin/`）、全栈联调、BFF。  
> **需求真源**：[`../../product-doc/product/roadmap.md`](../../product-doc/product/roadmap.md)（分阶段 HTTP 导航见遗留 [`development-roadmap.md`](../../product-doc/development-roadmap.md)）。  
> **运行时实现目录**：[`../`](../README.md)（本 `server/` 工程）。

本文说明：**产品路线图如何分阶段承接**、`server` 当前**对外暴露的路径**以及如何**用 OpenAPI / HTTP 接入**。契约细节以 **`product-doc/specs/openapi/`** 与 **`product-doc/specs/design/api.md`** 为准；尚有 **极少数**契约未落地的路径保留 **501**，见下文「当前状态」。

**时间与 UTC**：REST JSON 中 **`datetime`/`createdAt`/`updatedAt`/`ts` 等默认均为 UTC**（见 **`BACKEND_SPEC` §2.1**、下文 **§3.3** 表）；**浏览器展示**由 `admin/` 做时区格式化。

**收口验收（可勾选、与本服务实现对齐）**：[`PHASE1_ACCEPTANCE.md`](PHASE1_ACCEPTANCE.md)。

---

## 1. 文档与职责边界（避免接错网关）

| 能力面 | SSOT（优先读） | 典型调用方 |
|--------|----------------|-----------|
| **运营后台控制台**（Agent / Prompt / Tool / Billing / Access / Telegram 运维等） | `product-doc/specs/openapi/admin/*.yaml` | Vue `admin/` 多数页面应走团队统一的 **Admin BFF / 网关**，路径以 OpenAPI 为准（如 `/admin/agents/*`）。 |
| **Agent 运行时 / 开通 / Telegram Webhook / 编排相关 HTTP**（路线图 Phase 1 下列出的路径） | 路线图 + 后续与 `specs/openapi/` 中联调冻结的 YAML | 渠道、运行时、或由 BFF **聚合后再给前端**。 |
| **本仓库 Python 服务** | `server/` 当前实现、`/openapi.json` | **联调占位**与各 Phase 逐步实现。 |

前端开发时：**先确认接口属于「Admin OpenAPI」还是「运行时 Phase API」**，再选用 Base URL；不要把路线图里的 `/api/v1/agent/...` 默认等价于控制台已存在的 `admin` YAML。

---

## 2. 阶段一览（承接路线图）

以下与 **`product/roadmap.md`** / 遗留 **`development-roadmap.md`** 大章对齐；**列「HTTP 摘录」仅为导航**，完整清单以 specs 与 OpenAPI 为准。

| 阶段 | 主题（摘要） | HTTP / 契约锚点 |
|------|----------------|----------------|
| **第一阶段** | 子账户与开通、Telegram 接入、意图/路由、门禁、计费执行骨架 | **本文 §4** · 路线图 §「第一阶段」 |
| **第二阶段** | 现货/合约/杠杆等交易能力 | 路线图 §「第二阶段」+ `exchange`/`agent` 相关 OpenAPI |
| **第三阶段及以后** | 按路线图后续章节（监控、账单、风控等） | 以路线图与契约注册表迭代 |

---

## 3. 第一阶段：如何用「对外 API 文档」

### 3.1 获取机器可读契约（推荐）

本地启动 **`server`** 后：

| 资源 | URL（默认 `CHAINUP_AGENT_API_PORT=8080`） |
|------|-------------------------------------------|
| **Swagger UI** | `{base}/docs` |
| **OpenAPI JSON** | `{base}/openapi.json` |

`base` 示例：`http://127.0.0.1:8080`。  
前端可用 OpenAPI JSON 生成类型/客户端（`openapi-typescript`、`orval`、`hey-api/openapi-ts` 等），**但以产品冻结 YAML 为最终对齐对象**——当前 FastAPI 描述会随实现对齐并逐步替换占位模型。

### 3.2 跨域 / 网关

浏览器直连 `admin` dev server 与本服务不同源时：

- **推荐**：`admin` 侧 **Vite `proxy`** 把 `/api`、`/webhook` 指到后端（同源路径，无 CORS）。
- **或**：服务端配置 **CORS 允许列表**（生产须收紧）；当前 `server` 未默认开启宽 CORS，联调请以代理为准。

示例（写入 `admin/vite.config.ts` 思路，仅供参考）：

```ts
server: {
  proxy: {
    '/api': { target: 'http://127.0.0.1:8080', changeOrigin: true },
    '/webhook': { target: 'http://127.0.0.1:8080', changeOrigin: true },
  },
}
```

### 3.3 通用请求约定

| 项 | 约定 |
|----|------|
| **版本前缀** | ` /api/v1/...`（REST） |
| **Content-Type** | `application/json`（除非将来文件类接口另行规定） |
| **`x-request-id`** | **建议**前端生成 UUID 传入；服务端会回响，便于与支持/日志对齐。 |
| **日期时间（`*At` / `ts`）** | **均为 UTC**（ISO 8601，常带 **`Z`** / **`+00:00`**）。**禁止**把无时区字符串当「运营本地」理解；列表/详情 **须标明时区或转换为展示时区**（见 **`admin/FE_HANDOFF.md`**、**`BACKEND_SPEC` §2.1**）。 |

### 3.4 响应与错误（实现已统一骨架）

成功体：各接口以 OpenAPI/Pydantic 为准。

**结构化错误**（`AppError`、`HTTPException`、校验失败）形状与后端一致：

```json
{
  "code": "STRING",
  "message": "human readable",
  "request_id": "uuid-or-unknown",
  "details": {}
}
```

- 校验失败：`422`，`code` 常为 `VALIDATION_ERROR`，`details.errors` 为 FastAPI 校验明细。

### 3.5 当前实现状态（联调必读）

路线图 Phase 1 对应路由已在 `server` **注册**。仍有 **少数**路径在契约落地前保留 **`501` + `StubBody`**（`status`、`phase`、`operation_id`、`hint`）。

**已实现（非 StubBody）**：**`POST /api/v1/agent/api-binding/validate`**／**`.../confirm`**／**`POST /api/v1/me/agent/bindings/trading-api`**；**`GET /api/v1/agent/api-binding/status`**（Query **`userId`**）；**`GET /api/v1/agent/subaccount/status`**；**`POST /api/v1/agent/onboarding/initiate`**；**`POST /api/v1/agent/subaccount/create`**（**DEFERRED**，非真实创建）；以及 §4 中 **`intent` / `scenarios` / `routing` / `access` / `execution`** — 详见 §4.1。**未迁移 binding 表时** Webhook DB 查询 **降级**（仍走绑定引导）。

前端可先行：

1. **接好 Base URL / 代理**；  
2. **按路径封装 API 客户端**；对仍为 **501** 的路径做降级或 mock；其它路径以 **§4** 状态码/body 为准；  
3. 契约冻结后生成类型并与 **`product-doc/specs/openapi/`** 对齐。

### 3.6 管理 SPA 登录 / 注册（`admin/`）

- **`POST /api/auth/login`**：Body：`{ "username", "password" }`。**`ADMIN_CONSOLE_AUTH_MODE=env`**：依赖 **`ADMIN_PANEL_USERNAME` / `PASSWORD`** 成对配置，缺省 **`503 ADMIN_CONSOLE_AUTH_DISABLED`**。**`database`**：查表 **`admin_console_user`**（bcrypt），错误 **`401 ADMIN_CONSOLE_AUTH_INVALID_CREDENTIALS`**。
- **`POST /api/auth/register`**：**仅 `database`** 模式；首张管理员在 **`admin_console_user` 为空** 时可注册（口令 **`password` ≥ 8**）。已有账号时需 **`CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION=true`**，否则 **`403 ADMIN_CONSOLE_REGISTRATION_DISABLED`**。**`503`**：**`ADMIN_CONSOLE_REGISTRATION_REQUIRES_DATABASE_AUTH`**（误在 env 模式调用）。用户名冲突：**`409 ADMIN_CONSOLE_USERNAME_ALREADY_EXISTS`**。
- **成功**：`200`，`{ "access_token", "token_type", "username" }`。配置非空 **`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`（≥16）** 时 **`access_token`** 为 HS256 JWT，且 **`/api/v1/admin/*`** 须 **`Authorization: Bearer`**。
- **Vite**：将 `/api` 代理到 Agent API（见 `DEPLOYMENT_NOTES.md` / 各前端 `vite.config`），控制台使用相对路径即可。

---

## 4. 第一阶段接口清单（与路线图一致）

以下路径与 **路线图「第一阶段」**（`product/roadmap.md` / 遗留 `development-roadmap.md`）一致；**不含**控制台 Admin YAML 中的 `/admin/*`。

### 4.1 子账户体系与开通（§1.1）

**产品口径（与 PM）**：Agent 运行时 **不代用户开立**交易所子账户、**不代开** API Key。用户须在进入 Deeplink/H5 **之前**，于 **主站/所内控制台**自行创建子账户（若要求分立）与交易 API，再到绑定页做 **validate + confirm**。**`POST .../subaccount/create`** 为 **兼容占位**：始终 **`accepted=false`**，语义为「本能力不适用」，参见 **`BACKEND_SPEC` §3.1「子账户与 API Key」**。

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/agent/onboarding/initiate` | **已实现**：Body **`telegram.tg_id`**（数值串）；**200** **`onboardingId`、`nextStep`（`bind_trading_api` \| `complete`）、`agentTradingApiBindingStatus`**；缺 **`tg_id`** → **400** |
| `GET` | `/api/v1/agent/subaccount/status` | **已实现**：Query **`userId`**（TG **`tg_id`**）；**`subaccountReady`**≈是否已有托管绑定（**非**所内开立态）；**`agentSubAccountId`** 恒 **`null`** |
| `POST` | `/api/v1/agent/subaccount/create` | **已实现**：**200** **`accepted=false`、`DEFERRED_EXCHANGE_CONSOLE`**（**不提供**自动开立；用户自备 Key 后经 Deeplink 绑定） |
| `GET` | `/api/v1/agent/api-binding/status` | **已实现**：Query **`userId`**；**200** **`agentTradingApiBindingStatus`、`openapiBaseUrl?`、`bindingId?`** |
| `POST` | `/api/v1/agent/api-binding/confirm` | **已实现**：须在 **validate** 成功后再调；Body **`sub_account_id`**（必填）+ 同上 + **`telegram`**（**`tg_id` 必填**）；**GET /sapi/v1/account** 再探测；密钥 **Fernet** 写入 **`telegram_agent_trading_binding`**；**upsert `agent_instance`**；**200** 含 **`instanceId`、`agentSubAccountId`**；**503** `AGENT_BINDING_STORAGE_UNAVAILABLE` / `AGENT_BINDING_FERNET_KEY_INVALID`；**400** `AGENT_TELEGRAM_CONTEXT_*` / **`AGENT_SUB_ACCOUNT_*`** |
| `POST` | `/api/v1/me/agent/bindings/trading-api` | **已实现**：产品与 **`deeplink`** 对齐：**`openapiBaseUrl`**, **`apiKey`**, **`apiSecret`**, **`subAccountId`**（必填）, 可选 **`telegram`** / **`idempotencyKey`** / **`deeplinkToken`** → 同上落库语义 + **`instanceId`** |
| `POST` | `/api/v1/agent/api-binding/validate` | **已实现**：Body **`openapi_base_url`** + **`api_key`** + **`secret_key`** + **`sub_account_id`**；**GET /sapi/v1/account**；若响应含常见账户 id 字段须与 **`sub_account_id`** 一致；**200** `{ "valid": true, "ok": true }`；**400** `AGENT_API_KEYS_*` / **`AGENT_SUB_ACCOUNT_*`** / `AGENT_OPENAPI_BASE_URL_INVALID` / `AGENT_API_KEYS_REJECTED`；**502** `AGENT_OPENAPI_PROBE_FAILED` |

### 4.2 Telegram 渠道（§1.2）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/webhook/telegram/{botToken}` | Telegram 推送：**path token OK 后立即 `200`**（默认 **`sendMessage`** / LLM / 路由在 **后台任务**；**`CHAINUP_AGENT_TELEGRAM_WEBHOOK_INLINE_PROCESSING=true`** 时同请求内执行）。支持 **`callback_query`**：闪兑 **`fcp`/`fcx`**、限价 **`lcp`/`lcx`** + token → 对应 **`…/trade/spot/*`** 写路径。构建回复若异常仍会 **`sendMessage`** 兜底（**`telegram_webhook_build_reply_failed`**）。**未绑定**：Deeplink **明文链接**/**InlineKeyboard**；**已绑定**（DB **或** `CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST`）：**`access/evaluate`** → 意图 → **`read.*`** 经 **`routing/execute`**；**确认** 发 **`reply_markup`**；**`chat.faq`**：**`baseUrl`** 含 **`volces.com`** → **`POST …/api/v3/responses`**，否则 **`POST …/chat/completions`**；Bearer：**`secretRef`** 或 **`CHAINUP_AGENT_LLM_FALLBACK_API_KEY`**；门禁附带 **`telegramChatId`**。细则 **`BACKEND_SPEC` §3.1** |
| `POST` | `/api/v1/admin/channels/telegram/webhook` | 运维 **setWebhook**（Body 可选 `url` / `secretToken` / `dropPendingUpdates`，与 **`admin/telegram-channels.yaml`** 同窗） |
| `GET` | `/api/v1/admin/channels/telegram/webhook` | 运维 **getWebhookInfo** 摘要 |
| `DELETE` | `/api/v1/admin/channels/telegram/webhook` | **deleteWebhook** 后刷新摘要 |

### 4.2a Prompt Assembly（`chat.faq` LLM · Intent NLU）

与 **`runtime-injection` §1** 对齐的 **子集**（非全 **`scenarioId`** 通用编排）：  
- **TRADING LLM**：**`assemble_trading_llm_payload`**（**`scenario_id`** + **`TRADING`** 包）；允许列表 **`TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`**（**`chat.faq`**、**`read.market.*`** — **`0014`/`0015`**、**`read.account.balance`** / **`wealth.holdings_read`** — **`0016`**、**`trade.spot.flash_convert`** / **`trade.spot.limit_order`** — **`0018`**；各场景 env **`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_*`**，现货写路径 Type-A 仍为确定性文案）；扩展场景须 **`PUBLISHED`** TRADING 包 + **代码放行**。**`assemble_chat_faq_llm_payload`** = **`chat.faq`** 别名。拼装顺序：**SYSTEM**（**`agent.runtime.platform_system`**）→ **SAFETY** → **TRADING** **`messages`**（Few-shot）→ **Runtime Context** JSON → **Tool Spec** JSON Schema SSOT → **User**；出站仍走 §4.2 网关（**`/responses`** vs **`/chat/completions`**）。审计小节标题形如 **`SCENARIO_STRATEGY_<SLUG>`**（如 **`READ_MARKET_DEPTH`**、**`WEALTH_HOLDINGS_READ`**）。种子：**`0013`**～**`0016`**、**`0018`**；无 **`PUBLISHED`** 平台包时 **降级内置常量**。  
- **Intent NLU**（**`CHAINUP_AGENT_INTENT_NLU_USE_LLM=true`**）：**`assemble_intent_nlu_system_prompt`** — 平台 SYSTEM/SAFETY + 核心 NLU + **`INTENT_NLU_OUTPUT_JSON_SCHEMA`**。  

联调观测：Webhook / Timeline 若写入 LLM 步，可见 **`promptAssemblyContract`**、**`promptPackVersions`** 等（**`BACKEND_SPEC`** §11 · **`PHASE1_ACCEPTANCE.md`** §8）。

### 4.3 意图识别与路由（§1.3）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/agent/intent/recognize` | **已实现**：须 **DB**（**`DbSession`**）。Body **`text`**；可选 **`sessionId` / `executionId` / `locale` / `previousScenarioId`**。**NLU**：**`keyword_v1`**；**`CHAINUP_AGENT_INTENT_NLU_USE_LLM=true`** 时尝试 **LLM JSON**（**`llm_structured_v1`**，失败回退关键词）。**200**：**`scenarioId` / `confidence` / `candidates[]`**、**`nlu`**、**`plan`**、**`orchestrationVersion`**（**`intent-router.policy.v2`**）。交易类受 **`FEATURE_TRADING`**、**现货写**受 **`FEATURE_AGENT_SPOT`** 约束 |
| `GET` | `/api/v1/agent/scenarios` | **已实现**：内置场景目录 + **`flowSummary` / `executionSteps[]` / `closureStatus`** + **`readiness`**（**`trade.spot.flash_convert`**、**`trade.spot.limit_order`**、**`trade.spot.open_orders`**、**`trade.spot.cancel_order`**、**`chat.faq`**（LLM 兜底）为 **`ready`**；其它交易类多为 **`stub`**）；**`orchestrationRegistryVersion`**=`2026.05-orc-v1` |
| `GET` | `/api/v1/agent/scenarios/{scenarioId}` | **已实现**：单场景编排详情（**`flowSummary`**、**`executionSteps`**、**`specRefs`**、**`flowAnchor`**）；**404** **`AGENT_SCENARIO_NOT_FOUND`** |
| `POST` | `/api/v1/agent/routing/execute` | **已实现**：**`read.market.*` / `read.account.balance`** 等 **路由**（须托管绑定）；**每笔 HTTP 调用** **`execution_accept` → 交易所只读（或 orchestration **`note`）→ `agent_execution_event`（`trading.exchange_public` / `trading.exchange_private` · `exchange_read` 或失败 **`routing.read.failed`**）→ `agent.orchestration.step`（读路径步骤）→ `execution_finalize`** 并 **`commit`**；**200** 体含 **`executionId`**（Admin 时间线协查）；**`trade.spot.open_orders`** 返回 **`exchangeReadPreview`**（**`spot_open_orders_v1`**）；**`trade.spot.flash_convert`** / **`limit_order`** / **`cancel_order`** routing 仍为 **`note` 指引**（撤单写见 **`POST …/trade/spot/cancel`**；Telegram **`EXECUTE_SPOT_CANCEL`**）；其余 **`scenarioId`**：**200** **`routed=true`** + 占位 **`note`** |
| `GET` | `/api/v1/admin/orchestration/policy` | **已实现（Phase2）**：执行策略读模型；**`maxToolCalls` / `maxOrchestrationSteps`** 镜像 **`orchestrationExecutionBudget`** |

**`scenarioId` 下限（路线图摘录）**：`read.market.ticker`、`read.market.depth`、`read.market.trades`、`read.account.balance`、`trade.spot.flash_convert`、`trade.spot.limit_order`、`trade.spot.open_orders`、`trade.spot.cancel_order`、`trade.futures.market_order`、`trade.futures.limit_order`、`margin.cross.market_order`、`wealth.holdings_read`、`automation.condition_order`、`chat.faq`。

### 4.3a 第二阶段 · 现货闪兑（路线图 §2.1）

与 **ChainUp GitBook** [Spot · New Order](https://exchangedocsv2.gitbook.io/open-api-doc-v2/spot.md) **及** 本仓 **`server/coobit_openapi.md`** 基准地址说明一致；私有 **`POST /sapi/v2/order`**，签名 **`timestamp + POST + /sapi/v2/order + body`**（body 为 **key 排序** 后的紧凑 JSON）。**下单 JSON `symbol`** 为 **BASE/QUOTE**（如 **BTC/USDT**），与文档 *Request Body* 示例一致；**`MARKET BUY`** 的 **`volume`** 为 **计价 amount**（服务端由 base×价换算）。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/agent/trade/spot/quote` | **已实现**：Query **`userId`**（**`tg_id`**）、**`symbol`**；**200** **`scenarioId`**、**`symbol`**、**`symbolOrder`**、**`quotePreview`**（公开 **`GET /sapi/v2/ticker`**）；须托管绑定，否则 **403** **`AGENT_SUBACCOUNT_REQUIRED`** |
| `POST` | `/api/v1/agent/trade/spot/flash-convert` | **已实现**：Body **`userId`**、**`symbol`**、**`side`**（**`BUY`/`SELL`**）、**`volume`**（字符串，**base 数量**；**`BUY`** 时服务端按 ticker **`lastPrice`** 换算计价 **amount** 再调交易所；**`SELL`** 为 base）、可选 **`newClientOrderId`**（**须少于 32 字符**，缺省服务端生成 **`cu_agent_<hex>`** 总长 **31**）；**200** **`orderId`**、**`exchangeOrderPreview`** 等；**400** **`AGENT_SPOT_ORDER_REJECTED`**（**`message`** 常含交易所 **`msg`**；权限类拒单时 **`details.reject_reason`** 可为 **`API_PERMISSION_OR_SUBACCOUNT`**）；**502** **`AGENT_SPOT_ORDER_FAILED`** |

### 4.3b 第二阶段 · 现货限价（路线图 §2.2）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/agent/trade/spot/limit-order` | **已实现**：Body **`userId`**、**`symbol`**、**`side`**、**`volume`**（**base 数量** 字符串）、**`price`**、可选 **`timeInForce`**（**`GTC`/`IOC`/`FOK`**）、可选 **`newClientOrderId`**（**须少于 32 字符**，规则同闪兑）；**200** **`scenarioId`**=`trade.spot.limit_order`、**`type`**=`LIMIT` 等；**422** **`VALIDATION_ERROR` / `PRICE_REJECTED_AGENT_BAND`**（见 **`CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_*`**）；余错误码与闪兑同 family |

### 4.3c 第二阶段 · 现货当前委托与撤单（GitBook · `openOrders` / `cancel`）

与 **Spot** [Current Open Orders](https://exchangedocsv2.gitbook.io/open-api-doc-v2/spot.md) / **Cancel Order** 一致：私有 **`GET /sapi/v2/openOrders`**（Query **`symbol`**、**`limit`**）、**`POST /sapi/v2/cancel`**（Body **`symbol`**、**`orderId`**、可选 **`newClientOrderId`**）；签名 **`timestamp + METHOD + requestPath + body`**，GET 时 **`body`** 为空串、**`requestPath`** **含**查询串（服务端对 query **key 排序** 后编码）。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/agent/trade/spot/open-orders` | **已实现**：Query **`userId`**、可选 **`symbol`**、可选 **`limit`**（**1～1000**）；**200** **`scenarioId`**、`orders[]`、**`symbol`/`symbolOrder`**（有筛选时）；**403** **`AGENT_SUBACCOUNT_REQUIRED`**；**400** **`AGENT_SPOT_ORDER_REJECTED`**；**502** **`AGENT_SPOT_OPEN_ORDERS_FAILED`** / **`AGENT_OPENAPI_PROBE_FAILED`** |
| `POST` | `/api/v1/agent/trade/spot/cancel` | **已实现**：Body **`userId`**、**`symbol`**、**`orderId`** 或 **`newClientOrderId`**（至少其一）；**200** **`scenarioId`**=`trade.spot.cancel_order`；错误族与 **`…/flash-convert`** 一致；时间线 **`cancel_order`** |

### 4.3d §6 · 504/UNKNOWN 写路径对账（路线图 6.2）

写路径超时/504 或改单「撤成单败」后，用交易所 **查单** 闭合终态（现货 **`GET /sapi/v2/order`**、合约 **`GET /fapi/v1/order`**）。推荐带 **`executionId`** 从 **`agent_execution_event`** 推断 **`caseKind`** 与查单目标；亦可显式 **`venue`/`symbol`/`orderId`/`clientOrderId`/`caseKind`**。

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/agent/trading/reconcile` | **已实现**：Body **`userId`**、推荐 **`executionId`**；**200** **`reconcileId`**、**`caseKind`**、**`resolutionStatus`**、**`stillUnknown`**、**`userMessage`**、**`orderLookups[]`**；写入时间线 **`trading.reconcile`** |
| `GET` | `/api/v1/agent/trading/reconcile/status` | Query **`userId`**、**`executionId`**；**200** 最近一次对账或 **`resolutionStatus=UNKNOWN`**（时间线仍有 unknown 写、尚无 reconcile 事件） |

改单 **502** **`AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED`** 的 **`details`** 含 **`reconcileSuggested`**、**`reconcileCaseKind`**、**`reconcilePath`**。细则 **`BACKEND_SPEC`** §3.1 · **`pytest tests/test_trading_reconcile.py`**。

### 4.4 门禁（Gate）（§1.4）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/agent/access/evaluate` | **已实现**：**`userId`** = **Telegram `tg_id`**（数值串，**勿填子账户号**）；可选 **`subAccountId`** = 绑定 **`confirm`** 时子账户 ID（经 **`agent_instance`** 解析 **`tg_id`**）；须至少一项。**活跃封禁** → **`AGENT_USER_BLOCKED` / `AGENT_COMPLIANCE_RESTRICTED`**；**DB 绑定** **或** env 放行（**`telegramChatId`**）；**`enforce_rollout_whitelist`** 时须在 DB 白名单；**200** **`EligibilityEnvelope`**；响应可选 **`requiresMainSite`**（**`true`**=须 H5/API 绑定，**`false`**=允许名单或已 **`bindingVerified`**，其它常为 **`null`**）；**422** 参数非法 / **`subAccountId` 无实例** |
| `GET` | `/api/v1/agent/access/reasons` | **已实现**：阻断码与人类可读 **`summary`** 列表 |

业务错误 **`code`** 需与 **`agent-management` / `access-control`** OpenAPI **`enum`** 对齐（路线图示例：`AGENT_COMPLIANCE_RESTRICTED`、`AGENT_SUBACCOUNT_REQUIRED`、`AGENT_GLOBAL_OFF`、`AGENT_OPS_SUSPENDED`、`AGENT_REGION_BLOCKED`、`AGENT_KYC_REQUIRED`、`AGENT_ROLLOUT_BLOCKED`、`AGENT_MEMBERSHIP_BLOCKED` 等）。

运维开关：**`CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED`** · **`CHAINUP_AGENT_AGENT_RUNTIME_OPS_SUSPENDED`**（映射 **`AGENT_GLOBAL_OFF` / `AGENT_OPS_SUSPENDED`**）。

### 4.5 可计费执行（§1.5）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/agent/execution/accept` | **已实现**：表 **`agent_execution`**（**`executionId`** 前缀 **`exec-`**）；Body **`userId`** / 可选 **`scenarioId`** / **`channel`** / **`idempotencyKey`**；**`commit`** 后可见 |
| `GET` | `/api/v1/agent/execution/{executionId}` | **已实现**：**404** **`EXECUTION_NOT_FOUND`** |
| `POST` | `/api/v1/agent/execution/finalize` | Body **`executionId` + outcome**（`SUCCESS`/`FAILED`/`CANCELLED`）；状态 **`SUCCEEDED`/`FAILED`/`CANCELLED`**；可选 **`note`**（入库截断） |

核心概念：**`executionId`**、扣费与子账户 **`USDT`** 口径见路线图与 **`billing`** 需求卷。**当前无真实计费落账**；Telegram 已绑定会话每轮业务答复自动 **`accept→finalize`**（**`source=telegram_webhook`**），便于后续挂 **`billingTraceId` / token**。

### 4.6 运营控制台登录（`admin/` 联调）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/auth/login` | `admin/` 控制台登录（**路由非** `/api/v1/agent/*`）：**env** 模式靠 **`ADMIN_PANEL_*`**；**database** 靠表 **`admin_console_user`** |
| `POST` | `/api/auth/register` | **`database`** 模式自助注册：**空库首张**口令≥8；多账号须 **`ADMIN_CONSOLE_OPEN_REGISTRATION`** |

**请求**（`application/json`）：

```json
{ "username": "<CHAINUP_AGENT_ADMIN_PANEL_USERNAME>", "password": "<…>" }
```

**成功 `200`**：

```json
{
  "access_token": "<opaque | HS256 JWT>",
  "token_type": "bearer",
  "username": "<echo>"
}
```

**错误**（与 §3.4 **`ErrorBody`** 一致）：**`401`** `code=ADMIN_CONSOLE_AUTH_INVALID_CREDENTIALS`；**`503`** `code=ADMIN_CONSOLE_AUTH_DISABLED`（未配置控制台账号密码）；**`422`** 校验失败。

**Bearer（收口）**：配置非空 **`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`**（≥16）时：**`access_token`** 为 **JWT**；调用 **`/api/v1/admin/*`** **须** **`Authorization: Bearer <access_token>`**，否则 **401** **`ADMIN_CONSOLE_AUTH_REQUIRED`**（过期 **`ADMIN_CONSOLE_ACCESS_TOKEN_EXPIRED`**；无效 **`ADMIN_CONSOLE_ACCESS_TOKEN_INVALID`**）。**Secret 留空**：保持 联调——随机 **`access_token`**、Admin 路由不强制 Bearer。**`/api/v1/agent/*`**、Webhook **不在**本条强制范围。

**`CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE`**：`env`（默认，单账号环境变量）或 `database`（表 **`admin_console_user`** + bcrypt；`alembic upgrade head` 后 `chainup-agent-seed-admin`）。产品契约冻结后可能与 SSO 合并 — 以 OpenAPI 为准。

**`CHAINUP_AGENT_TELEGRAM_BOT_TOKEN`**（可选，阶段一）：Telegram **BotFather** Token，仅 **`server/.env`** / 密钥管理；**不写**控制台前端环境变量；Webhook 能力与验签就绪后才会消费。**泄漏须 BotFather 轮换**。

**`CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL`**（可选，阶段一）：用户在 Web / App **完成 Telegram ↔ 账户绑定**的落地页 **`http(s)`** URL（各平台、各交易所自建；运行时注入）；用户对 Bot 发文本时在回复中附带 Telegram **`InlineKeyboard` URL** 按钮。未配置时仅发送运维占位说明。**正式路径以 `design/api` 冻结为准**。

**`CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST`**（可选，仅限联调）：逗号分隔的 Telegram **`chat_id`**，命中则跳过绑定引导；**与 DB 托管绑定并存** — 任一命中即走简化回执（见 `BACKEND_SPEC` §3.1）。

**`CHAINUP_AGENT_LLM_FALLBACK_API_KEY`**（可选）：Telegram **`chat.faq`** 闲聊走 LLM 时，若 Provider **`secretRef`** 为空则用该 Bearer；路由与 **`BACKEND_SPEC` §3.1** 一致（**`volces.com`** → **`/api/v3/responses`**，否则 **`/chat/completions`**）。**`secretRef`** 非空时：匹配 env 变量名规则则读环境变量，否则按 **明文 Key** 使用（见 **`BACKEND_SPEC`**）。

### 4.6a 运营 · Access control（`admin/access-control.yaml` · Phase1）

与 **`product-doc/specs/openapi/admin/access-control.yaml`** 路径前缀 **`/api/v1/admin/access-control`** 对齐；**`alembic upgrade head`** 须含迁移 **`0010_admin_access_control`**。鉴权同 §4.6 **`Bearer`** 规则。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/access-control/whitelist` | Query 可选 **`listId`**、**`q`**；**200** **`items`、`total`**（camelCase） |
| `POST` | `/api/v1/admin/access-control/whitelist` | Body **`listId`、`userUid`**，可选 **`userIdMasked`、`note`**；**201**；重复 **`listId`+`userUid`** **409** **`AGENT_ADMIN_ACCESS_WHITELIST_DUPLICATE`** |
| `DELETE` | `/api/v1/admin/access-control/whitelist/{entryId}` | **204**；**404** **`AGENT_ADMIN_ACCESS_WHITELIST_NOT_FOUND`** |
| `GET` | `/api/v1/admin/access-control/bans` | 可选 **`q`**；**200** **`items`、`total`** |
| `POST` | `/api/v1/admin/access-control/bans` | Body **`userUid`、`reasonCode`**，可选 **`scope`、`expiresAt`、`linkedPause`**；**201** |
| `DELETE` | `/api/v1/admin/access-control/bans/{banId}` | **204**；**404** **`AGENT_ADMIN_ACCESS_BAN_NOT_FOUND`** |
| `GET` \| `PATCH` | `/api/v1/admin/access-control/membership/min-vip-tier` | **`minVipTier`**（**`configKey`** 恒 **`AGENT_MIN_VIP_TIER`**）；PATCH **200** |
| `GET` \| `PATCH` | `/api/v1/admin/access-control/rollout` | **`rolloutWhitelistEnforced`**；PATCH Body 须含该 **bool**（否则 **422**） |
| `GET` | `/api/v1/admin/access-control/users/{userId}/kyc-mirror` | **stub**：**`available=false`** |

### 4.7 运营 · Agent 实例（`admin/` · Phase1）

与 **`product-doc/specs/openapi/admin/agent-management.yaml`** **I01 / I02 / I03 / I04 / I05 / I06** 及 **G01 / R01–R06 / L01–L03（Phase1）** 路径对齐。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/agents/instances` | 列表；Query **`limit`/`offset`**；可选 **`instanceId`**、**`telegramUserId`**；**200** **`items`、`total`**（**`runtimeState`**、**`agentState`** 等，无 Secret） |
| `GET` | `/api/v1/admin/agents/instances/{instanceId}` | 详情；**404** **`AGENT_ADMIN_INSTANCE_NOT_FOUND`** |
| `POST` | `/api/v1/admin/agents/instances` | **I02** 创建；**201** **`instanceId`**；**422** **`AGENT_GLOBAL_OFF`** / **`AGENT_OPS_SUSPENDED`** / **`AGENT_ROLLOUT_BLOCKED`** / 封禁码 / **`AGENT_QUOTA_EXCEEDED`** |
| `PATCH` | `/api/v1/admin/agents/instances/{instanceId}` | **I05** **`instanceOverrides`**（白名单键）· 可选 **`runtimeState`**；**200** **`AdminAgentInstanceItem`** |
| `POST` | `/api/v1/admin/agents/instances/{instanceId}/binding` | **I04** Body **`exchangeSubAccountUserId`** 或 **`subAccountId`**；**200**（不代填 API Secret） |
| `DELETE` | `/api/v1/admin/agents/instances/{instanceId}/binding` | **I04** 解绑托管行；**204**；保留 **`agent_instance`** |
| `DELETE` | `/api/v1/admin/agents/instances/{instanceId}` | **I06** 删除实例并 **解绑** `telegram_agent_trading_binding`（可再走 Deeplink 绑定）；**204**；**404** / **422** 同上 |
| `GET` | `/api/v1/admin/agents/runtime/global-agent-gate` | **G01** 只读：**`globalAgentSwitchOn`**、**`opsSuspended`**、**`bannerMessage`**、**`reasonCodes`** |
| `POST` | `/api/v1/admin/agents/instances/{instanceId}/runtime/{action}` | **R01–R05**：**`action`**=`start`\|`pause`\|`resume`\|`stop`；**200** 更新后实例项；**422** **`AGENT_GLOBAL_OFF`** / **`AGENT_OPS_SUSPENDED`** / **`RUNTIME_COMMAND_REJECTED`** |
| `POST` | `/api/v1/admin/agents/instances/runtime/batch` | **R06**：Body **`instanceIds`**、**`action`**；**200**；部分失败 **`code`**=`AGENT_BATCH_PARTIAL` + **`failures[]`** |
| `GET` | `/api/v1/admin/agents/instances/{instanceId}/logs/conversations` | **L01**：执行行投影 + **`observabilityExecutionPath`**（深链 Observability） |
| `GET` | `/api/v1/admin/agents/instances/{instanceId}/logs/tools` | **L02**：**`trading.exchange_*`** 时间线条目 + **`observabilityTimelinePath`** |
| `GET` | `/api/v1/admin/agents/instances/{instanceId}/logs/errors` | **L03**：失败执行与时间线合并 + **`observabilityTimelinePath`** |

**Base URL**：与同目录 **`admin/`** SPA —— Vite 已将 **`/api`** 代理到本服务（默认 **`127.0.0.1:8080`**），前端可用相对路径如上。

### 4.7a 运营 · Observability · 执行（`admin/observability.yaml` · Phase1）

表 **`agent_execution`**（与 **`§4` `execution/*`**、Telegram **`accept→finalize`** 同源）；执行协查时间线 **`agent_execution_event`**（迁移 **`0007_exec_event`**）。**`GET …/executions/{executionId}/timeline`** 已实现，与 **`ObservabilityTimelineResponse`** 对齐；**工具调用 / LLM 明细**等路径仍以 **`openapi/admin/observability.yaml`** 增量为准。**字段级契约**：**[`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`](./API_ADMIN_OBSERVABILITY_EXECUTIONS.md)**。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/observability/executions` | 列表；Query **`limit`/`offset`**；可选 **`executionId`**、**`userId`**、**`channel`**、**`scenarioId`**、**`state`**（**`ACCEPTED`/`SUCCEEDED`/`FAILED`/`CANCELLED`**）、**`keyword`**、**`createdAfter`**、**`createdBefore`**；**422** 非法 **`state`** |
| `GET` | `/api/v1/admin/observability/executions/{executionId}` | 单行详情；**404** **`AGENT_ADMIN_EXECUTION_NOT_FOUND`** |
| `GET` | `/api/v1/admin/observability/executions/{executionId}/timeline` | 协查时间线；**`items[]`**（**`eventName`**、**`ts`**、**`executionId`**、**`userId`**、**`summary`** **对象**）；**404** 父执行不存在。现货闪兑链见 **`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`** §5 |
| `GET` | `/api/v1/admin/observability/executions/{executionId}/tool-calls` | **FR-MC803** · **`items[]`**（**`toolId`**、**`toolCallSeq`**、**`invocationState`**、**`phase`**、**`summary`**） |
| `GET` | `/api/v1/admin/observability/executions/{executionId}/llm` | **FR-MC804** · **`modelId`**、**`calls[]`**（**`llm.*`** · **`gatewayModelId`**；无 messages 全文） |
| `DELETE` | `/api/v1/admin/observability/executions/{executionId}` | 硬删除 **`agent_execution`**（**级联**时间线行）；**204**；**404** **`AGENT_ADMIN_EXECUTION_NOT_FOUND`** |

### 4.8 运营 · AI Settings（`admin/ai-settings.yaml` · Phase1）

空 **`admin_ai_provider`** 时 **默认不会** 自动插入 **`demo`**（避免删除后刷新「复活」）。仅当 **`CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY=true`**（ORM-only SQLite 便利）时在 **`GET …/admin/ai/*`** 首访注入演示目录；常规环境请依赖 **`alembic upgrade`**（**`0004_aisettings`** + **`0017_admin_ai_model_api_model`**）写入初始数据。

**「厂商 → 模型」**：**`gateway_defaults`** 场景字段（如 **`scenarioChatModel`**）存 **`model_id`（catalog 主键）**；运行时按行解析 **`providerId`**。**不同厂商共用同一上游 `model` 串**（如 **`deepseek-ai/DeepSeek-V4-Flash`**）时：**各厂商一条目录行**，**`modelId`** 须在全局唯一，**可选 **`apiModel`**** 填入对端 **`model`** 字段；不传则 **`apiModel`** 等价于 **`modelId`**。**`PATCH /api/v1/admin/ai/defaults`**：**422 **`AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG`**** 若有策略字段指向不存在的 **`modelId`**。**观测**：**`gatewayModelId`** / **`gatewayUpstreamModel`**。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/ai/providers` | Provider 列表（空库时自动 **`demo`** 种子） |
| `POST` | `/api/v1/admin/ai/providers` | **201** 创建；Body **`displayName`/`baseUrl`/`secretRef`** |
| `GET` | `/api/v1/admin/ai/providers/{providerId}` | 详情 **404** **`AGENT_AI_PROVIDER_NOT_FOUND`** |
| `PATCH` | `/api/v1/admin/ai/providers/{providerId}` | 更新；**409** **`AGENT_AI_SETTINGS_VERSION_CONFLICT`** |
| `DELETE` | `/api/v1/admin/ai/providers/{providerId}` | **204**；下属模型随 DB **CASCADE** 删除；可选 **`If-Match`**；**404** / **409** 同 PATCH |
| `GET` | `/api/v1/admin/ai/models` | Query 可选 **`providerId`**。**或**单列 Query **`modelId`**（`**items.length=1`**，**404** **`AGENT_AI_MODEL_NOT_FOUND`**；**勿与 **`providerId` 同时出现**→ **422**）。**`model_id` 含 `/` 时请用此项**而非 **`/models/{modelId}`**（path `%2F` 易被代理误判）。未及时应用迁移 **`0017`** 时亦可 **503 **`AGENT_DB_SCHEMA_OUT_OF_DATE`****。 |
| `GET` | `/api/v1/admin/ai/models/{modelId}` | **404** **`AGENT_AI_MODEL_NOT_FOUND`**（与 **`?modelId=`** 二选一优先 Query） |
| `POST` | `/api/v1/admin/ai/models` | **201** 注册目录项；Body **`providerId`/`modelId`**；可选 **`apiModel`**；**404** **`AGENT_AI_PROVIDER_NOT_FOUND`**；**409** **`AGENT_AI_MODEL_ID_CONFLICT`** |
| `PATCH` | `/api/v1/admin/ai/models/{modelId}` | 同上 **Body**；或与下行等价 |
| `PATCH` | `/api/v1/admin/ai/models` | Query **必填 **`modelId`**；**Body** 同路径版（**catalog id 含 `/` 首选**） |
| `DELETE` | `/api/v1/admin/ai/models/{modelId}` | **204**；可选 **`If-Match`** |
| `DELETE` | `/api/v1/admin/ai/models` | Query **必填 **`modelId`**（**204**；语义同上） |
| `GET` | `/api/v1/admin/ai/defaults` | 网关默认 + 原型 Runtime 策略字段（camelCase） |
| `PATCH` | `/api/v1/admin/ai/defaults` | 合并 PATCH；预算字段校验 **422**；策略 **`modelId`** 须已在目录 → 否则 **422 **`AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG`** |
| `GET` | `/api/v1/admin/ai/health-policy` | Health 策略 JSON |
| `PATCH` | `/api/v1/admin/ai/health-policy` | 合并 PATCH |
| `POST` | `/api/v1/admin/ai/providers/{providerId}/health` | 连通性探针 **200** |

### 4.8.1 运营 · Trading Agent Config Bundle（`users-global-config.yaml` · MR-MEM）

**`STM_*` / `SESSION_*` / `READ_*`** 键真源 **`trading-agent-config/keys.md` §2.1～§2.3**；PATCH **values** 经 **`memory_runtime_settings`** **热覆盖** Env（**`get_effective_settings()`**），**无需** 重启进程。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/trading-agent-config/bundle` | **`configVersion`** + **`values`**（合并后生效值）+ **`defaults`** |
| `PATCH` | 同上 | Body **`{ values, expectedConfigVersion? }`**；**`If-Match`** 或 body 版本；**409** **`AGENT_AI_SETTINGS_VERSION_CONFLICT`**（与 AI Settings 同窗乐观锁码）；未知键 **422** |

### 4.9 运营 · Prompt Management（`admin/prompt-management.yaml` · 子集）

迁移 **`0006_pm_tg`** 种子 **`pack_system_intent_nlu_v1`**（**`scenarioId`=`agent.runtime.intent_nlu`**）；**`0008_intent_nlu_read_market_expand`** 将已发布种子包系统消息扩展为含 **`read.market.depth`** / **`read.market.trades`**。**`INTENT_NLU_USE_LLM`** 系统提示自 DB 注入（缺省回退代码模板）。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/internal/prompts/effective` | Query **`scenarioId`**（必填）；**200** **`messages`** / **`resolvedPromptBinding`** / 可选 **`variableSchema`**；**304** **`If-None-Match`**；**404** **`AGENT_PROMPT_PACK_NOT_FOUND`** |
| `GET` | `/api/v1/admin/prompt-packs` | 列表；Query 可选 **`promptPackType`、`scenarioId`、`lifecycle`**；每项含只读 **`title`**（场景 **`flow.title`** / 平台 runtime 文案 / 草稿后缀）；**`updatedAt`、`rowVersion`** |
| `POST` | `/api/v1/admin/prompt-packs` | **201** 创建 **`DRAFT`**；Body **`promptPackType`**（必填）、**`scenarioId`**（**TRADING/ANALYSIS 必填**且须在场景寄存器）、可选 **`promptPackId`**、**`sourcePromptPackId`**（从模板复制） |
| `GET` | `/api/v1/admin/prompt-packs/{promptPackId}` | 详情；含 **`bodyMarkdown`**、**`rowVersion`**、**`updatedAt`** |
| `PATCH` | `/api/v1/admin/prompt-packs/{promptPackId}` | Body **`messages`** 与/或 **`variableSchema`**（**至少其一**）；可选 **Header `If-Match`**（**`rowVersion`**）→ **409** **`AGENT_PROMPT_PACK_VERSION_CONFLICT`**；**`LOCKED`/`DEPRECATED`** → **409** |
| `POST` | `/api/v1/admin/prompt-packs/{promptPackId}/fork` | **201** 从已有包快照复制 **新 DRAFT 版本线**（**LOCKED SYSTEM** 编辑路径）；Body 可选 **`promptPackId`** |
| `GET` | `/api/v1/admin/prompt-packs/{promptPackId}/versions` | 版本履历 **`items[]`**（**`PUBLISH`/`ROLLBACK`** 事件） |
| `POST` | `/api/v1/admin/prompt-packs/{promptPackId}/publish` | **仅 `DRAFT`→发布**；**`TRADING`/`ANALYSIS`** 须寄存器内 **`scenarioId`**；**`SYSTEM`→`LOCKED`** |
| `POST` | `/api/v1/admin/prompt-packs/{promptPackId}/rollback` | Body **`promptPackVersion`**；**`PUBLISHED`/`LOCKED`** 指针回滚；**404** **`PROMPT_VERSION_NOT_FOUND`** |

### 4.10 运营 · 人工确认规则（`ai.confirmation-rules`）

迁移 **`0020_admin_confirmation_rules`**；内置 6 条 + 演示自定义 3 条（首次空库 **GET** 自动 seed）。契约详见 **`BACKEND_SPEC`** · Admin · Confirmation rules。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/internal/confirmation-rules/effective` | 运行时读路径；**200** 同 Admin 列表 |
| `GET` | `/api/v1/admin/confirmation-rules` | **200** **`items`/`total`/`enabledCount`** |
| `POST` | `/api/v1/admin/confirmation-rules` | **201** 创建自定义规则 |
| `GET` | `/api/v1/admin/confirmation-rules/{ruleId}` | **404** **`AGENT_ADMIN_CONFIRMATION_RULE_NOT_FOUND`** |
| `PUT` | `/api/v1/admin/confirmation-rules/{ruleId}` | 自定义更新；内置 **409** **`AGENT_ADMIN_CONFIRMATION_RULE_BUILTIN_READONLY`** |
| `DELETE` | `/api/v1/admin/confirmation-rules/{ruleId}` | **204**；内置 **409** |
| `PATCH` | `/api/v1/admin/confirmation-rules/{ruleId}/enabled` | Body **`enabled`** |
| `POST` | `/api/v1/admin/confirmation-rules/reset` | 恢复演示样例 + 默认启用态 |

### 4.11 运营 · 安全防护（`ai.prompt-safety`）

迁移 **`0021_admin_safety_intercept_log`**；**SAFETY 包** 编辑/发布仍用 **`§4.9`** **`/api/v1/admin/prompt-packs`**（**`promptPackType=SAFETY`**）。详见 **`BACKEND_SPEC`** · Admin · Prompt Safety。

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/api/v1/admin/prompt-safety/overview` | 总览（平台 SAFETY 包、规则 revision、确认规则数、G01 闸） |
| `GET` | `/api/v1/admin/prompt-safety/blocklist` | **§7.1.1** 短语表 + **`safetyPhraseScanScopeDefault`** |
| `GET` | `/api/v1/admin/prompt-safety/prompt-packs` | 仅 **SAFETY** 列表 |
| `GET` | `/api/v1/admin/prompt-safety/runtime-governance` | Runtime 治理摘要（链到确认规则/编排） |
| `GET` | `/api/v1/admin/prompt-safety/tool-policies` | 工具调用策略（Phase1） |
| `GET` | `/api/v1/admin/prompt-safety/session-policy` | 会话风控说明 |
| `GET` | `/api/v1/admin/prompt-safety/intercepts` | 拦截流水；Query **`category`**、**`limit`/`offset`** |

**Publish/Patch 增补**：命中越狱/绕过护栏用语 → **422 **`PROMPT_SAFETY_VIOLATION`**（**`matchedRuleId`**）；Publish 阻断写入 **`intercepts`**（**`category=prompt`**）。

---

## 5. 与健康检查

| 方法 | 路径 | 用途 |
|------|------|------|
| `GET` | `/health` | 存活探测 |
| `GET` | `/ready` | 就绪（后续可改为依赖 DB） |

---

## 6. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-05-25 | §**4.3d**：**`POST|GET /api/v1/agent/trading/reconcile`**（§6 504/UNKNOWN 对账；改单 **`reconcileSuggested`**） |
| 2026-05-22 | §**4.3**：**`intent/recognize`** 关键词 MVP 覆盖 **路线图 Phase2 stub**（**合约/永续** vs 现货、**条件单**、**全仓杠杆** 等）；**`STUB_NOT_EXECUTABLE`** Telegram 话术分流 · **`BACKEND_SPEC`** §**11** |
| 2026-05-21 | §**4.2a**：**`read.account.balance` / `wealth.holdings_read`** TRADING Assembly、**`NARRATE_READ_ACCOUNT_BALANCE` / `…WEALTH_HOLDINGS_READ`**、**`0016`**、时间线 **`llm.read.account.balance`** / **`llm.wealth.holdings_read`** · **`BACKEND_SPEC`** |
| 2026-05-18 | §**4.2a**：**`read.market.depth`/`trades`** TRADING Assembly、**`NARRATE_DEPTH`/`TRADES`**、**`0015`**、时间线 **`llm.read.market.depth`** / **`llm.read.market.trades`** · **`BACKEND_SPEC`** |
| 2026-05-18 | §**4.2a**：**`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER`**、**`read.market.ticker`** TRADING Assembly（**`0014`**、**`llm.read.market.ticker`** 事件）· **`BACKEND_SPEC`** §**3.1** / §**11** |
| 2026-05-20 | §4.2：Telegram **默认不**带出「编排预览」行（**`TELEGRAM_INTENT_PREVIEW_IN_REPLY`**）；**`POST …/intent/recognize`** 显式余额/资产用语优先 **`read.account.balance`**（制衡 LLM **`chat.faq`**）· **`BACKEND_SPEC`** §**3.1** env 表 · §**11** |
| 2026-05-14 | §4.7：**G01**、**Runtime**（单实例 + 批量）、**实例日志 Tab**（L01–L03，Observability 深链）；**`BACKEND_SPEC`** Admin · Agent 实例 |
| 2026-05-19 | §**4.2a**：Prompt Assembly（**`chat.faq`** / NLU）、**`0013`**；§**4.4**：**`variableSchema`**（**§8 AC-09f** 部分）；详见 **`BACKEND_SPEC`** §11 |
| 2026-05-15 | §4.7a：现货 **`trade.spot.*`** 时间线 **`summary`** 可含 **`venue`**（**`coobit`**）、**`canonicalOp`**（**`place_order`**）；详见 **`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`** §5.2 |
| 2026-05-14 | §4.7a：**`GET …/executions/{executionId}/timeline`**（**`items[]`** **`agent_execution_event`**）；闪兑链 **quote → confirm（Type-A）→ order** 事件写入（Telegram 与 **`POST …/flash-convert`**） |
| 2026-05-14 | §4.3：**`intent/recognize`**：**DbSession**、**`nlu`/`plan`**、**`INTENT_NLU_USE_LLM`**、**`FEATURE_TRADING`/`FEATURE_AGENT_SPOT`**；**Telegram 已绑定**内联 **`recognize_intent_full`**（**`BACKEND_SPEC`** §3.1） |
| 2026-05-13 | **§4.3a**：路线图 **Phase2.1** 现货闪兑 **`GET …/trade/spot/quote`**、**`POST …/flash-convert`**（Coobit **`POST /sapi/v2/order`** **MARKET**）；§4.3 **`routing/execute`** / **`scenarios`** 与 **`trade.spot.flash_convert`** 同步 |
| 2026-05-11 | 初稿：对齐路线图第一阶段 + 前端联调/OpenAPI 使用说明 |
| 2026-05-23 | §3.6：**`POST /api/auth/register`**、**`CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION`**、§4.6 登记表 |
| 2026-05-11 | §4.6：补充 `database` 模式与迁移 / seed 命令 |
| 2026-05-13 | §4.2：Webhook **`200`** 先于 **`sendMessage`**（后台任务），避免上游慢导致全无回复 |
| 2026-05-13 | §4.2：Webhook 可选 **`CHAINUP_AGENT_TELEGRAM_WEBHOOK_INLINE_PROCESSING`**；构建回复异常仍 **`sendMessage`** 兜底（**`telegram_webhook_build_reply_failed`**） |
| 2026-05-13 | §4.2：**`chat.faq`** LLM：`volces.com` → **`/api/v3/responses`**；否则 **`chat/completions`**；**`secretRef`** / **`CHAINUP_AGENT_LLM_FALLBACK_API_KEY`** 见 **`BACKEND_SPEC`** |
| 2026-05-13 | Telegram Webhook：**门禁 → 意图 → 只读路由**（与 **`telegramChatId`**、放行名单对齐）；§4.3 **`routing/execute`** 行情/余额接线说明 |
| 2026-05-13 | §4：**`execution/*`** 持久化 **`agent_execution`**（**`0005_exec`**）；Telegram bound **`accept→finalize`** |
| 2026-05-12 | §4：**`access` / `intent` / `scenarios` / `routing`**（**`read.market.ticker` · `read.account.balance`** 已接线交易所只读）/ **`execution`（内存）**；Webhook 已绑定：**门禁 + 意图 + 只读路由**；环境变量：**`CH…_RUNTIME_GLOBAL_DISABLED`** / **`…_OPS_SUSPENDED`** |
| 2026-05-12 | Deeplink **`postTradingApiBinding`** 已与 **`openapiBaseUrl`**（同 validate 口径）对齐本服务 **`POST /api/v1/me/agent/bindings/trading-api`** |
| 2026-05-12 | §4.1：PM **不提供**运行时自动开立子账户/代开 API Key；用户在 **Deeplink 前自备**（与 **`BACKEND_SPEC` §3.1** 一致）；**`/subaccount/create`** 占位语义 |
| 2026-05-12 | §4.1：**`api-binding/status`、`subaccount/status`、`onboarding/initiate`、`subaccount/create`（DEFERRED）** 实现落位 |
| 2026-05-13 | §4.1：**`sub_account_id` / `subAccountId`** 必填；校验与账户接口 id 交叉比对；**`confirm`** / **`me` bindings** 写入 **`agent_instance`**（**`instanceId`**）；迁移 **`0003_ai`** |
| 2026-05-13 | §4.8：**空目录默认不自动种子 demo**（**`ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY`**） |
| 2026-05-13 | §4.8：**`DELETE …/providers/{providerId}`**（**204**） |
| 2026-05-13 | §4.8：模型 **`GET`/`DELETE`**；**`PATCH`** 支持 **`providerId`** |
| 2026-05-13 | §4.8：**`POST /api/v1/admin/ai/models`**（扩展）；错误码 **`AGENT_AI_MODEL_ID_CONFLICT`** |
| 2026-05-13 | §4.8：**Admin AI Settings** **`/api/v1/admin/ai/*`**（对齐 **`admin/ai-settings.yaml`**；运行时网关默认值兼容 **`product-doc` `/ai-settings` 原型字段） |
| 2026-05-13 | §4.6：控制台 JWT Secret — **`/api/v1/admin/*`** 强制 Bearer（见 **`BACKEND_SPEC`** §3.1） |
| 2026-05-13 | §4.7a：**`DELETE …/observability/executions/{executionId}`**（执行记录清理） |
| 2026-05-13 | §4.7a：Observability 执行 API **契约专篇** **`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`** |
| 2026-05-13 | §4.7a：**Admin Observability** **`GET …/observability/executions*`**（**`agent_execution`**） |
| 2026-05-13 | §4.7：**Admin Agent 实例** **`GET /api/v1/admin/agents/instances*`**（只读） |
| 2026-05-20 | §4.8：**`GET|PATCH|DELETE …/models?modelId=`**（catalog id 含 **`/`** 时绕过 path **`%2F`** 网关问题）；**`GET /models`** 禁 **`modelId`+`providerId` 同用**（**422**） |
| 2026-05-19 | §4.8：**`apiModel`** · **`gateway_defaults`** 策略字段 **catalog `modelId` 校验**（**422 **`AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG`**）；迁移 **`0017_admin_ai_model_api_model`** |

后续阶段上线时：**在路线图对应章节发布后**，于本文 **§2、§4** 增补表格并链到冻结 OpenAPI PR。
