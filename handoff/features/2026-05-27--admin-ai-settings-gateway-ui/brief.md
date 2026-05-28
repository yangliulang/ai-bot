# Admin AI 网关开关 UI

> 功能 ID：`2026-05-27--admin-ai-settings-gateway-ui`  
> 产品 Agent 定稿 · Phase-2 **P1** · Phase-1 **FE 债**（API 已由 **`nlu-llm-strategy`** / **`telegram-llm-narrate`** 交付）

## 背景

**`intentNluUseLlm`** 与 **`gateway_defaults.telegramLlmNarrate`**（9 场景）已在 **`GET/PATCH /api/v1/admin/ai/defaults`** 落库，Runtime/Telegram 按 **Admin + env 覆盖** 解析有效策略（见 **`2026-05-26--nlu-llm-strategy`**、**`2026-05-26--telegram-llm-narrate`** · **done**）。

存量 **`/ai-settings`**（**`AiSettingsPage`**）已具备 **厂商与模型**、**使用策略**（模型下拉、预算、降级等）并联调 **`patchAiGatewayDefaults`**，但 **未** 暴露 NLU / narrate 网关开关。运营仍须改环境变量，与产品「控制台可配置」目标不符。

本包在 **使用策略** Tab（**`?tab=runtime`**）内 **增量** 增加 **「网关策略」** 分区（对齐 `product-doc` 控制台信息架构），**不** 重做目录 CRUD 与模型策略表单。

## 用户故事

- 作为 **平台运营**，我希望在 **模型配置 → 使用策略** 中开关 **意图 NLU 优先 LLM**，无需部署改 **`CHAINUP_AGENT_INTENT_NLU_USE_LLM`**。
- 作为 **平台运营**，我希望按 **9 个 Telegram 场景** 单独开关 **LLM narrate / Type-A preamble**，无需改 9 条 **`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_*`**。
- 作为 **SRE**，我希望页面上 **明示 env 强制开启** 优先于 Admin 关闭项，避免误判配置未生效。

## 验收标准

- [x] **AC-1**：访问 **`/ai-settings?tab=runtime`**（或默认进入 **使用策略** Tab）时，在存量 Runtime 策略表单 **之外** 可见 **「网关策略」** 分区，含 **「意图 NLU」** 与 **「Telegram LLM 叙述」** 两个子区；页面 **无白屏**。
- [x] **AC-2**：**`GET /api/v1/admin/ai/defaults`** 加载成功后，**`intentNluUseLlm`** 开关状态与响应一致（未配置时 **false**）；**`telegramLlmNarrate`** 下 **9 个** boolean 与响应一致（未配置键视为 **false**）。
- [x] **AC-3**：仅切换 **`intentNluUseLlm`** 并保存 → **`PATCH /api/v1/admin/ai/defaults`** Body **`{ "intentNluUseLlm": true|false }`** → **200**；刷新后 GET 回显一致；成功有 **Toast**；失败展示 **`message`/`code`**。
- [x] **AC-4**：仅切换 **`telegramLlmNarrate.readMarketTicker`**（或任一合法字段）并保存 → **PATCH** 仅含该嵌套对象 → **200**；**其它 8 个 narrate 字段** 保持 PATCH 前值（与 **AC-8** 后端语义一致）；UI 刷新后与 GET 一致。
- [x] **AC-5**：**PATCH** 返回 **409**（版本冲突）或 **422**（如 catalog 校验）时，界面 **不** 静默成功；展示 API **`message`**（含已知 **`AGENT_AI_SETTINGS_VERSION_CONFLICT`** / **`AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG`** 友好文案，复用存量 **`admin-ai-settings`** 解析）。
- [x] **AC-6**：**「Telegram LLM 叙述」** 子区按 **只读行情（5）** 与 **交易确认 Type-A（4）** 分组展示；每行含 **运营中文标签** + **Admin 字段名**（小字 `readMarketTicker` 等）+ 开关；并展示 **env 覆盖说明**（至少列出 ticker 与 NLU 各 1 条代表性 env 变量名）。
- [x] **AC-7**：**「厂商与模型」** Tab（**`tab` 缺省或 `catalog`）** 与存量 **使用策略** 内模型下拉 / **保存** 行为 **不退化**（仍可 **`PATCH defaults`** 更新 `scenarioChatModel` 等字段）。
- [x] **AC-8**：**加载态**：defaults 首次加载显示 loading / 禁用保存；**保存中** 相关按钮 **submitting** 且防重复提交。

### `telegramLlmNarrate` 字段（FE 标签）

| Admin 字段 | 运营标签 | 分组 |
|------------|----------|------|
| `readMarketTicker` | 行情 · 最新价 | 只读 |
| `readMarketDepth` | 行情 · 深度 | 只读 |
| `readMarketTrades` | 行情 · 成交 | 只读 |
| `readAccountBalance` | 账户余额 | 只读 |
| `wealthHoldingsRead` | 理财持仓 | 只读 |
| `spotFlashConfirm` | 现货闪兑 · 确认前叙述 | Type-A |
| `spotLimitConfirm` | 现货限价 · 确认前叙述 | Type-A |
| `futuresMarketConfirm` | 合约市价 · 确认前叙述 | Type-A |
| `futuresLimitConfirm` | 合约限价 · 确认前叙述 | Type-A |

### 有效策略（文案须出现在 AC-6 说明区）

| 能力 | env 强制开启（优先） | Admin 字段 |
|------|---------------------|------------|
| Intent NLU LLM | `CHAINUP_AGENT_INTENT_NLU_USE_LLM=true` | `intentNluUseLlm` |
| Telegram narrate（每场景） | `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_<SCENARIO>=true` | `telegramLlmNarrate.<field>` |

## 范围

### 本期包含

- **Admin FE**：**`/ai-settings`** · **使用策略** Tab 内 **网关策略** UI（开关 + 分组 + 说明 + 保存）。
- **`admin-ai-settings.ts`** 类型扩展：**`intentNluUseLlm`**、**`TelegramLlmNarrateFlags`**（9 字段）；**`patchAiGatewayDefaults`** 复用。
- **功能包契约**：`api.openapi.yaml`（defaults 子集）、`test/*`、**`frontend/integration.md`** 计划。
- **测试**：API 回归（defaults GET/PATCH，指向前序包 pytest）+ **E2E** 主流程（见 `test/e2e-cases.md`）。

### 本期不包含

- **后端新路由或 DB 变更**（已由 **`2026-05-26--nlu-llm-strategy`** / **`telegram-llm-narrate`** 实现；本包 **backend-agent** 仅 **回归确认** + **`backend/notes.md`** 标注 N/A 或指向前序包）。
- 重做 **厂商与模型** 台账 UI、**Health 探针**、**health-policy** 编辑。
- **`POST /api/v1/agent/intent/recognize`** / Telegram webhook 的 **新** 自动化 UI 验收（仍由 API/pytest 覆盖）。
- per-tenant 策略、A/B 实验、批量导入 defaults。

## 界面与交互（含页面）

**含页面：是**。

| 入口 | 路由 | 说明 |
|------|------|------|
| 模型配置 | **`/ai-settings`** | 存量页 |
| 使用策略 + 网关 | **`/ai-settings?tab=runtime`** | 本包增量 **网关策略** 分区 |

**主流程**：进入使用策略 → 加载 defaults → 展示 NLU + 9 场景开关 → 单项或分区保存 → Toast。

**错误态**：GET 失败页内错误条；PATCH 失败 Toast + 行内/分区错误（不丢用户已改未保存状态为佳，最低要求展示 API 原因）。

**参考原型**：`product-doc/src/admin` · **`/ai-settings`** 双 Tab 结构；网关字段交互可参考 **`product-doc`** 运营文档，**数据** 以真实 API 为准。

## 非功能要求

- 单次 PATCH **仅提交变更字段**（至少 narrate 单场景保存时 **不得** 误提交未改动的 `intentNluUseLlm` 为错误值，实现可用 dirty 追踪）。
- 不写入 **localStorage** 作为策略真源；以 **GET defaults** 为准。
- 鉴权：与其它 Admin API 一致（Bearer）。

## 待确认问题

- [x] Q1：网关策略放在哪？— **使用策略 Tab 内** 独立分区（不新增侧栏路由）。
- [x] Q2：是否改后端？— **否**；`contract_ready` 后 **backend-agent** 回归确认即可 **backend_done**。
- [x] Q3：保存粒度？— **按分区或单开关保存** 均可；须满足 AC-3/AC-4 PATCH 语义。
