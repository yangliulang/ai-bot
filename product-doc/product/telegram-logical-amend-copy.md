# 逻辑改单 · Telegram 文案模板（简中 + English · i18n）

**用途**：[`specs/requirements/domains/agent/telegram/overview.md`](../specs/requirements/domains/agent/telegram/overview.md) **§2.5.2 / §2.5.4** **`trade.*.amend_limit_order`**。实现层 **建议** `t(locale, "key")` **与下表 `key` 对齐**。**允许** **运营/合规** **微调语气** **但** **须** **保留** **两阶段披露** **与** **撤成单败** **诚实语义**（**中/英** **一致**）。

**人类阅读**：[`telegram-and-cards.md`](telegram-and-cards.md) **「修改在途挂单」**；**流程** [`trade-via-agent.md`](../specs/requirements/flows/trade-via-agent.md) **专节 · 逻辑改单**。

**历史文件名**：[`telegram-logical-amend-copy-zh-CN.md`](telegram-logical-amend-copy-zh-CN.md) **仅作重定向**，**请以本篇为 SSOT**。

---

## 类型 A · 卡面

| key | 默认文案（zh-CN） | Default copy (en) | 备注 |
|-----|-------------------|-------------------|------|
| `amend.card.title` | 修改挂单 | Modify order | 气泡首行 / 加粗首句 |
| `amend.card.lead` | 将按下方参数撤销原委托，并提交一笔新的限价委托。 | We will cancel your open order as shown below, then place a new limit order. | 固定披露 |
| `amend.card.section.original` | 当前委托 | Current order | 原单摘要区标题 |
| `amend.card.section.new` | 修改为 | New order | 新参摘要区标题 |
| `amend.card.pair` | 交易对：{symbol} | Pair: {symbol} | |
| `amend.card.side` | 方向：{side} | Side: {side} | Buy/Sell human-readable |
| `amend.card.order_ref` | 委托编号：{orderRef} | Order ref: {orderRef} | orderId or clientOrderId summary |
| `amend.card.compare.price` | 委托价：{oldPrice} → {newPrice} {quote} | Limit price: {oldPrice} → {newPrice} {quote} | 无变更可单行新价 |
| `amend.card.compare.qty` | 数量：{oldQty} → {newQty} {base} | Quantity: {oldQty} → {newQty} {base} | |
| `amend.card.tif` | 有效期：{tif} | Time in force: {tif} | GTC/IOC/FOK |
| `amend.card.disclosure` | 点「确认修改」后，将先撤销原单，再提交新单（交易所分两步处理，不是一键改单）。 | After you tap **Confirm change**, we cancel the existing order first, then submit the new one (two exchange steps—not a single “amend” API). | 可与 `lead` 合并，须保留含义 |
| `amend.btn.confirm` | 确认修改 | Confirm change | 主按钮 |
| `amend.btn.cancel` | 取消 | Cancel | |

**合约额外占位**：`{positionSide}`、`{reduceOnlyHint}`、`{leverage}` 等可插在 section 下方独立短行（**英** **示例**：`Position: {positionSide}`、`Leverage: {leverage}x`）。

---

## 确认后 · 进度与结果

| key | 默认文案（zh-CN） | Default copy (en) | 备注 |
|-----|-------------------|-------------------|------|
| `amend.progress.cancel` | 正在撤销原委托… | Cancelling your open order… | 阶段 1 |
| `amend.progress.place` | 正在提交新委托… | Submitting your new order… | 阶段 2 |
| `amend.progress.slow` | 交易所处理可能需数秒，请稍候。 | This may take a few seconds. | 可选长耗时 |
| `amend.success` | 已提交新委托：{symbol}，限价 {newPrice}，数量 {newQty}，单号 {orderRef}。请在「当前委托」中核对。 | New limit order submitted: {symbol}, price {newPrice}, qty {newQty}, ref {orderRef}. Please verify in **Open orders**. | 勿写「改单成功」若仍 UNKNOWN |
| `amend.err.cancel` | 未能撤销原委托，新委托未提交。原挂单仍可能在交易所。请稍后在 App 查看，或重试。 | Could not cancel the original order; the new order was **not** placed. Your old order may still be live—check the app shortly or try again. | 序 1 失败 |
| `amend.err.place` | 原委托已撤销，但新委托未挂上。当前可能无该挂单，请在 App 检查持仓/委托，或在本对话中重试下单。 | The original order was cancelled, but the **new** order was **not** placed. You may have no resting order now—check positions/open orders in the app, or place again here. | 撤成单败 |
| `amend.err.unknown` | 处理结果暂时不确定。请勿重复点击。请在 App 核对「当前委托」后，如需再改价请重新发起。 | Result unclear—please don’t tap repeatedly. Check **Open orders** in the app; start a new request if you still need to change price. | 504/UNKNOWN |
| `amend.err.partial_fill` | 该委托已部分成交。将仅对剩余可撤数量处理；若与预期不符请先取消。 | This order was partially filled. We will only adjust the **remaining** cancellable size—tap Cancel if that’s not what you want. | 部成前置澄清 |

---

## 极简版（字数紧时）

| key | 默认文案（zh-CN） | Default copy (en) |
|-----|-------------------|-------------------|
| `amend.card.title.short` | 改单 | Edit order |
| `amend.card.disclosure.short` | 先撤原单，再挂新单。 | Cancel old order, then place new. |

---

*规范锚点：ADR-001、[telegram/overview §2.5.2 / §2.5.4 · 逻辑改单](../specs/requirements/domains/agent/telegram/overview.md)、[telegram/overview §2.6](../specs/requirements/domains/agent/telegram/overview.md)。*
