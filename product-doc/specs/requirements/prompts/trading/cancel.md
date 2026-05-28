# Trading · Cancel（条文）

**路径**：`specs/requirements/prompts/trading/cancel.md`。  
**性质**：**写路径 Prompt 下限（撤单）** — Publish [`prompt-management`](../../domains/admin/prompt-management/overview.md)。

**索引**：[`README`](./README.md)

> **Publish 正文**：[`governance-map.md`](../governance-map.md)（改单/撤单场景见 `pp-trading-*-amend` 等）。**本文**为 Git **评审下限**，**勿**抄 API/FR 进六段运营正文。

**域宿主**：[`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)；[`trade-assistance` §2·§8](../../domains/agent/exchange-agent/trade-assistance.md)；[`order-confirmation`](../confirmation/order-confirmation.md)。

---

## 1. 前置

- **取消对象可解析**：**订单 ID** 优先；否则 **交易对 + 方向 + 可区分价位/时间** 等 **唯一定位**，不足则 **澄清**。  
- **类型 A**：撤单仍为写路径 — 须满足 [`order-confirmation`](../confirmation/order-confirmation.md) 与 [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md) 的步骤定义；不得以 MVP 话术绕过。若路由特例豁免，须有 [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md) 与 [`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md) **明文**。

---

## 2. 执行下限

- **幂等 / 重复撤同一单**：以编排 **`executionId`** / 交易所语义为准，**不**催促用户「连点撤单」— [`system/system` §3](../system/system.md)。  
- **无成功闭环**不得声称已撤 — [`unknown-state`](../../Runtime/unknown-state.md)、[`hallucination`](../../observability/hallucination.md)。  
- **工具**：仅登记 `toolId`/skill — [`trade-assistance` §8](../../domains/agent/exchange-agent/trade-assistance.md)。

---

## 3. 终端态

- **已成交 / 不存在 / 已撤**：**如实转述**归一结果，**引导**查挂单或历史 — [`error-normalization`](../../Runtime/error-normalization.md)。

---

## 4. 其它同窗

- **与分析分流 / 防幻觉 / UNKNOWN**：同窗 [`buy.md` §4](./buy.md)；[`shared/common-phrases` §2](../shared/common-phrases.md)。

---

**Publish**：同窗 [`prompt-management/config`](../../domains/admin/prompt-management/config.md)。

**文档版本**：1.4.0-mvp · **维护**：产品 + Prompt owner · **本版**：**性质**、**撤单类型 A**、**幂等**。
