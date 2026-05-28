# Canonical Trading Model · 统一交易语义层（设计 SSOT · 草案）

**路径**：`specs/design/canonical-trading-model.md`。  
**ADR**：[**ADR-004**](adr/004-intent-centric-execution-and-canonical-trading-model.md)。  
**配套**：[`architecture.md`](architecture.md)（逻辑容器与数据流 · **「与通用 Agent 栈之对照」**）、[`api.md`](api.md)（**V1 · Coobit HTTP 矩阵**）、[`requirements/domains/agent/exchange-agent/trade-assistance.md`](../requirements/domains/agent/exchange-agent/trade-assistance.md)（`skillId`/`toolId` 登记）。

**定位**：定义 **执行链路内侧** 的 **与交易所 REST 字段解耦** 的 **最小领域语义**，使 **同一套 `skillId`/`toolId`** 在未来 **多 `venue`** 下 **仍** **可路由**。**不** 替代 [`api.md`](api.md) **PATH 冻结**（V1）；**不** 在本文抄写 OpenAPI 字段表。

**关单余量（MR 首节）**：[`closure-remaining` §0](../requirements/closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../requirements/closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../requirements/closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../requirements/contract-closure.md)。

---

## 1. 分层（与 Runtime 的交界）

```text
Skill / Planner（产品能力 · FR-T07 / scenarioId）
      ↓
Trading Intent（结构化意图 · 可选显式 JSON，随 Prompt/编排版本冻结）
      ↓
Canonical Command（本文 §3～§4 · 领域动词 + P0 对象）
      ↓
Execution Gateway（venue 解析、能力矩阵、幂等键策略入口）
      ↓
Exchange Adapter（V1：Coobit；实现可承载 openapi-ai / 直连 HTTP）
      ↓
交易所 HTTP/WS（[`api.md`](api.md) 矩阵 · allowlist）
```

**原则**：**交易所** **仅** **流动性与账户后端**；**业务编排与用户承诺** **以 Canonical 与域 FR 为准**。

---

## 2. `venue`（执行后端标识）

| 取值（示意） | 说明 |
|--------------|------|
| **`coobit`** | **V1 默认且唯一**；子账户 scope、GitBook/OpenAPI 同窗矩阵。 |
| **未来扩展** | **须** **新 Adapter + 能力矩阵行** + **contract-closure 登记**；**禁止** **仅 fork 一套「某所 Skill」** **作为产品 SSOT**。 |

**用户绑定**（未来）：**`userId` + `venue` + `credentialsRef` + 能力标签**；**单会话默认 venue** **须** **来自绑定** **或** **用户显式切换（产品冻结）**。

---

## 3. P0 · 统一枚举与对象（最小集）

### 3.1 `InstrumentRef`（交易标的）

| 字段 | 说明 |
|------|------|
| `baseAsset` | 如 `BTC` |
| `quoteAsset` | 如 `USDT` |
| `marketKind` | **示意**：`SPOT` \| `LINEAR` \| `INVERSE` \| …（与 [`trade-assistance`](../requirements/domains/agent/exchange-agent/trade-assistance.md) 业务线对签后冻结枚举） |

**映射**：**Adapter** **负责** `InstrumentRef` → 所侧 `symbol` / `instId` / `category` 等。**Planner** **不得** **以** **某一所的字符串** **为唯一真源**。

### 3.2 `CanonicalOrderState`（订单生命周期 · 平台侧）

**用途**：**对账、观测、用户话术** **收敛** **到** **与所无关的稳定集合**；**所侧原始状态** **须经 Adapter 映射**。

| 状态 | 含义（摘要） |
|------|----------------|
| `PENDING_SUBMIT` | 已接受意图，尚未得可靠交易所回执 |
| `OPEN` | 在市，可成交或撤销 |
| `PARTIALLY_FILLED` | 部分成交 |
| `FILLED` | 全部成交 |
| `CANCELED` | 已撤销（含未成交撤） |
| `REJECTED` | 交易所明确拒单 |
| `EXPIRED` | 按所规则过期 |
| `FAILED` | 平台判定失败（非 UNKNOWN） |
| `UNKNOWN` | **与** [`Runtime/unknown-state.md`](../requirements/Runtime/unknown-state.md) **同窗** · **504/对账前** |

**Coobit 原始状态 → Canonical** **映射表**：**由实现维护** · **所内对拍**；**文档 MR** **可** **附录样例** **非** **SSOT**。

### 3.3 `OrderIntent` / `PlaceOrder`（示意 · P0）

**领域动词** **`place_order`** **至少** **承载**（**字段名实现可调整，语义须等价**）：

- `instrument`：`InstrumentRef`  
- `side`：`BUY` \| `SELL`（或域内等价）  
- `orderType`：`MARKET` \| `LIMIT` \| …（与 `skillId` 族对齐）  
- `quantity` / `quoteAmount`：**按** **产品边界** **二选一或并存**（**闪兑/市价额** **同窗** [`trade-via-agent.md`](../requirements/flows/trade-via-agent.md)）  
- `price`：限价必填  
- `timeInForce`：若适用  
- `clientOrderId`：**幂等键** **策略** **同窗** [`api.md`](api.md) **「请求幂等（写）」** **与** **FR-T01**

**Coobit 现货 HTTP 投影（工程实现须与 [`api.md`](api.md) 矩阵对拍）**：`POST /sapi/v2/order` body 使用 **`type`**、**`volume`**（**非** `orderType` / `quoteQty` 命名），**与** **`openapi-ai` · `chainup-spot-order`** / **`cws spot createOrder`** **同窗** — **MARKET** 时 **`volume`** = **计价币** 成交金额（Canonical **`quoteAmount`**）；**LIMIT** 时 **`volume`** = **基础币** 数量（Canonical **`quantity`**）。

**动词 `cancel_order`**：`instrument` + **`exchangeOrderId` 与/或 `clientOrderId`** → **`POST /sapi/v2/cancel`**（**矩阵** **同窗** [`api.md`](api.md)）。

**动词 `get_order`**：**`instrument` + `exchangeOrderId` 与/或 `clientOrderId`** → **`GET /sapi/v2/order`**（**query**）；**响应 `status`** **→** **`CanonicalOrderState`**（**所侧 → Canonical** **映射表** **由工程维护并对拍**）；**504/空体** **→** **`UNKNOWN`**（**同窗** [`Runtime/unknown-state.md`](../requirements/Runtime/unknown-state.md)）。

**动词 `list_open_orders`**（**只读**）：**可选** **`instrument`**（**限定** **`symbol`**）**与** **可选** **`limit`** → **`GET /sapi/v2/openOrders`**（**query**）；**省略** **`instrument`** **时** **与** **`cws spot openOrders`** **同窗** **查** **全量**。**返回形态**：**不** **套** **单笔** **`canonicalOrderState`** — **工程实现** **可** **采用** **列表结果载体**（**示意**：判别字段 + **`items`** **摘要行** + **`ok`** **表示** **HTTP/业务码** **可判定成功**），**精确类型名** **非** **本文 SSOT**。

**其他动词（P1）**：`replace_order`（逻辑改单 **仍** **可为** **cancel+place 组合**）、**条件单** **另表** **与** **`skill.futures.take_profit_stop`** **对签**。

### 3.4 `ExecutionReport` / Fill（示意）

- `canonicalOrderState`、`filledQty`、`avgPrice`（若可得）、`fees`（若可得）、`exchangeOrderId`、`raw`（诊断，**默认可归因**）

---

## 4. Execution Gateway（逻辑职责）

1. **解析 `venue`**（V1 固定 `coobit` 或来自绑定）。  
2. **Capability check**：**意图** **是否** **被** **该 venue 支持**（**未来** **能力矩阵**；**不支持** **须** **可读拒答** **FR-T05**）。  
3. **派生幂等键** **与** **`executionId` 分层**（**同窗** [`api.md`](api.md)）。  
4. **调用 Adapter**；**收敛** **结果为 Canonical + UNKNOWN 语义**。  
5. **不** **在 Gateway 内** **写死** **具体 PATH** — **PATH** **属 Adapter 与映射表**。

---

## 5. 与现存登记表的过渡

| 现存 SSOT | 过渡策略 |
|-----------|----------|
| [`trade-assistance` §4](../requirements/domains/agent/exchange-agent/trade-assistance.md) **`skillId` → PATH** | **短期保留 PATH 列** **作为 Coobit Adapter 实现索引**；**新增列或外链** **`canonicalOp`**（后续 MR）。 |
| [`tool-registry`](../requirements/tools/tool-registry.md) | **`toolId`** **不变**；**实现** **转入** **Gateway→Adapter**。 |
| **openapi-ai `skills/*`** | **Coobit Adapter 可选宿主**；**不** **升格** **为** **跨所契约**。 |

---

## 6. OpenAPI 组件（未来）

**若** **将 Canonical 载荷** **暴露为 BFF/OpenAPI**，**须** **新 YAML** **与** **本条同窗** ** versioning**；**首版** **可** **仅运行时内存结构** **不落对外 Spec**。

**代码宿主**：**Execution Gateway / Adapter** **可执行实现** **在** **所内工程或 Runtime 仓库** **维护**；**本规格仓** **`product/`**、**`specs/`** **仅承载** **需求与设计** — **非** **可执行代码 SSOT**。

---

## 7. 非目标（本文）

- **具体浏览器/托管公链**、**非 CEX 流动性** **的完整模型**（**可** ** future 扩展 Router**）。  
- **策略 DSL 全量**（网格/做市 **可** **未来** **作为** **高级 Intent**）。  
- **替代** [**`Runtime/reconciliation.md`**](../requirements/Runtime/reconciliation.md) **WS/REST 矩阵** — **须** **互引**。

---

**文档版本**：0.1.5 · **维护**：产品 + 架构接口 owner + Agent Runtime owner · **本版**：**篇首** **`contract-closure`/`closure-remaining` §0～§6.4。** **承** **0.1.4**。
