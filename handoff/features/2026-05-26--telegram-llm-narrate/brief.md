# 场景 LLM narrate 扩面

> 功能 ID：`2026-05-26--telegram-llm-narrate`  
> 产品 Agent 定稿 · **`done`**（product.accept 2026-05-26）

## 背景

Phase-1 已在 Telegram **已绑定** 回合为 **9 类场景** 实现可选 **LLM narrate / Type-A preamble**（只读行情/余额/理财、现货闪兑/限价、合约市价/限价确认），由 **9 条** 环境变量 **`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_*`** 独立开关，**默认 `false`**，LLM 不可用时 **回落确定性文案**（见 `server/docs/BACKEND_SPEC.md` §Telegram narrate）。

运营无法在 **Admin 网关默认配置** 中按场景开启 narrate，生产变更依赖部署改 env。本功能将 **per-scenario narrate 开关** 纳入 **`gateway_defaults.telegramLlmNarrate`**，并与既有 env **强制开启**、回落与时间线语义对齐（模式同 **`2026-05-26--nlu-llm-strategy`**）。

## 用户故事

- 作为 **平台运营**，我希望在 **AI 网关默认配置** 中为各 Telegram 场景单独打开 LLM narrate，以便无需改 9 条 env 即可升级回复体验。
- 作为 **SRE**，我希望保留各 **`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_*`** 作为紧急开关（**env=true 强制开启**），覆盖 Admin 关闭项。
- 作为 **交易员（TG）**，当 LLM 暂不可用时，我仍收到 **确定性摘要/确认块**，而不是 5xx 或无回复。

## 验收标准

- [x] **AC-1**：**`gateway_defaults`** 持久化对象 **`telegramLlmNarrate`**，含 9 个 boolean 字段（见下表）；**`GET /api/v1/admin/ai/defaults`** 返回该对象；**`PATCH`** 可 **部分更新** 子字段且 **If-Match** 与存量 defaults 一致；**未配置时各字段默认 `false`**（向后兼容）。
- [x] **AC-2**：当 **read.market.ticker** 的 **有效 narrate 为启用**（见下表）且 Telegram 只读路由 **成功** 时，调用 **`invoke_llm_chat_for_telegram`**（**`scenario_id=read.market.ticker`**），成功则用户可见 LLM 叙述 + 既有 footer；并写入时间线 **`llm.read.market.ticker`**。
- [x] **AC-3**：当 narrate **已启用** 但 LLM/网关/拼装 **失败** 时，Telegram 仍 **200 出站**（`sendMessage` 成功），正文为 **原确定性 ticker 行**（**不** 因 narrate 失败 5xx 或无回复）。
- [x] **AC-4**：当 **有效 narrate 为关闭** 时，**不** 调用 LLM narrate helper，仅输出确定性 ticker 行；时间线 **无** **`llm.read.market.ticker`** 成功/失败 narrate 行（或等价：不进入 narrate 分支）。
- [x] **AC-5**：**`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER=true`** 时 **强制启用** ticker narrate，**即使** **`gateway_defaults.telegramLlmNarrate.readMarketTicker=false`**；**env 未显式 `true`** 时以 Admin 字段为准。
- [x] **AC-6**：其余 **8 个场景**（depth、trades、balance、wealth、spot flash/limit、futures market/limit）共用同一 **`resolve_effective_telegram_llm_narrate(scenario_key)`**（或等价）解析 **有效开关**；Admin/env 字段映射与下表一致；各场景启用时行为与存量 env-only 单测语义一致（只读 → narrate；Type-A → preamble + 确定性确认块）。
- [x] **AC-7**：narrate **已尝试**（无论成败）的时间线事件 payload 含 **`effectiveTelegramLlmNarrateEnabled: true`**（boolean），值为 **effective**（非仅 settings 原始 env）；**未进入 narrate 分支** 时不写该键或写 **`false`**（实现对齐一种即可，须在 **`backend/notes.md`** 注明）。
- [x] **AC-8**：**`PATCH …/defaults`** 仅更新 **`telegramLlmNarrate.readMarketDepth: true`** 时，其它 8 字段 **保持** PATCH 前值；GET 回显合并结果。

### `telegramLlmNarrate` 字段 ↔ 场景 ↔ env（有效策略）

| Admin 字段（camelCase） | scenario_id / 用途 | env（`true` 强制开启） |
|-------------------------|-------------------|------------------------|
| `readMarketTicker` | `read.market.ticker` | `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER` |
| `readMarketDepth` | `read.market.depth` | `…_READ_MARKET_DEPTH` |
| `readMarketTrades` | `read.market.trades` | `…_READ_MARKET_TRADES` |
| `readAccountBalance` | `read.account.balance` | `…_READ_ACCOUNT_BALANCE` |
| `wealthHoldingsRead` | `wealth.holdings_read` | `…_WEALTH_HOLDINGS_READ` |
| `spotFlashConfirm` | Type-A 闪兑确认 preamble | `…_SPOT_FLASH_CONFIRM` |
| `spotLimitConfirm` | Type-A 限价确认 preamble | `…_SPOT_LIMIT_CONFIRM` |
| `futuresMarketConfirm` | Type-A 合约市价 preamble | `…_FUTURES_MARKET_CONFIRM` |
| `futuresLimitConfirm` | Type-A 合约限价 preamble | `…_FUTURES_LIMIT_CONFIRM` |

**有效策略（每场景独立）**

| 优先级 | 条件 | 是否 narrate |
|--------|------|----------------|
| 1 | 对应 env = `true` | 是（可回落） |
| 2 | `gateway_defaults.telegramLlmNarrate.<field>=true` | 是（可回落） |
| 3 | 否则 | 否 |

## 范围

### 本期包含

- **`admin_ai_document.gateway_defaults`**：嵌套 **`telegramLlmNarrate`**；**`read_gateway_defaults_merged` / `patch_gateway_defaults`** 合并、校验与 seed 默认。
- **`telegram_bound_reply`**：9 处 **`enabled=`** 改为 **effective** 解析（读 DB merged defaults + settings env）。
- **时间线 payload**：**`effectiveTelegramLlmNarrateEnabled`**（或场景级等价键，实现统一即可）。
- **OpenAPI 增量**：本包 `api.openapi.yaml`（defaults GET/PATCH）。
- **pytest**：Admin defaults PATCH/GET 部分合并 + ticker 启用/关闭/回退/env 覆盖 + 至少 1 个 Type-A preamble 场景 + 1 个额外只读场景 spot-check。

### 本期不包含

- **Admin `/ai-settings` 页面** 九场景开关 UI（API 先行；可后续 FE 包）。
- 新增第 10+ 场景 narrate、修改 TRADING prompt 包正文或 **`chat.faq`** 链。
- **`telegram_error_llm_rewrite`**（拒单友好改写，独立 env，非 narrate 矩阵）。
- per-tenant / per-user narrate 策略。
- 将 **种子默认值** 改为全 `true`（部署策略单独决策）。

## 界面与交互

**无本期页面**（`含页面: 否`）。运营通过 **Admin API** 或后续 `/ai-settings` UI 配置。

## 非功能要求

- narrate **关闭** 时 **不增加** 网关 RTT；开启时仍受既有 LLM 超时与网关 **`timeoutSec`** 约束。
- 配置变更 **无需重启** 进程（读 DB merged defaults）。
- 日志可选增加 **`effective_telegram_llm_narrate`** 场景键便于排障。

## 待确认问题

- [x] Q1：Admin 默认是否改为全 `true`？— **否**；各字段默认 **false**，由运营显式开启。
- [x] Q2：env 与 Admin 冲突时谁优先？— **env=true 强制开启**；否则 Admin；均 false 则关闭 narrate。
- [x] Q3：是否合并为单全局开关？— **否**；保持 **9 场景独立** 与存量 env 粒度一致。
