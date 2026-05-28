# Observability · 运行时健康（Runtime Monitor）

**路径**：`specs/requirements/observability/runtime-monitor.md`。

**职责**：**Agent 网关 / Worker / 队列 / 外部依赖** **的健康信号** **与 ** **告警叙事下限** — **与 ** **[`overview.md`](./overview.md) §2 **「单笔执行可追溯」** **正交**：本条关注 **系统能否稳定吃掉负载**，**不 ** **重写 ** **事件字段表**。

---

## 1. 范围

| 在内 | 不在 |
|------|------|
| **Webhook 摄入**、**会话调度队列**、**工具执行池**、**LLM 网关连接** | **单笔 **`executionId`** **业务时间线** — **`overview` §2 + `FR-MC801`**（**主态迁移 Trigger** **见** **§2.4** **`transitionTrigger`**，**不** **本条重写**） |

**恢复与退避**：平台策略 — **[`Runtime/recovery.md`](../Runtime/recovery.md)**；**推送通道** — **[`integrations/notifications/push-delivery.md`](../integrations/notifications/push-delivery.md)**（**集成边界**）。

---

## 2. 健康信号（下限）

| 信号 | 说明 | 典型告警 |
|------|------|-----------|
| **`webhook_ingress_lag`** | Telegram（及后续渠道）**Update **→ **入队 **耗时 | **p99 **>** SLO **→ **扩容或排查下游 |
| **`execution_queue_depth`** | **待调度 **`executionId`** **队列长度 | **持续高位 **→ **背压 / 限流** |
| **`tool_worker_saturation`** | **并发工具槽占用率 | **接近 1 **→ **扩容或 **`toolId`** **隔离** |
| **`exchange_client_circuit`** | **子账户网关 **熔断 **状态 **（开/半开/关） | **与 **`exchange_unknown_rate`**（[`metrics.md`](./metrics.md)）** **同窗复盘** |
| **`llm_stream_timeout_rate`** | **流式响应 **超时 **占比 **按 **`providerId`** | **对齐 **`integrations/llm/provider-routing.md`** |

**标签**：**须 ** **含 **`environment`**、**`region`**（若有）；**禁止 ** **默认可枚举全量 **`userId`** **作为 metric label**。

---

## 3. 控制台（FR-MC805）

**嵌入或外链** **Grafana/Datadog** **等** **须 ** **单点登录 ** **与 ** **只读 IAM** — **[`observability-management/functions.md`](../domains/admin/observability-management/functions.md) `FR-MC805`**、[`observability-management/config.md`](../domains/admin/observability-management/config.md) **§4**。**本条 ** **§2 ** **表 ** **为 ** **看板 ** **最小章节清单** **（实现可增不可减默认章节 **未经 ** **书面 ** **豁免 ** **）。**

---

## 4. 互引

| 文档 | 关系 |
|------|------|
| [`metrics.md`](./metrics.md) | **SLI **→ **告警联动** |
| [`tracing.md`](./tracing.md) | **根 span **标签 **`executionId`** |
| [`Runtime/recovery.md`](../Runtime/recovery.md) | **退避 / 恢复 **政策 |

---

**文档版本**：0.1.1 · **维护**：SRE + Agent Runtime · **本版**：**§1** **「不在」** **脚注** **§2.4。**承** **0.1.0**。
