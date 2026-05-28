# Observability · 指标与看板（Metrics）

**路径**：`specs/requirements/observability/metrics.md`。

**职责**：把 **可观测信号** **落成** **SLI 命名空间与数据源**，供 **FR-MC805**（[`observability-management/functions.md`](../domains/admin/observability-management/functions.md)）**嵌入看板或外链**。**不**重复 **[`overview.md`](./overview.md) §2** **事件字段 SSOT** — 本条只定义 **「从哪些事件/计数聚合」**。

---

## 1. 与域索引的关系

| 主题 | 索引文档 |
|------|-----------|
| **可靠性 / UNKNOWN / 504** | [`../metrics/reliability.md`](../metrics/reliability.md)、[`../../design/architecture.md`](../../design/architecture.md)、[`Runtime/recovery.md`](../Runtime/recovery.md) |
| **AI / Token / 回合** | [`../metrics/ai-metrics.md`](../metrics/ai-metrics.md)、[`integrations/llm/token-usage.md`](../integrations/llm/token-usage.md) |
| **交易结果 / 矩阵维度** | [`../metrics/trading-metrics.md`](../metrics/trading-metrics.md)、[`exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md) |

---

## 2. SLI 清单（下限 · 命名示意）

**基数约束**：**默认** **按** **`scenarioId`**、**`toolId`（聚合 TOP-N）**、**`modelId`** **分桶** — **禁止** **将 `userId` 写入 high-cardinality label** **作为默认**（**须** **采样或聚合层** **冻结**）。

| SLI（示意名） | 定义 | 数据源 |
|---------------|------|--------|
| **`billing_entitlement_debit_accept_ratio`** | **`billing.entitlement_debit_success` / (`billing.entitlement_debit_attempt` − 明确取消类)** **滑动窗**（**Agent 消耗主链**） | **`overview` §2** |
| **`billing_charge_accept_ratio`** | **`billing.charge_success` / (`billing.charge_attempt` − 明确取消类)** **滑动窗**（**轨 A 对读**） | **`overview` §2** `billing.*` 事件 |
| **`exchange_unknown_rate`** | **`trading.exchange_private`** **`exchangeOutcome=unknown`** **占比**（**写路径** **优先**） | **`overview` §2.2**、`SC-OBS03` |
| **`tool_invocation_fail_rate`** | **`agent.tool.call`** **`phase=fail`** **或** **`invocationState=FAILED`**（按 **`toolId`**） | **`overview` §2.1、`SC-OBS05`** |
| **`orchestration_missing_scenario_rate`** | **已调 B/C 工具但** **同 **`executionId`** **缺 **`scenarioId`** **join** **计数**（**应对 SC-OBS01**） | **`overview` §2.1** |
| **`view_source_mixed_ratio`** | **`exchangeViewSource=MIXED`** **占比**（**对账复杂度哨兵**） | **`overview` §2、`SC-OBS06`** |
| **`telegram_webhook_lag_p99`** | **Telegram Update **接收 **→** **首条 **`agent.*`** **落库 **延迟 **p99**（**所内 span**） | **APM** **`traceId` span** + **[`integrations/telegram/webhook.md`](../integrations/telegram/webhook.md)** |
| **`llm_provider_error_rate`** | **模型网关 **5xx/超时 **按 **`providerId`** | **[`integrations/llm/provider-routing.md`](../integrations/llm/provider-routing.md)** + **网关日志** |

---

## 3. 告警与复盘（叙事下限）

- **页级**：**`exchange_unknown_rate`** **突增** **须** **联动 ** **`Runtime/reconciliation`** **矩阵变更 ** **或 ** **所内网关发布** **之复盘条目**。  
- **计费**：**`billing_entitlement_debit_accept_ratio`**（**主链**）**与** **`billing_charge_accept_ratio`**（**对读**）**跌破 SLO** **须** **可分 **`failureClass`** **（[`billing.md`](../domains/admin/billing-management/overview.md) **同窗）**。  
- **产品门禁**：**`GLOBAL_AGENT_SWITCH=OFF`** **时段** **指标** **须** **标注** **「停机」** **避免误告警**（[`management-console-v1-prd.md`](../domains/admin/management-console-v1-prd.md) **`FEATURE_*`** **同窗**）。

---

## 4. 互引

| 文档 | 关系 |
|------|------|
| [`overview.md`](./overview.md) | **事件 SSOT** · **SC-OBS*** |
| [`tracing.md`](./tracing.md) | **APM** **与 **`executionId`** **标签** |
| [`domains/admin/observability-management/functions.md`](../domains/admin/observability-management/functions.md) | **`FR-MC805`** |

---

**文档版本**：0.1.0 · **维护**：SRE + 产品 · **本版**：占位 **落地** **SLI 清单与数据源锚**。
