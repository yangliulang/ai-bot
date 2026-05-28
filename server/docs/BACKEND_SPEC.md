# ChainUp AI Agent — 后端工程规范（SSOT for `server/`）

> **阶段与前端/API 接入**（路线图、Phase 1 清单、Swagger、桩状态）：参见同目录 **[`API_INTEGRATION_GUIDE.md`](API_INTEGRATION_GUIDE.md)**。  
> **产品契约真源**：`../product-doc/specs/design/api.md`、`../product-doc/specs/openapi/`、`../product-doc/product/roadmap.md`（遗留 HTTP 阶段清单见 `../product-doc/development-roadmap.md`）。  
> **收口验收**（本仓可实现 · 可勾选）：[`PHASE1_ACCEPTANCE.md`](PHASE1_ACCEPTANCE.md)。  
> **时间与 UTC**：见 **§2.1**（全文权威）；**Admin 展示接力**见 **`admin/FE_HANDOFF.md`** 顶部最新小节。  
> **优先级**：契约 / 路线图 / 当期 PR 明示范围 **高于** 本文；若有冲突 **先修契约或本条**再改代码。

---

## 1. 技术选型（冻结至书面变更）

| 类别 | 选型 | 备注 |
|------|------|------|
| 语言运行时 | Python **≥ 3.11** | 与 CI/容器镜像对齐后再改条目 |
| Web 框架 | **FastAPI** | 自动生成 OpenAPI；异步优先 |
| ASGI | **uvicorn** | 生产可加 gunicorn+workers 或 k8s 多副本 |
| 校验 / 配置 | **Pydantic v2** + **pydantic-settings** | 环境变量前缀 `CHAINUP_AGENT_` |
| HTTP 客户端 | **httpx** | 调用 Telegram、交易所、账务等出站 |
| 持久化 | **SQLAlchemy 2.0**（async）+ **Alembic** | PG 优先；本地可用 `aiosqlite` |

包管理：**uv**（`pyproject.toml` + 锁文件由团队决定是否提交）。

---

## 2. 逻辑架构（与 `architecture.md` 对齐）

采用 **六角/洋葱浅层**：**依赖方向向内**——`domain` 不导入 FastAPI/SQLAlchemy；适配器在外层。

```
chainup_agent/
├── api/                 # HTTP 适配：Router、DTO（Pydantic）、依赖注入入口
├── application/          # 用例 / 编排服务（transactions、用例脚本）
├── domain/               # 实体、不变式、领域错误语义（无副作用）
├── infrastructure/       # DB、外部系统客户端（Coobit、Telegram、billing）
└── core/                 # 配置、日志、横切异常基类（无业务）
```

**映射产品逻辑容器（概念）**：

| 产品文档术语 | 代码落点（建议） |
|--------------|------------------|
| 渠道接入（Telegram inbound） | `api/routers/webhook*` + `infrastructure/telegram/bot_api` |
| 渠道运维 **Bot / Webhook**（`admin/telegram-channels.yaml`） | `api/routers/admin_telegram` + `application/telegram_bot_admin` + `telegram_webhook_admin` + `telegram_runtime_config`（**`GET|PATCH …/bot`** · **`runtimeParams`** 存 `admin_ai_document` **`telegram_channel_runtime`**；**`POST …/self-test`** · **`GET|POST|DELETE …/webhook`**） |
| **Agent 实例（运营只读 · Phase1）** | `api/routers/admin_agent_instances` + `application/admin_agent_instances` |
| Agent 运行时 / 编排 | `application/orchestration*` + `domain` |
| 交易所适配 | `infrastructure/exchange*` |
| **Canonical 交易语义（ADR-004 · V1 Coobit）** | `domain/canonical_trading`（`InstrumentRef` / `PlaceOrder` → **`coobit_sapi_v2_order_body_from_place_order`**）+ `application/agent_spot_trade` |
| 计费账务 | `infrastructure/billing*` |

### 2.1 时间与时刻（UTC、Telegram）

**目的**：统一 **存库、API、排障日志** 的口径，避免与控制台/本地日志 **相差整时区**（如东八区与 UTC 差 8 小时）却被误认为数据错误。

| 类别 | 约定 |
|------|------|
| **权威时区** | **UTC**。服务内新建记录、事件时间戳使用 **`datetime.now(UTC)`**（见 **`api/schemas/agent_runtime.py`** · **`utc_now()`**）；持久化列优先 **`DateTime(timezone=True)`**（naive 禁止混入新代码）。 |
| **HTTP JSON** | **`datetime`** 字段序列化为 **ISO 8601**，带 **`Z`** 或 **`+00:00`** 偏移；**默认语义均为 UTC**，除非字段文档单独写明（目前 无「本地墙钟」字段）。 |
| **Telegram `message.date`** | Bot API 为 **Unix 时间戳（秒）**，表示该消息的 **UTC 时点**。若产品需要展示「用户发送时间」，可作为 **单独字段**（如 **`sourceEventAt`**）衍生并仍按 UTC 存储/下发；**不可替代** **`created_at`**（行记录创建时刻 = 服务端处理节拍）。 |
| **进程日志** | 控制台 **`asctime`** 常见为 **宿主机本地时区**；与 DB **`08:xx`**（UTC）和本机 **`16:xx`**（CST）对表时 **先确认时区再比对**。生产建议统一 **UTC 日志** 或在运维文档写明。 |
| **Admin / 展示** | **接口不改为「运营本地」**：仍返 UTC；**`admin/`** 将 **`createdAt` / `updatedAt` / `ts`** 等 **格式化为运营时区**（如 **`Asia/Shanghai`）并在表头标注 **「UTC+8」** 或提供 **UTC 切换**（见 **`admin/FE_HANDOFF.md` 最新小节）。 |

---

## 3. HTTP API 约定

### 3.1 版本与前缀

- 对外 REST：**`/api/v1/...`** 与路线图一致。
- **运营控制台登录 / 自助注册**：**`POST /api/auth/login`**、**`POST /api/auth/register`**。\
  - **`POST /api/auth/register`**：仅 **`admin_console_auth_mode=database`**：在表 **`admin_console_user`**（bcrypt）创建一行。**`503`** **`ADMIN_CONSOLE_REGISTRATION_REQUIRES_DATABASE_AUTH`** 若为 **env** 模式。准许条件：**（1）** 表中 **尚无任何控制台用户**（首张管理员，免额外配置）；**（2）** 或 **`CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION=true`**（后续开放注册）；否则 **403** **`ADMIN_CONSOLE_REGISTRATION_DISABLED`**。Body **`username`**、**`password`**（口令 **不少于 8 字符**）；用户名已存在 **409** **`ADMIN_CONSOLE_USERNAME_ALREADY_EXISTS`**。成功体与 **`POST /api/auth/login`** 相同（**`access_token`** / **`token_type`** / **`username`**）。路由使用 **`DbSession`**，须可用的 **`DATABASE_URL`**。\
  - **`POST /api/auth/login`**：\
    - **`admin_console_auth_mode=env`（默认）**：单账号来自 **`CHAINUP_AGENT_ADMIN_PANEL_USERNAME` / `PASSWORD`**；未配置则 **503** `ADMIN_CONSOLE_AUTH_DISABLED`。\
    - **`admin_console_auth_mode=database`**：账号存表 **`admin_console_user`**（bcrypt）；首张账号可通过 **`POST /api/auth/register`**，之后可用 **`CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION`** 或 **`chainup-agent-seed-admin`**；错误口令 / 未知用户 / 禁用均为 **401** `ADMIN_CONSOLE_AUTH_INVALID_CREDENTIALS`（防用户名枚举）。\
  **env 模式登录不打开 DB 会话**；database 模式下 **login** 使用按需打开的登录专用会话。**register** 使用 **`DbSession`**。成功 **`access_token`** + **`token_type`** **`bearer`**。

  **控制台 JWT（收口 `/api/v1/admin/*` Bearer）**：配置非空 **`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`**（≥16 字符）时：（1）登录成功返回 **HS256 JWT**（仍置于 **`access_token`**）；（2）**`/api/v1/admin/*`** **须** **`Authorization: Bearer <access_token>`**，否则 **401** **`ADMIN_CONSOLE_AUTH_REQUIRED`**；过期 **401** **`ADMIN_CONSOLE_ACCESS_TOKEN_EXPIRED`**；无效 **401** **`ADMIN_CONSOLE_ACCESS_TOKEN_INVALID`**。TTL：**`CHAINUP_AGENT_ADMIN_CONSOLE_ACCESS_TOKEN_TTL_SECONDS`**（默认 43200）。**Secret 留空（默认）**：登录仍为 **不可服务端校验** 的随机串，Admin 路由 **不强制 Bearer**（仅本地联调；生产须配 Secret 或网关代校验）。

  **运行时 **`/api/v1/agent/*`**、**`/api/v1/me/*`**、Webhook** 等 **不在**本条强制 Bearer 范围内（渠道/BFF 契约另立）。
- Telegram Webhook：**`POST /webhook/telegram/{bot_token}`**：校验 path token 后 **`200`** **立即**返回（Body 已读入）；出站 **`sendMessage`**（含门禁 / LLM / 只读路由）默认在 **后台任务**执行（**`CHAINUP_AGENT_TELEGRAM_WEBHOOK_INLINE_PROCESSING=false`**），避免 Telegram 等待上游过久断开 HTTP；若运行环境在返回响应后**不再执行后台任务**（部分无服务器冻结），可置 **`…=true`** 改为同请求内处理（ACK 可能变慢）。**构建回复**若发生未捕获异常，仍会 **`sendMessage`** 中文兜底提示（并打 **`telegram_webhook_build_reply_failed`** 日志），避免全无回复；对 **文本** `message` 调 **`sendMessage`**。**未绑定**：简短绑定引导文案 + **InlineKeyboard「前往绑定页面」**（URL 为 **公网 `https://`** 且 **非 localhost/环回**）；**不**回显用户原文、**不**在正文中重复粘贴绑定 URL。**http/localhost** 时无按钮，正文末尾给出可复制链接。**已绑定**（**`telegram_agent_trading_binding`** **与** **`agent_instance`** 同时存在；**`CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST`** **不**单独跳过绑定引导，仅影响 **`access/evaluate`** 联调放行）：串 **`POST /api/v1/agent/access/evaluate`**（同源门禁）、**`recognize_intent_full`**（**`plan.nextStep`**：等价 HTTP **`POST /api/v1/agent/intent/recognize`**；可选 **`INTENT_NLU_USE_LLM`**）、对 **`read.*`** 调 **`routing_execute_exchange_reads`**（只读交易所快照）并在当轮 **`executionId`** 下追加 **`agent_execution_event`**（与 HTTP **`POST /api/v1/agent/routing/execute`** 同款 **`trading.exchange_public` / `trading.exchange_private`** · **`exchange_read`** 或 **`routing.read.failed`**）；**`trade.spot.flash_convert`**（**`FEATURE_AGENT_SPOT`** 开）：槽位齐时 **公开询价**（与 **`GET …/trade/spot/quote`** 同源）并落 **Admin 时间线 `quote`**，再 **`sendMessage`** 附 **InlineKeyboard**（**`callback_data`**：`fcp`/`fcx`+16hex **token**）并在 **`agent_telegram_pending_confirm`** 落库（**`payload_json.executionId`** 绑定当轮 **`agent_execution`**，用户点按确认前 **`state=ACCEPTED`**；15min，重复发起覆盖旧 pending）；**`callback_query`** 确认则 **`answerCallbackQuery`** 并调用 **`spot_flash_convert_for_bound_user`**（与 HTTP **`POST …/trade/spot/flash-convert`** 同源；校 **`from.id`/`chat.id`/token）：若 pending 携带的 **`executionId`** 仍 **`ACCEPTED`** 且用户/场景一致则 **复用该行**（否则 **`execution_accept`**，**`source=telegram_callback`**）；取消仅删 pending。HTTP **`routing/execute`** 对闪兑仍为 orchestration 指引（真实写走 **`…/flash-convert`**）。**`sendMessage` 正文仅含业务结果**（门禁拒绝、LLM 答复、行情/余额摘要、占位/提示等），**不**再附带 抬头、用户原文 echo、**`tg_id`** / 用户名 / 语言调试块（排查依赖服务端日志）；失败则映射 **`AppError`** 话术（如未完成绑定、缺 **`symbol`**、OpenAPI 不可达）。**Webhook** 调用门禁时在 Body 附带 **`telegramChatId`**（信封 **`chat.id`**），以便放行名单既可匹配 **`tg_id`** 又可匹配 **`chat_id`**（与既有 **`PHASE1_BOUND_CHAT_IDS`** 语义对齐）。**未配置绑定页**且会话未绑定时仅运维说明占位。**生产必须把 token 撤出 path** 或改用 **secret path**，见 §8。
  - **闲聊 LLM（`chat.faq`）**：关键词未命中行情/余额/交易等强意图时，默认分支 **`chat.faq`** 会按 Admin **`gateway_defaults`**（**`scenarioChatModel`** → **`defaultModelId`** → **`defaultInferenceModel`**）解析 **`admin_ai_model` / `admin_ai_provider`**：若 Provider **`baseUrl`** 主机名含 **`volces.com`**（火山方舟），则 **`POST {baseUrl}/api/v3/responses`**（非流式 **`stream=false`**，**`input`** 内 **`input_text`** **仅**承载用户修剪后的纯文本）；否则 **`POST {baseUrl}/chat/completions`**（OpenAI 兼容）。**`Authorization: Bearer …`**：`secretRef` 符合 **`^[A-Za-z_][A-Za-z0-9_]*$`** 时读 **`os.environ[secretRef]`**，否则 **`secretRef` 本身即 Bearer**（**明文**写入 **`admin_ai_provider.secret_ref`**，Phase1）；**`secretRef`** 为空则用 **`CHAINUP_AGENT_LLM_FALLBACK_API_KEY`**。
  - **现货 ticker 可选 LLM 叙述（`read.market.ticker`）**：当 **`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER=true`** 且当轮 **`routing_execute_exchange_reads`** 对 **`read.market.ticker`** **成功**返回 **`exchange_read_preview`** 时，再调用 **`invoke_llm_chat_for_telegram`**（**`scenario_id`**=`read.market.ticker`，**`runtime_context`** 含 **`kind`**、**`exchangeReadPreview`**（JSON 安全副本）、**`routingNote`** 截断）；拼装链与 **`chat.faq`** 一致（见 **`agent_prompt_assembly`**）。**LLM 无可用答复**时行为与 **`false`** 相同（确定性 **`_lines_from_ticker_preview`** + 场景 ID）；并写入 **`agent_execution_event`** **`llm.read.market.ticker`**（**成功/失败 `outcome`**，**`promptPackVersion` / `resolvedPromptBinding`** 来自 **`effective_prompt_snapshot_for_scenario`**）。**迁移 `0014`** 提供 **`PUBLISHED` TRADING** 种子包 **`pack_trading_read_market_ticker_v1`**；未跑迁移且无包时 **TRADING** 正文走与 **`chat.faq`** 类似的 **代码回退 system 段**，仍尝试 LLM；若网关或 HTTP 仍失败则回落确定性行情行。
  - **盘口深度 / 近期成交 可选 LLM 叙述**：**`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_DEPTH`**（**`read.market.depth`**）与 **`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TRADES`**（**`read.market.trades`**）— 语义与 ticker 条目对称：**`invoke_llm_chat_for_telegram`** + **`_try_telegram_public_read_llm_narration`**；时间线 **`llm.read.market.depth`**（**`read_market_depth_llm`**）、**`llm.read.market.trades`**（**`read_market_trades_llm`**）。**迁移 `0015`**：**`pack_trading_read_market_depth_v1`** / **`pack_trading_read_market_trades_v1`**。
  - **账户余额 / 理财 OTC 持仓（托管只读）可选 LLM**：**`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_ACCOUNT_BALANCE`**（**`read.account.balance`**）与 **`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_WEALTH_HOLDINGS_READ`**（**`wealth.holdings_read`**）— 同上链（**`exchangeReadPreview`** 入 **`runtime_context`**）；时间线 **`llm.read.account.balance`**（**`read_account_balance_llm`**）、**`llm.wealth.holdings_read`**（**`wealth_holdings_read_llm`**）。**迁移 `0016`**：**`pack_trading_read_account_balance_v1`** / **`pack_trading_wealth_holdings_read_v1`**。

  **入库绑定（`telegram_agent_trading_binding`）**：若以 **`CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY`** 成功执行 **`POST /api/v1/agent/api-binding/confirm`**（或等价 **`POST /api/v1/me/agent/bindings/trading-api`**），则 Webhook 会按 Telegram **会话锚点**（`from.id`，私聊无 `from` 时回退 **`chat.id`（private）**，与 Deeplink **`tg_id`** 预填对齐）查询 DB；命中则跳过「前往绑定」主 CTA，**不写**文末绑定链接。**未执行迁移**以致表缺失时：**仅告警**，走原绑定引导链路（不向用户暴露崩溃）。

#### 绑定页 URL 查询串预填（`tg_*`）

- **拼装**：`application.telegram_inbound.merge_bind_url_with_tg_prefill` 在配置的 **bind base URL** 上 **合并** query（UTF-8 `urlencode`；同名键由预填覆盖）。  
- **来源**：`message` / `edited_message` / `channel_post` 信封中的 `from`；若缺 `from.id` 且 `chat.type == "private"`，则 **`tg_id` 回退为 `chat.id`**（字符串形式）。  
- **键名（供 H5 只读预填；稳定）**：

| Query | 含义 |
|-------|------|
| `tg_id` | Telegram 用户数值 id |
| `tg_username` | 用户名（不含前缀 `@`） |
| `tg_first_name` / `tg_last_name` | `from` 内姓名（长度截断见实现常量） |
| `tg_lang` | `language_code` |

- **安全语义**：**非签名校验**；仅作 **表单预填 / 展示**，**不可替代**服务端身份认定；可被终端用户篡改——正式绑定须走 **ticket / 服务端交换**（见产品 `design` / `risk`）。

#### 子账户与 API Key · 不提供自动开立

- **产品口径**：**不**在本服务为用户 **自动创建** 交易所子账户，**不** **代开** 交易 API Key。用户须在打开 **Deeplink / H5 绑定流程之前**，于 **主站 / 交易所控制台** 自行完成 **Agent 专用子账户**（若产品线要求分立）及 **对应 API Key/Secret** 的创建；进入绑定页仅提交已由用户持有的凭据并接受 **validate 探针**与 **confirm 托管落库**。  
- **服务端职责**：`validate` / `confirm`（及 `POST /api/v1/me/agent/bindings/trading-api`）与 **`GET …/api-binding/status`**、`GET …/subaccount/status`、`POST …/onboarding/initiate` 等为 **就绪与绑定链路**所需；不包含所内开立子账户的编排。  
- **`POST /api/v1/agent/subaccount/create`**：保留 **契约/兼容**占位；正文恒 **`accepted=false`**、**`DEFERRED_EXCHANGE_CONSOLE`** **`AGENT_SUBACCOUNT_CREATE_PHASE1_NOT_AUTOMATED`**，语义为 **本产品不开此能力**，非「延后实现」的承诺。

### 3.2 幂等与追踪

- 入站：读取 **`x-request-id`**；若缺省则由中间件生成并 **回响**。
- **出站**：为 Coobit 写调用生成 **`newClientOrderId` / `clientOrderId`** 等（字段名以所内 OpenAPI 为准）；与 **`executionId`** 分层，语义见 `product-doc/specs/design/api.md`。**Spot 闪兑 / 限价**：透传或生成的 **`newClientOrderId`** **须少于 32 字符**（服务端 OpenAPI **`maxLength=31`**；缺省生成 **`cu_agent_` + 22 hex**，总长 **31**）。

### 3.3 占位路由（现阶段）

路线图 Phase 1 端点已实现 **路由器注册**；**仍为 `501`** 的少数路径返回 **`StubBody`**（见 **`chainup_agent/api/stubs`** 与路线图差分）。以下 **已实现**：\
- **`GET /api/v1/agent/api-binding/status`**：**200**；Query **`userId`**（Telegram **`tg_id`** 非空数值串）；命中 **`telegram_agent_trading_binding`** 则 **`agentTradingApiBindingStatus=BOUND`** 及 **`openapiBaseUrl`** / **`bindingId`** / **`tgUsername`** / **`updatedAt`**；未命中 **`NONE`**；**422** **`VALIDATION_ERROR`**（`userId` 非法）。\
- **`GET /api/v1/agent/subaccount/status`**：**200**；同上 **`userId`**；**`subaccountReady`** 表示是否已有 **托管绑定**（**非**代替所内开立状态）；**`agentSubAccountId`** 恒 **`null`**（尚未与所内子账户主键对签入库）；**`tradingApiBindingStatus`**：**`NONE` \| `BOUND`**。\
- **`POST /api/v1/agent/onboarding/initiate`**：**200**；Body **`telegram`**（至少 **`tg_id`** 数值串）；返回 **`onboardingId`**、**`nextStep`**（**`bind_trading_api`** 无绑定 \| **`complete`** 已绑定）、**`agentTradingApiBindingStatus`**；缺 **`tg_id`** → **400** **`AGENT_TELEGRAM_CONTEXT_REQUIRED`**；格式错 → **`AGENT_TELEGRAM_CONTEXT_INVALID`**。\
- **`POST /api/v1/agent/subaccount/create`**：**200**；**见 §3.1「子账户与 API Key」** — 恒 **`accepted=false`**、**`DEFERRED_EXCHANGE_CONSOLE`**、**`code=AGENT_SUBACCOUNT_CREATE_PHASE1_NOT_AUTOMATED`** + **`message`**（**不**提供自动开立；用户 Deeplink 前自备子账户与 Key）。\
- **`POST /api/v1/agent/api-binding/validate`**：**200**（**不落库**）；Body **`openapi_base_url`** + **`api_key`** + **`secret_key`** + **`sub_account_id`**（必填）；**GET /sapi/v1/account** 探针；若响应含常见账户 id 字段则须与 **`sub_account_id`** 一致；**400** **`AGENT_SUB_ACCOUNT_ID_REQUIRED`** / **`AGENT_SUB_ACCOUNT_ID_MISMATCH`** / **`AGENT_SUB_ACCOUNT_ID_INVALID`**；其余错误码见 §11。\
- **`POST /api/v1/agent/api-binding/confirm`**：**200**：落库 **`telegram_agent_trading_binding`** 并 **upsert** **`agent_instance`**（每 **`telegram_user_id`** 至多一行；公钥 **`instance_id`** 前缀 **`inst_`**）；响应 **`instanceId`**、**`agentSubAccountId`**（回显）；须在 **`validate`** 语义成功后再调（本路由会 **重复探针**）；Body 额外 **`telegram`**（至少 **`tg_id`**）；依赖 **`CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY`**（见 §5）。\
- **`POST /api/v1/me/agent/bindings/trading-api`**：**camelCase** 产品与 Deeplink **等价**绑定入口；须 **`subAccountId`**；成功体含 **`instanceId`** / **`bindingRowCreated`** 等。\
- **`POST /api/v1/agent/access/evaluate`**：Body 须含 **`userId`**（**Telegram `tg_id` 数值串**，**非**交易所子账户号）**或** **`subAccountId`**（**`confirm` 时提交的子账户 ID**，服务经 **`agent_instance.exchange_sub_account_user_id`** 解析为 **`telegram_user_id`**；无对应行 → **422** **`VALIDATION_ERROR`**）；二者同时传时 **`userId`** 须与解析结果一致。**活跃封禁**（若有）→ **`allowed=false`**；校 **DB 绑定** **或** **`TELEGRAM_BOUND_CHAT_ALLOWLIST`**（命中解析后的 **`telegram_user_id`** 或 **`telegramChatId`**）；若配置 **`enforce_rollout_whitelist`**（**`admin_access_membership_policy`**）且无 env 放行，则须命中 **DB 白名单** **`user_uid`**，否则 **`AGENT_ROLLOUT_BLOCKED`**；**200** 返回 **`EligibilityEnvelope`**（camelCase）；开关 **`AGENT_RUNTIME_GLOBAL_DISABLED`** / **`AGENT_RUNTIME_OPS_SUSPENDED`**。响应可选 **`requiresMainSite`**（布尔）：**`true`** 表示 **Deeplink/H5/主站绑定** 链路为推荐下一步（如 **`AGENT_SUBACCOUNT_REQUIRED`**）；**放行名单内已允许**或 **DB 绑定已验证** 等 Telegram 闭环会话为 **`false`**；其它阻断码常为 **`null`/缺省**。\
- **`GET /api/v1/agent/access/reasons`**：**`AGENT_*`** 阻断码与中文摘要。\ 
- **`POST /api/v1/agent/intent/recognize`**：须 **DB 会话**（与其它 `DbSession` 路由一致）。Body **`text`**（**必填**）；可选 **`sessionId`**、**`executionId`**、**`locale`**、**`previousScenarioId`**（**camelCase**）。**响应**：除 **`nlu` / `plan`** 等外含 **`effectiveLocale`**（**`zh-Hans` \| `zh-Hant` \| `en`**）——由请求 **`locale`** BCP-47 提示映射（未知语种回退 **`en`**），**非**自动语种识别。**NLU**：默认 **`keyword_v1`**；**`CHAINUP_AGENT_INTENT_NLU_USE_LLM=true`** 时在同会话内调用 Admin 网关模型输出 **JSON 草案**（**`nlu.source=llm_structured_v1`**），失败则回退关键词；草案经 **规则槽位补缺**后与 **裁决层**合一。**`agent.runtime.intent_nlu`** **PUBLISHED** 的 **system** 正文在出站网关调用前会做 **`{{…}}`** **runtime** 替换（平台内置占位符：**`effective_locale`**、**`scenario_id`**、**`prompt_pack_version`**、**`execution_id`**、**`session_id`** 等）；**variableSchema** 为非空对象时，未获准占位符在进入 LLM 前触发 **`AppError`** **`PROMPT_INJECTION_FORBIDDEN`**——**本条 HTTP 不落 4xx**（意图 LLM 路径 **跳过**，回退 **`keyword_v1`**，并打 **`error`** 级日志 **`intent_nlu_llm_skip`**，**details** 含 **`PROMPT_INJECTION_FORBIDDEN`**）；schema 缺失/空对象时未知占位符 **剔除为空串**并打 **`warning`** **`prompt_runtime_placeholder_stripped`**。**后处理（词法）**：用户文含 **市价 / 闪兑 / 市价单** 且不含 **限价 / 挂单 / 委托** 时，若合并后主场景为 **`trade.spot.limit_order`**，则 **重排候选** 为 **`trade.spot.flash_convert`** 优先（缓解 LLM 将「市价买入」误判为限价、落入 stub）。**裁决**（确定性）：**`scenarioId`** 寄存器、**`FEATURE_TRADING`** / **`FEATURE_AGENT_SPOT`**、**FR-AO02**、只读 / **闪兑与限价**槽位检查。**`orchestrationVersion`**：`intent-router.policy.v2`。**`CHAINUP_AGENT_INTENT_NLU_LLM_TIMEOUT_SEC`** 上限与网关 **`timeoutSec`** 取 min。
- **`GET /api/v1/agent/scenarios`**：场景目录（与 Admin **运行场景** 寄存器 **`2026.05-orc-v1`** 对齐；响应 **`orchestrationRegistryVersion`**）；条目含 **`flowSummary`**（人类可读 **执行流程**）、**`executionSteps[]`**（**`stepKey` / `labelZh` / `order`**，**FR-AO01**）、**`closureStatus`**（**`FROZEN` / `TBD` / `PLACEHOLDER`**），以及 **`title`** / **`category`** / **`riskLevel`**；**`readiness`**：**`ready`** \| **`stub`**。真源 **`application/orchestration_flow_catalog.py`**。\
- **`GET /api/v1/agent/scenarios/{scenarioId}`**：单场景编排详情（**`flowSummary`**、**`executionSteps`**、**`specRefs`**、**`flowAnchor`**、**`promptBindingHint`**）；未知 id → **404** **`AGENT_SCENARIO_NOT_FOUND`**。\
- **`POST /api/v1/agent/routing/execute`**：已对 **`read.market.ticker`**、**`read.market.depth`**、**`read.market.trades`**（均须 **`symbol`**；可选 **`marketDataLimit`** 1～100，默认 **20**：depth 为每侧档位数，trades 为成交条数）、**`read.account.balance`** 与 **`wealth.holdings_read`**（**`POST /sapi/v1/asset/account/by_type`**，**`accountType=4`**，理财/OTC 映射以所内为准）调用交易所 OpenAPI 只读摘要（**公开行情层仍要求**用户已完成托管绑定，与 ticker 一致）；**`trade.spot.open_orders`** 调用 **`GET /sapi/v2/openOrders`** 摘要（**`exchangeReadPreview.kind`**=`spot_open_orders_v1`；可选 **`symbol`** / **`marketDataLimit`**）；**`trade.spot.flash_convert`**、**`trade.spot.limit_order`**、**`trade.spot.cancel_order`** 在 routing 层仍仅 **orchestration 指引**（真实写分别见 **`POST …/flash-convert`**、**`POST …/limit-order`**、**`POST …/trade/spot/cancel`**；Telegram 撤单槽位齐全时 **`plan.nextStep`**=`**EXECUTE_SPOT_CANCEL**` 直调 cancel）。其余 **`scenarioId`** 返回占位 **`note`**。**HTTP 路由内** **`execution_accept`（`source=http_api`）→ 只读 / orchestration → `agent_execution_event`（`trading.exchange_public` / `trading.exchange_private` · `exchange_read` 或占位 `routing_note` / `orchestration`）→ 编排步骤事件 **`agent.orchestration.step`**（读路径：**`access.evaluate` / `read.*` / `summarize.return`**）→ `execution_finalize`（成功/失败后均 `commit`）**；**200** 响应带 **`executionId`** 以便 Admin 协查；**业务拒绝**（如 **403** **`AGENT_SUBACCOUNT_REQUIRED`**）在 **`finalize FAILED`** 后仍 **`commit`** 并 **回抛** **`AppError`**，时间线含 **`routing.read.failed`** 摘要。**`intent/recognize`** 在带 **`executionId`** 且裁决出主 **`scenarioId`** 时追加 **`agent.orchestration.step`**（**`intent.route`**）。**FR-AO06**：**`append_execution_timeline_event`** 写入前校验 Admin **`orchestrationExecutionBudget`**，超限 **422** **`ORCHESTRATION_BUDGET_EXCEEDED`**。\
- **Phase2.1 · 现货闪兑（路线图 §2.1）**（须托管绑定，签名为 GitBook **`X-CH-*`** / **`POST /sapi/v2/order`**，见 **`server/coobit_openapi.md`** 外链）：\
  - **`GET /api/v1/agent/trade/spot/quote`**：Query **`userId`**（**`tg_id`**）、**`symbol`**；**200** **`symbol`**（如 **BTC-USDT**）、**`symbolOrder`**（紧凑 id **BTCUSDT**，用于展示/兼容）、**`quotePreview`**（公开 **`GET /sapi/v2/ticker`** 摘要）；**403** **`AGENT_SUBACCOUNT_REQUIRED`**。**`POST /sapi/v2/order`** 请求体 **`symbol`** 为 **GitBook v2** 之 **BASE/QUOTE**（如 **BTC/USDT**），见实现 **`normalize_coobit_spot_order_body_symbol`**。\
  - **`POST /api/v1/agent/trade/spot/flash-convert`**：Body **`userId`**、**`symbol`**、**`side`**（**`BUY` \| `SELL`**）、**`volume`**（十进制字符串：**标的资产 base 数量**，如 BTC-USDT 下的 BTC；**`BUY`** 时服务会先 **`GET /sapi/v2/ticker`** 取 **`lastPrice`** 换算为 GitBook 要求的 **计价 amount** 再签名下单；**`SELL`** 时 **`volume`** 直传为 base）、可选 **`newClientOrderId`**（**长度须 \<32**，缺省 **`cu_agent_<22hex>`** 总长 **31**）；**200** **`orderId`** / **`orderIdString`** / **`clientOrderId`** / **`type`**=**`MARKET`** / **`exchangeOrderPreview`**；未绑 **403**；交易所拒绝 **400** **`AGENT_SPOT_ORDER_REJECTED`**（**`message`** 尽量附带 **`msg`** 摘要；若识别为 **API / 子账户无交易权限** 类文案，**`details.reject_reason`** 为 **`API_PERMISSION_OR_SUBACCOUNT`** 并附 **中文处理建议**）；其他 **502** **`AGENT_SPOT_ORDER_FAILED`** / **`AGENT_OPENAPI_PROBE_FAILED`**。**协查**：路由内 **`execution_accept`（`channel=http`）→ 下单 → `execution_finalize`**，时间线见 Admin **`…/timeline`**（**quote / submit_order / `trading.exchange_private`**）。\
  - **Phase2.2 · 现货限价（§2.2）· `POST /api/v1/agent/trade/spot/limit-order`**：Body **`userId`**、**`symbol`**、**`side`**、**`volume`**（**base** 数量字符串）、**`price`**、可选 **`timeInForce`**（**`GTC`/`IOC`/`FOK`**）、可选 **`newClientOrderId`**（**长度须 \<32**，规则同闪兑）；**200** **`type`**=**`LIMIT`** 等；**422** **`PRICE_REJECTED_AGENT_BAND`**（见配置 **`CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_*`**）；余同闪兑。**Telegram Type-A**：**`lcp`/`lcx`** 与闪兑 **callback_data** 前缀分流。\
  - **`GET /api/v1/agent/trade/spot/open-orders`**：Query **`userId`**、可选 **`symbol`**、可选 **`limit`**（**1～1000**，缺省时由交易所默认，文档默认 **100**）；**200** **`scenarioId`**=`trade.spot.open_orders`、**`orders`**（字段裁剪）、**`symbol`**/**`symbolOrder`**（仅筛选时有值）；交易所 **`GET /sapi/v2/openOrders`**（签名 **`timestamp + GET + requestPath + ''`**，`requestPath` **含**排序后的 **`?symbol&limit`**）；未绑 **403** **`AGENT_SUBACCOUNT_REQUIRED`**；交易所业务 **`msg`** → **400** **`AGENT_SPOT_ORDER_REJECTED`**；响应形状异常 → **502** **`AGENT_SPOT_OPEN_ORDERS_FAILED`**；超时等 → **`AGENT_OPENAPI_PROBE_FAILED`**（家族与§11一致）。不传 **`symbol`** 时查询全交易对（GitBook **权重较高**）。\
  - **`POST /api/v1/agent/trade/spot/cancel`**：Body **`userId`**、**`symbol`**、**`orderId`** **或** **`newClientOrderId`**（至少其一；**`newClientOrderId`** 长度 **\<32**）；**200** **`scenarioId`**=`trade.spot.cancel_order`；交易所 **`POST /sapi/v2/cancel`**（JSON body **key 排序** compact）；**422** 参数缺失 **`VALIDATION_ERROR`**；其余错误码与 **`POST …/flash-convert`** 同族（**`AGENT_SPOT_ORDER_REJECTED`** / **`AGENT_SPOT_ORDER_FAILED`** / **`AGENT_OPENAPI_PROBE_FAILED`**）。**协查**：**`execution_accept` → `cancel_order` 步 → `trading.exchange_private`**（**`cancelRequest`** / **`exchangeResponsePreview`**）。\
  - **Phase2.x · 现货逻辑改单（CC-P0-02）· `POST /api/v1/agent/trade/spot/amend-limit-order`**：Body **`userId`**、**`symbol`**、**`orderId`**、**`price`** 和/或 **`volume`**（新 base 数量，至少改一项）；可选 **`timeInForce`**、**`newClientOrderId`**；**200** **`scenarioId`**=`trade.spot.amend_limit_order`、**`amendCorrelationId`**、**`priorOrderPreview`** / **`cancelledOrderPreview`** / 新单 **`exchangeOrderPreview`**；单次授权顺序 **`POST /sapi/v2/cancel` → `POST /sapi/v2/order`**；撤成单败 **502** **`AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED`**；原单非 LIMIT **422** **`AGENT_SPOT_AMEND_NOT_LIMIT`**；未找到在途单 **404** **`AGENT_SPOT_AMEND_ORDER_NOT_FOUND`**。**Telegram Type-A**：**`smp`/`smx`** · 「确认修改」+ 新旧对比 + 先撤后挂披露；**`0026`** TRADING 包。**`trade.spot.oco` / `trade.spot.bracket`**：寄存器 **`stub`** · 意图 **`STUB_NOT_EXECUTABLE`**（CC-P1-01）。\
  - **Phase2.3 · 合约市价/限价（§2.3）· `POST /api/v1/agent/trade/futures/order`**：Body **`userId`**、**`symbol`**、**`side`**、**`orderType`**（**`MARKET` \| `LIMIT`**）、**`volume`**、限价时 **`price`**、可选 **`openClose`**（**`OPEN`/`CLOSE`**）、可选 **`reduceOnly`**、可选 **`newClientOrderId`**；**200** **`scenarioId`**=`trade.futures.market_order` / **`trade.futures.limit_order`**、**`exchangeOrderPreview`**；交易所 **`POST /fapi/v1/order`**；**403** **`FEATURE_AGENT_FUTURES_OFF`**（**`CHAINUP_AGENT_FEATURE_AGENT_FUTURES=false`**）；拒单 **400** **`AGENT_FUTURES_ORDER_REJECTED`**。**Telegram Type-A**：槽位齐全 → inline **`ump`/`umx`**（市价）或 **`ulp`/`ulx`**（限价）确认；callback 复用 **`agent_telegram_pending_confirm`**；可选 LLM preamble（**`0023`** TRADING 包）。详见 **`server/docs/TRADING_PHASE2_REMAINING.md`**。\
  - **Phase2.4 · 全仓杠杆（§2.4）· `POST /api/v1/agent/trade/margin/order`**：Body **`userId`**、**`symbol`**、**`side`**、**`orderType`**（**`MARKET` \| `LIMIT`**）、**`volume`**、限价时 **`price`**、可选 **`newClientOrderId`**；**200** **`scenarioId`**=`margin.cross.market_order` / **`margin.cross.limit_order`**、**`exchangeOrderPreview`**；交易所 **`POST /sapi/v2/margin/order`**（symbol **`BTC/USDT`**）；**403** **`FEATURE_AGENT_MARGIN_OFF`**；拒单 **400** **`AGENT_MARGIN_ORDER_REJECTED`**。**Telegram 双确认**：首张 **`xm1/xl1`** → 第二张 **`xm2/xl2`** 后提交；**`0024`** TRADING 包。划转 **`margin.cross.transfer_in`** **未**在本步交付。\
  - **Phase2.5 · 条件单（§2.5）· `POST /api/v1/agent/trade/futures/condition-order`**：Body **`userId`**、**`symbol`**、**`side`**、**`orderType`**（触发后 **`MARKET` \| `LIMIT`**）、**`volume`**、**`triggerPrice`**、**`triggerType`**（**`3UP` \| `4DOWN`**）、触发后限价时 **`price`**、可选 **`openClose`**、可选 **`positionType`**（默认 **1**）、可选 **`orderUnit`**（默认 **2**）；**200** **`scenarioId`**=`automation.condition_order`、**`contractName`**（**`E-BTC-USDT`**）、**`exchangeOrderPreview`**；交易所 **`POST /fapi/v1/conditionOrder`**；**403** **`FEATURE_AGENT_FUTURES_OFF`**；拒单 **400** **`AGENT_FUTURES_CONDITION_ORDER_REJECTED`**。**Telegram Type-A**：触发条件区块置顶 · inline **`cop`/`cox`**；**`0025`** TRADING 包 **`pack_trading_automation_condition_order_v1`**。\
  - **Phase2.5 · 条件单查/撤 + 合约撤单（P0）**：**`GET …/trade/futures/condition-orders`**（Query **`userId`**、可选 **`symbol`**）→ **`GET /fapi/v1/openOrders`**，响应 **`scenarioId`**=`automation.condition_orders_read`、**`orders`**（含 **`triggerPrice`/`triggerType`** 等裁剪字段）、**`totalOpenOrders`**；**`POST …/trade/futures/cancel-condition`**（Body **`userId`**、**`symbol`**、**`orderId`**）→ **`POST /fapi/v1/cancel`**（**`contractName`+`orderId`**），**`scenarioId`**=`automation.condition_order_cancel`；**`POST …/trade/futures/cancel`** → **`trade.futures.cancel_order`**（同交易所撤单 PATH）。拒单 **400** **`AGENT_FUTURES_CANCEL_REJECTED`**；列表异常 **502** **`AGENT_FUTURES_OPEN_ORDERS_FAILED`**。**意图**：合约撤单槽位齐全 → **`EXECUTE_FUTURES_CANCEL`**；条件单列表 → **`ROUTE_READ_SKILL`**；条件单撤销 → **`CONFIRM_TYPE_A`** + Telegram **`ccp`/`ccx`**。\
  - **§6 P0 · 504/UNKNOWN 写路径对账（路线图 6.2）**：**`POST /api/v1/agent/trading/reconcile`**、**`GET /api/v1/agent/trading/reconcile/status`**。Body/Query **`userId`**（**`tg_id`**）；推荐 **`executionId`** — 从 **`agent_execution_event`** 推断 **`caseKind`** 与查单目标（**`trading.exchange_private`** 之 **`exchangeOutcome=unknown`**、改单 **`AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED`** / cancel 成功 + submit 失败步）。可选显式 **`venue`**（**`spot`/`futures`**）、**`symbol`**、**`orderId`** / **`clientOrderId`**、**`caseKind`** 覆盖。**查单 PATH**：现货 **`GET /sapi/v2/order`**；合约 **`GET /fapi/v1/order`**（复用 futures 封装）。**200** **`reconcileId`**、**`caseKind`**、**`resolutionStatus`**（**`OPEN`/`FILLED`/`CANCELLED`/`PARTIAL_FAILURE`/`INCONCLUSIVE`/`UNKNOWN`**）、**`stillUnknown`**、**`userMessage`**（中性话术）、**`orderLookups[]`**；改单 **`CANCEL_SUCCEEDED_REPLACE_FAILED`** 优先核对原单已撤 + 新单是否存在。**时间线**：**`trading.reconcile`**（**`stepKind`**=`reconcile`）。**Status**：有 reconcile 事件则回显最近一次；否则若时间线仍有 unknown 写则 **`resolutionStatus=UNKNOWN`**。**改单 502** **`details`** 增 **`reconcileSuggested`**、**`reconcileCaseKind`**、**`reconcilePath`**=`/api/v1/agent/trading/reconcile`。**504/超时**：**`exchange_http_status_indicates_unknown`** / **`AGENT_EXCHANGE_WRITE_UNKNOWN`**（查单与 **`app_error_indicates_exchange_unknown`**）；全量 **`post_signed_*` 写** 统一抛 unknown **未**在本步穷尽，依赖时间线 **`exchangeOutcome`** + 对账闭合。**验收**：**`pytest tests/test_trading_reconcile.py`**。\
  - **`trade.spot.oco` / `trade.spot.bracket`**：寄存器 **`stub`** · **`STUB_NOT_EXECUTABLE`**（**CC-P1-01** 矩阵 PATH 未冻结；禁止假 OCO 成交）。
- **`POST /api/v1/agent/execution/accept`**、**`GET .../execution/{id}`**、**`POST .../execution/finalize`**：表 **`agent_execution`**（**`execution_id`**、`user_id`、`scenario_id`、`channel`、`state`、`source`、`note`、**`prompt_pack_version`**、**`resolved_prompt_binding`**（JSON，与 **`GET …/internal/prompts/effective`** 同源 **`resolvedPromptBinding`** 形状；无已发布场景包时为 **`null`**）、时间戳）；**`accept`** 在 Body **未**显式提供 **`promptPackVersion`/`resolvedPromptBinding`** 时，若带 **`scenarioId`**，服务自动按 **`GET …/internal/prompts/effective?scenarioId=`** 快照写入（产品 observability **AC-09j/k**）。Telegram 已绑定/放行会话每轮业务答复前 **`accept`→…→`finalize`**（**`source=telegram_webhook`**）；HTTP 直连 **`source=http_api`**。**迁移**：**`0005_exec`**；列 **0011**：**`0011_exec_prompt_meta`**。

#### Admin · Agent 实例（`agent-management` I01 / I03 + G01 / R01–R06 / L01–L03 · Phase1）

- **迁移 `0009_agent_instance_runtime`**：表 **`agent_instance.runtime_state`**（**`RUNNING` \| `PAUSED` \| `STOPPED` \| `ERROR`**，默认 **`RUNNING`**）。  
- **`GET /api/v1/admin/agents/instances`**：**200** **`items[]`、`total`**（camelCase）；Query **`limit`**（1～200，默认 50）、**`offset`**（默认 0）；可选 **`instanceId`**、**`telegramUserId`**（数值串；非法 → **422** **`VALIDATION_ERROR`**）；**LEFT JOIN** **`telegram_agent_trading_binding`**；**不含 Secret**。响应 **`runtimeState`** 来自 DB；**`agentState`** 为 **`GLOBAL_OFF` \| `OPS_SUSPENDED` \| `NORMAL` \| `AGENT_SUBACCOUNT_BLOCKED`**（全局/运维闸优先于未绑定：**`lastProductBlockReason`** 为简要中文说明）。  
- **`GET /api/v1/admin/agents/instances/{instanceId}`**：**200** 单体；**404** **`AGENT_ADMIN_INSTANCE_NOT_FOUND`**。  
- **`DELETE /api/v1/admin/agents/instances/{instanceId}`**（**I06**）：**204** 硬删 **`agent_instance`**，并 **删除** 同 **`telegram_user_id`** 的 **`telegram_agent_trading_binding`**（Agent 侧解绑；**不**动交易所子账户本身，符合 rules §2.3）。删除后 **`POST …/onboarding/initiate`** → **`nextStep=bind_trading_api`**，用户可 **重新走 Deeplink 绑定** 并 **upsert 新 `instanceId`**。**404** **`AGENT_ADMIN_INSTANCE_NOT_FOUND`**。**422** **`AGENT_ADMIN_INSTANCE_DELETE_BLOCKED`**：存在 **未终局** **`agent_execution`** 或 **`agent_telegram_pending_confirm`**；**`details`** 含 **`openExecutions`**、**`pendingConfirmations`**。  
- **G01 只读横幅**：**`GET /api/v1/admin/agents/runtime/global-agent-gate`**：**200** **`globalAgentSwitchOn`**（**`!CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED`**）、**`opsSuspended`**（**`CHAINUP_AGENT_AGENT_RUNTIME_OPS_SUSPENDED`**）、**`bannerMessage`**、**`reasonCodes`**（如 **`AGENT_GLOBAL_OFF`** / **`AGENT_OPS_SUSPENDED`**）。  
- **Runtime 写（R01–R05）**：**`POST /api/v1/admin/agents/instances/{instanceId}/runtime/{action}`**，**`action`**=`start` \| `pause` \| `resume` \| `stop`；成功 **200** 体为更新后的 **`AdminAgentInstanceItem`**；路由内 **`commit`**。**`start`/`resume`** 在全局关闸或运维暂停时 **422** **`AGENT_GLOBAL_OFF`** / **`AGENT_OPS_SUSPENDED`**；非法状态机转移 **422** **`RUNTIME_COMMAND_REJECTED`**。**`pause`/`stop`** 不因 G01 拦截。  
- **Runtime 批量（R06）**：**`POST /api/v1/admin/agents/instances/runtime/batch`**，Body **`instanceIds[]`**、**`action`**；若该批 **`start`/`resume`** 在 G01 整批关闸，**422**（与单实例语义一致）。逐实例执行；**HTTP 200**；部分/全部失败时 **`code`**=**`AGENT_BATCH_PARTIAL`**，**`failures[]`**（**`instanceId`/`code`/`message`**），**`succeeded[]`**。  
- **实例日志 Tab（L01–L03 · Phase1）**：基于 **`agent_execution` / `agent_execution_event`**，按实例 **`telegram_user_id`** 过滤；与 PRD 完全对齐需 Observability 扩展，当前提供执行与时间线深链字段。  
  - **`GET …/instances/{instanceId}/logs/conversations`**：**`items[]`** 含 **`observabilityExecutionPath`**（**`/api/v1/admin/observability/executions/{executionId}`**）、**`total`**、**`observabilityBasePath`**。  
  - **`GET …/instances/{instanceId}/logs/tools`**：**`trading.exchange_public` \| `trading.exchange_private`** 时间线条目；**`observabilityTimelinePath`**（**`…/executions/{executionId}/timeline`**）。  
  - **`GET …/instances/{instanceId}/logs/errors`**：**FAILED** 执行与失败 outcome 时间线合并；**`observabilityTimelinePath`** 同上。  
- **I02 / I04 / I05（P1）**：**`POST /api/v1/admin/agents/instances`**（创建；门禁 **G01** / 封禁 / 灰度；**`AGENT_QUOTA_EXCEEDED`** 重复 **tg**）；**`PATCH …/instances/{instanceId}`**（**`instanceOverrides`** 白名单键 · 可选 **`runtimeState`**）；**`POST|DELETE …/instances/{instanceId}/binding`**（登记/解绑 **`exchangeSubAccountUserId`** · 删除 **`telegram_agent_trading_binding`** 保留实例；**API 密钥**仍走 Deeplink）。迁移 **`0027_agent_instance_overrides`**。

#### Admin · Access control — 准入 / 白名单 / 封禁（FR-MC601–607）

与 **`product-doc/specs/openapi/admin/access-control.yaml`** 路径前缀 **`/api/v1/admin/access-control`** 对齐；迁移 **`0010_admin_access_control`**（**`admin_access_whitelist_entry`**、**`admin_access_user_ban`**、**`admin_access_membership_policy`** 单例行）。

- **`GET|POST /api/v1/admin/access-control/whitelist`**、**`DELETE …/whitelist/{entryId}`**：白名单 CRUD；**`POST`** **201**；同一 **`listId` + `userUid`** 重复 → **409** **`AGENT_ADMIN_ACCESS_WHITELIST_DUPLICATE`**；删除未知条目 → **404** **`AGENT_ADMIN_ACCESS_WHITELIST_NOT_FOUND`**。  
- **`GET|POST /api/v1/admin/access-control/bans`**、**`DELETE …/bans/{banId}`**：封禁列表与创建/删除；**`linkedPause=true`** 且 **`userUid`** 为数值时，**`UPDATE agent_instance`** 将对应 **`telegram_user_id`** 的 **`runtime_state`** 置 **`PAUSED`**。  
- **`GET|PATCH /api/v1/admin/access-control/membership/min-vip-tier`**：最低 VIP 档位（**`minVipTier`**）持久化；运行时与交易所 **`vipTier`** 比对为 **I02 · TBD**（当前仅控制台配置）。  
- **`GET|PATCH /api/v1/admin/access-control/rollout`**：**`rolloutWhitelistEnforced`** 开关；**`PATCH`** Body 须含 **`rolloutWhitelistEnforced`**（**bool**），否则 **422**。  
- **`GET …/users/{userId}/kyc-mirror`**：**stub**（**`available=false`**），待上游 KYC 接线。  
- **`POST /api/v1/agent/access/evaluate`**（增补）：在 **env 放行名单之前** 校验 **活跃封禁**（**`reasonCode=COMPLIANCE_ABUSE`** → 信封 **`AGENT_COMPLIANCE_RESTRICTED`**，其余 → **`AGENT_USER_BLOCKED`**）；在 **env 放行之后、绑定校验之前**，若 **`enforce_rollout_whitelist=true`** 且解析得到的 **`telegram_user_id`** 不在 DB 白名单任一 **`user_uid`**，则 **`AGENT_ROLLOUT_BLOCKED`**。DB 异常时该两步与绑定探针类似 **降级跳过**（不阻断原 行为）。

#### Admin · Confirmation rules — 人工确认规则（`ai.confirmation-rules`）

与产品原型 **`/ai/confirmation-rules`** 对齐；迁移 **`0020_admin_confirmation_rules`**（**`admin_confirmation_rule_custom`**、**`admin_confirmation_rule_enabled`**）。**内置规则**（6 条）在代码目录 **`domain/confirmation_rules_catalog.py`**，**不可编辑/删除**，仅可切换 **`enabled`**；**自定义规则** **`rule_id`** 前缀 **`custom-`**，可 CRUD。首次 **`GET`** 若自定义表为空，自动 **seed** 三条演示样例（与原型 **`DEMO_CUSTOM_CONFIRMATION_RULES`** 一致）。

- **`GET /api/v1/admin/confirmation-rules`**：**200** **`items[]`、`total`、`enabledCount`**（camelCase）；条目含 **`isBuiltin`、`enabled`、`defaultEnabled`**、**`triggerConditions[]`**（**`fieldKey`/`operator`/`value`**）、**`scenarios[]`**、**`action`**（**`force_confirm`/`second_confirm`/`otp_confirm`/`block_auto_execute`**）、**`riskLevel`**。  
- **`POST /api/v1/admin/confirmation-rules`**：**201** 创建自定义规则；Body 同条目字段（无 **`id`**）；**422** 校验失败。  
- **`GET /api/v1/admin/confirmation-rules/{ruleId}`**：**200**；**404** **`AGENT_ADMIN_CONFIRMATION_RULE_NOT_FOUND`**。  
- **`PUT /api/v1/admin/confirmation-rules/{ruleId}`**：更新 **自定义** 规则；内置 → **409** **`AGENT_ADMIN_CONFIRMATION_RULE_BUILTIN_READONLY`**。  
- **`DELETE /api/v1/admin/confirmation-rules/{ruleId}`**：**204** 删除自定义；内置 → **409** 同上。  
- **`PATCH /api/v1/admin/confirmation-rules/{ruleId}/enabled`**：Body **`enabled`**（bool）；内置/自定义均可。  
- **`POST /api/v1/admin/confirmation-rules/reset`**：**200** 清空自定义与启用覆盖，恢复演示样例 + 内置默认启用态。  
- **`GET /api/v1/internal/confirmation-rules/effective`**：运行时读路径，形状同 Admin 列表（**无 Bearer 强制**，与 **`internal/prompts`** 同窗）。

**Runtime 消费（Telegram Type-A · Phase1 子集）**：现货 **闪兑/限价** 在 **Type-A 确认卡** 提供前调用 **`confirmation_rules_evaluate`**：  
- 命中已启用 **`block_auto_execute`** → **拒答**，不写 pending；时间线 **`agent.execution.step`** · **`stepKind`**=`confirm_gate` · **`transitionTrigger`**=`confirmation.rules_evaluated`。  
- 命中 **`second_confirm`** → 确认文案前追加 **二次确认** 前缀（如大额 **`nominal_usdt`** 阈值）。  
- 命中 **`otp_confirm`** → 追加 **OTP 提示**（Phase1 **不阻断**，完整 OTP 待后续）。  
- **`force_confirm`** 关闭 **不** 跳过 ADR-001 Type-A（代码层仍强制），但 **`forceConfirmDisabledForWrite`** 写入观测摘要。  
**`scenarioId`→场景键**：如 **`trade.spot.flash_convert`→`convert`**、**`trade.spot.limit_order`→`spot`**（见 **`SCENARIO_ID_TO_KEY`**）。

#### Admin · Orchestration — 运行场景 · 执行策略（Phase 2）

与 Admin **`/ai/runtime-orchestration`** 对齐；场景 **执行流程** 登记真源 **`application/orchestration_flow_catalog.py`**（经 **`GET /api/v1/agent/scenarios`** 暴露）。

- **`GET /api/v1/admin/orchestration/policy`**：**200** 编排 **执行策略** 读模型（camelCase）：运营字段（自动执行/确认/风险限制/稳定性）+ 工程镜像 **`maxToolCalls` / `maxOrchestrationSteps` / `maxModelRounds`**（自 **`GET …/admin/ai/defaults`** 之 **`orchestrationExecutionBudget`** 与 **`timeoutSec`** 合并）；**`budgetExceededStableCode`**=`ORCHESTRATION_BUDGET_EXCEEDED`；**`engineeringSpecRefs[]`** 只读引用。**PATCH** 暂未实现（预算仍经 **`PATCH …/admin/ai/defaults`**）。


与 **`product-doc/specs/openapi/admin/observability.yaml`** 路径前缀 **`/api/v1/admin/observability`** 对齐；实现 **`agent_execution`** **列表 / 单行** 与 **`…/executions/{executionId}/timeline`**（**FR-MC801** 下限）：时间线项 **`eventName`** 与产品 **`observability/overview.md`** §2 / §2.1 建议名一致（如 **`agent.execution.step`**、**`trading.exchange_private`**），**`summary`** 为脱敏摘要对象。**P1**：**`GET …/executions/{executionId}/tool-calls`**（**FR-MC803** · **`trading.exchange_*`** / **`agent.tool.call`** → **`invocationState`**）；**`GET …/llm`**（**FR-MC804** · **`llm.*`** 事件 · **`gatewayModelId`** · **`calls[]`** 无 messages 全文）。联合检索 / 审计导出仍以 OpenAPI **后续迭代**为准。**协查流程**同窗 **`product-doc/specs/requirements/domains/admin/observability-management/flow.md`**（输入 **`executionId`** → 时间线）。**字段级契约** 见 **`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`**。**迁移**：**`0007_exec_event`** → **`agent_execution_event`**（**`ON DELETE CASCADE`** 随 **`agent_execution`** 清理；Admin **硬删**执行会先删子表事件行）。

- **`GET /api/v1/admin/observability/executions/{executionId}/timeline`**：**200** **`items[]`**（**`eventName`**、**`ts`**、**`executionId`**、**`userId`**、**`summary`** **对象**）；按 **`seq` / `ts` 升序**；父执行不存在 → **404** **`AGENT_ADMIN_EXECUTION_NOT_FOUND`**。写入源：**Telegram Type-A 闪兑** 同一 **`executionId`** 串起 **询价 → 确认提示 →（callback）用户确认 → 下单**；**`POST …/flash-convert`** 在 accept 后写入 **quote（公开 ticker / 或 SELL base）→ submit_order → `trading.exchange_private`**。**`POST /api/v1/agent/routing/execute`**（HTTP）：每请求独立 **`executionId`**；成功时典型 **`trading.exchange_public`**（**`read.market.*`**）或 **`trading.exchange_private`**（**`read.account.balance`**）· **`stepKind`**=`exchange_read`，**`summary`** 含 **`exchangeReadPreviewSummary`** 与 **`transitionTrigger`**（**`routing.read.public_*`**）；失败 **`agent.execution.step`** · **`routing.read.failed`**。**Telegram **`read.*`**：与当轮 **`run_telegram_turn_execution`** 共用 **`executionId`**，事件形状与 HTTP 一致（轮次仍可 **`finalize SUCCESS`**）。**`summary`** 可含产品 §2.4 对齐之 **`transitionTrigger`**（如 **`flash.quote.public_ticker`**、**`flash.confirm.type_a_offered`**、**`confirmation.type_a_callback`**）；**`trading.exchange_private`** 含脱敏 **`orderRequest`**；**`orderRequest.flashMarketMeta`** 解读 **GitBook** **MARKET BUY** **`volume`**=**计价 amount** vs **用户 base 数量**。**`exchangeResponsePreview`** 在**下单成功**时为订单 ACK 白名单字段，在**交易所返回可解析 JSON 的拒单/错误**（如 **`AGENT_SPOT_ORDER_REJECTED`**、部分 **`AGENT_SPOT_ORDER_FAILED`**）时为对端 **`code`/`msg`** 等同源摘要；**超时、非 JSON** 等路径通常仅有 **`httpStatus`/`appErrorCode`**。payload 受 **`agent_execution_events`** JSON 上限约束，**不含 Secret**。**现货闪兑 / 限价** 链路（**`agent_spot_trade`**）之 **`quote`/`submit_order`/`trading.exchange_private`**（及 Telegram callback 下单异常占位）在 **`summary`** 中另含 **`venue`**（V1 固定 **`coobit`**）与 **`canonicalOp`**（**`place_order`**），与 **ADR-004** 观测建议一致。  
- **`GET /api/v1/admin/observability/executions`**：**200** **`items[]`、`total`**（camelCase）；Query **`limit`**（1～200，默认 50）、**`offset`**（默认 0）；可选 **`executionId`**（精确）、**`userId`**、**`channel`**、**`scenarioId`**、**`state`**（**`ACCEPTED` \| `SUCCEEDED` \| `FAILED` \| `CANCELLED`**；非法 → **422** **`VALIDATION_ERROR`**）、**`keyword`**（子串匹配 **`execution_id` / `user_id` / `scenario_id`**）、**`createdAfter`** / **`createdBefore`**（**`date-time`**）；按 **`created_at`** **降序**。  
- **`GET /api/v1/admin/observability/executions/{executionId}`**：**200**；**404** **`AGENT_ADMIN_EXECUTION_NOT_FOUND`**。  
- **`DELETE /api/v1/admin/observability/executions/{executionId}`**：**204** 硬删除 **`agent_execution`** 及其 **`agent_execution_event`**；**404** **`AGENT_ADMIN_EXECUTION_NOT_FOUND`**（联调清理 / 运维；详见 **`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`**）。
- **`GET …/executions/{executionId}/queue`**、**`…/events`**、**`…/retries`**、**`…/recovery`**：执行详情内嵌 Tab（**`runtime.execution-detail`**）；队列来自 **`orchestration_flow_catalog`** + 未完成 **`agent.orchestration.step` / `agent.execution.step`**；运行事件为时间线摘录（**排除** **`agent.orchestration.step`**）；重试来自 **`retry.*` / `trading.reconcile` / exchange `unknown`**；恢复复用对账推断 + **`observabilitySearchPath`**。详见 **`API_ADMIN_OBSERVABILITY_EXECUTIONS.md` §6**。

#### Admin · Prompt Management（子集）

与 **`product-doc/specs/openapi/admin/prompt-management.yaml`** **子集**对齐：**`GET /api/v1/internal/prompts/effective?scenarioId=`**（**200** / **304** **`If-None-Match`** / **404** **`AGENT_PROMPT_PACK_NOT_FOUND`**；仅 **`lifecycle=PUBLISHED`** 命中；同 **`scenarioId`** 下多包时 **以发布流水线顶替**：旧 **`PUBLISHED`**（**`TRADING`/`ANALYSIS`**）在新发发布时标记 **`DEPRECATED`**）。**`GET /api/v1/admin/prompt-packs`**（Query 可选 **`promptPackType`、`scenarioId`、`lifecycle`**；响应含 **`updatedAt`、`rowVersion`**）、**`POST …`**（**201** 创建 **`DRAFT`**，Body **`promptPackType`** 必填，**`scenarioId`** 可选，**`promptPackId`** 可选；冲突 **409** **`AGENT_PROMPT_PACK_ID_CONFLICT`**）、**`GET …/{promptPackId}`**（含 **`bodyMarkdown`** 便利字段）、**`PATCH …/{promptPackId}`**（Body **`messages[]`/`variableSchema`** 至少其一；可选 **Header `If-Match`** 对 **`row_version`** → **409** **`AGENT_PROMPT_PACK_VERSION_CONFLICT`**；**`LOCKED`/`DEPRECATED`/`DISABLED`** → **409** **`PROMPT_PACK_LOCKED`** / **`PROMPT_PACK_DEPRECATED`**；正文超 **256KiB** → **400** **`PROMPT_BODY_TOO_LARGE`**；占位符 / §7.1 用语闸 → **422** **`PROMPT_VALIDATION_FAILED`** / **`PROMPT_SAFETY_VIOLATION`**）、**`POST …/{promptPackId}/fork`**（**201** 从 **LOCKED/PUBLISHED/DRAFT** 快照复制 **新 DRAFT 版本线**；Body 可选 **`promptPackId`**）、**`GET …/{promptPackId}/versions`**（**`items[]`**：`promptPackVersion`、`publishedAt`、`lifecycle`、`event` **`PUBLISH`/`ROLLBACK`**）、**`POST …/{promptPackId}/publish`**（**仅 `DRAFT`**；**`TRADING`/`ANALYSIS`** 须寄存器内 **`scenarioId`**；**`SYSTEM`** → **`LOCKED`** 并 **deprecate** 同 **`scenarioId`** 旧 **SYSTEM**；**`SAFETY`** → **`PUBLISHED`** 并顶替同场景旧版；写入 **`admin_prompt_pack_version_event`**）、**`POST …/{promptPackId}/rollback`**（Body **`promptPackVersion`**；**`PUBLISHED`/`LOCKED`** 可回滚；**404** **`PROMPT_VERSION_NOT_FOUND`**）。Runtime **SYSTEM** 生效读 **含 `lifecycle=LOCKED`**（**`get_published_pack_for_scenario_and_type`**）。**未实现**：**Few-shot 子资源**、**沙箱 runs**。

#### Admin · Prompt Safety — 安全防护（`ai.prompt-safety`）

与原型 **`/prompts/safety`** 对齐；迁移 **`0021_admin_safety_intercept_log`**。**SAFETY Prompt 包** CRUD/发布仍走 **`/api/v1/admin/prompt-packs`**（**`promptPackType=SAFETY`**）；本模块提供 **聚合读** 与 **拦截流水**。

- **`GET /api/v1/admin/prompt-safety/overview`**：**200** **`safetyPhraseBlocklistRevision`**、**`platformSafetyPack`**、**`safetyPromptPackCount`**、**`enabledConfirmationRulesCount`**、**`globalAgentSwitchOn`**、**`opsSuspended`** 等。  
- **`GET /api/v1/admin/prompt-safety/blocklist`**：**200** 当前 **§7.1.1** 短语表 + **`safetyPhraseScanScopeDefault`**（**`FULL_PACK`**）。  
- **`GET /api/v1/admin/prompt-safety/prompt-packs`**：**200** 仅 **SAFETY** 类型列表（等价 **`GET …/prompt-packs?promptPackType=SAFETY`**）。  
- **`GET /api/v1/admin/prompt-safety/runtime-governance`**：**200** Runtime 治理摘要行（动态嵌入 **人工确认规则** 启用数、**G01** 闸状态）。  
- **`GET /api/v1/admin/prompt-safety/tool-policies`**：**200** Phase1 工具策略（**`exchange_tool_schema_registry`** 只读白名单语义）。  
- **`GET /api/v1/admin/prompt-safety/session-policy`**：**200** 会话风控说明（Phase1 部分为 **info/warning** 占位）。  
- **`GET /api/v1/admin/prompt-safety/intercepts`**：Query **`category`**（**`runtime|prompt|tool|session`**）、**`limit`/`offset`**；**200** 合并 **`admin_safety_intercept_log`**（如 **Publish 阻断**）与 **`agent_execution_event`**（**`confirm_gate` 失败**、**`band_check` 失败** 等）。

**Runtime 拼装**：平台 **SAFETY** 包（**`agent.runtime.platform_safety`** · 治理 **`pp-safety-global`**，回落 **`pack_platform_safety_v1`**）经 **`agent_prompt_assembly`** 在 **SYSTEM 之后、TRADING 之前** 注入；**不可被后续块撤销**（**`runtime-injection` §7**）。

**治理 16 包入库（2026-05-27）**：迁移 **`0030_governance_prompt_pack_seed`** 将产品 **`pp-*`** 清单（[`governance-map`](../../product-doc/specs/requirements/prompts/governance-map.md)）以 **PUBLISHED v1** 写入 **`admin_prompt_pack`**；正文与 Demo **`promptBodyTemplates.ts`** 同窗（六段 Markdown）。**`get_published_pack_for_scenario`** 优先 **`governance_pack_id_for_scenario`** → **`pp-*`** 行；读侧 **`read.market.*`** 等统一 **`pp-analysis-core`**。 Superseded **`pack_*_v1`** 标 **DEPRECATED**。**`chat.faq`** 仍用 legacy **`pack_trading_chat_faq_v1`**（不在 16 包内）。

#### Admin · AI Settings（模块四 · Phase1）

与 **`product-doc/specs/openapi/admin/ai-settings.yaml`** 对齐（对外字段仍为 **`secretRef`**）。**服务端 语义**：**`secretRef`** 若匹配 **`^[A-Za-z_][A-Za-z0-9_]*$`** 则视为 **环境变量名**（进程读取）；**否则**视为 **Bearer/API Key 明文**，持久化在 **`admin_ai_provider.secret_ref`**（与部分 OpenAPI「不落明文」表述若有冲突，以本节与 **`agent_llm_chat`** 实现为准，或由 **`/pm`** 修订条文）。**`POST|GET|DELETE …/models`**、**`DELETE …/providers`**、**`PATCH`** 含 **`providerId`** 等为 运行时扩展（OpenAPI 原为列表 + PATCH 部分字段）。**空 Provider 目录默认不会再运行时写入 `demo`**：仅 **`CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY=true`**（默认 **false**）时，若干 **`GET …/admin/ai/*`** 才对空库执行 **`seed_demo_ai_catalog`**；否则删除后刷新不会因种子逻辑再次插入 **`demo`**。持久化表：**`admin_ai_provider`**、**`admin_ai_model`**、**`admin_ai_document`**（**`gateway_defaults`** / **`health_policy`** JSON）；迁移 **`0004_aisettings`** 含 **`demo`** Provider、模型目录与网关默认（与产品原型 **`/ai-settings`** 字段兼容：`defaultInferenceModel`、`scenarioChatModel`、`scenarioTradingModel`、`scenarioRiskModel`、`maxContextTokens`、`timeoutSec`、降级与成本限流等）。

**模型目录与「厂商 → 模型」**：表 **`admin_ai_model`** 以 **`model_id`**（**64～128 字节内**）为 **全局唯一主键**：**`gateway_defaults`** 中 **`scenarioChatModel` / `scenarioTradingModel` / `scenarioRiskModel` / `defaultModelId` / …** 存的是 **catalog `model_id`**，再由 **`provider_id` FK** 解析 **Base URL / 鉴权**。因此 **不同厂商若上游 `model` 字符串相同**（如均为 **`deepseek-ai/DeepSeek-V4-Flash`**），**不能只靠策略里的「模型名」区分**——须为各厂商登记 **不同的 **`model_id`****（例：`volc/deepseek-v4-flash`、`silicon/deepseek-v4-flash`），并在可选列 **`api_model`** 中填入 **实际传给对端 JSON 的 **`model`****；**`api_model` 留空**则运行时 **`model` 字段等于 **`model_id`**。**`PATCH …/ai/defaults`** 在保存前校验上述策略字段引用的 **`model_id`** 均已在目录中存在，否则 **422 **`AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG`**。LLM 出站观测含 **`gatewayModelId`**（catalog）与 **`gatewayUpstreamModel`**（线 id）。

- **`GET|POST /api/v1/admin/ai/providers`** / **`GET|PATCH|DELETE …/providers/{providerId}`**：Provider CRUD 摘要；**`POST`** **201**；**`DELETE`** **204**（**`admin_ai_model`** 随 FK **`ON DELETE CASCADE`** 一并删除）；**404** **`AGENT_AI_PROVIDER_NOT_FOUND`**；**409** **`AGENT_AI_SETTINGS_VERSION_CONFLICT`**（**`If-Match`** 与 **`row_version`** 不一致）。  
- **`GET /api/v1/admin/ai/models`**（Query 可选 **`providerId`**）。若提供 Query **`modelId`**（单列），响应 **`items` 长度为 1**（**404** **`AGENT_AI_MODEL_NOT_FOUND`**）；**`modelId` 与 `providerId` 禁止同用** → **422** **`VALIDATION_ERROR`**。**catalog `model_id` 允许含 `/`**（常与上游 **`model`** 一致）；此类 ID 若以路径段传递需 **`/` → `%2F`**，部分 **反向代理会破坏** 致路由 **404**，故 **单行读改删推荐**：**`GET` / `PATCH` / `DELETE`** 均可用 **`…/models?modelId=`**（与路径形参版语义相同）。  
- **`GET …/models/{modelId}`**（**404** **`AGENT_AI_MODEL_NOT_FOUND`**）、**`POST /api/v1/admin/ai/models`**（Body **`providerId`/`modelId`** 必填；可选 **`apiModel`**、**`status`**、**`contextWindowTokens`**；**201**；**404** **`AGENT_AI_PROVIDER_NOT_FOUND`**；**409** **`AGENT_AI_MODEL_ID_CONFLICT`**）、**`PATCH …/models/{modelId}`** 或 **`PATCH …/models?modelId=`**（Body 可选 **`providerId`**、**`apiModel`**、**`status`**、**`contextWindowTokens`**；**404** **`AGENT_AI_MODEL_NOT_FOUND`** / **`AGENT_AI_PROVIDER_NOT_FOUND`**）、**`DELETE …/models/{modelId}`** 或 **`DELETE …/models?modelId=`**（**204**；可选 **`If-Match`** / **409** 版本冲突）。  
- **`GET|PATCH /api/v1/admin/ai/defaults`**：网关默认与 **`orchestrationExecutionBudget`**（**`FR-AO06`** 下限）；GET 返回 **内置默认值与 DB 合并视图**；PATCH 支持浅合并 **`orchestrationExecutionBudget`** 与 **策略模型字段**；PATCH 后 **422 **`AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG`** 见上。  
- **`GET|PATCH /api/v1/admin/ai/health-policy`**：Health 策略 JSON（自由结构）。  
- **`POST /api/v1/admin/ai/providers/{providerId}/health`**：同步探测 **`baseUrl`**（HEAD/GET），**200** **`ok`/`latencyMs`/`checkedAt`**。

仍为 **`501`** 或未列路径替换为真实实现时：

1. 在 **`../product-doc/specs/openapi/`** 找到对应 YAML 与 **`$ref`**。  
2. 将 Handler 的请求/响应模型改为 **对齐 OpenAPI** 的 Pydantic 模型（可_codegen 或由人工维护）。  
3. 移除 `501`，按契约返回 **精确状态码 / 错误 `code`**（与 observability、`agent-management` I02 **`enum`** 等同窗）。

---

## 4. 错误体（与用户可见话术分离）

结构化错误载体：**`ErrorBody`**（见 `chainup_agent/api/schemas/common.py`）。

- **`code`**：稳定机器码；业务拒绝须与 **`agent-management` / `access-control`** 等 OpenAPI `enum` 对齐 incremental。  
- **`message`**：给人读；**不向用户泄漏内部栈**。  
- **`request_id`**：与日志、观测链路关联。  
- **`details`**：可选；放校验明细、网关原始码等 **非密钥**信息。

校验失败：**`422`** + `code=VALIDATION_ERROR`。  
自定义领域错误：抛 **`AppError`**。

**`AGENT_DB_SCHEMA_OUT_OF_DATE`**（**503**）：服务端 ORM 期望 **`admin_ai_model.api_model`**（迁移 **`0017_admin_ai_model_api_model`**）但当前库未升级时，典型命中 **`GET /api/v1/admin/ai/models`**（此前多表现为隐式 **500 «no such column … api_model»**）。**`details`** 含 **`migrationHint`** 与建议命令 **`cd server && uv run alembic upgrade head`**。**根治**：对运行中的 DB 执行 **完整迁移链至 head**。

**`ADMIN_TELEGRAM_TRANSPORT_ERROR`**（**`POST …/admin/channels/telegram/webhook`** 等出站调用 Telegram）：表示 **未能与** **`api.telegram.org`** **完成 HTTP 往返**（连接/DNS/TLS/代理/超时等），**不是** Bot API 返回的 **`ok:false`**。**客户端**对 **`httpx.RequestError`** 默认 **额外重试 2 次**（指数退避，**`CHAINUP_AGENT_TELEGRAM_BOT_API_TRANSPORT_RETRIES`**，`0` 关闭）；成功前可在日志中看到 **`telegram_bot_api_transport_retry`**。排查：**运行服务的机器**能否访问公网 **`https://api.telegram.org`**（防火墙、出口策略、公司代理需配置 **`HTTPS_PROXY`**、部分地区网络）；仍失败时查看 **`details.transport_error_type`** / **`transport_error_message`** / **`transport_attempts`** 与 **`telegram_bot_api_transport`**。若已收到 Telegram JSON 但业务失败，错误码一般为 **`ADMIN_TELEGRAM_BOT_API_REJECTED`** / **`ADMIN_TELEGRAM_BOT_API_UNAVAILABLE`**，且含 **`description`** 语义。

---

## 5. 配置

- **`Settings`**：`chainup_agent/core/config.py`，环境变量前缀 **`CHAINUP_AGENT_`**。  
- `.env.example` 列出占位；**秘钥只允许 secretRef / 外部环境注入**，不写进仓库。

关键项：

| 变量 | 说明 |
|------|------|
| `CHAINUP_AGENT_DATABASE_URL` | 异步 SQLAlchemy URL；开发默认 **`sqlite+aiosqlite:///./db/chainup_agent.sqlite3`**（工作目录 **`server/`**；库文件 **`db/chainup_agent.sqlite3`**，宜对 **`db/`** 挂卷）；生产常用 **`postgresql+asyncpg://…`**。线上变量清单见 **`server/.env.online.example`**（合并进 **`.env`** 或注入编排环境） |
| `CHAINUP_AGENT_PUBLIC_BASE_URL` | Webhook、`setWebhook` 辅助 |
| `CHAINUP_AGENT_DEBUG` | 开发者详细日志 |
| `CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE` | `env`（默认）或 `database`（表 `admin_console_user`） |
| `CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION` | **默认 `false`**；**`database`** 模式下，**首张**控制台用户仍可无配置 **`POST /api/auth/register`**；置 **`true`** 允许在已有账号后再注册 |
| `CHAINUP_AGENT_ADMIN_PANEL_USERNAME` / `PASSWORD` | 仅 **env** 模式控制台单账号；**database** 模式可留空 |
| `CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET` | **非空（≥16）**：登录 **`access_token`** 为 **HS256 JWT**，且 **`/api/v1/admin/*`** **强制** **`Authorization: Bearer`**；**空**：随机串、Admin 路由不校验（仅联调） |
| `CHAINUP_AGENT_ADMIN_CONSOLE_ACCESS_TOKEN_TTL_SECONDS` | JWT **`exp`** TTL（秒）；默认 **43200** |
| `CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL` | Deeplink / H5 **绑定落地页**（与各交易所/BFF 或本地 Vite Dev，如 `http://localhost:5174/`）；**非空时**正文附带明文链接并发 `InlineKeyboard` URL；空则不落按钮与明文链接 |
| `CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST` | 联调：逗号分隔 `chat_id`/`tg_id`，仅 **`access/evaluate`** 放行；**Webhook 绑定引导**须 **托管绑定 + 实例** 同时存在 |
| `CHAINUP_AGENT_TELEGRAM_BOT_API_TRANSPORT_RETRIES` | **默认 `2`**（**0～8**）：出站 **`api.telegram.org`** 遇 **`ConnectError`** / 超时 / 代理等 **`RequestError`** 时，在首次之外再试的次数（指数退避）；**`0`** 仅单次；**不能**替代出口封禁（需 **`HTTPS_PROXY`** / 放行目标机） |
| `CHAINUP_AGENT_TELEGRAM_ERROR_LLM_REWRITE` | **默认 `true`**：对 **`AGENT_SPOT_ORDER_REJECTED`** / **`AGENT_SPOT_ORDER_FAILED`** / **`PRICE_REJECTED_AGENT_BAND`**，Telegram 回复经 Admin AI **LLM 改写**为友好中文（网关不可用或超时时 **回退** 原文案） |
| `CHAINUP_AGENT_TELEGRAM_ERROR_LLM_TIMEOUT_SEC` | **默认 `15`**（**3～60**）；改写调用 HTTP 超时，与网关 **`timeoutSec`** 取 **较小者** |
| `CHAINUP_AGENT_TELEGRAM_INTENT_PREVIEW_IN_REPLY` | **默认 `false`**；**`true`** 时在 Telegram 兜底话术末尾附带「（编排预览）粗略意图…」调试行（**`_format_faq_hint`**）；生产建议 **false** |
| `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER` | **默认 `false`**；**`true`** 时 Telegram **已成功** **`read.market.ticker`** 只读后 **额外调用一次 LLM**（Prompt Assembly：**`scenario_id`**=`read.market.ticker`，**`runtime_context`** 含 **`exchangeReadPreview`**）；网关/拼装失败则 **回落**为原有 **确定性** ticker 摘要行；观测事件 **`llm.read.market.ticker`**（**`stepKind`**=`read_market_ticker_llm`）。须迁移 **`0014`** **`PUBLISHED` TRADING** 包 **`pack_trading_read_market_ticker_v1`** |
| `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_DEPTH` | **默认 `false`**；**`true`** 时 Telegram **`read.market.depth`** **成功后**再走 **一轮** LLM 叙述（**`llm.read.market.depth`** / **`read_market_depth_llm`**）；须 **`0015`** **`pack_trading_read_market_depth_v1`** |
| `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TRADES` | **默认 `false`**；**`true`** 时 Telegram **`read.market.trades`** **成功后**再走 **一轮** LLM（**`llm.read.market.trades`** / **`read_market_trades_llm`**）；须 **`0015`** **`pack_trading_read_market_trades_v1`** |
| `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_ACCOUNT_BALANCE` | **默认 `false`**；**`true`** 时 Telegram **`read.account.balance`** **成功后**再走 **一轮** LLM（**`llm.read.account.balance`** / **`read_account_balance_llm`**）；须 **`0016`** **`pack_trading_read_account_balance_v1`** |
| `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_WEALTH_HOLDINGS_READ` | **默认 `false`**；**`true`** 时 Telegram **`wealth.holdings_read`** **成功后**再走 **一轮** LLM（**`llm.wealth.holdings_read`** / **`wealth_holdings_read_llm`**）；须 **`0016`** **`pack_trading_wealth_holdings_read_v1`** |
| `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_SPOT_FLASH_CONFIRM` | **默认 `false`**；**`true`** 时在闪兑 **Type-A** 确定性确认文案 **之前**可选 LLM 风险提示（**`llm.trade.spot.flash_convert`** / **`type_a_preamble`**）；须 **`0018`** TRADING 包 |
| `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_SPOT_LIMIT_CONFIRM` | **默认 `false`**；**`true`** 时在限价 **Type-A** 前可选 LLM preamble（**`llm.trade.spot.limit_order`**）；须 **`0018`** |
| `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_FUTURES_MARKET_CONFIRM` | **默认 `false`**；**`true`** 时在合约市价 **Type-A** 前可选 LLM preamble（**`llm.trade.futures.market_order`**）；须 **`0023`** |
| `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_FUTURES_LIMIT_CONFIRM` | **默认 `false`**；**`true`** 时在合约限价 **Type-A** 前可选 LLM preamble（**`llm.trade.futures.limit_order`**）；须 **`0023`** |
| `CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY` | **Fernet** 密钥（`Fernet.generate_key().decode()`）— 密封 **confirm** 写入的 **`api_key` / `secret_key`**（表 **`trading_credentials_sealed`**）；**空**则禁止落库（503） |
| `CHAINUP_AGENT_DEFAULT_AGENT_TEMPLATE_ID` | **Phase1**：绑定确认时写入 **`agent_instance.template_id`**（默认 **`tmpl_agent_default`**） |
| `CHAINUP_AGENT_DEFAULT_AGENT_TEMPLATE_VERSION` | 同上 **`template_version`**（默认 **`1`**） |
| `CHAINUP_AGENT_FEATURE_TRADING` | **`true`**（默认） **`false`** 时 **`trade.*`** 意图在 **`POST …/intent/recognize`** 裁决为 **`BLOCKED_FEATURE`** |
| `CHAINUP_AGENT_FEATURE_AGENT_FUTURES` | **默认 `true`**；**`false`** 时 **`trade.futures.*`** HTTP 写与意图策略 **`FEATURE_AGENT_FUTURES_OFF`** 阻断 |
| `CHAINUP_AGENT_FEATURE_AGENT_MARGIN` | **默认 `true`**；**`false`** 时 **`margin.cross.*`** HTTP 写与意图策略 **`FEATURE_AGENT_MARGIN_OFF`** 阻断 |
| `CHAINUP_AGENT_INTENT_NLU_USE_LLM` | **默认 `false`**；**`true`** 时 **`POST …/intent/recognize`** 与 **Telegram 已绑定**会话优先尝试 **LLM JSON 意图草案**（失败回退 **`keyword_v1`**） |
| `CHAINUP_AGENT_INTENT_NLU_LLM_TIMEOUT_SEC` | **默认 `25`**（**5～120**）；与 Admin 网关 **`timeoutSec`** 取较小者作为意图 LLM HTTP 超时 |
| `CHAINUP_AGENT_AGENT_RUNTIME_OPS_SUSPENDED` | **`true`** 时同上接口 **`AGENT_OPS_SUSPENDED`** |
| `CHAINUP_AGENT_LLM_FALLBACK_API_KEY` | Admin LLM Provider 的 **`secretRef`** 为空时的 Bearer；上游路由见 §3.1 **`chat.faq`**（**`volces.com`** → **`/api/v3/responses`**，否则 **`/chat/completions`**）；生产推荐 **`secretRef`**→环境变量名或 Vault 注入进程 env，**避免** DB 明文 Key |

---

## 6. 数据库与迁移

- **Session**：`get_db_session` 依赖：**一请求一会话**（`infrastructure/persistence/base.py`）。\
  控制台登录在 **`admin_console_auth_mode=env`** 时使用 **`get_admin_login_db_session`**，**不**创建会话（避免无效 `DATABASE_URL` 阻断 env 登录）。
- **运营控制台账号（可选）**：表 **`admin_console_user`**（见 `infrastructure/persistence/models/admin_console_user.py`）— 字段 `id`、`username`（唯一）、`password_hash`（bcrypt）、`is_active`、`created_at`。仅 **`admin_console_auth_mode=database`** 时参与 **`POST /api/auth/login`**。
- **迁移**：根目录 **`alembic.ini`** + **`alembic/versions/`**；应用前 **`uv run alembic upgrade head`**（异步 env 读 **`CHAINUP_AGENT_DATABASE_URL`**）。**禁止**在生产用手写 DDL 绕过版本表。\
  **增量**：**`0002_tatb`** → **`telegram_agent_trading_binding`**（Telegram 用户锚点与子账户密钥密封列；详见模型文件）。**`0003_ai`** → **`agent_instance`**（**`instance_id`**、**`telegram_user_id`**（唯一）、**`exchange_sub_account_user_id`**、模板钉扎字段）。**`0006_pm_tg`** → **`admin_prompt_pack`**（Prompt Management 持久化）+ **`agent_telegram_pending_confirm`**（Telegram 闪兑二次确认令牌）。
- **模型**：`infrastructure/persistence/models/`（增量表在同目录登记并_revision）。

### 6.1 Bootstrap 控制台账号（database 模式）

首张账号任选其一：**`POST /api/auth/register`**（空库、`AUTH_MODE=database`、口令 ≥8）；或 CLI：

```bash
cd server
uv run alembic upgrade head
uv run chainup-agent-seed-admin --username admin --password '<一次性强口令>'
```

本地可临时加 **`--ensure-schema`** 等同 `create_all`（**生产禁用**，仅以迁移为准）。

后续账号： **`CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION=true`** 后再调 **`POST /api/auth/register`**，或继续使用 **`chainup-agent-seed-admin`**。

---

## 7. 测试

- **`pytest`** + **`pytest-asyncio`**，`httpx.ASGITransport` 打 **内存 ASGI**。  
- 覆盖率底线由 CI 约束；核心业务与 **网关适配**优先单测 / 契约测。  
- **禁止**在未 mock 情况下对 production 交易所做集成测试默认。

命令：`uv run pytest`、`uv run ruff check chainup_agent tests`。

---

## 8. 安全（最低线）

1. **Bot Token**：禁止入日志、禁止进运营台；URL path 中的 token **仅开发可用**，生产须改为 **固定 secret 路径** 或 **header 验签** 方案并对照 `telegram-channels` OpenAPI。  
2. **Telegram Webhook**：校验 **`X-Telegram-Bot-Api-Secret-Token`**（若配置）与 payload 来源。  
3. **子账户 API Key**：仅存密钥服务；运行时注入；**默认禁止主账户 Key**（FR-T01）。  
4. **Rate limit / IP 允许列表**：与运维、渠道配置对签后实现。

---

## 9. 观测与审计（增量）

- 结构化日志：默认文本；`CHAINUP_AGENT_LOG_JSON=true` 切 JSON。  
- 事件名、**`executionId` / `billingTraceId`** 等须与 `product-doc/specs/requirements/observability/overview.md` **同窗增量适配**（非本文件一次写死）。

---

## 10. 迭代纪律（给 Agent / 审阅者）

1. **改行为先对 OpenAPI / ADR**：无登记能力不「假开」。  
2. **改本文当「架构决策」**：在 PR 说明中链接理由；重大变更升 ADR。  
3. **Router 薄、用例厚**：复杂分支进 `application/`，`api` 只做参数解析与 HTTP 映射。  
4. **保持 Phase 1 路由表**与 `product/roadmap.md` / specs 及遗留 `development-roadmap.md` §1 一致；新增路径先改路线图或契约再写代码。

---

## 11. 版本记录

| 日期 | 变更摘要 |
|------|-----------|
| 2026-05-20 | **Phase2 · 运行场景编排（FR-AO01/05/06 子集）**：**`orchestration_flow_catalog`** — **`flowSummary` / `executionSteps[]`**；**`GET …/agent/scenarios/{scenarioId}`**；**`GET …/admin/orchestration/policy`**；运行时 **`agent.orchestration.step`**（**`intent/recognize`** + **`routing/execute`** 读路径）；**`ORCHESTRATION_BUDGET_EXCEEDED`** 写入前 enforcement |
| 2026-05-20 | **Admin · 安全防护（`ai.prompt-safety`）**：**`GET …/admin/prompt-safety/*`** 聚合 API；**§7.1** 用语闸 **`PROMPT_SAFETY_VIOLATION`**（PATCH/Publish）；**`0021_admin_safety_intercept_log`**；SAFETY 发布顶替同场景旧版 |
| 2026-05-20 | **Admin · 人工确认规则（`ai.confirmation-rules`）**：**`GET|POST|PUT|DELETE|PATCH …/admin/confirmation-rules`** + **`POST …/reset`**；内置 6 条（代码）+ 自定义 DB；**`GET …/internal/confirmation-rules/effective`**。Telegram 闪兑/限价 Type-A 前 **`confirmation_rules_evaluate`**（**`block_auto_execute`** 拦截、**`second_confirm`** 前缀）。迁移 **`0020_admin_confirmation_rules`** |
| 2026-05-20 | **限价 price band · Type-A 前预检**：Telegram **`CONFIRM_TYPE_A`** 在 **`create_spot_limit_pending`** / 内联键盘 **之前** 调用 **`check_spot_limit_price_agent_band`**（与 callback/HTTP 共用）；失败 **`limit.price_band_rejected_pre_confirm`**，**不**下发确认按钮 |
| 2026-05-20 | **§2.1/§2.2 边界 + LLM 上游 + Type-A 可选 LLM**：pytest 覆盖 **交易所拒单**、**`PRICE_REJECTED_AGENT_BAND`**（HTTP + Telegram callback）；**`agent_llm_upstream`**（`normalize_openai_compat_base_url` 去重 `/chat/completions`、`UpstreamHttpResult`、HTML/404 友好提示）；**`TELEGRAM_LLM_NARRATE_SPOT_FLASH_CONFIRM`** / **`…LIMIT_CONFIRM`**（Type-A 前可选 LLM  preamble，确定性确认不变） |
| 2026-05-20 | **限价 Telegram 回归 + 现货 TRADING 拼装**：**`lcp`/`lcx`** E2E 测试（Type-A 键盘、callback 时间线、复用 **`executionId`** 跳过重复 quote）；**`TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`** 增 **`trade.spot.flash_convert`** / **`trade.spot.limit_order`**；迁移 **`0018_spot_trade_trading_prompt_seed`** |
| 2026-05-20 | **Telegram 现货 §2.1/§2.2 闭环（当前委托 / 撤单）**：**`routing/execute`** · **`trade.spot.open_orders`** 实调 **`openOrders`**；Telegram **`ROUTE_READ_SKILL`** 展示委托列表；**`EXECUTE_SPOT_CANCEL`** + **`orderId` 槽位**（订单号 / 长数字）直撤；关键词 **「委托」** 不与 **当前委托 / 撤单** 混触限价 bump |
| 2026-05-23 | **Admin 控制台**：**`POST /api/auth/register`**（**`database`** 模式；**空库**首张管理员免 **`OPEN_REGISTRATION`**；其后须 **`CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION`** 或 **`chainup-agent-seed-admin`**）。**`503`** **`ADMIN_CONSOLE_REGISTRATION_REQUIRES_DATABASE_AUTH`**；**`403`** **`ADMIN_CONSOLE_REGISTRATION_DISABLED`**；**`409`** **`ADMIN_CONSOLE_USERNAME_ALREADY_EXISTS`**。响应同 **`POST /api/auth/login`** |
| 2026-05-25 | **P1 运营**：Observability **`…/tool-calls`** / **`…/llm`**；实例 **I02/I04/I05** + **`0027_agent_instance_overrides`**；**`pytest tests/test_admin_p1_ops.py`** |
| 2026-05-25 | **§6 P0 · 504/UNKNOWN 对账**：**`POST|GET /api/v1/agent/trading/reconcile`**（**status**）；**`domain/trading_reconcile`** + **`application/agent_trading_reconcile`**；现货 **`GET /sapi/v2/order`**；改单 **`reconcileSuggested`**；时间线 **`trading.reconcile`**；**`pytest tests/test_trading_reconcile.py`** |
| 2026-05-25 | **P0 合约撤单 + 条件单查/撤**：**`POST …/futures/cancel`**、**`GET …/condition-orders`**、**`POST …/cancel-condition`**；Coobit **`GET/POST /fapi/v1/openOrders|cancel|order`**；场景 **`trade.futures.cancel_order`**、**`automation.condition_orders_read`**、**`automation.condition_order_cancel`**；意图 **`EXECUTE_FUTURES_CANCEL`** / **`ccp`/`ccx`**；**`AGENT_FUTURES_CANCEL_REJECTED`** · **`AGENT_FUTURES_OPEN_ORDERS_FAILED`** |
| 2026-05-22 | **Phase2.x 现货逻辑改单 + OCO stub**：**`POST …/trade/spot/amend-limit-order`**（**`cancel`→`order`** · **`amendCorrelationId`**）；**`trade.spot.amend_limit_order`** **`ready`** · Telegram **`smp`/`smx`**；**`0026_spot_amend_trading_prompt_seed`**；**`trade.spot.oco` / `bracket`** 寄存器 **`stub`** · **`FR_T05_SCENARIO_STUB`** |
| 2026-05-22 | **Phase2.4 全仓杠杆 E2E**：**`POST …/trade/margin/order`** → **`/sapi/v2/margin/order`**；Telegram **双确认** **`xm1/xm2`**、**`xl1/xl2`**；**`0024_margin_trading_prompt_seed`**；**`FEATURE_AGENT_MARGIN`** |
| 2026-05-22 | **Phase2.3 合约 E2E（2.3b/2.3c）**：Telegram **`ump`/`umx`**（市价）、**`ulp`/`ulx`**（限价）Type-A + callback → **`futures_order_for_bound_user`**；**`0023_futures_trading_prompt_seed`**；**`TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`** 增 **`trade.futures.market_order`** / **`limit_order`**；**`NARRATE_FUTURES_*_CONFIRM`** |
| 2026-05-22 | **路线图 Phase2 stub · 意图关键词**：**`recognize_intent_keyword`** — 合约/U本位/永续 与 **现货** 市价·限价 **解耦**（**`trade.futures.market_order` / `trade.futures.limit_order`**）；**`automation.condition_order`**（条件单、止盈止损、触发价等）；**`margin.cross.market_order`**（全仓/逐仓杠杆、杠杆市价；命中时 **不再叠加** 现货 bump，缓解 FR-AO02）；**`read.account.balance`** 之「仓」**排除** **全仓/逐仓/开平仓** 子串。**`STUB_NOT_EXECUTABLE`**（Telegram）时 **`_format_trade_stub`** 按 **`trade.futures` / `margin` / `automation`** 分流提示。**NLU**：**`_intent_family`** / **`_coarse_intent_family`** 增补 **`wealth` / `margin` / `automation`**；**`agent_prompt_effective`** fallback **`primaryScenarioId`** 列表对齐寄存器 |
| 2026-05-21 | **Telegram · 托管只读可选 LLM**：**`read.account.balance`** / **`wealth.holdings_read`** — **`telegram_llm_narrate_read_account_balance`**、**`telegram_llm_narrate_wealth_holdings_read`**；时间线 **`llm.read.account.balance`**、**`llm.wealth.holdings_read`**。**`TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`** 已含两键。**迁移 `0016_read_account_balance_wealth_trading_prompt_seed`**（**`pack_trading_read_account_balance_v1`**、**`pack_trading_wealth_holdings_read_v1`**） |
| 2026-05-18 | **现货撤单 / 当前委托（GitBook Spot）**：**`GET …/trade/spot/open-orders`** → **`GET /sapi/v2/openOrders`**；**`POST …/trade/spot/cancel`** → **`POST /sapi/v2/cancel`**；**`build_coobit_signed_get_request_path`**（GET 签名字符串 **`requestPath`** 含 **`?`**）；**`routing/execute`** / **`GET /scenarios`** **`trade.spot.open_orders`** · **`trade.spot.cancel_order`**；关键词 **撤单 / 当前委托**；**`AGENT_SPOT_OPEN_ORDERS_FAILED`** |
| 2026-05-18 | **`read.market.depth` / `read.market.trades`（Telegram 可选 LLM）**：**`telegram_llm_narrate_read_market_depth`** / **`…_trades`**；**`_try_telegram_public_read_llm_narration`**；事件 **`llm.read.market.depth`**、**`llm.read.market.trades`**。**`TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`** 扩展。**迁移 `0015_read_market_depth_trades_trading_prompt_seed`** |
| 2026-05-18 | **Telegram · `read.market.ticker` 可选 LLM 叙述**：**`telegram_llm_narrate_read_market_ticker`**（**`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER`**）— 成功后 **拼装** **`read.market.ticker`**（与 **`chat.faq`** 同链：平台 SYSTEM/SAFETY → TRADING → Runtime Context → Tool Spec → User），**`runtime_context`** 注入 **`exchangeReadPreview`**；失败回落确定性行情行；**`llm.read.market.ticker`** 时间线。**`TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`** 含 **`read.market.ticker`**。**迁移 `0014_read_market_ticker_trading_prompt_seed`**（**`pack_trading_read_market_ticker_v1`**） |
| 2026-05-18 | **`agent_execution` 观测字段**：**`prompt_pack_version`**、**`resolved_prompt_binding`**（JSON）；**`execution/accept`** 未显式传入时按 **`scenarioId`** 与 **`GET …/internal/prompts/effective`** 对齐快照。**迁移 `0011_exec_prompt_meta`**。**`POST …/intent/recognize`** 响应 **`effectiveLocale`**（**zh-Hans/zh-Hant/en**）。**Prompt PATCH/publish**：**`{{…}}` 占位符 denylist** → **422** **`PROMPT_VALIDATION_FAILED`**（**runtime-injection** §2.3.1 子集）。**pytest**：**`conftest`** 每测隔离 SQLite + **`create_all`**，避免依赖本地**仓库内**旧路径 **`chainup_agent.sqlite3`**（现默认 **`./db/chainup_agent.sqlite3`**，见 **`CHAINUP_AGENT_DATABASE_URL`**） |
| 2026-05-18 | **Intent NLU runtime 占位符**（**`prompt_runtime_substitution`**）：**`load_intent_nlu_system_prompt`** 注入 **`locale`/`previousScenarioId`/`executionId`/`sessionId`**；**enforce** **`variableSchema`** 下 **`PROMPT_INJECTION_FORBIDDEN`** → 跳过网关 LLM、**keyword** 回退 + **`error` 日志**。**`POST …/access/evaluate`** 响应 **`requiresMainSite`**（**`EligibilityEnvelope`**）。 |
| 2026-05-18 | **Telegram 闲聊协查（§8 AC-09k）**：已绑定会话 **`ROUTE_CHAT_FAQ`** 当轮写入 **`agent_execution_event`**：**`prompt.snapshot`**（**`stepKind`**=`intent_nlu`，**`scenarioId`**=`agent.runtime.intent_nlu`，含 **`promptPackVersion`** / **`resolvedPromptBinding`** / **`nluSource`** 等）与 **`llm.chat.faq`**（**`stepKind`**=`chat_faq`，**`chat.faq`** 包快照 + **`gatewayModelId`** 等；失败时 **`outcome`**=`failure`）。**`server/tests/test_product_doc_registry_check.py`** 复跑 **`product-doc/.../check_registry_vs_routing_engine.py`**（**AC-09q**） |
| 2026-05-20 | **Telegram UX**：**`telegram_intent_preview_in_reply`**（**`CHAINUP_AGENT_TELEGRAM_INTENT_PREVIEW_IN_REPLY`**）— 默认 **不**附带「编排预览」行。**意图**：**`_prefer_read_balance_on_explicit_phrase`** — 「账户余额/查余额/…」在 **`INTENT_NLU_USE_LLM`** 归为 **`chat.faq`** 时 **升格** **`read.account.balance`**；关键词路由对显式短语 **叠加 bump**。 |
| 2026-05-19 | **TRADING LLM 拼装泛化**：**`assemble_trading_llm_payload`**（按 **`scenario_id`** 加载 **TRADING** 包；小节锚 **`SCENARIO_STRATEGY_<SLUG>`**）。**允许列表** **`TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`**（**`chat.faq`**、**`read.market.ticker`** / **`read.market.depth`** / **`read.market.trades`**（**`0014`/`0015`** + **`…NARRATE…`**）、**`read.account.balance`** / **`wealth.holdings_read`**（**`0016`** + 对应 env））；**`invoke_llm_chat_for_telegram(..., scenario_id=)`**。**`GET /api/v1/agent/scenarios`**：**`chat.faq`** **`readiness`**=`ready`。**`assemble_chat_faq_llm_payload`** 仍为 **`chat.faq`** 别名。 |
| 2026-05-19 | **Prompt Assembly（§8 AC-09a/e 部分 · `runtime-injection` §1）**：**`agent_prompt_assembly`** — Telegram **`chat.faq`**：`SYSTEM`（**`agent.runtime.platform_system`**）→ **`SAFETY`**（**`agent.runtime.platform_safety`**）→ **`TRADING`** **`chat.faq`**（场景正文 + Few-shot）→ Runtime Context JSON → **Tool Spec**（**`exchange_tool_schema_registry`** JSON Schema SSOT）→ User；Ark 路径同序扁平化为单条 **`input_text`**。**Intent NLU**：前置平台 SYSTEM/SAFETY + 输出 Shape JSON Schema SSOT。**迁移 `0013_phase1_prompt_assembly_seed`**（三包种子）；CI SQLite **`create_all`** 无种子时用代码 **fallback** 文本。**观测**：**`llm.chat.faq`** meta 可能含 **`promptAssemblyContract`** / **`promptPackVersions`**。 |
| 2026-05-19 | **§8 AC-09f（部分）**：**`admin_prompt_pack.variable_schema_json`**（迁移 **`0012_prompt_pack_variable_schema`**）；**`PATCH …/admin/prompt-packs/{id}`** Body 可选 **`variableSchema`**（与 **`messages`** 至少其一）；**非空** `variableSchema` 时 **`{{slug}}`** 须在 **声明键 ∪ 平台白名单**（**ASSEMBLY/`runtime-injection` 下限键名**）；**`GET …/internal/prompts/effective`**、包详情返回 **`variableSchema`** |
| 2026-05-15 | **时间与 UTC**：新增 **§2.1**（DB/API **UTC**、`Telegram message.date`、日志与 Admin 展示分工）；**`API_INTEGRATION_GUIDE` §3.3** 增补 **`datetime` 约定**；**`admin/FE_HANDOFF`** 接力运营时区展示 |
| 2026-05-15 | **Telegram Bot API**：**`call_telegram_bot_api`** 对 **`httpx.RequestError`**（**ConnectError**、超时、代理等）默认 **额外重试 2 次**（退避）；**`CHAINUP_AGENT_TELEGRAM_BOT_API_TRANSPORT_RETRIES`**；失败 **`details.transport_attempts`** |
| 2026-05-15 | **现货市价买单**：**`POST …/flash-convert`** **MARKET BUY** 发往交易所的 **计价 ``volume``**（如 USDT）与 Telegram 二次确认一致，按 **向下取整保留至多 2 位小数**（原 8 位量化） |
| 2026-05-15 | **Telegram Type-A 二次确认**：闪兑 / 限价确认文案在可解析 **`BASE-QUOTE`** 且可算名义时增加一行 **`{QUOTE}:xx.xx`**（**展示用** **2** 位小数；闪兑按 **ticker 最新价 × base 数量**，限价按 **限价 × base 数量**）；数量行展示 **`数量：`n` BASE`** |
| 2026-05-15 | **Telegram 错误话术**：**`AGENT_SPOT_ORDER_REJECTED`** 等现货相关 **`AppError`** 在 **Telegram** 上可选经 **Admin AI LLM** 改写为友好中文（**`telegram_app_error_user_message`** + **`invoke_llm_rewrite_telegram_app_error`**）；**`CHAINUP_AGENT_TELEGRAM_ERROR_LLM_REWRITE`** / **`…TIMEOUT_SEC`**；失败或 LLM 路径未预期异常均回退 **`format_app_error_reply_plain`**（用户仍收到确定性文案） |
| 2026-05-15 | **Telegram 出站**：**`ADMIN_TELEGRAM_TRANSPORT_ERROR`** 的 **`details`** 增补 **`transport_error_type`**、**`transport_error_message`**（便于区分 **ConnectTimeout** / **ConnectError** / **ProxyError** 等；**不**含 token）。**§4** 增补该码排查要点 |
| 2026-05-15 | **ADR-004（本仓渐进）**：**`domain/canonical_trading`** 承载 **`PlaceOrder`** 与 Coobit **`POST /sapi/v2/order`** 映射；**`agent_spot_trade`** 经该层组单；执行时间线 **`summary`** 增 **`venue`**（**`coobit`**）、**`canonicalOp`**（**`place_order`**）（闪兑/限价 **`quote`~`trading.exchange_private`**，含 Telegram 异常占位）。**不**替代所内 **Execution Gateway** 可执行体（**CC-P1-07 · DoD B**） |
| 2026-05-14 | **Admin Agent 管理**：**G01** **`GET …/admin/agents/runtime/global-agent-gate`**；**Runtime** **`POST …/instances/{instanceId}/runtime/{action}`**、**`POST …/instances/runtime/batch`**；**日志 Tab** **`GET …/instances/{instanceId}/logs/conversations|tools|errors`**；**`agent_instance.runtime_state`**（迁移 **`0009_agent_instance_runtime`**） |
| 2026-05-14 | **现货限价（§2.2）**：**`POST /api/v1/agent/trade/spot/limit-order`**（**`LIMIT`**，**`volume`**=**base**，**`price`**，**`timeInForce`** 可选）；**`spot_limit_order_for_bound_user`** 与闪兑共用签名下单；时间线 **`trade.spot.limit_order`**。**可选** **`CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_ENABLED`**：相对 **`lastPrice`** 超 **`CHAINUP_AGENT_TRADE_SPOT_LIMIT_PRICE_BAND_MAX_PCT`** → **422** **`PRICE_REJECTED_AGENT_BAND`**。**意图**：**`trade.spot.limit_order`** **`ready`**，**`CONFIRM_TYPE_A`**（槽位 **symbol/side/quantity/price**）。**Telegram**：**`lcp`/`lcx`** + **`agent_telegram_pending_confirm`**（**`kind=spot_limit_order`**）。**关键词**：含 **限价/挂单/委托** 时 **「价格」** 不 bumped **ticker**（避免与限价槽位冲突） |
| 2026-05-14 | **执行协查 · `POST /routing/execute`**：**`execution_accept` → 只读 / 占位 → **`agent_execution_event`**（**`trading.exchange_public`** / **`trading.exchange_private`** · **`exchange_read`**，或 **`routing.read.failed`**）→ **`finalize`**；**200** 体 **`executionId`**。**Telegram **`read.*`**：同轮 **`executionId`** 写同款事件 |
| 2026-05-14 | **只读行情扩展**：**`read.market.depth`**（**`GET /sapi/v2/depth`**）、**`read.market.trades`**（**`GET /sapi/v2/trades`**）；**`routing/execute`** Body **`symbol`** + 可选 **`marketDataLimit`**；意图关键词 / **`GET /scenarios`** / Telegram **`ROUTE_READ_SKILL`** 已接线。**`coobit_openapi`** 多形态 **`symbol`** 顺序尝试与 **`/ticker`** 一致。**迁移 `0008_intent_nlu_read_market_expand`**（意图 NLU 种子包文案） |
| 2026-05-14 | **可观测时间线 · 现货下单**：**`trading.exchange_private`** **`summary`** 增加脱敏 **`orderRequest`**；**成功**时 **`exchangeResponsePreview`**（订单字段白名单）。**失败**：**`AGENT_SPOT_ORDER_REJECTED`** / **`AGENT_SPOT_ORDER_FAILED`**（HTTP≠200 且已解析 JSON 体）在 **`AppError.details.exchange_response_preview`** 中带 **`code`/`msg`** 及已知订单字段；时间线同步 **`exchangeResponsePreview`**。**超时 / 非 JSON** 等仅 **`httpStatus`/`appErrorCode`**，无对端 body |
| 2026-05-14 | **可观测**：**`trading.exchange_private`.`orderRequest.flashMarketMeta`** 标明 **MARKET BUY** **`volume`**=计价 amount、**`baseQtyUserRequested`**=用户 ETH/base 数量 |
| 2026-05-14 | **现货下单体 `symbol`**：对齐 **OpenAPI v2 Spot · New Order** Request Body（*E.g. BTC/USDT*），**`POST /sapi/v2/order`** 使用 **`BASE/QUOTE`**（**`normalize_coobit_spot_order_body_symbol`**）；**`symbolOrder`** 仍为紧凑 **BTCUSDT** 供询价/展示 |
| 2026-05-27 | **写路径 / 记忆 / 澄清**：全量 **`scenario_to_skill_id`** 映射 · Type A 前统一 **`agent.skill.spec_read`**（含闪兑 Telegram/HTTP）· Telegram **STM** 召回/写回/§2.8 · **`previousScenarioId`** 多轮 · LLM 槽位 **`prune_llm_slots_without_text_evidence`** |
| 2026-05-27 | **执行详情 Tab**：**`GET …/queue|events|retries|recovery`**（**`admin_observability_execution_tabs`**） |
| 2026-05-14 | **执行协查 · 闪兑全链**：**`agent_execution_event`** 写入 **quote →（Type-A）confirm_prompt / confirm_accept → submit_order → `trading.exchange_private`**；**`POST …/flash-convert`** 与 Telegram callback **同源 `spot_flash_convert_for_bound_user`**；Type-A **pending `executionId`** 与 **`ACCEPTED`** 回合对齐可 **单 `executionId` 协查**。**`GET …/admin/observability/executions/{executionId}/timeline`**。**迁移 `0007_exec_event`** |
| 2026-05-14 | **`AGENT_SPOT_ORDER_REJECTED`**：识别交易所 **无权限 / permission / access denied** 等文案时 **`details.reject_reason`**=**`API_PERMISSION_OR_SUBACCOUNT`**，**`message`** 追加 **中文处理建议**（Key 权限、子账户、IP 白名单、重绑） |
| 2026-05-28 | **修复**：`agent_llm_clarify._build_clarify_user_block` 误用未定义 **`session_id`** → 已绑定用户走 CLARIFY+LLM 时 Telegram 误报「门禁/路由不可用」 |
| 2026-05-28 | **只读多轮上下文修复**：**`extract_symbol_for_ticker`** 支持中文紧邻 **`BTC-USDT`/`BTCUSDT`**；成功 **`read.market.*`** 后 **`pending_clarify_slots`** 保留 **`symbol`**；跟进话术（**盘面/深度**）路由 **`read.market.depth`** 并继承交易对 |
| 2026-05-28 | **交易多轮上下文**：**`last_trade_slots`/`last_trade_scenario_id`**（**`remember_trade_write_context`**）在 **Type-A 清 pending** 后仍保留 **symbol/side/qty**；**`clarify_phrase_slots`**（闪兑/闪队/当前市价）+ **`_prefer_pending_trade_clarify_context`** 避免 **「当前市价」** 误落 **`read.market.ticker`**；已设 **`tradeMode`** 时跳过 LLM 澄清复读 |
| 2026-05-28 | **现货槽位补齐守卫**：**`_prefer_trade_on_complete_spot_slots`** 在 **永续/合约/杠杆/条件单** 语境下不覆盖 **futures/margin/automation** 路由（修复 **「BTC永续市价买入」** 误落 **spot flash**） |
| 2026-05-28 | **只读续轮槽位/分数**：**`read.*` pending** 优先于 **`last_trade_slots`**（避免 **「深度数据呢」** 交易对污染）；**`_clamp_ranked_scores`** 防止 **IntentCandidate.score>1** 触发 **ValidationError**；Telegram **`_resolve_read_symbol_for_telegram`** 回退 **pending symbol** |
| 2026-05-28 | **MR-MEM-01（续）· GlobalConfigBundle + 只读澄清键盘**：**`GET|PATCH /api/v1/admin/trading-agent-config/bundle`**（**`If-Match`/`expectedConfigVersion`** · **409** 乐观锁 · **`memory_runtime_settings`** 热生效覆盖 **`CHAINUP_AGENT_*`**）· **`ReadClarify` 出站 `rc:scope:*`/`rc:sym:*`/`rc:mon:*` 键盘** · **`coalesce_latest` 入站合并** · **类型 A cancel** 释放 **`pendingTypeA`/`activeWriteExecution`** |
| 2026-05-28 | **MR-MEM-01 · 澄清会话 v1.6 / stale+Resume / 并发**：**`ClarifySessionSnapshot`**（**`lifecycleState`** · **`cl:*`/`rc:*` 回调**）· **idle/TTL → stale** + **`WarmExecutionEpisode`** · **Resume 规则分类器** + 时间线 **`agent.memory.resume_classified`** · **inbound §2.3** · **`memory_governance`** 四步闸 · **`SESSION_*`/`STM_*` 配置** · **`update_id` 幂等** + **串行队列** · **澄清出站 `inline_keyboard`**（**`telegram_clarify_keyboard`/`telegram_clarify_outbound`**）· **`sendChatAction(typing)`** · **D-1**：**`execution.state=UNKNOWN`** / DB **pending_confirm** 挡新写 |
| 2026-05-27 | **S11 交易澄清（规则 + 可选 LLM + 多轮槽位）**：**`trade_slot_clarify`** 统一 **闪兑/限价/全仓杠杆/合约** 市价·限价；**`quantity|quoteQty`**、**`QUOTE_PAIR_NOT_FROZEN`**、**`FUTURES_NOMINAL_AMBIGUOUS`**、**`notionalMode`** → **`RESOLVE_TRADE_NOTIONAL`**（同 **`RESOLVE_FLASH_NOTIONAL`**，现货余额换算）；**`sessionId`** 多轮 **`pending_clarify_slots`** 合并；**`CHAINUP_AGENT_INTENT_CLARIFY_USE_LLM`** / **`intentClarifyUseLlm`** 用 **`agent.runtime.runtime_clarify`** 润色规则 **`plan.clarify`**（失败回退规则文案） |
| 2026-05-14 | **公开 ticker 兼容**：**`GET /sapi/v2/ticker`** 对 **``symbol``** 多形态顺序尝试（如 **BTC-USDT**、**BTCUSDT**、**BTC/USDT**）；HTTP JSON 含 **`code`/`msg`** 时 **`code`** 为 **`0`/`200`**（及常见字符串变体）视为成功；**`last`** / **`lastPrice`** 可从 **`data`/`result`/`ticker`** 内层读取（与部分网关封装体一致） |
| 2026-05-14 | **现货闪兑**：**`POST …/trade/spot/flash-convert`** 的 **`volume`** 约定为 **base 数量**；**`BUY`** 时先拉公开 **`/sapi/v2/ticker`**，用 **`lastPrice`** 换算计价 **amount** 再 **`POST /sapi/v2/order`**（GitBook：市价买单 `volume`=amount）。**`AGENT_SPOT_ORDER_REJECTED`** 的 **`message`** 尽量拼接交易所 **`msg`** |
| 2026-05-14 | **Telegram 闪兑**：**`callback_query`** + **`agent_telegram_pending_confirm`**；确认走 **`…/trade/spot/flash-convert`**。**Prompt**：表 **`admin_prompt_pack`**；**`GET /api/v1/internal/prompts/effective`**；Admin **`/api/v1/admin/prompt-packs`** 列表/详情/**PATCH `messages`**；**`agent.runtime.intent_nlu`** 注入 **`INTENT_NLU_USE_LLM`** 系统提示（失败回退内置）。**迁移 `0006_pm_tg`** |
| 2026-05-14 | **意图**：**`POST …/intent/recognize`** 须 **DbSession**；**NLU** **`keyword_v1`** 与可选 **`INTENT_NLU_USE_LLM`**（**`llm_structured_v1`**，`agent_llm_intent_nlu`）；**`load_llm_gateway_context`**（**`agent_llm_chat`**）；**裁决** 寄存器 / **FEATURE_*** / **FR-AO02** / 闪兑 **CONFIRM_TYPE_A**；**`orchestrationVersion` `intent-router.policy.v2`**。**Telegram 已绑定**：**`recognize_intent_full`** + **`plan.nextStep`**（澄清、只读、闲聊、闪兑摘要、占位、关闸） |
| 2026-05-13 | **Admin Bearer 收口**：**`ADMIN_CONSOLE_JWT_SECRET`** 非空时登录签发 JWT；**`/api/v1/admin/*`** 强制 **`Authorization: Bearer`**（错误码 **`ADMIN_CONSOLE_AUTH_REQUIRED`** 等）；运行时 **`/api/v1/agent/*`** 等不在此强制范围 |
| 2026-05-12 | **`GET .../api-binding/status`**、**`GET .../subaccount/status`**、**`POST .../onboarding/initiate`**、**`POST .../subaccount/create`**（DEFERRED）；查 **`telegram_agent_trading_binding`** |
| 2026-05-12 | **`access/evaluate` · `intent/recognize` · `routing/execute`**（noop）· **`execution/*`**（进程内 scaffold）· **`GET /access/reasons` / `GET /scenarios`**；Webhook 已绑定会话附 **粗略意图**（关键词）；配置 **`CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED`** / **`OPS_SUSPENDED`** |
| 2026-05-13 | **收口验收清单**：[`PHASE1_ACCEPTANCE.md`](PHASE1_ACCEPTANCE.md) |
| 2026-05-13 | Admin Observability：**`DELETE …/observability/executions/{executionId}`**（**204** 硬删 **`agent_execution`**） |
| 2026-05-13 | Admin Observability：**契约专篇** **`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`**（**`GET …/observability/executions*`**） |
| 2026-05-13 | Admin Observability：**`GET /api/v1/admin/observability/executions`**、**`GET …/{executionId}`**（**`agent_execution`** 分页筛选） |
| 2026-05-13 | Telegram Webhook：**读 Body 后立即 `200`**，**`sendMessage`** / LLM / 路由在 **后台任务**，避免上游慢导致 Telegram 断连后用户侧全无回复 |
| 2026-05-13 | Telegram Webhook：可选 **`CHAINUP_AGENT_TELEGRAM_WEBHOOK_INLINE_PROCESSING`**（响应后即冻结的环境改用同请求处理）；构建回复异常仍 **`sendMessage`** 兜底 + **`telegram_webhook_build_reply_failed`** |
| 2026-05-13 | Telegram Webhook：**门禁 → 关键词意图 → `routing/execute`**（**`read.market.ticker`** / **`read.account.balance`**）；**`access/evaluate`** 可选 **`telegramChatId`**；放行且无绑定时的正文提示 |
| 2026-05-13 | **绑定校验**：**`sub_account_id`** 必填；与 **`GET /sapi/v1/account`** 可识别 id 字段交叉校验；**`confirm`** / **`me`…bindings** 同步 **upsert `agent_instance`**；响应 **`instanceId`**；迁移 **`0003_ai`**；配置 **`DEFAULT_AGENT_TEMPLATE_*`** |
| 2026-05-13 | **Admin AI Settings**：空目录 **默认不再** 运行时种子 **`demo`**（配置 **`ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY`**，默认 **false**）；删除后刷新不再「复活」 |
| 2026-05-13 | **Admin AI Settings**：**`DELETE …/providers/{providerId}`**（**204**；模型 **CASCADE**） |
| 2026-05-13 | **Admin AI Settings**：模型 **`GET …/{modelId}`**、**`DELETE …/{modelId}`**（**204**）；**`PATCH`** 可选 **`providerId`** |
| 2026-05-13 | **Admin AI Settings**：**`POST /api/v1/admin/ai/models`**（自定义 **`modelId`**）；Provider 详情响应 **Pydantic v2** 序列化修复 |
| 2026-05-13 | **Admin AI Settings**：**`/api/v1/admin/ai/*`**（Provider / Model / defaults / health-policy / health probe）；表 **`admin_ai_*`**；迁移 **`0004_aisettings`** |
| 2026-05-27 | **Prompt 治理 16 包**：迁移 **`0030_governance_prompt_pack_seed`** · **`pp-*`** PUBLISHED · **`prompt_governance_catalog`/`resolve`** · legacy **`pack_*` → DEPRECATED** |
| 2026-05-21 | **Prompt 列表展示名**：**`GET/POST` 包摘要与详情** 增加只读 **`title`**（**`resolve_prompt_pack_title`**：场景 **`flow.title`**、**`agent.runtime.*`** 固定文案、**`DRAFT`** 后缀） |
| 2026-05-20 | **Prompt 新建草稿**：**`POST …/prompt-packs`** 支持 **`sourcePromptPackId`** 模板复制；**TRADING/ANALYSIS** 创建须 **`scenarioId`** 且在场景寄存器；空白草稿带场景说明 **system** 占位正文 |
| 2026-05-20 | **Telegram 未绑定回复**：去掉「内容摘要」与正文 Deeplink 明文；HTTPS 仅按钮 + 优化引导语 |
| 2026-05-20 | **Telegram Webhook**：**已绑定**判定改为 **`is_telegram_user_agent_hosted_bound`**（托管行 + **`agent_instance`**）；删除实例后 **恢复绑定引导**（allowlist 不再单独跳过） |
| 2026-05-20 | **Admin · I06**：**`DELETE …/instances/{instanceId}`**（**204**；级联删 **`telegram_agent_trading_binding`**，可重新绑定；**422** **`AGENT_ADMIN_INSTANCE_DELETE_BLOCKED`**） |
| 2026-05-13 | **Admin**：**`GET /api/v1/admin/agents/instances`**、**`GET …/{instanceId}`**（只读；**`AGENT_ADMIN_INSTANCE_NOT_FOUND`**） |
| 2026-05-13 | Telegram：**已绑定** **`sendMessage`** 正文去掉 抬头、「你说：」摘要及 **`tg_id`/用户名/语言** echo（仅用业务答复）；运维对照服务端日志 |
| 2026-05-13 | **`execution/*`**：**`agent_execution`** 表持久化（**`0005_exec`**）；Telegram bound turn **`accept→finalize`**（**`source=telegram_webhook`**）；HTTP **`source=http_api`** |
| 2026-05-12 | Telegram 已绑定：**不**再在回复末附带明文 Deeplink |
| 2026-05-11 | **`POST /api/v1/agent/api-binding/validate`**：**`openapi_base_url` + Key**；**GET /sapi/v1/account** 实探测；**400** `AGENT_API_KEYS_*` / `AGENT_OPENAPI_BASE_URL_INVALID` / `AGENT_API_KEYS_REJECTED`；**502** `AGENT_OPENAPI_PROBE_FAILED`；**不落库** |
| 2026-05-12 | 绑定 Deeplink URL 合并 **`tg_*`** query 预填（非签名校验）；见 §3.1「`tg_*`」 |
| 2026-05-12 | Webhook：``POST /webhook/telegram/{bot_token}`` 验签后 **200**；文本消息 **sendMessage** 联调（``application/telegram_inbound``）；禁 **501** 致 Telegram 重试 |
| 2026-05-12 | Telegram 入站：默认 **绑定引导** + 绑定页 URL 按钮（`TELEGRAM_BIND_PAGE_URL`）；可选 **已绑定 chat 列表**（无 DB） |
| 2026-05-11 | 配置：`CHAINUP_AGENT_TELEGRAM_BOT_TOKEN`（仅存本地 `.env`/密钥管理；泄漏须 BotFather 轮换） |
| 2026-05-11 | 配置重命名：**`CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL`** 替代 ~~`CHAINUP_AGENT_TELEGRAM_COOBIT_BIND_PAGE_URL`~~（绑定页可多平台注入） |
| 2026-05-11 | 初版：FastAPI 骨架、分层、`BACKEND_SPEC`、Phase 1 占位路由与测试 |
| 2026-05-11 | §3.1：登记 **`POST /api/auth/login`**（控制台）与 `AppError` 错误码 |
| 2026-05-11 | §6：`admin_console_user`、Alembic、`admin_console_auth_mode`、`chainup-agent-seed-admin` |
