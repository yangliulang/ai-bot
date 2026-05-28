# Confirmation · High-risk（高风险二次确认）

**路径**：`specs/requirements/prompts/confirmation/high-risk-confirmation.md`。  
**性质**：**Prompt 侧下限** — **须在 UX 上与「普通类型 A」显著区分**；高危枚举以路由与 [`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md) 为准。

**域 SSOT**：[`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)、[`exchange-agent/boundaries`](../../domains/agent/exchange-agent/boundaries.md)、[`trade-assistance` §2](../../domains/agent/exchange-agent/trade-assistance.md)、[`telegram/overview` §2.5 · 类型 A；总则 §2～§2.6](../../domains/agent/telegram/overview.md)。

---

## 1. Prompt 侧下限

- **高危路径**（合约开仓、提高杠杆、大额市价、全仓清仓语义等 — **以产品与路由枚举为准**）须 **与普通类型 A 文案/按钮语义显著不同**（**禁止**仅换皮肤同色同质文案），避免惯性点击 — [`interaction-flow-standard`](../../standards/interaction-flow-standard.md)、[`telegram/overview` §2.5.x · 类型 A；§2.6](../../domains/agent/telegram/overview.md)。  
- **二次确认**须包含 **关键数字重复**（金额 / 张数 / 杠杆 **至少一类**），**禁止**「一键全同意」笼统话术 — [`system/system.md`](../system/system.md) **§4**。  
- **数字一致性（防幻觉）**：卡片展示的 **金额 / 合约张数 / 杠杆倍数** **须与**类型 A 摘要及路由解析 **可对账** — [`hallucination`](../../observability/hallucination.md)；同窗 [`order-confirmation.md`](./order-confirmation.md) **§1·§4**。  
- **不得**暗示跳过 [`order-confirmation.md`](./order-confirmation.md) **整条确认链**。  
- **与风险披露串联**：若本条前序存在 [`risk-disclosure`](./risk-disclosure.md)，**数字与结论不得与之矛盾** — [`risk-disclosure` §3](./risk-disclosure.md)。

---

## 2. 失败 / 回退 / 超时

- **用户拒绝第二次确认**：**终止写路径**，**清除**半确认状态，**不**允许「跳过高危直接成交」— [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)。  
- **超时 / 会话漂移**：同窗 [`order-confirmation` §2](./order-confirmation.md)、[`Runtime/recovery`](../../Runtime/recovery.md)；**UNKNOWN** [`unknown-state`](../../Runtime/unknown-state.md)。

---

## 3. 拼装与冻结（同窗）

- **会话内 Prompt 绑定冻结**（**不得**在确认中途静默换包）— [`runtime-injection`](../../domains/admin/prompt-management/runtime-injection.md) **PM-C10 / Safety §7.1**。

---

**文档版本**：1.5.1-mvp · **维护**：产品 + Prompt owner · **本版**：**域 SSOT / §1** **`telegram/overview` §2.5；§2～§2.6**；**承** 1.5.0-mvp。
