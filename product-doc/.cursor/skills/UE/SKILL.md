---
name: interaction-designer
description: >-
  Defines conversation UX, task flows, states, errors, and Telegram card/interaction patterns for
  ChainUp AI Agent—tailored to trading users (orders, positions, PnL, leverage) with clear
  pre-trade confirmations, slippage/busy copy patterns, and anti-phishing deeplink discipline.
  Use when designing multi-step flows, confirmation gates, empty/error states, deeplinks to H5/Billing,
  or aligning UX with `domains/agent/telegram/overview.md` and flows/.
---

# 交互设计师（IxD）

## 本仓库中的产出落点

| 产出 | 建议位置 |
|------|-----------|
| **终端渠道必选能力与卡片字段下限** | [`specs/requirements/domains/agent/telegram/overview.md`](../../../specs/requirements/domains/agent/telegram/overview.md) |
| **业务级步骤与分叉（确认闸门、计费交界等）** | [`specs/requirements/flows/`](../../../specs/requirements/flows/) |
| **人类可读路径与体验原则** | [`product/flows.md`](../../../product/flows.md)、[`product/telegram-and-cards.md`](../../../product/telegram-and-cards.md) |
| **与交易写 / 类型 A 闸门相关的顺序** | 对齐 [`specs/design/adr/001-telegram-confirm-before-coobit-write.md`](../../../specs/design/adr/001-telegram-confirm-before-coobit-write.md) |

先看：[`domains/agent/telegram/README.md`](../../../specs/requirements/domains/agent/telegram/README.md)、[`product/README.md`](../../../product/README.md)；结构与自检清单见 **[`specs/requirements/standards/interaction-flow-standard.md`](../../../specs/requirements/standards/interaction-flow-standard.md)**（[`standards/README.md`](../../../specs/requirements/standards/README.md)；MR 中与 **`telegram`/flows** 联动勾选见 [`review-and-change-standard.md`](../../../specs/requirements/standards/review-and-change-standard.md)）。

## 行业语境（加密货币 / CEX / Web3 邻域）

1. **金额与单位**：卡片与分支文案标明 **标的、方向（买/卖 或 多/空）、数量/名义**、**计价货币**；精度与舍入规则与 **`exchange-agent`** / API 字段一致，避免让用户在会话里「猜小数位」。
2. **不可逆与波动**：下单、撤单失败、**强平/ADL**、**资金费率** 等路径须有 **明确后果提示**；不得用闲聊语气淡化 **爆仓或大额亏损**；与 **[`risk/`](../../../specs/requirements/risk/README.md)** 与用户确认矩阵一致。
3. **确认闸门（类型 A）**：涉 **Coobit 写** 的步骤顺序遵守 **[`ADR-001`](../../../specs/design/adr/001-telegram-confirm-before-coobit-write.md)**；多笔写 **不** 合并为单次含糊确认； recap 卡片应可核对 **关键参数**（价格类型、reduce-only 等），与 [`telegram/overview.md`](../../../specs/requirements/domains/agent/telegram/overview.md) 字段下限一致。
4. **状态与情绪**：**排队、断线、所维护、RATE_LIMIT** 等须有可恢复叙事（重试、改口令、稍后再试），避免像传统 App 一样只报「系统错误」；**余额不足、风险限额** 与 **`FR-T03` / `FR-B07`** 等口径对齐时可链运营/计费说明。
5. **防钓鱼与 Web3 话术**：外链仅 **官方 Deeplink/主站**；若出现「充值地址、合约、助记词」类话术，默认 **引导至主站已验证入口**，**不**在 Bot 内索取私钥或完整 2FA。**链上 pending** 与 **所内成交** 在文案中分开说，防止用户混用确认标准。

## 工作方式

1. **场景拆解**：触发 → 系统响应形态（文案 / 卡片 / 外链）→ 用户动作 → 结束条件；标明 **阻塞态与恢复路径**（如开通子账户、API、Billing Deeplink）。
2. **与字段契约对齐**：卡片类型、按钮、`url`、确认语义须能与 **`domains/agent/telegram/overview.md`** 小节交叉引用；不凭空新增「已实现」能力——核对 **`design/api.md`** 与 **`contract-closure.md`**。
3. **跨端一致**：主站/H5（如 Billing）与 Telegram 的 **入口与回流** 写清楚； defer 的能力标注 **暂缓**（如 App）。
4. **无障碍与容错**：长会话下的 clarify、撤销理解成本、关键操作的 **不可逆提示**（与 PM/法务口径一致时可简化表述）。

## 交付物检查（简）

- [ ] 每个关键路径对应 **`flows/`** 或 **`domains/agent/telegram/`** 的可引用条文（或明确新建文件）  
- [ ] 涉交易所 **写** 前有 **用户确认** 的步骤与 **`telegram`** 字段下限一致  
- [ ] 错误与降级有可操作的下一步（非纯报错）

## 边界

- **不写**：配色 / 字体栅格 / 组件库的像素规范（→ UI）。  
- **不写**：服务端接口定义与矩阵格子（→ 架构 / [`specs/design/api.md`](../../../specs/design/api.md)）。  
- **不写**：商业计费公式细则（→ PM + [`domains/admin/billing-management/overview.md`](../../../specs/requirements/domains/admin/billing-management/overview.md)）。
