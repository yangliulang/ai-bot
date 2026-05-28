# Tool Permission Matrix（摘要）

**终裁**：[`design/api.md`](../../design/api.md) **矩阵** + [`exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md) **门禁** + [`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **§8**。本节 **浓缩** **类 / 确认 / 运营策略 / 风险**，**不**替代 **`tool-management`** FR。

---

## 1. 能力类 × 用户确认 × IO

| 类 | 定义（详见 **§8.1**） | 须 **类型 A** 确认？ | 典型 IO |
|----|------------------------|----------------------|---------|
| **A** | Coobit **私有写**（`call_exchange_write`） | **是**（**每用户授权单元**；**逻辑改单** **见** [`trade-assistance`](../domains/agent/exchange-agent/trade-assistance.md) **§8.1**） | 下单 / 撤单 / 改单 / 理财写 / 划转写 |
| **B** | 子账户 scope 或所内 **只读** | **否** | 行情 / 挂单 / 持仓 / 盘口 |
| **C** | 外网 / 检索 / 通用能力 | **否**（**须有**合规、速率、上下文预算） | 舆情 / 搜索 / 翻译 |

**升格**：仅询价 **不得** 静默升级为 A；**写** → [`trade-via-agent`](../flows/trade-via-agent.md) **专节**。

---

## 2. 运营 Tool Profile（`FR-TM03` / T05）

| 概念 | 落点 |
|------|------|
| **是否可被模板声明** | [`tool-management/functions.md`](../domains/admin/tool-management/functions.md) **`FR-TM03`**、**Tool Profile** |
| **本次 `executionId` 是否真可调** | [`runtime-contract.md`](../domains/admin/tool-management/runtime-contract.md) **§5** · 权限链 **1～5** |
| **「缺失可调用配置不得 Enable」** | 控制台 / **`SC-TM`** 同窗 **PRD 模块三** |

---

## 3. 风险级与 Retry（`toolRiskLevel`）

| Level | 默认自动 Retry | 摘要 |
|-------|----------------|------|
| **LOW** | 允许（退避 + 上限 **`design`**） | 只读快照、**`get_balance`** 族等 |
| **MEDIUM** | **禁止** 同参写重放 | **`create_order`** 等 · **UNKNOWN** 走 **对账后显式二次提交** |
| **HIGH** | 默认禁止 | 出金 / 不可逆划转等 · **Production 白名单** |

全文：**[`runtime-contract.md`](../domains/admin/tool-management/runtime-contract.md)** §2～§3。

---

## 4. 观测与归因

**`agent.tool.call`**、`invocationState`、**`executionId`**：**[`observability/overview.md`](../observability/overview.md) §2.1**、**`execution-lifecycle`**。
