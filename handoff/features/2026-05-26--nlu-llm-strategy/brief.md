# NLU LLM 默认策略

> 功能 ID：`2026-05-26--nlu-llm-strategy`  
> 产品 Agent 定稿 · **`done`**（product.accept 2026-05-26）

## 背景

Phase-1 已交付 **`POST /api/v1/agent/intent/recognize`** 与 Telegram 内联 **`recognize_intent_full`**：默认 **`keyword_v1`**，仅当运维将环境变量 **`CHAINUP_AGENT_INTENT_NLU_USE_LLM=true`** 时才尝试 **LLM JSON 草案**（**`llm_structured_v1`**，失败回退关键词）。运营无法在 **Admin 网关配置** 中切换策略，生产默认仍为关键词 MVP。本功能将 **「是否优先 LLM 意图 NLU」** 纳入 **`gateway_defaults`** 可配置项，并与既有 env 覆盖、回退语义对齐。

## 用户故事

- 作为 **平台运营**，我希望在 **AI 网关默认配置** 中打开「意图 NLU 优先 LLM」，以便无需改部署环境变量即可升级识别策略。
- 作为 **SRE**，我希望保留 **`CHAINUP_AGENT_INTENT_NLU_USE_LLM`** 作为紧急开关，覆盖 Admin 配置。
- 作为 **交易员（TG/HTTP）**，当 LLM 暂不可用时，我仍能得到 **关键词回退** 的识别结果，而不是 5xx。

## 验收标准

- [x] **AC-1**：**`gateway_defaults`** 持久化字段 **`intentNluUseLlm`**（boolean）；**`GET /api/v1/admin/ai/defaults`** 返回该字段；**`PATCH`** 可更新且 **If-Match** 语义与存量 defaults 一致；**未配置时默认 `false`**（向后兼容）。
- [x] **AC-2**：当 **有效策略为启用 LLM**（见下表）且 DB 会话 + Admin 网关 catalog/model 可用时，**`POST /api/v1/agent/intent/recognize`** 对代表性 utterance 返回 **`nlu.source=llm_structured_v1`**（或顶层 **`nluSource`** 同值）。
- [x] **AC-3**：当启用 LLM 但网关不可用、传输失败、JSON 解析失败或 registry 拒绝草案时，**HTTP 200**，**`nlu.source=keyword_v1`**（回退），**不得** 因 NLU 失败返回 5xx。
- [x] **AC-4**：当 **有效策略为关闭 LLM** 时，**不** 调用 **`try_llm_intent_nlu_draft`**，响应 **`nlu.source=keyword_v1`**。
- [x] **AC-5**：**`CHAINUP_AGENT_INTENT_NLU_USE_LLM=true`** 时 **强制尝试 LLM**（在 AC-3 回退规则下），**即使** **`gateway_defaults.intentNluUseLlm=false`**；**env 未显式开启** 时以 Admin 字段为准。
- [x] **AC-6**：**`POST …/intent/recognize`** 响应新增 **`effectiveIntentNluUseLlm`**（boolean），表示本请求是否 **已进入 LLM 尝试分支**（与 timeline **`intentNluLlmEnabled`** 一致）。
- [x] **AC-7**：Telegram **已绑定** 文本回合与 HTTP 共用 **`recognize_intent_full`**；时间线 **`prompt.snapshot`** payload 中 **`intentNluLlmEnabled`** 为 **effective** 值（非仅 env 原始值）。
- [x] **AC-8**：**`PROMPT_INJECTION_FORBIDDEN`**（intent NLU 组装）时 **跳过 LLM**、回退 **`keyword_v1`**，**HTTP 200**（回归，不落 4xx）。

### 有效策略（优先级）

| 优先级 | 条件 | 是否尝试 LLM |
|--------|------|----------------|
| 1 | `CHAINUP_AGENT_INTENT_NLU_USE_LLM=true` | 是（可回退） |
| 2 | `gateway_defaults.intentNluUseLlm=true` | 是（可回退） |
| 3 | 否则 | 否 |

## 范围

### 本期包含

- **`admin_ai_document.gateway_defaults`**：字段 **`intentNluUseLlm`**；**`read_gateway_defaults_merged` / `patch_gateway_defaults`** 合并与校验。
- **`recognize_intent_full`**：按上表解析 **effective**；传入 **`try_llm_intent_nlu_draft`** 条件。
- **`IntentRecognizeResponse`**：**`effectiveIntentNluUseLlm`**；**`telegram_bound_reply`** timeline 字段对齐。
- **OpenAPI 增量**：本包 `api.openapi.yaml`（defaults + intent/recognize）。
- **pytest**：Admin defaults PATCH/GET + intent recognize 启用/关闭/回退/ env 覆盖。

### 本期不包含

- **Admin `/ai-settings` 页面** 开关与文案（API 先行；可后续 FE 包）。
- 修改 **`agent.runtime.intent_nlu`** 提示词正文或场景注册表。
- per-tenant / per-user NLU 策略、A/B 实验框架。
- 将 **种子默认值** 改为 `intentNluUseLlm=true`（部署策略单独决策，本包仅支持字段）。
- Telegram **全场景** narrate 扩面（见 `2026-05-26--telegram-llm-narrate`）。

## 界面与交互

**无本期页面**（`含页面: 否`）。运营通过 **Admin API** 或后续 `/ai-settings` UI 配置。

## 非功能要求

- 未启用 LLM 时 **不增加** 网关 RTT；启用时超时仍受 **`INTENT_NLU_LLM_TIMEOUT_SEC`** 与网关 **`timeoutSec`** 较小值约束。
- 配置变更 **无需重启** 进程（读 DB merged defaults）。
- 日志：保留 **`intent_nlu_llm_skip`** / **`intent_nlu_llm_ok`**；可选增加 **`effective_intent_nlu_use_llm`** 字段便于排障。

## 待确认问题

- [x] Q1：Admin 默认是否改为 `intentNluUseLlm=true`？— **否**；字段默认 **false**，由运营显式开启。
- [x] Q2：env 与 Admin 冲突时谁优先？— **env=true 强制开启**；否则 Admin；均 false 则 keyword。
