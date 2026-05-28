# Skill · `skill.futures.take_profit_stop`（合约止盈止损 / 条件离场）

**路径**：`specs/requirements/skill-specs/futures/skill.futures.take_profit_stop.md`。

**业务**：永续/合约 **条件委托**（触价离场）— **`POST /fapi/v1/conditionOrder`** 族；**不得** 与单笔 **`POST /fapi/v1/order`** 市价/限价 **混为同一未声明多腿**。

**别名**：编排亦可能登记 **`futures.condition.order_create`** — **正文以本篇 `skillId` 为准**；`scenarioId` 以 [`routing-engine` §2](../../domains/agent/agent-orchestration/routing-engine.md) **冻结键** 对签。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.futures.take_profit_stop` |
| **`skillSpecVersion`** | `0.1.0-mvp` |
| **`scenarioId`（主）** | `trade.futures.take_profit_stop` |
| **`scenarioId`（备）** | `futures.condition.order_create` |
| **`confirmation-flow`** | [`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md) |
| **流程** | [`trade-via-agent` · 合约止盈止损分流](../../flows/trade-via-agent.md) |
| **编排冻结** | [`runtime-freeze` §3.6](../../domains/agent/agent-orchestration/runtime-freeze.md) |
| **Telegram** | [`telegram/overview` §2.5.4 · 止盈止损/条件](../../domains/agent/telegram/overview.md) |
| **PRS** | [`prompts/trading/futures.md`](../../prompts/trading/futures.md) |
| **状态** | **`contract-complete`**（**矩阵 `conditionOrder` PATH `TBD`** 时 **仅** 拒答/主站，见 §5） |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`symbol`** | ✓ | string | 合约代码 |
| **`positionSide` / 持仓方向** | ✓ | — | 与 **触发后减仓/平仓** 语义一致 |
| **`triggerType`** | ✓ | enum | 标记价 / 最新价 / 指数价等 — **寄存器冻结** |
| **`triggerPrice`** | ✓ | decimal | 触发价；对齐 **`tickSize`** |
| **`triggerDirection`** | △ | enum | 上穿 / 下穿 — **可由** 触发价与参考价 **推断**；**歧义须追问** |
| **`orderTypeOnTrigger`** | ✓ | enum | 触发后 **市价** 或 **限价** 离场 |
| **`price`** | △ | decimal | **`orderTypeOnTrigger=LIMIT`** 时 **必填** |
| **`quantity`** | ✓ | decimal | 平仓/减仓数量；**> 0** |
| **`qtyUnit`** | ✓ | enum | **张** 或 **币** — **与 API 一致** |
| **`reduceOnly`** | △ | bool | **离场** 意图 → **默认 `true`**；**卡面须可见** |
| **`workingType` / 条件子类型** | △ | — | 止盈 vs 止损 vs 跟踪等 — **以矩阵登记分型为准** |

**分流（FR-T07）**：

- 「止盈」「止损」「触价卖/买」「到 X 平仓」**且非** 仅表达 **单笔即时限价/市价入场** → **本 skill**。  
- 「95000 开多」「市价平仓」**无触发条件** → **`skill.futures.market_order`** / **`skill.futures.limit_order`**。  
- **同时** 要求「开仓 + 挂止盈止损」→ **分步**：**先** 入场 skill **独立类型 A**；**再** 本 skill **第二次类型 A** — **禁止** 一张卡未声明双写。  
- **全仓杠杆 / 现货** 条件单 → **FR-T05** / 主站（**首版不承诺**）。

**关联持仓（可选）**：

- 用户 **点名** 某持仓 → **只读** 持仓后 **预填** `symbol`/方向/数量上界；**禁止** 无事实猜仓位。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_TRADING=ON` 且 `FEATURE_AGENT_FUTURES=ON` | **`FR-T05`** |
| **V-02** | **FR-T02** · **fapi** scope | 绑定引导 |
| **V-03** | `symbol` 可交易且 **支持条件单** | **`FR-T05`** |
| **V-04** | `triggerPrice` > 0；**`tickSize`** | 追问 |
| **V-05** | 数量步进 / 最小张数 | 追问 |
| **V-06** | **触发逻辑自洽**（产品规则表）：例 **多仓止损** 触发价 **须低于** 参考价；**空仓止盈** 等 — **所内冻结** | 拒答 + 可读原因 |
| **V-07** | 触发后限价 **`price`** 合法 | 追问 |
| **V-08** | **写前预检**（可平数量、条件单限额等） | **无类型 A** |
| **V-09** | **`design/api` 矩阵** **`conditionOrder` PATH 已冻结** | **`FR-T05`** — **禁止类型 A 后无 API** |

**矩阵 TBD**：条文 **contract-complete**；运行时 **门禁** 以 §5 为准（**禁止** 类型 A 假闭环）。

---

## 3. Confirmation Schema（类型 A）

**版式**：**「触发条件」区块须与「即时挂单」视觉分离** — [`telegram/overview` §2.5.4](../../domains/agent/telegram/overview.md)。

**类型 A MUST**（顺序建议）：

| 区块 | 字段 |
|------|------|
| **触发条件（置顶）** | 触发价、触发逻辑（上穿/下穿）、参考价类型（标记价等） |
| **触发后将提交** | 合约、`orderTypeOnTrigger`、数量与单位、`price`（若限价）、`reduceOnly` |
| **风险说明** | **一行**：条件单触发前 **非** 普通盘口挂单；触发后 **市价** 可能有滑点 |
| **业务线** | **永续 · 条件委托**（与即时开平仓卡区分） |

**禁止**：

- 与 **`POST /fapi/v1/order`** **单笔开平仓** **同一类型 A** **未声明** 混挂。  
- 无 Secret；**禁止** 谎称「已同时挂好入场+止盈止损」。

**步骤 3 之前**：**禁止** `call_exchange_write`；**禁止** 声称条件单已生效。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **无触发价** | 追问 | **类型 A** |
| **触发方向歧义** | 澄清上穿/下穿 | 默认猜测 |
| **无数量** | 追问 | **类型 A** |
| **仅要即时市价平仓** | 切 **market_order** | 滥用条件 skill |
| **预检失败** | 短因 | 类型 A |
| **504 / UNKNOWN** | [`unknown-state`](../../Runtime/unknown-state.md) | 重复下单 |

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| **`conditionOrder` PATH TBD** | 能力边界 + **不展示可点确认写** | **`FR-T05`** |
| **OCO / bracket 一次性双挂** | 分步或主站 | **`product.md` §非目标** |
| **margin 侧计划条件单** | 主站 Deeplink | **trade-via-agent 全仓专节** |
| **现货条件单 TBD** | 纠偏或拒答 | **FR-T05** |
| **强平原因查询** | 只读 **`futures.read_liquidation_context`** | 无写 |
| **Automation 全链监控** | [`automation-alerts`](../../flows/automation-alerts.md) | 非本 skill 冒充 |

---

## 6. API / 写路径（设计索引）

| 动作 | PATH |
|------|------|
| **条件单创建** | `POST /fapi/v1/conditionOrder`（**矩阵终裁**；**TBD → §5**） |
| **预检只读** | 持仓、`GET` 条件单规则、账户 — 矩阵登记 |
| **对账** | 条件单状态查询 — **UNKNOWN** 时 **禁止** 断言已触发 |

**对签**：[`agent-coobit-api-allowlist`](../../integrations/exchange/agent-coobit-api-allowlist.md)、[`design/api`](../../../design/api.md) **合约 · 自动化 / conditionOrder**。

**与入场单关系**：**不** 要求 API 层 OCO 捆绑；**编排** **两次** **`executionId`** / **两次类型 A**。

---

**文档版本**：0.1.0-mvp · **维护**：产品 + Agent Runtime owner · **本版**：**S-05 mvp-ready · 对齐 runtime-freeze §3.6 + telegram §2.5.4**。
