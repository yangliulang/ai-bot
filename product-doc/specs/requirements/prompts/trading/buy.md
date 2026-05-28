# Trading · Buy（条文）

**路径**：`specs/requirements/prompts/trading/buy.md`。  
**性质**：**写路径 Prompt 下限（买入主轴）** — **`scenarioId`/skill 真源** 见 [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)、[`trade-assistance` §8](../../domains/agent/exchange-agent/trade-assistance.md)；**正文 Publish**：[`prompt-management`](../../domains/admin/prompt-management/overview.md)。

**索引**：[`README`](./README.md)

> **Publish 正文**：[`governance-map.md`](../governance-map.md) · [`product/prompt-governance-checklist.md`](../../../../product/prompt-governance-checklist.md)。**本文**为 Git **评审下限**（可含 FR / Skill / 工具指称），**勿**将 API、`call_exchange_write` 等抄进 `pp-*` **六段运营正文**。`buy.md` **≠** 独立 `pp-trading-buy` 包。

**域宿主**：[`confirmation-flow` §1](../../domains/agent/agent-orchestration/confirmation-flow.md)；[`trade-assistance` §2·§8](../../domains/agent/exchange-agent/trade-assistance.md)；[`../confirmation/README`](../confirmation/README.md)。  
**操作契约**：市价/闪兑 → [`skill.spot.flash_convert`](../../skill-specs/spot/skill.spot.flash_convert.md)；限价 → [`skill.spot.limit_order`](../../skill-specs/spot/skill.spot.limit_order.md) — **槽位/确认/UNKNOWN 以 skill-spec 为准**。

---

## 1. 前置（缺一不可则先澄清）

- **交易对**、**买方向**（现货/合约语义 **以路由为准**）、**数量或名义金额**（二者至少其一可推断）；限价委托须 **价格或可推断价位区间**。**校验 / 偏离带 / 槽位补全**同窗 [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md) **步骤 2**（`FR-T07` / `FR-AO02`）；限价运营偏离带另见 **`FR-T12`** — [`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md)、[`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md)。  
- **子账户 scope / 绑定就绪**：[`onboarding/overview`](../../domains/agent/onboarding/overview.md)、[`exchange-agent/overview` FR-T01/T02](../../domains/agent/exchange-agent/overview.md)。  
- **类型 A（及按需串联的风险/高危确认）已完成**后方可触发写 — [`order-confirmation`](../confirmation/order-confirmation.md)、[`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)。

### 1.1 语义买满 / 全部买入（INV-010 · 买侧）

**适用**：**「全部买入 BNB」**、**「用全部 U 买」**、**「买满」** **等** — **同窗** [`trade-via-agent` S11.1](../../flows/trade-via-agent.md#trade-inv-010-semantic-full-book)、[`skill.spot.flash_convert` §4.1](../../skill-specs/spot/skill.spot.flash_convert.md)。

- **已选闪兑/市价** 且 **缺 `quoteQty`**：**编排** **须** **`runtime_read_balance`**（quote 可用，如 USDT）**落数** — **禁止** LLM **单独** 填金额后进类型 A。  
- **对用户**：说明 **将查子账户可用余额再确认** — [`clarify-user-visible` §2](../shared/clarify-user-visible.md)；**已说闪兑** → **不再** 问市价/限价；**已说 BNB** → **承接** BNB/USDT，**禁止** 无关币对举例。  
- **大额/满仓市价**：**宜** 串联 [`high-risk-confirmation`](../confirmation/high-risk-confirmation.md)（**以路由枚举为准**）。

---

## 2. 执行下限

- **写路径**：`FR-T09`/`FR-T11`、Telegram **摘要 / 卡片**可序列化 — [`trade-assistance`](../../domains/agent/exchange-agent/trade-assistance.md)、[`telegram/overview` §2.5 · 类型 A；总则 §2～§2.6](../../domains/agent/telegram/overview.md)、[`shared/response-format`](../shared/response-format.md)。  
- **工具**：仅 **已登记** `toolId`/skill — [`trade-assistance` §8](../../domains/agent/exchange-agent/trade-assistance.md)。  
- **精度 / 最小名义 / stepSize / 风控拒绝**：**复述**须与交易所返回及 **`error-normalization`** **一致**，**不**编造成交 — [`Runtime/error-normalization`](../../Runtime/error-normalization.md)、[`unknown-state`](../../Runtime/unknown-state.md)、[`reconciliation`](../../Runtime/reconciliation.md)。  
- **部分成交 / 挂单状态**：以编排归一与 **`unknown-state`** **为准**，**不**口头断定用户界面外的隐藏状态。

---

## 3. 拒答

- 矩阵缺项 → **`FR-T05`** — [`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md)；句式锚 [`shared/common-phrases` §1](../shared/common-phrases.md)。

---

## 4. 与分析分流 & 防幻觉

- **用户本轮仅询价 / 分析**：[`../intents/analysis.md`](../intents/analysis.md)，**不**夹带弱化确认链的下单诱导。  
- **声称委托已提交 / 已成交**：须 **写工具成功闭环** — [`../safety/privilege`](../safety/privilege.md)、[`hallucination`](../../observability/hallucination.md)。  
- **UNKNOWN / 工具失败**：[`shared/common-phrases` §2](../shared/common-phrases.md)、[`unknown-state`](../../Runtime/unknown-state.md)。

---

**Publish**：同窗 [`prompt-management/config`](../../domains/admin/prompt-management/config.md)。

**文档版本**：1.6.0-mvp · **维护**：产品 + Prompt owner · **本版**：**§1.1 INV-010 买满语义 · clarify-user-visible 同窗**。**承** 1.5.1-mvp。
