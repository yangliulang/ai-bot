# Skill · `skill.spot.limit_order`（现货限价）

**路径**：`specs/requirements/skill-specs/spot/skill.spot.limit_order.md`。

**业务**：币币 **限价挂单**（**LIMIT**）— **买/卖** 由 **`side`** 表达，**不** 拆为两个 `skillId`。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.spot.limit_order` |
| **`skillSpecVersion`** | `0.1.0-mvp` |
| **`scenarioId`（主）** | `trade.spot.limit_order` |
| **`confirmation-flow`** | [`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md) 步骤 1→5 |
| **流程专节** | [`trade-via-agent` 专节 · 现货限价](../../flows/trade-via-agent.md) |
| **PRS 延展条文** | [`prompts/trading/buy.md`](../../prompts/trading/buy.md)、[`sell.md`](../../prompts/trading/sell.md) |
| **状态** | **`contract-complete`**（金样 · 阈值数值仍须所内 symbol 元数据冻结） |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`symbol`** | ✓ | string | 交易对（与交易所一致，如 `BTCUSDT`） |
| **`side`** | ✓ | enum | `BUY` \| `SELL`（**不** 用独立 buy/sell skill） |
| **`type`** | ✓ | enum | **固定** `LIMIT` |
| **`price`** | ✓ | decimal string | 限价 **单价**（报价币种） |
| **`quantity`** | △ | decimal string | **base** 数量；与 **`quoteQty`** **二选一** |
| **`quoteQty`** | △ | decimal string | **成交额口径**；与 **`quantity`** **二选一** |
| **`timeInForce`** | △ | enum | API **必选** 或用户 **已选** 时 **必填**（GTC / IOC / FOK 等） |
| **`newClientOrderId`** | — | string | 编排生成 · 幂等；**非**用户口述必填 |

**歧义消解**：

- 「买/卖 BTC」无数量 → **追问** `quantity` 或 `quoteQty`。  
- 「市价买」→ **不得** 走本 skill；路由 **`skill.spot.flash_convert`** 族。  
- 含杠杆/借币措辞 → **不得** 走本 skill；路由 **`margin.cross.*`** 或澄清。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_TRADING=ON` 且 `FEATURE_AGENT_SPOT=ON` | 否则 **`FR-T05`** 可读拒答 |
| **V-02** | 子账户绑定就绪（**FR-T02**） | 引导绑定 / 拒答 |
| **V-03** | `symbol` 在矩阵已冻结且可交易 | **`FR-T05`** / 不支持交易对 |
| **V-04** | `price` > 0；对齐 **`tickSize`**（工具/元数据） | 追问或拒答 · 不静默改价 |
| **V-05** | `quantity` 或 `quoteQty` 满足 **`stepSize` / `minNotional`** | 追问或拒答 |
| **V-06** | **FR-T12** · `AGENT_PRICE_BAND_GUARD_ENABLED=ON` 时限价相对参考价在偏离带内 | **`PRICE_REJECTED_AGENT_BAND`** 或 **建议价第二张类型 A**（**不写** 扣费 `billCode`） |
| **V-07** | 建议价第二张卡确认后参数与卡面 **一致** | 禁止确认后悄悄改价量 |

**数值 SSOT**：`tickSize`、`stepSize`、`minNotional` — **以所内 symbol 元数据 / 预检工具回填为准**。

---

## 3. Confirmation Schema（类型 A）

**步骤 3 之前**：**禁止** `call_exchange_write`；**禁止** 声称已挂单/已成交。

**类型 A 卡片 MUST 可见**（[`telegram/overview` §2.5.2](../../domains/agent/telegram/overview.md)、[`trade-via-agent` 专节 · 现货限价](../../flows/trade-via-agent.md)）：

| 字段 | 说明 |
|------|------|
| **业务线** | **币币**（与合约/杠杆版式区分） |
| **`symbol`** | 交易对 |
| **`side`** | 买 / 卖 |
| **订单类型** | **限价** |
| **`price`** | 委托单价 + 报价币种 |
| **数量** | **`quantity`（base）** 或 **`quoteQty`** — **单位写清** |
| **`timeInForce`** | 若适用则展示 |
| **预估手续费** | **仅** 工具返回可得时展示 |

**可选第二张卡**：**FR-T12** 建议价路径 — **须** 重复关键数字，用户 **明示确认** 后方可写。

**数字一致性**：卡面 = 步骤 2 校验通过参数 = 将提交 API 载荷 — [`hallucination`](../../observability/hallucination.md)。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **无 `symbol`** | 追问交易对 | 猜默认 BTCUSDT |
| **无 `side`** | 追问买/卖 | 默认 BUY |
| **无 `price`** | 追问限价 | **进入类型 A** |
| **无 `quantity` 且无 `quoteQty`** | 追问数量或金额 | **进入类型 A** / 声称已挂单 |
| **仅询价**（「多少钱」「盘面」） | 切只读 / MNRA | 附带下单诱导 |
| **工具预检失败** | [`common-phrases` §2](../../prompts/shared/common-phrases.md) | 编造成交 |
| **504 / UNKNOWN 写后** | [`unknown-state`](../../Runtime/unknown-state.md) | 让用户重复下单 |

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| 矩阵 PATH **TBD** / 现货写闸关闭 | 短因 + 能力边界 | **FR-T05** |
| **OCO/bracket** 组合写（本阶段） | 拒答或分步/主站 | **`product.md` §非目标** |
| 现货条件单 PATH **TBD** 且用户要组合腿 | 先限价入场或降级 | **FR-T05** / Deeplink |
| 未 KYC / 子账户未就绪 | 引导绑定 | **FR-T02** |
| 余额不足（交易所返回） | 复述交易所语义 | **`INSUFFICIENT_BALANCE`** 等 · **非** Agent 带 |

**改单**：**无原生 amend** — **`skill.spot.amend_limit_order`** · **单次类型 A** 后 **`cancel`→`order`** — [`trade-via-agent` 专节 · 逻辑改单](../../flows/trade-via-agent.md)。

**仅撤单**：**独立** `skill` / 场景 · **单独类型 A** · `POST /sapi/v2/cancel`。

---

## 6. API / 写路径（设计索引）

| 动作 | PATH（[`design/api`](../../../design/api.md) 矩阵为准） |
|------|--------------------------------------------------------|
| **下单写** | `POST /sapi/v2/order` |
| **撤单写** | `POST /sapi/v2/cancel` |
| **委托只读** | `GET /sapi/v2/openOrders`、`GET /sapi/v2/order`（解释未成交 / UNKNOWN 对账） |

**幂等**：`newClientOrderId` + **`executionId`** 分拆 — 见流程专节。

---

**文档版本**：0.1.0-mvp · **维护**：产品 + Agent Runtime owner · **本版**：**S-02 金样 · 对齐 trade-via-agent 现货限价专节**。
