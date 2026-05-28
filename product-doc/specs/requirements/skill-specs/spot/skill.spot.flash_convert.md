# Skill · `skill.spot.flash_convert`（现货市价 / 闪兑）

**路径**：`specs/requirements/skill-specs/spot/skill.spot.flash_convert.md`。

**所属体系**：[**PRS L0**](../../prompt-runtime/README.md) · **派工** → **[PRS §4](../../prompt-runtime/README.md#prs-where-to-edit)**。

**业务**：币币 **即时市价 / 闪兑** — **无** 用户委托价；**禁止** 与现货限价、全仓杠杆、合约混路由。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | `skill.spot.flash_convert`（族；实现可分子 `*.buy` / `*.sell`，**登记仍以族为准**） |
| **`skillSpecVersion`** | `0.1.0-mvp` |
| **`scenarioId`（主）** | `trade.spot.flash_convert` |
| **`confirmation-flow`** | [`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md) |
| **流程** | [`trade-via-agent` 四轨 · 闪兑](../../flows/trade-via-agent.md)、[`runtime-freeze` §3.1](../../domains/agent/agent-orchestration/runtime-freeze.md) |
| **Telegram 卡面** | [`telegram/overview` §2.5.2 · 闪兑](../../domains/agent/telegram/overview.md) |
| **PRS 延展** | [`prompts/trading/buy.md`](../../prompts/trading/buy.md)、[`sell.md`](../../prompts/trading/sell.md) |
| **状态** | **`contract-complete`** |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| **`symbol`** | ✓ | string | 交易对（如 `BTCUSDT`） |
| **`side`** | ✓ | enum | `BUY` \| `SELL` |
| **`type`** | ✓ | enum | **固定** `MARKET`（或矩阵登记的市价等价枚举） |
| **`quantity`** | △ | decimal string | **base** 数量 |
| **`quoteQty`** | △ | decimal string | **quote 金额**（如 USDT 口径） |
| **`newClientOrderId`** | — | string | 编排生成 · 幂等 |

**互斥**：

- **`quantity`** 与 **`quoteQty`** **至少其一** 可推断；**二者皆无** → **追问**，**禁止** 类型 A。  
- **不得** 出现用户 **`price` / 限价 / 挂单到 X** — 有明确限价语义 → **`skill.spot.limit_order`** + `trade.spot.limit_order`。  
- **不得** 含杠杆/借币/合约措辞 → **`margin.cross.*`** / **`trade.futures.*`** 或澄清。

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| **V-01** | `FEATURE_TRADING=ON` 且 `FEATURE_AGENT_SPOT=ON` | **`FR-T05`** |
| **V-02** | **FR-T02** 子账户 + 交易 Key 就绪 | 引导绑定 / 拒答 |
| **V-03** | `symbol` 矩阵可交易 | **`FR-T05`** |
| **V-04** | `quantity` 或 `quoteQty` 满足 **stepSize / minNotional**（工具/元数据） | 追问或拒答 |
| **V-05** | **无** `price` 字段进入写载荷（市价语义） | 若用户坚持限价 → **改路由** |
| **V-06** | 矩阵 PATH **非 TBD**（[`allowlist` §2.2](../../integrations/exchange/agent-coobit-api-allowlist.md)） | **`FR-T05`** |

**说明**：**FR-T12 限价偏离带** **不适用于** 本 skill（无委托价）；滑点风险 **仅在类型 A 披露**，**非** 偏离带拒答。

---

## 3. Confirmation Schema（类型 A）

**步骤 3 之前**：**禁止** `call_exchange_write`；**禁止** 「已成交终局」措辞（仅可「将提交市价委托」）。

**类型 A MUST**（[`telegram/overview` §2.5.2 · 闪兑](../../domains/agent/telegram/overview.md)）：

| 字段 | 说明 |
|------|------|
| **业务线** | **币币 · 闪兑 / 市价**（**禁止** 出现委托价、**禁止** 冒充限价单） |
| **`symbol`** | 交易对 |
| **`side`** | 买 / 卖 |
| **成交口径** | **base 数量** 或 **quote 金额** — **单位写清** |
| **市价语义** | 可读「市价 / 即时 / 闪兑」 |
| **风险一句** | 流动性 / **滑点** 提示（篇幅受 Telegram 约束） |

**提交后话术**（非类型 A）：**须** 区分 **「委托已受理 / 撮合中」** 与 **「买入/卖出已成交终局」** — 禁止含糊「已完成」— 同窗 **telegram §2.5.2 · 提交后/终局**、[`trade-via-agent` S5.1.1](../../flows/trade-via-agent.md)。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| **无 `symbol`** | 追问交易对 | 猜默认币对 |
| **无 `side`** | 追问买/卖 | 默认 BUY |
| **无数量且无金额**（**且无** **§4.1 · ALL_IN** 语义） | 追问「买多少 / 用多少 U」 | **进入类型 A** |
| **§4.1 · 全部买入 / 用全部 U 买 / 买满**（**INV-010**） | **编排** **`slot_fill_read_balance`** → 填 **`quoteQty`**（**`provenance=runtime_read_balance`**）；对用户 **说明将查余额** — **禁止** 仅 LLM 追问「买多少 U」 | LLM **单独** 填 `quoteQty` · **载货类型 A** |
| **§4.1 · 全部卖出 / 清仓 / 卖光**（**INV-010**） | **`slot_fill_read_position`** → 填 **`quantity`** | 同上 · **`quantity`** |
| **用户给限价** | 说明将走 **限价挂单** 并切 `limit_order` | 用市价 skill 硬提交 |
| **仅询价** | 切 MNRA / 只读 | 附带下单 |
| **504 / UNKNOWN 写后** | [`unknown-state`](../../Runtime/unknown-state.md) | 重复下单 / 假称已成交 |

### 4.1 语义买满 / 卖清（INV-010）

**同窗** [`trade-via-agent` S11.1](../../flows/trade-via-agent.md#trade-inv-010-semantic-full-book) · [`clarify-user-visible` §2](../../prompts/shared/clarify-user-visible.md) · **编排** **`orchestrationNextSteps`**（Demo · [`allInOrchestration.ts`](../../../src/admin/src/productionRuntime/allInOrchestration.ts)）。

---

## 5. Refusal Conditions

| 条件 | 对用户 | 码 / FR |
|------|--------|---------|
| 现货写闸关闭 / PATH TBD | 短因 | **FR-T05** |
| 用户要 OCO/bracket 组合单 | 分步或拒答 / 主站 | **`product.md` §非目标**（OCO/bracket 写） |
| 矩阵未冻结「入场+离场」组合 | 先市价入场或 **FR-T05** | [`trade-via-agent` S12](../../flows/trade-via-agent.md) |
| 余额不足 | 复述交易所语义 | 交易所返回码 · **非** 编造成功 |

---

## 6. API / 写路径（设计索引）

| 动作 | PATH |
|------|------|
| **市价下单写** | `POST /sapi/v2/order`（及 `/order/test` 若预检） |
| **撤单** | `POST /sapi/v2/cancel`（**独立意图 · 单独类型 A**） |

**对签**：[`agent-coobit-api-allowlist` §2.2](../../integrations/exchange/agent-coobit-api-allowlist.md)。

---

**文档版本**：0.1.1-mvp · **维护**：产品 + Agent Runtime owner · **本版**：**§4.1 INV-010 ALL_IN 与 flash_convert 对齐**。**承** 0.1.0-mvp。
