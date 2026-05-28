# Global Risk · Symbol restriction

**职责**：**可交易品种**（allowlist/blocklist）与 **限价相对参考价之运营偏离带** 的 **横切收口**。**稳定码在用户侧的叫法** 以 [`../domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md) **§2** 与 [`../flows/trade-via-agent.md`](../flows/trade-via-agent.md) **为准**。

---

## 1. 配置键（下限）

| `configKey` | 说明 | SSOT |
|-------------|------|------|
| **`SYMBOL_POLICY_MODE`** | **allowlist / blocklist**（枚举 **`design` 终裁**） | [`keys.md` §3](../domains/admin/trading-agent-config/keys.md) |
| **`SYMBOL_ALLOWLIST`** | 可执行写之 **symbol 列表** | 同上 |
| **`SYMBOL_BLOCKLIST`** | 可选并行 **黑名单** | 同上 |

**高危运营动作**：如 **清空 `SYMBOL_ALLOWLIST`** → **二次确认** + 可选 **双人审批** — [`../domains/admin/trading-agent-config/flow.md`](../domains/admin/trading-agent-config/flow.md) **§1**。

---

## 2. 限价偏离带（价格护栏）

| 稳定码 / 主题 | 触发（概念） | 用户侧 |
|----------------|-------------|--------|
| **`PRICE_REJECTED_AGENT_BAND`** | 限价相对 **参考价** 超出 **`AGENT_PRICE_DEVIATION_BPS`**（**`FR-T12` / `AGENT_PRICE_*`**） | **可读拒答**；**不**入 **`billing` `billCode`** — **同窗** **`boundaries` §2**、**`trade-via-agent` 现货限价** |

---

## 3. 互引

| 文档 | 关系 |
|------|------|
| [`../domains/agent/exchange-agent/trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) | **`skillId`** 与 **流程专节** |
| [`../tools/tool-registry.md`](../tools/tool-registry.md) | 工具索引（**不**替代矩阵） |
| [`../domains/agent/agent-orchestration/routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md)、[`../domains/agent/exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md) | **矩阵缺项 / `TBD`** → **`FR-T05`** **透明拒答** |
| [`acceptance.md`](acceptance.md) | **SC-RISK-03**（**symbol / 偏离带**） |

---

**文档版本**：0.2.1 · **维护**：产品 + 风控 owner · **本版**：**`SC-RISK-03`** 指针。**顺延 0.2.0** …
