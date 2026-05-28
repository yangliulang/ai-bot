# Prompt Library · 拼装契约（默认）

**路径**：`specs/requirements/prompts/library/ASSEMBLY.md`。  
**对上实现**：[`runtime-injection`](../../domains/admin/prompt-management/runtime-injection.md) **占位符 denylist / Assembly** **须** **同窗或显式 OVERRIDE**。

---

## 1. 默认拼接顺序（自上而下）

**会话首轮或重置上下文后**，建议按下列顺序拼接为 **单一 SYSTEM**（或等价多段 SYSTEM + developer）；**用户消息 / 工具结果** **不入 SYSTEM**。

| 序号 | 片段文件 | 说明 |
|------|-----------|------|
| **L1** | [`packs/core-runtime-root.{locale}.md`](./packs/core-runtime-root.zh-CN.md) | **必选** · 身份 / 工具铁闸 / 禁止项 |
| **L2** | **错误对用户可见**：`effective_locale` **非 `en`** → [`fragment-errors-user-visible.zh-CN.md`](./packs/fragment-errors-user-visible.zh-CN.md)；**`en` 桶** → [`fragment-errors-user-visible.en.md`](./packs/fragment-errors-user-visible.en.md) | **必选**：① **[`registry`](./scenarios/registry.md)** 配方含 **E** 之 **`scenarioId`**；② **任意可能调用交易所/网关/计费依赖工具** 之会话（典型：**IT / IM + 写路径**）。**仅**「永不触工具之纯闲聊预热」可省略 — **上线默认建议始终带上**，由 **`prompt-management`** **按包裁剪**。 |
| **L3** | **Safety**：非 `en` → [`fragment-safety.zh-CN.md`](./packs/fragment-safety.zh-CN.md)；**`en`** → [`fragment-safety.en.md`](./packs/fragment-safety.en.md) | **必选**（可与 L1 合并维护，发布时拆开亦可） |
| **L4** | **意图桥**：非 `en` → [`fragment-intent-{trade|analysis|monitoring}.zh-CN.md`](./packs/fragment-intent-trade.zh-CN.md) **族**；**`en`** → 同名 [`fragment-intent-*.en.md`](./packs/fragment-intent-trade.en.md) | 按 Orchestration 分流 **三选一** |
| **L5** | **类型 A**：非 `en` → [`fragment-confirmation-type-a.zh-CN.md`](./packs/fragment-confirmation-type-a.zh-CN.md)；**`en`** → [`fragment-confirmation-type-a.en.md`](./packs/fragment-confirmation-type-a.en.md) | **`scenarioId` 命中任意写路径** **必选** |
| **L6** | **场景加深** — 见 [`scenarios/registry.md`](./scenarios/registry.md) **「延展条文」** | 指向 [`../trading/`](../trading/)、[`../analysis/`](../analysis/) **等** Markdown **条文**（运行时可选注入摘要） |

**英文桶（`effective_locale` / EN bucket）**：**L1** = [`core-runtime-root.en.md`](./packs/core-runtime-root.en.md)；**L2～L5** = 同名 **`*.en.md`**（[`packs/`](./packs/)）。**简中 / 繁中基底**：**L1** + **`*.zh-CN.md`** 片段。

**冷启动整段粘贴（仅 L1+L2+L3）**：[`INITIAL_SYSTEM.zh-CN.md`](./INITIAL_SYSTEM.zh-CN.md)、[`INITIAL_SYSTEM.en.md`](./INITIAL_SYSTEM.en.md) — **与** 上表 **前三段正文同窗**；**不得**替代 **`packs/`** 为 SSOT；改字须先改 **`packs/*.md`** 再同步该二文件。

---

**默认触点**：**用户问题在 Telegram 内解决** — [`shared/response-format` §1](../../shared/response-format.md)。**主站 Deeplink** **仅** 在上下文 **`requires_main_site`** **且** 与 [`exchange-agent/boundaries`](../../domains/agent/exchange-agent/boundaries.md) **一致时出现**。

---

## 2. 占位符（运行时注入 · 示意）

**键名下限（`user_visible_message` / `requires_main_site`）**：[`runtime-injection` §2.4](../../domains/admin/prompt-management/runtime-injection.md)。

| 占位符 | 含义 |
|--------|------|
| `{{effective_locale}}` | `zh-Hans` / `zh-Hant` / `en` **三桶之一** — [`telegram/overview` §2.4](../../domains/agent/telegram/overview.md) |
| `{{scenario_id}}` | 当前 **`scenarioId`** — [`routing-engine` §1～§4](../../domains/agent/agent-orchestration/routing-engine.md) |
| `{{execution_id}}` | 若有 **须告知用户协查** **时出现** |
| `{{prompt_pack_version}}` | 观测对齐 — [`observability/overview` §2.3](../../observability/overview.md) |
| **`context.user_visible_message`**（示意） | 编排已定稿用户可见句：模型 **保持事实走向**，仅按 **`{{effective_locale}}`** 润色 — 同窗 **L2 错误片段** |
| **`context.requires_main_site`**（示意） | **`true`** 且与 **`exchange-agent/boundaries`** **冻结一致** → **本条末尾** **方可**附官方 Deeplink — [`response-format` §1](../../shared/response-format.md) |

**块 5 · Runtime Context（不入 SYSTEM 正文 · 示意键）** — [`runtime-injection` §2.4.1](../../domains/admin/prompt-management/runtime-injection.md)：

| 键（示意） | 典型 `scenarioId` | 说明 |
|------------|-------------------|------|
| **`userVisibleMarketData`** | **`market.read_quote`** 等 | **须含 **`lastPrice`**（**§3.3**） |
| **`marketInsightData`** / **`marketNarrativeHints`** | **`market.read_deep_analysis`**、`futures.read_funding` | **phase/hints 草案 · Facts 优先** |
| **`semanticNarrativeBlock`** | **记忆管理意图**（**LTM · 默认 OFF**） | **同窗** [`memory-runtime-schemas`](../../../../openapi/components/memory-runtime-schemas.yaml) |

**禁止**：向 SYSTEM 注入 **Secret**、**完整 API Key**、**用户 Cookie** — [`TEMPLATE-draft`](../TEMPLATE-draft.md)。

---

## 3. Few-shot 与对白库

**本仓库** **不提供** 长 Few-shot **混入 L1 SYSTEM**；**ANALYSIS 包 Few-shot** **Git 镜像** → [`packs/fewshot-narrative-analysis.zh-CN.md`](./packs/fewshot-narrative-analysis.zh-CN.md)（**`en`** → [`.en.md`](./packs/fewshot-narrative-analysis.en.md)）— **须** **[`prompt-management`](../../domains/admin/prompt-management/overview.md) Publish** **才生效**（**FR-PM05 §2.5.1**）。**评审索引** → [`analysis/narrative-few-shot-specimens.md`](../analysis/narrative-few-shot-specimens.md)。

**市场叙事锚**（**非 Trader Phrase Library**）→ [`shared/common-phrases` §8](../shared/common-phrases.md)；**体系** → [`market-intelligence` §4](../../domains/agent/exchange-agent/market-intelligence.md)；**Runtime hints 草案** → [`market-runtime-payload` §3.4](../../domains/agent/exchange-agent/market-runtime-payload.md)。**禁止** **`TRADER_PHRASE`** **类 **`promptPackKind`**。

---

**文档版本**：1.0.9 · **维护**：产品 + Prompt owner · **本版**：**§3 ANALYSIS Few-shot Git 镜像路径**。**承** 1.0.8。
