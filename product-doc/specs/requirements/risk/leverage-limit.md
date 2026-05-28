# Global Risk · Leverage & product-line limits

**职责**：**合约 / 杠杆产品线** 与 **运营侧杠杆/相关数值护栏** 的 **横切收口**（**配置键名与附录 A** 以 OpenAPI/登记为准）。**具体技能路径、类型 A、FR-T09/T11** → [`../domains/agent/exchange-agent/trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md)。

---

## 1. 产品线闸（Feature flags）

| 键（示意） | 下限 | SSOT |
|------------|------|------|
| **`FEATURE_AGENT_FUTURES`** | **V1 默认 OFF**；开启须与 **合规/所内** 对签 | [`keys.md` §2](../domains/admin/trading-agent-config/keys.md)、[`../domains/agent/exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md) **§3** |
| **`FEATURE_AGENT_MARGIN`** | 全仓杠杆轨道与现货分叉 | [`keys.md` §2](../domains/admin/trading-agent-config/keys.md) |
| **`FEATURE_AGENT_SPOT`** | 现货/闪兑轨道 | 同上 |

**矩阵终裁**：**`design/api` 未冻结 PATH** → **不承诺闭环** — [`../domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md) **§1**。

---

## 2. 运营护栏（杠杆与相关）

- **`AGENT_MAX_LEVERAGE`** 等 **`AGENT_*` 扩展键**：与 **`boundaries`**、旧 **`§10.5`** 映射 **同窗增补** — [`keys.md` §3 表脚注](../domains/admin/trading-agent-config/keys.md)。
- **模板 vs 全局**：运营模板风控 **只可收紧** 全局底 — [`../domains/admin/trading-agent-config/functions.md`](../domains/admin/trading-agent-config/functions.md) **§2.6**。
- **现货限价运营偏离带（`FR-T12` / `AGENT_PRICE_*`）**：流程专节 — [`../flows/trade-via-agent.md`](../flows/trade-via-agent.md)；稳定码同窗 [`../domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md)。

---

## 3. 用户侧确认串联（写前）

- **合约 / 杠杆族写路径**：**须** 完成域定义的 **`risk-disclosure`** 与 **`high-risk-confirmation`** **串联**（顺序以 **编排** 为准）— [`../prompts/trading/futures.md`](../prompts/trading/futures.md)、[`../domains/agent/agent-orchestration/confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md)。
- **类型 A**：每笔 **`call_exchange_write`** 前 **[`telegram/overview` §2.5 · 类型 A](../domains/agent/telegram/overview.md)**（总则 §2～§2.6）— [`../../design/adr/001-telegram-confirm-before-coobit-write.md`](../../design/adr/001-telegram-confirm-before-coobit-write.md)。

---

## 4. 互引

| 文档 | 关系 |
|------|------|
| [`../prompts/safety/illegal-request.md`](../prompts/safety/illegal-request.md) | **禁止**话术隐蔽抬杠杆、绕过确认 |

---

**文档版本**：0.2.1 · **维护**：产品 + 风控 owner · **本版**：**类型 A** 描点至 **[`telegram/overview` §2.5](../domains/agent/telegram/overview.md)**；**承 0.2.0**。
