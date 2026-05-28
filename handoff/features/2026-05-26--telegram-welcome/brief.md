# 开通欢迎语

> 功能 ID：`2026-05-26--telegram-welcome`  
> 产品 Agent 定稿 · `contract_ready`

## 背景

产品 SSOT（[`telegram/overview.md`](../../../product-doc/specs/requirements/domains/agent/telegram/overview.md) **§2.1.1**、[`admin-bot-config.md`](../../../product-doc/specs/requirements/domains/agent/telegram/admin-bot-config.md) **FR-TG-ADMIN-06** / **SC-TG-ADMIN-05**）要求：用户 **首次** 达成 **Agent 开通就绪 ∧ Telegram 交易 API 已绑定** 时，Bot **可配置** 投递 **一条** 多语言欢迎消息（**幂等**、**回退链**、**无正文不发送**）。

**存量**：Admin **`PATCH /api/v1/admin/channels/telegram/bot`** 已支持 **`runtimeParams`** 写入 **`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_*`**（`telegram_runtime_config.py`）；**`TelegramChannelDetailPage`** 有单框「开通欢迎语」映射当前 UI 语言键。**缺口**（见 `server/docs/PHASE1_ACCEPTANCE.md` **AC-09o**）：运行时 **无** §2.1.1 **语言解析/回退**、**无** `sendMessage` 投递、**无** 每用户 **幂等** 落库。

## 用户故事

- 作为 **平台运营**，我希望在 **渠道管理 · Telegram** 分 **简/繁/英** 维护欢迎模板，以便用户开通后收到对应语言问候。
- 作为 **交易员**，我在 **Deeplink 完成 API 绑定** 后，希望在 **Telegram 私聊** 收到 **一条** 欢迎语（若运营已配置且 Bot 可用）。
- 作为 **SRE**，我希望绑定 **confirm 仍 200** 即使 Telegram 发送失败，且 **同一 tg_id 不重复骚扰**。

## 验收标准

- [x] **AC-1**：**`PATCH /api/v1/admin/channels/telegram/bot`** 的 **`runtimeParams`** 可读写 **`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN` / `_ZH_TW` / `_EN`** 与遗留 **`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT`**；单键长度 **≤ 4096**；超长 **400** **`ADMIN_TELEGRAM_WELCOME_TEXT_TOO_LONG`**；**`GET`** 回显一致（**If-Match** 与存量 bot PATCH 一致）。
- [x] **AC-2**：运行时 **`resolve_activation_welcome_text`** 实现 **§2.1.1** **语言桶**（`zh-Hans` / `zh-Hant` / `en`）与 **回退链**：命中桶 → 简体 → 英文 → 繁体 → 遗留键 → **空则 `null`**（不发送）。
- [x] **AC-3**：**`POST /api/v1/agent/api-binding/confirm`**（及 **`POST /api/v1/me/agent/bindings/trading-api`**）在 **首次** 对该 **`telegram_user_id`** 满足欢迎投递条件时：Bot Token 已配置、回退链 **非空** → **调用** `sendMessage`（私聊 **`chat_id`** = **`tg_id`**，与 Deeplink 预填对齐）；响应含 **`activationWelcomeSent: true`**。
- [x] **AC-4**：**同一 `telegram_user_id`** 再次 confirm（更新绑定）或已记幂等 → **不** 再发欢迎语；**`activationWelcomeSent: false`**（可附 **`activationWelcomeSkipReason`**，如 `already_sent`）。
- [x] **AC-5**：三语键与遗留键 **皆空**（或仅空白）→ confirm **200**，**不** 调用 `sendMessage`；**`activationWelcomeSent: false`**，**`activationWelcomeSkipReason: no_template`**。
- [x] **AC-6**：`sendMessage` **传输失败**或 Bot API **4xx** → confirm **仍为 200**；**`activationWelcomeSent: false`**；日志含可检索原因（**不算** 绑定失败）。
- [x] **AC-7**：模板中的 **`{displayName}`** 渲染为 **`tg_first_name`**，否则 **`@tg_username`**，否则 **`用户`**（占位符 **白名单** 仅此一项，非法占位 **原样保留**（实现对齐：非法占位原样保留））。
- [x] **AC-8**：Admin **`/system/channels/telegram`** **分语言** 编辑三语欢迎语（简/繁/英 **独立字段**），保存后 **刷新** 仍可见；与 **§4 用户体验** 文案说明一致（**SC-TG-ADMIN-05** 配置面）。

### 开通就绪（本包 MVP 定义）

**「Agent 开通就绪 ∧ Telegram 已绑定」** 在实现上等价于：**`api-binding/confirm` 成功**（`telegram_agent_trading_binding` + **`agent_instance`** upsert）。不在本包扩展 KYC/计费/初始化流其它步骤。

### 语言解析（首版）

按 overview **§2.1.1**：**①** 请求 **`telegram.tg_lang`**（Telegram `language_code`）→ 三桶；**②** 否则 **`TELEGRAM_DEFAULT_LOCALE`**（`runtimeParams`）→ 三桶；**③** 否则 **英文桶**。用户主档语言 **本包可留 TODO/P2**（无表时跳过）。

## 范围

### 本期包含

- **`server/`**：欢迎语解析/渲染；**幂等**持久化（新表或 `agent_instance` 字段，由 **/be** 选型）；**`confirm_agent_trading_api_binding`** 后 **可选** `sendMessage`；**`ConfirmAgentApiBindingResponse`** / **`MeAgentTradingApiBindingResponse`** 增加 **`activationWelcomeSent`**（及可选 **`activationWelcomeSkipReason`**）；**`bindingRowCreated`** 与 agent confirm **对齐暴露**。
- **`admin/`**：**三语** 欢迎语编辑 UX（可保留「菜单摘要」与欢迎语分离或同区块分 Tab）。
- **功能包 OpenAPI** + **pytest**（解析链、confirm 发送/幂等/跳过）+ **E2E**（Admin 保存三语）。
- **时间线（可选 P1）**：`telegram.activation_welcome` 事件 **info**（sent/skipped）。

### 本期不包含

- 换绑后对 **老用户** 因模板改版 **自动重发**（overview 默认 **不**）。
- **非私聊** / **群组** 欢迎语。
- Deeplink **成功页** 展示欢迎语全文（仅 TG 投递）。
- **CHANNEL_TELEGRAM** 独立运维开关（以 **Bot Token 是否配置** 为下限；`channelTelegramEnabled` 只读展示沿用存量）。
- 欢迎语 **Markdown 富文本** 全量（首版 **纯文本** `sendMessage`）。

## 界面与交互（含页面）

| 路由 | 行为 |
|------|------|
| **`/system/channels/telegram`** | **§4 用户体验**：**简中 / 繁中 / 英文** 三个多行输入（或 Tab），分别写入对应 **`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_*`**；说明 **触发时机**（绑定成功 · 每用户一次）与 **`{displayName}`** 占位符；**保存** 走 **`PATCH …/bot`** `runtimeParams` + **If-Match** |
| Deeplink **`/onboarding/...`** | **无 UI 变更**（欢迎语在 TG 侧送达） |

**加载/错误**：PATCH **409** 提示刷新；超长 **400** 展示服务端 **`message`**。

## 非功能要求

- confirm 路径 **额外 RTT** 仅一次 `sendMessage`（超时 **≤ 10s**，可配置，**不** 阻塞 DB commit 之前逻辑 **`design` 冻结为 commit 后 best-effort 发送**）。
- 欢迎语配置 **T+N≈0**（读 `telegram_channel_runtime` 文档，无进程重启）。
- **禁止** 在审计/日志中打印欢迎语全文若含 PII（可 log hash/length）。

## 待确认问题

- [x] Q1：触发点 — **绑定 confirm 成功** 是否为 MVP「开通就绪」？— **是**（与 inventory §4、PHASE1 gap 一致）。
- [x] Q2：重复绑定 — **不** 再发（**AC-4**）。
- [x] Q3：Admin 三语 UI — **本期 FE 交付**（**AC-8**），不单列后续包。
