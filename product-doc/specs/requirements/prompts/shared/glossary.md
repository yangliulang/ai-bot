# Shared · Glossary（术语锚）

**路径**：`specs/requirements/prompts/shared/glossary.md`。  
**性质**：**Prompt / Runtime 拼装评审用薄表** — **非**产品百科；条目缺省请回 **`domains`** / **`routing-engine`** / **`prompt-management`**。

**索引**：[`README`](./README.md)

---

## 表

| 术语 | 指向 |
|------|------|
| **类型 A / 确认** | [`confirmation/order-confirmation.md`](../confirmation/order-confirmation.md)、[`confirmation/README`](../confirmation/README.md)、[`telegram/overview` §2.5 · 类型 A；§2～§2.6](../../domains/agent/telegram/overview.md) |
| **`scenarioId`** | [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md) |
| **`promptPackVersion` / `promptPackId`** | [`prompt-management/functions`](../../domains/admin/prompt-management/functions.md)、[`config`](../../domains/admin/prompt-management/config.md) |
| **`resolvedPromptBinding` / 冻结** | [`runtime-injection`](../../domains/admin/prompt-management/runtime-injection.md) **PM-C10 · §7.1** |
| **子账户 / Agent scope** | [`exchange-agent/overview` FR-T01/T02](../../domains/agent/exchange-agent/overview.md)、[`onboarding/overview`](../../domains/agent/onboarding/overview.md) |
| **`executionId`** | [`consume-and-bill`](../../flows/consume-and-bill.md)、[`execution-lifecycle`](../../domains/agent/agent-orchestration/execution-lifecycle.md) |
| **UNKNOWN（504/终态不明）** | [`unknown-state`](../../Runtime/unknown-state.md) |
| **`FR-T05`（透明拒答）** | [`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md) |
| **`call_exchange_write`** | [`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md)、[`design/api`](../../../design/api.md) **登记** |
| **`analysis/` 四分卷** | [`../analysis/README.md`](../analysis/README.md)；[`../intents/analysis.md`](../intents/analysis.md) |
| **`trading/` 四场景** | [`../trading/README.md`](../trading/README.md)；[`../intents/trade.md`](../intents/trade.md)；写侧同窗 [`buy.md`](../trading/buy.md) |
| **`intents/`** | [`../intents/README.md`](../intents/README.md) |
| **`safety/`** | [`../safety/README.md`](../safety/README.md)；[`runtime-injection` §7.1](../../domains/admin/prompt-management/runtime-injection.md) |
| **`confirmation/`** | [`../confirmation/README.md`](../confirmation/README.md) |
| **`system/`**（Runtime Root） | [`../system/README.md`](../system/README.md)、[`system.md`](../system/system.md) |
| **`shared/`**（术语 / 格式 / 话术锚） | [`README`](./README.md) |
| **Trader Phrase Library（非 SSOT · 禁升格）** | **不存在独立卷** — **市场叙事** → [`common-phrases` §8](./common-phrases.md)；**体系** → [`market-intelligence` §4](../../domains/agent/exchange-agent/market-intelligence.md) |
| **Market Narrative System** | [`market-intelligence` §4](../../domains/agent/exchange-agent/market-intelligence.md)；锚句 [`common-phrases` §8](./common-phrases.md)；Runtime [`market-runtime-payload` §3.4](../../domains/agent/exchange-agent/market-runtime-payload.md) |
| **Trader Narrative Anchors** | [`common-phrases` §8](./common-phrases.md) |

---

**文档版本**：1.10.0-mvp · **维护**：产品 + Prompt owner · **本版**：**Market Narrative / Trader Phrase 别名映射**。**承** 1.9.1。
