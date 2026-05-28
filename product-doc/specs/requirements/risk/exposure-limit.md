# Global Risk · Exposure & throttle limits

**职责**：**净名义敞口、集中度、会话亏损、大额、冷却、高频写窗** 等 **交易护栏** 的 **横切索引**（**数值口径与窗边界** 由 **`design`/ADR** 冻结）。**提醒话术与 Risk Alerts 能力** → [`../domains/agent/exchange-agent/risk-alerts.md`](../domains/agent/exchange-agent/risk-alerts.md)；**持仓/盈亏只读叙事** → [`../domains/agent/exchange-agent/portfolio-insight.md`](../domains/agent/exchange-agent/portfolio-insight.md)。

**SSOT 边界**：[`portfolio-insight`](../domains/agent/exchange-agent/portfolio-insight.md) **私有快照输出** **不等于** **`risk/README`** 或本文作为 **运营风控规则唯一 SSOT** — **同窗该文矩阵说明**。

---

## 1. `configKey` 族（摘录）

下列键 **登记形态** 见 [`keys.md` §3](../domains/admin/trading-agent-config/keys.md)；**与模板叠层** 见 [`../domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md) **§1** 互引及 **`trading-agent-config/functions.md` §2.6**。

| `configKey`（示意） | 产品含义（概念） |
|---------------------|------------------|
| **`AGENT_MAX_NET_EXPOSURE_USDT`** | 最大 **净名义** 敞口 |
| **`AGENT_MAX_DISTINCT_SYMBOLS`** | **最大交易币种数**（distinct symbol） |
| **`AGENT_MAX_SINGLE_SYMBOL_WEIGHT_BPS`** | **单币占比** 上限（bps） |
| **`AGENT_MAX_SESSION_LOSS_USDT`** | **会话最大亏损**（实现+浮亏；窗定义见 `design`） |
| **`AGENT_LARGE_ORDER_THRESHOLD_USDT`** | **大额订单** 阈（可与 **增强确认** 同窗） |
| **`AGENT_COOLDOWN_SEC`** | 写操作 **冷却** |
| **`AGENT_HFT_WINDOW_SEC`** + **`AGENT_HFT_MAX_WRITES_PER_WINDOW`** | **高频写** 滑动窗与上限 |

**超限处理**：**透明拒答**、**禁止静默写** — 与 **`FR-T09`** 精神一致 — [`../domains/agent/exchange-agent/trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **§2**。

---

## 2. 验收指针（横切）

- **在途与排队**：「上一笔未完是否挡下一笔」**须** **risk / exchange-agent** 对签后在 **`Runtime`** 收敛为可测叙述 — [`../Runtime/execution.md`](../Runtime/execution.md) **§2**；**单 session 产品优先级 SSOT** → [`../domains/agent/agent-orchestration/session-concurrency-policy.md`](../domains/agent/agent-orchestration/session-concurrency-policy.md) **§3～§5**。
- **文案**：风险提醒 **不暗示已代用户成交** — **`FR-RA01`** — [`../domains/agent/exchange-agent/risk-alerts.md`](../domains/agent/exchange-agent/risk-alerts.md)。
- **运营数值护栏抽检**：**SC-RISK-04** — [`acceptance.md`](acceptance.md)。

---

**文档版本**：0.2.1 · **维护**：产品 + 风控 owner · **本版**：**`SC-RISK-04`** 指针。**顺延 0.2.0** …
