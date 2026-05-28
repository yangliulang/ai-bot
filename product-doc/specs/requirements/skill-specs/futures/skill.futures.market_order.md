# Skill · `skill.futures.market_order`（合约市价）

**路径**：`specs/requirements/skill-specs/futures/skill.futures.market_order.md`。

**业务**：永续/合约 **市价** 开平仓 — **`POST /fapi/v1/order`** 族；**止盈止损 / 条件单** **不得** 用本 skill。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.futures.market_order` |
| **`skillSpecVersion`** | `0.1.0-mvp` |
| **`scenarioId`（主）** | `trade.futures.market_order` |
| **`confirmation-flow`** | [`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md) |
| **流程** | [`trade-via-agent` 专节 · 合约交易](../../flows/trade-via-agent.md) |
| **Telegram** | [`telegram/overview` §2.5.4 · 永续市价](../../domains/agent/telegram/overview.md) |
| **PRS** | [`prompts/trading/futures.md`](../../prompts/trading/futures.md) |
| **状态** | **`contract-complete`** |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`symbol`** | ✓ | string | 合约代码（所内登记，如 `BTC_USDT`） |
| **`side`** | ✓ | enum | 与 **开平/多空** 映射表对签（**禁止** 口语反向） |
| **`positionSide` / 开平语义** | ✓ | — | **开多/开空/平多/平空** → API `side` + **`reduceOnly`** 等 |
| **`type`** | ✓ | enum | **固定** `MARKET`（用户 **未** 给可解析限价时） |
| **`quantity`** | ✓ | decimal | **> 0** |
| **`qtyUnit`** | ✓ | enum | **`CONTRACT`（张）** 或 **`BASE`（币）** — **卡面与 API 一致** |
| **`leverage`** | △ | number | 用户指定「N 倍」时填入；**未指定** → **沿用账户默认**（**卡上宜展示** 将用之倍数） |
| **`marginMode`** | △ | enum | `cross` / `isolated` — **未指定** → **沿用账户** |
| **`reduceOnly`** | △ | bool | **平仓** 意图 → **`true`** 且 **卡面可见** |
| **`price`** | ✗ | — | **市价 skill 禁止** 用户委托限价；有明确限价 → **`skill.futures.limit_order`** |

**歧义消解**：

- 「100U 开多」是 **名义仓位** 还是 **保证金** → **须澄清**，**禁止** 类型 A。  
- 「买点 BTC」无多空 → **追问**。  
- 「止盈/止损/触价」→ **`skill.futures.take_profit_stop`** / `futures.condition.order_create`，**非** 本 skill。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_TRADING=ON` 且 `FEATURE_AGENT_FUTURES=ON` | **`FR-T05`** |
| **V-02** | **FR-T02** · **fapi** 子账户 scope | 拒答 / 绑定 |
| **V-03** | `symbol` 可交易 | **`FR-T05`** |
| **V-04** | 数量 **步进 / 最小张数** 合法 | 追问 |
| **V-05** | **写前预检**（[`trade-via-agent` 第五步](../../flows/trade-via-agent.md)）：保证金、限额、黑名单等 | **预检失败** → **无类型 A** |
| **V-06** | 若将 **`edit_lever` / 调保证金模式** 且与用户当前不一致 | **类型 A 卡须明示**「将先调整杠杆/模式再下单」；**独立用户意图** 各须 **单独类型 A** |
| **V-07** | 开平 × 多空 × `reduceOnly` **自洽** | 追问或拒答 |

**限价偏离**：合约市价 **不适用** 现货 **FR-T12**；滑点风险 **在类型 A 单行披露**。

---

## 3. Confirmation Schema（类型 A）

**预检（步骤 2 与 3 之间）**：**须** 完成只读/validate 预检 **且通过** 后方可展示类型 A — [`trade-via-agent` 专节 · 第五步](../../flows/trade-via-agent.md)。

**类型 A MUST**（[`telegram/overview` §2.5.4](../../domains/agent/telegram/overview.md)）：

| 字段 | 说明 |
|------|------|
| **业务线** | **合约 / 永续**（与现货闪兑、限价、全仓 **版式区分**） |
| **方向与开平** | 开多/开空/平多/平空 **可读文案** |
| **订单类型** | **市价** — **不得** 展示用户委托限价 |
| **数量与单位** | 张或币 — **与 OpenAPI 一致** |
| **`leverage`** | 将使用的杠杆倍数（含沿用默认） |
| **`marginMode`** | 逐仓 / 全仓 |
| **预估保证金** | **仅** 预检返回可得 |
| **滑点风险** | **市价须有一行** |
| **`reduceOnly`** | 若为 true **须可见** |

**开仓路径**：可能串联 [`risk-disclosure`](../../prompts/confirmation/risk-disclosure.md)、[`high-risk-confirmation`](../../prompts/confirmation/high-risk-confirmation.md) — 以路由与产品枚举为准。

**提交后**：区分 **委托受理** vs **成交终局** vs **部成在途** — [`trade-via-agent` S5.1.1](../../flows/trade-via-agent.md)。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **无合约标的** | 追问 | 猜 `BTC_USDT` |
| **无方向/开平** | 追问 | 默认开多 |
| **无数量** | 追问 | **类型 A** |
| **名义歧义未消** | 澄清 U 含义 | 静默下单 |
| **用户给限价** | 切 `skill.futures.limit_order` | 市价 skill 带 `price` |
| **预检未通过** | 短因 + 修正建议 | 发类型 A |
| **504 / UNKNOWN** | [`unknown-state`](../../Runtime/unknown-state.md) | 假称已成交 |

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| 合约写闸关闭 | **FR-T05** | |
| 用户意图为现货/闪兑 | 纠偏路由 **`trade.spot.*`** | **FR-T07** |
| 强平原因查询 | 只读 **`futures.read_liquidation_context`** | 无写 |
| 条件单/止盈止损 | 切 **`take_profit_stop`** 专 skill | |
| 余额/保证金不足 | 复述预检或交易所语义 | |

---

## 6. API / 写路径（设计索引）

| 动作 | PATH |
|------|------|
| **合约下单** | `POST /fapi/v1/order` |
| **预检（只读）** | `GET /fapi/v1/account` 等 + 规则引擎；或 `order/test`（矩阵登记时） |
| **调杠杆（若需）** | 矩阵登记的 `edit_lever` 等 — **独立类型 A**（非逻辑改单序） |

**对签**：[`agent-coobit-api-allowlist` §2.5](../../integrations/exchange/agent-coobit-api-allowlist.md)、[`design/api`](../../../design/api.md) **合约矩阵**。

---

**文档版本**：0.1.0-mvp · **维护**：产品 + Agent Runtime owner · **本版**：**S-03 mvp-ready · 对齐 trade-via-agent 合约专节**。
