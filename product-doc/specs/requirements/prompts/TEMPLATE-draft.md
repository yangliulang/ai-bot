# Prompt 草稿（MR）

> **禁止**：Secret、API Key、Cookie、用户隐私。**线上 SSOT**：[`prompt-management`](../domains/admin/prompt-management/overview.md)。

---

## 元数据

| 键 | 值 |
|----|-----|
| **MR 标题 / 背景** | （一句话） |
| **落点** | `system` \| `intents` \| `trading` \| `analysis` \| `confirmation` \| `safety` \| `shared`（见 [`README` §1](./README.md)） |
| **`scenarioId`/skill（若挂钩）** | [`routing-engine`](../domains/agent/agent-orchestration/routing-engine.md)、[`trade-assistance` §8](../domains/agent/exchange-agent/trade-assistance.md) |
| **Telegram** | 是否改卡片模板 / `callback_data` 字段 → [`telegram/overview` §2.5 · 类型 A；§2～§2.6](../domains/agent/telegram/overview.md) |

---

## 正文

完整 **`body`** 默认只在 **`prompt-management`** 编辑器维护；Git **仅**条文/大纲。

---

## 自检

- [ ] **运营包映射**：先查 [`governance-map.md`](./governance-map.md) · [`product/prompt-governance-checklist.md`](../../../product/prompt-governance-checklist.md) — **改 Publish 正文** 走 **六段**（Demo：[`promptBodyTemplates.ts`](../../../src/admin/src/data/promptBodyTemplates.ts)），**Git 条文** 仅作评审下限  
- [ ] **文档版本约定**：根 [`README`](./README.md)（索引 `1.x.0` vs 条文 `1.x.0-mvp`）  
- [ ] **System**：[`system/README.md`](./system/README.md) · [`system/system.md`](./system/system.md)（读优先 / 步骤序 / §5 观测）；横切 **`pp-runtime-clarify` / `pp-runtime-output-contract`** 见 governance-map §2  
- [ ] **意图分流**：[`intents/README.md`](./intents/README.md) ↔ [`exchange-agent/intents`](../domains/agent/exchange-agent/intents.md)（**不**各发 `pp-intent-*`）  
- [ ] [`confirmation/order-confirmation.md`](./confirmation/order-confirmation.md) **类型 A** 无弱化表述（**无**独立 `promptPackId`）  
- [ ] **Safety**：[`safety/README.md`](./safety/README.md)；线上 **`pp-safety-global`**；[`runtime-injection` §7.1](../domains/admin/prompt-management/runtime-injection.md)  
- [ ] **Shared**：[`shared/README.md`](./shared/README.md) · [`glossary`](./shared/glossary.md) · [`response-format`](./shared/response-format.md) · [`common-phrases`](./shared/common-phrases.md)  
- [ ] **UNKNOWN**：[`unknown-state`](../Runtime/unknown-state.md) 话术 **不**夸大全成功/全失败  
- [ ] 若改 **`analysis/`**：**禁止**拆多运营包；Publish **仅** `pp-analysis-core`；[`analysis/README.md`](./analysis/README.md) 四分卷 = Git 能力语义  
- [ ] 若改 **`trading/`**：**写路径** 对照 governance-map §3 **`scenarioId` → `pp-trading-*`**；[`buy.md`](./trading/buy.md) / [`sell.md`](./trading/sell.md) **≠** 须各发独立包  

---

**模板版本**：1.2.0 · **对齐**：[`README`](./README.md) §1 · [`governance-map`](./governance-map.md)。
