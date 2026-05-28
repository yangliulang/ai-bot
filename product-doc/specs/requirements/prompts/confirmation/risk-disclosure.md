# Confirmation · Risk disclosure（风险提示）

**路径**：`specs/requirements/prompts/confirmation/risk-disclosure.md`。  
**性质**：**Prompt 侧下限** — **非**法务意见书模板；插入步骤序（相对类型 A）以 [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)、[`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md) 为准。

**域 SSOT**：[`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)、[`exchange-agent/boundaries`](../../domains/agent/exchange-agent/boundaries.md)、[`trade-assistance` §2](../../domains/agent/exchange-agent/trade-assistance.md)、[`telegram/overview` §2.5 · 类型 A；总则 §2～§2.6](../../domains/agent/telegram/overview.md)、[`ADR-001`](../../../design/adr/001-telegram-confirm-before-coobit-write.md)。

---

## 1. 触发（示意）

| 场景（示意） | 裁决参考 |
|--------------|-----------|
| **杠杆 / 合约 / 调整保证金或模式** | [`boundaries`](../../domains/agent/exchange-agent/boundaries.md)、路由枚举 |
| **强平价 proximity / 清算风险提醒型文案** | [`risk-alerts`](../../domains/agent/exchange-agent/risk-alerts.md)、域 Policy |
| **大额**（阈值由 **产品与路由** 定义） | [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)、[`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md) |
| **首次开通某类交易权限 / 首次合约路径** | [`onboarding`](../../domains/agent/onboarding/overview.md)、[`boundaries`](../../domains/agent/exchange-agent/boundaries.md) |

**不在 MVP 硬编码阈值**：以 [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)、[`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md) 为准。

---

## 2. Prompt 侧下限

- **可读摘要**：亏损可能、强平机制 **概述**（**非**法律意见书）；篇幅受 Telegram **分段与按钮**约束 — [`telegram/overview` §2～§2.6、§2.5.x](../../domains/agent/telegram/overview.md)、[`interaction-flow-standard`](../../standards/interaction-flow-standard.md)。  
- **披露 ≠ 授权**：「我已知晓风险」类按钮/话术 **不得**与「确认下单」**同一文案混淆** — 同窗 [`order-confirmation.md`](./order-confirmation.md) §1。  
- **披露 ≠ 订单摘要**：**禁止**用风险披露 **代替** **交易对 / 数量 / 方向** 的可读重复；订单字段仍以 [`order-confirmation`](./order-confirmation.md) 为准。  
- **数字与事实（防幻觉）**：强平价、爆仓距离、保证金率、预估亏损金额、费率等 **须有**交易所或编排侧 **可查事实**；若无闭环数据，**只可定性**或 **标明「示意、非实时」**，**禁止捏造精确数值或伪造监管结论** — [`hallucination`](../../observability/hallucination.md)。  
- **语言**：可与用户语言一致；合规敏感句须与 [`prompt-management/rules.md`](../../domains/admin/prompt-management/rules.md)（Prompt 域 RBAC，若启用）同窗。

---

## 3. 与高危二次确认 / 类型 A（同窗）

- **高危路径**须叠加 [`high-risk-confirmation.md`](./high-risk-confirmation.md)，**顺序**以 [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md) **为准**。  
- **与类型 A 摘要可对账**：披露中的 **定量表述**（若有）**不得与** [`order-confirmation`](./order-confirmation.md) §1 摘要、§4 **冲突** — [`hallucination`](../../observability/hallucination.md)。

---

## 4. 用户跳过 / 未完成披露

- **产品规定须读完/点选才可继续**：编排 **应阻塞写路径**，话术 **不**暗示「已默认勾选」— 同窗 [`trade-assistance` §2](../../domains/agent/exchange-agent/trade-assistance.md)。  
- **用户明确放弃**：**终止写**；可见话术同窗 [`shared/common-phrases` §3](../shared/common-phrases.md)。

---

**文档版本**：1.5.1-mvp · **维护**：产品 + Prompt owner · **本版**：**域 SSOT / §2** **链** **`telegram/overview` §2.5；§2～§2.6**；**承** 1.5.0。
