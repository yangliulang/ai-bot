# Confirmation · Order（下单确认 · 类型 A）

**路径**：`specs/requirements/prompts/confirmation/order-confirmation.md`。  
**性质**：**Prompt 侧下限** — **非**线上卡片模板正文 SSOT；卡片字段与步骤序以 **域文档 + `prompt-management` 发布**为准。

**域 SSOT**：[`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md)（步骤序）、[`trade-assistance` §2](../../domains/agent/exchange-agent/trade-assistance.md)（`FR-T09`/`FR-T11`、`SC-TA*`）、[`telegram/overview` §2.5 · 类型 A（§2.5.x）；**§2.5.0a · 正文格式与设计规格**；总则 §2～§2.6](../../domains/agent/telegram/overview.md)、[`ADR-001`](../../../design/adr/001-telegram-confirm-before-coobit-write.md）。  
**拼装 / 冻结**：[`runtime-injection`](../../domains/admin/prompt-management/runtime-injection.md)（`resolvedPromptBinding`、Safety §7.1）。

---

## 1. Prompt 侧下限（成交前）

- **步骤序**：**类型 A** 须发生在 `call_exchange_write` **之前** — [`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md)；具体 **`scenarioId`** 步骤展开以 [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)、[`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md) 为准。  
- **任何写交易**须在用户侧完成 **类型 A**（卡片按钮 / `callback_data` 等可审计动作）后再触发写工具。  
- **确认前摘要**：卡片或紧随话术须 **可读重复关键字段**（交易对、方向、数量/名义、价格类型（若适用）、预估费用如可得）；手续费等 **若无接口事实不得捏造** — [`hallucination`](../../observability/hallucination.md)。  
- **偏离带 / 槽位**：摘要须与 Planner **已校验参数一致**，**不**在确认文案中悄悄改写用户意图 — 同窗 [`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md) 之 `FR-T07` / `FR-AO02`（步骤见 [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)）。  
- **卡片字段与回调**须在 Telegram `callback_data` **上限内可序列化** — [`telegram/overview` §2.5.x、§2.5.0a、§2.6](../../domains/agent/telegram/overview.md)。

---

## 2. 超时 / 失效 / 重复点击 / UNKNOWN

- **超时**：引导 **重新发起**或 **安全终止**，**不**声称旧确认仍生效 — [`Runtime/recovery`](../../Runtime/recovery.md)。  
- **重复提交**：编排层须 **幂等**（[`system/system.md`](../system/system.md) §3）；话术侧 **不**鼓励「连点加速成交」。  
- **确认态不明（UNKNOWN）**：**不**推断用户已确认；同窗 [`Runtime/unknown-state`](../../Runtime/unknown-state.md)、[`error-normalization`](../../Runtime/error-normalization.md)。  
- **会话 / Deeplink**：绑定与会话恢复同窗 [`Runtime/sessions`](../../Runtime/sessions.md)、[`onboarding/telegram-binding`](../../domains/agent/onboarding/telegram-binding.md)。

---

## 3. 用户拒绝 / 中止

- **用户在类型 A 上点「取消」或未在规定时间内确认**：**终止写路径**，**不**触发 `call_exchange_write`；可见话术 **短因 + 可再发起** — [`shared/common-phrases` §3](../shared/common-phrases.md)。

---

## 4. 与风险揭示 / 高危二次确认（数字口径同窗）

- **风险披露**（[`risk-disclosure.md`](./risk-disclosure.md)）**不能**替代类型 A；两者 **可串联**，**不可**合并为静默授权。披露中出现的强平、保证金、费率、预估亏损等数字约束，同窗 [`risk-disclosure`](./risk-disclosure.md) §2「数字与事实」。  
- **高危二次确认**（[`high-risk-confirmation.md`](./high-risk-confirmation.md)）中的金额 / 张数 / 杠杆 **须与本条 §1 确认前摘要可对账** — 同窗 [`high-risk-confirmation`](./high-risk-confirmation.md) §1「数字一致性」。  
- **顺序与是否必经**：以 [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)、[`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md) 为准；幻觉底线见 [`hallucination`](../../observability/hallucination.md)。

---

**文档版本**：1.5.2-mvp · **维护**：产品 + Prompt owner · **本版**：**域 SSOT** 增补链向 **`telegram/overview` §2.5.0a**。**承** 1.5.1-mvp。
