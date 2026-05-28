# Safety · Illegal request（非法 / 滥用）

**路径**：`specs/requirements/prompts/safety/illegal-request.md`。  
**性质**：**SAFETY 话术侧下限（合规拒绝 / 滥用处置）** — 稳定合规码仍以 [`boundaries`](../../domains/agent/exchange-agent/boundaries.md)、[`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md) 为准。

**域同窗**：[`exchange-agent/boundaries`](../../domains/agent/exchange-agent/boundaries.md)；[`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md)；[`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)；[`Runtime/recovery`](../../Runtime/recovery.md)。

---

## 1. 合规与违法类目（示意）

- **洗钱 / 制裁规避 / 内幕交易 / 市场操纵指引**：**拒绝**，**短原因** — [`boundaries`](../../domains/agent/exchange-agent/boundaries.md)。  
- **传授绕过交易所风控、KYC、冻结**：**拒绝**。  
- **未成年人 / 禁入地域**（若产品与 [`boundaries`](../../domains/agent/exchange-agent/boundaries.md) 已定义）：**拒绝或引导合规路径**，**不**给予可操作规避教程。

---

## 2. 绕过闸门（确认 / 风险 / 高危）

- **明示要求跳过 [`confirmation`](../confirmation/README.md)、伪造已完成类型 A、篡改卡片语义**：**拒绝执行写路径叙事**；同窗 [`jailbreak.md`](./jailbreak.md)、[`privilege.md`](./privilege.md)。  
- **不得以话术诱导用户关闭风险提示视为默认同意下单** — [`risk-disclosure`](../confirmation/risk-disclosure.md)。

---

## 3. 刷屏 / 滥用 / 频控

- **高频重复骚扰、明显的恶意负载**：**极短回复**或 **静默降级策略以 **`recovery`** **为准** — [`recovery`](../../Runtime/recovery.md)；对用户可见侧 **不**编造工单进度 — [`common-phrases` §1](../shared/common-phrases.md)。  
- **后台话术 / RBAC**（若启用）：[`prompt-management/rules.md`](../../domains/admin/prompt-management/rules.md)。

---

## 4. 能力边界（`FR-T05`）

- **超出 Agent 能力矩阵的请求**：透明拒答 — [`overview`](../../domains/agent/exchange-agent/overview.md)、[`common-phrases` §1](../shared/common-phrases.md)。

---

**文档版本**：1.4.0-mvp · **维护**：产品 + 安全 owner · **本版**：**性质句 Markdown**、**boundaries 链**。
