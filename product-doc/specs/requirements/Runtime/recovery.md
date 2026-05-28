# Runtime · 恢复、重试与降级

**职责**：**网关未知、超时、可重试错误**、**Provider/Model 降级**、**出站推送退避** 等在 **平台 Runtime** 与 **域内 `retry-policy`** 之间的 **横切下限**。**`504` / `UNKNOWN` 状态机下限**（须保留 UNKNOWN、禁止冒充终局）→ [`unknown-state.md`](./unknown-state.md)。**码表与 PATH** → **`design/api`**。

> **迁移说明**：原 **`Runtime/fallback.md`**（及 **`retry.md`**）之 **占位立意** **并入**本文；全库外链请使用 **`recovery.md`**。

**同窗**（短）：[`failure-matrix.md`](./failure-matrix.md)；[`runtime-error-taxonomy.md`](./runtime-error-taxonomy.md)；[`execution-transition-matrix.md`](./execution-transition-matrix.md)（**工具重试** **不** **改变** **附录 A** **主行** **终局单调性**）；[`fallback-policy.md`](./fallback-policy.md)；[`unknown-state.md`](./unknown-state.md)；[`error-normalization.md`](./error-normalization.md)；[`reconciliation.md`](./reconciliation.md)；[`domains/agent/agent-orchestration/retry-policy.md`](../domains/agent/agent-orchestration/retry-policy.md)；[`design/api.md`](../../design/api.md)。**横向全表** → [`boundaries.md`](./boundaries.md)。

**交易所私域 IO（`504`/`UNKNOWN`/重试）** **须** **同窗** **统一交易语义** [`canonical-trading-model.md`](../../design/canonical-trading-model.md)、[`ADR-004`](../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../domains/agent/exchange-agent/trade-assistance.md)、[`CC-P1-07`](../contract-closure.md#cc-p1-07)、[`requirements-review` §7.5](../../../product/requirements-review.md#cc-adr004-review-checklist)、[`execution` §1 步 7](./execution.md) — **不得** **冒充成交终局**（见上 **`unknown-state`**）。

**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## UNKNOWN 收口（与 SLA 宿主）

- **`504`/`UNKNOWN`** **停留在** **`unknown_pending`** **时**：**退避/最大查单轮次/超时后的终局或人工路径** **须** **与** [`unknown-state.md`](./unknown-state.md) **「收口与无进展（产品下限）」** **一致**，**不得** **仅以** **无限 Retry** **替代** **闭环**。**具体阈值与配置键** → **`exchange-agent` / `risk` / `design`** **专项 MR**（**见** **`unknown-state` 收口检查**）。

## Retry

- **可重试 vs 终局失败** **须** **可区分**于 **观测**与 **用户 copy**（**不得**无限「请重试」掩盖 **终局**业务拒绝）。  
- **退避与队列** **实现** → **Planner/Executor**；**上限**须与 **SLO/成本** **对签**（同窗 **observability**）。  

## Fallback

- **类型学与 **`prompts/` **分界**：[`fallback-policy.md`](./fallback-policy.md) **§2 场景决策树**（**LLM 超时 / 解析失败 / 工具不可用 / 不安全动作 / 504**）；**§1 类型分类** **见同篇 §1**。  

- **LLM 路由/备用 Model** **须** **可观测**（`modelId`/`providerId` **同窗** **FR-MC804**、**`observability/overview`** 中关于 **`modelId`** 的约定）。  
- **连续 Health 失败** **驱动** **禁止新流量**或 **切换备用** **须**与 **ai-settings** **FR-MC407** **演练一致**。  
- **不得**以 **Fallback** **静默** **削弱** **须用户确认**的写路径（同窗 **exchange-agent boundaries**）。  

## Outbound channels（推送等）

- **APNs / FCM / 厂商通道** 的 **HTTP 429/5xx**、**invalid token**：**退避、DLQ、最大尝试次数** **与本篇 Retry 小节同一套平台语义**；上游载荷形状见 [`integrations/notifications/push-delivery.md`](../integrations/notifications/push-delivery.md)。  
- **与编排重试分清**：会话内 Tool 重试 → [`domains/agent/agent-orchestration/retry-policy.md`](../domains/agent/agent-orchestration/retry-policy.md)；**出站推送队列** → **本文 + `design`**。

**文档版本**：1.0.6 · **维护**：产品 + Agent Runtime owner · **本版**：篇首 **补** **统一交易语义链 / CC-P1-07 / §7.5**（**私域 IO 恢复**）。**承** 1.0.5。
