# Skill · `skill.futures.limit_order`（合约限价）

**路径**：`specs/requirements/skill-specs/futures/skill.futures.limit_order.md`。

**业务**：永续/合约 **限价** 开平仓 — **`POST /fapi/v1/order`**（`type=LIMIT` + `price`）；**止盈止损 / 条件单** **不得** 用本 skill。

**FR-T11**：本篇 **§1～§6 自包含** — **禁止** 运行时仅加载「增量条文」而不读本文件全文。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.futures.limit_order` |
| **`skillSpecVersion`** | `0.2.0-contract` |
| **`scenarioId`（主）** | `trade.futures.limit_order` |
| **`confirmation-flow`** | [`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md) |
| **流程** | [`trade-via-agent` 专节 · 合约交易](../../flows/trade-via-agent.md) |
| **Telegram** | [`telegram/overview` §2.5.4 · 永续限价](../../domains/agent/telegram/overview.md) |
| **PRS** | [`prompts/trading/futures.md`](../../prompts/trading/futures.md) |
| **状态** | **`contract-complete`** |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`symbol`** | ✓ | string | 合约代码（如 `BTC_USDT`） |
| **`side`** | ✓ | enum | 与 **开平/多空** 映射表对签 |
| **`positionSide` / 开平语义** | ✓ | — | 开多/开空/平多/平空 → API 字段 + **`reduceOnly`** |
| **`type`** | ✓ | enum | **固定** `LIMIT` |
| **`price`** | ✓ | decimal | 委托单价；**`tickSize`** 对齐 |
| **`quantity`** | ✓ | decimal | **> 0** |
| **`qtyUnit`** | ✓ | enum | **张** 或 **币** — 卡面与 API 一致 |
| **`leverage`** | △ | number | 用户指定倍数；未指定 → **沿用账户**（卡上展示） |
| **`marginMode`** | △ | enum | `cross` / `isolated`；未指定 → **沿用账户** |
| **`reduceOnly`** | △ | bool | 平仓意图 → **`true`** 且卡面可见 |
| **`timeInForce`** | △ | enum | API 必选或用户已选时必填（GTC 等） |

**路由**：

- 可解析委托价（「95000 开多」「限价 xxx」）→ **本 skill**。  
- **无价位**、即时撮合 → **`skill.futures.market_order`**。  
- 触价离场 / 止盈止损 → **`skill.futures.take_profit_stop`**。

**歧义**：「100U 开多」为名义还是保证金 → **须澄清**；**禁止** 类型 A。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_TRADING=ON` 且 `FEATURE_AGENT_FUTURES=ON` | **`FR-T05`** |
| **V-02** | **FR-T02** · **fapi** scope | 绑定 / 拒答 |
| **V-03** | `symbol` 可交易 | **`FR-T05`** |
| **V-04** | `price` > 0；**`tickSize`** | 追问 |
| **V-05** | 数量步进 / 最小张数 | 追问 |
| **V-06** | **写前预检**通过（保证金、限额等） | **无类型 A** |
| **V-07** | 开平 × `reduceOnly` 自洽 | 追问或拒答 |
| **V-08** | 限价偏离（**非** 现货 FR-T12 默认）：预检 / `config` / 所内规则 | 拒答或建议价第二张 A |
| **V-09** | 若将调杠杆/保证金模式且与当前不一致 | 类型 A **明示**调整顺序；**独立意图** 各须单独类型 A |

**数值**：`tickSize`、步进、最小张数 — **symbol 元数据 / 预检工具** 回填，**禁止** Prompt 臆造。

---

## 3. Confirmation Schema（类型 A）

**预检通过后** 方可类型 A — [`trade-via-agent` 合约专节 · 第五步](../../flows/trade-via-agent.md)。

**步骤 3 之前**：**禁止** `call_exchange_write`；**禁止** 声称已成交。

**类型 A MUST**：

| 字段 | 说明 |
|------|------|
| **业务线** | **合约 / 永续** |
| **方向与开平** | 开多/开空/平多/平空可读文案 |
| **订单类型** | **限价** + **`price`** + 报价币种 |
| **成交说明** | **一行**：不保证立即成交 |
| **数量与单位** | 张或币 |
| **`leverage` / `marginMode`** | 将使用值 |
| **预估保证金** | **仅** 预检可得 |
| **`reduceOnly`** | true 时须可见 |

**开仓**：可串联 [`risk-disclosure`](../../prompts/confirmation/risk-disclosure.md)、[`high-risk-confirmation`](../../prompts/confirmation/high-risk-confirmation.md)。

**改单**：**无 amend** → **`skill.futures.amend_limit_order`** · [`trade-via-agent` 专节 · 逻辑改单](../../flows/trade-via-agent.md)（**单次类型 A** · `cancel`→`order`）。

**数字一致性**：卡面 = 校验通过参数 = API 载荷。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **无合约标的** | 追问 | 猜默认币对 |
| **无方向/开平** | 追问 | 默认开多 |
| **无 `price`** | 追问或切市价 skill | **类型 A** |
| **无数量** | 追问 | **类型 A** |
| **用户要市价** | 切 **`skill.futures.market_order`** | 限价 skill 提交市价 |
| **名义歧义** | 澄清 | 静默下单 |
| **预检失败** | 短因 + 建议 | 类型 A |
| **504 / UNKNOWN** | [`unknown-state`](../../Runtime/unknown-state.md) | 假称已成交 |

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| 合约写闸关闭 / PATH TBD | **FR-T05** | |
| 现货/闪兑 | **`trade.spot.*`** | **FR-T07** |
| 全仓杠杆借买 | **`margin.cross.*`** | **FR-T07** |
| 条件单/止盈止损 | **`take_profit_stop`** | |
| 强平原因 | 只读 **`futures.read_liquidation_context`** | |
| 保证金不足 | 复述预检/交易所 | |
| OCO/bracket 一次双挂 | 分步或拒答 | **`product.md` §非目标** |

---

## 6. API / 写路径（设计索引）

| 动作 | PATH |
|------|------|
| **限价下单** | `POST /fapi/v1/order`（`LIMIT` + `price`） |
| **预检** | `GET /fapi/v1/account` 等；或 `order/test`（矩阵登记） |
| **逻辑改单** | `cancel` + `order`（新 `clientOrderId`） |
| **调杠杆（若需）** | 矩阵 `edit_lever` 等 — **独立类型 A** |

**对签**：[`agent-coobit-api-allowlist` §2.5](../../integrations/exchange/agent-coobit-api-allowlist.md)、[`design/api`](../../../design/api.md)。

---

**文档版本**：0.2.0-contract · **维护**：产品 + Agent Runtime owner · **本版**：**S-04 自包含正文（原增量骨架已合并）**。
