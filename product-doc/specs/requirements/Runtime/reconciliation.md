# Runtime · 对账（REST ↔ WebSocket ↔ 会话视图）

**职责**：**多通道真相源**并存时，平台 **以何种次序采信**、**何种条件下**用 REST **补足或推翻** WS/会话视图 — **运行时政策层**。  
**不**描述 Telegram 卡片 UX；**不**抄写交易所 PATH（PATH → **`design/api.md`**）。

**同窗**（短）：[`unknown-state.md`](./unknown-state.md)；[`recovery.md`](./recovery.md)；[`persistence.md`](./persistence.md)；[`design/api.md`](../../design/api.md)。**§1 矩阵** 另需 **上游 ENUM/WS 形状** → [`integrations/exchange/order-lifecycle.md`](../integrations/exchange/order-lifecycle.md)、[`integrations/exchange/websocket-api.md`](../integrations/exchange/websocket-api.md)。**横向全表** → [`boundaries.md`](./boundaries.md)。

**写路径 REST↔WS 对账** **同窗** **Intent→Canonical→Gateway** [`canonical-trading-model.md`](../../design/canonical-trading-model.md)、[`ADR-004`](../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../domains/agent/exchange-agent/trade-assistance.md)；[`CC-P1-07`](../contract-closure.md#cc-p1-07)；[`requirements-review` §7.5](../../../product/requirements-review.md#cc-adr004-review-checklist)；[`execution` §1 步 7](./execution.md)。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 边界（归属）

| 内容 | 归属 |
|------|------|
| WS GZIP、ping、`sub`、`broker` | **`integrations/exchange/websocket-api.md`** |
| 市价单是否推送 `executionReport` | **上游文档事实** → **`integrations/exchange/order-lifecycle.md`** |
| **首选真相源次序**、**REST 拉齐触发条件**、**可接受偏差窗口** | **本文 + `design` 登记表 + `exchange-agent` FR（可对签）** |
| 用户可见「是否算成交」文案 | **`domains/agent/exchange-agent`**、**`flows`** |

---

## 1. 须冻结的配置矩阵（占位）

下列矩阵 **须在 `design` 或 `exchange-agent` FR 中单义冻结**（允许多环境行）。

### 1.1 订单视图

| 维度 | 待冻结项 |
|------|-----------|
| 默认真相源 | **WS** / **REST** / **会话推导** 的 **优先级链**（可多段） |
| WS 缺口 | 当上游 **不推送**某类事件时，是否 **必选 REST** 查询及 **查询 PATH** |
| 竞态 | 同一 `orderId` 上 **REST 与 WS** **字段冲突**时 **采信规则** |
| 终局判定 | 何种字段集合出现时标记 **终局**（与 ENUM 对齐） |

### 1.2 余额 / 仓位视图

| 维度 | 待冻结项 |
|------|-----------|
| 快照偏好 | REST 余额 vs WS `outboundAccountPosition` / 合约 `ACCOUNT_UPDATE` **优先级** |
| 漂移 | **短时数值不一致**是否允许；若允许 **阈值与时间窗** |

### 1.3 WS 生命周期触发（REST 拉齐）

须在 **`design`/运维手册** 显式列举触发之一或多个（示例，非默认赋值）：

- WS 断连超过约定时长 Δt（Δt **不在本文赋值**）
- 连续 n 次 `ping` 无 `pong`（n **不在本文赋值**）
- 订阅失败，或收到上游 `SYSTEM` / `close` 类事件
- UNKNOWN 消退后对指定 `orderId` 强制对齐

具体 **Δt、n** → **SLO** / **`risk`** / **`exchange-agent`**。

---

## 2. 与 UNKNOWN 交界

若 REST 拉齐 **仍不可判定** → 状态 **留在** [`unknown-state.md`](./unknown-state.md)，**不得**借对账逻辑 **假装终局**。

---

## 3. 收口检查（评审用）

- [ ] **`design/api.md`**：**endpoint 矩阵** **与** **「REST ↔ WebSocket 对账」专节** **已为每条「拉齐用」REST **登记 PATH** **且** **同窗** **§1**  
- [ ] **`exchange-agent`** **FR/SC** 已引用本文矩阵版本号或锚点  
- [ ] **观测**（**如** **`trading.exchange_private.exchangeViewSource`**）可区分「视图来源 = WS / REST / MIXED」以便排障（**同窗** **`observability` §4 · `SC-OBS06`**）

---

**文档版本**：0.2.4 · **维护**：Agent Runtime owner · **本版**：篇首 **补** **ADR-004 / CC-P1-07 / §7.5** **与写路径对账同窗**。**承** **0.2.3**。
