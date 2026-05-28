# Runtime · 邻域边界

各分卷篇首 **同窗** 仅列 **本篇直接依赖**；**与 `domains` / `design` / `integrations` / `observability` 的横向分工** 以 **下表** 为全表索引。

本文 **固定** **`Runtime/`** 与各域 / 设计的 **SSOT 分工**；与 [`overview.md`](overview.md) **§2** 对读。

| 主题 | **权威仍优先在** | **`Runtime/` 分卷** |
|------|------------------|---------------------|
| 交易门禁、工具壳、用户侧稳定码 | [`domains/agent/exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md) | [execution.md](./execution.md)、[runtime-state.md](./runtime-state.md) **仅**串联结论 + **指向 FR/§** |
| 配置叠层、确认/仓位、Kill、会话冻结（产品政策） | [`domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md) | [freeze-policy.md](./freeze-policy.md)、[recovery.md](./recovery.md) **政策层**；码表 **仍** `design` + `flow` |
| `scenarioId`、DAG、步骤寄存器 | [`domains/agent/agent-orchestration/routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md)；索引 [`overview.md`](../domains/agent/agent-orchestration/overview.md) | [execution.md](./execution.md)、[freeze-policy.md](./freeze-policy.md) **与观测字段绑定的序** |
| 编排 **FR-AO***、用户可见重试叙事 | [`domains/agent/agent-orchestration/overview.md`](../domains/agent/agent-orchestration/overview.md)、[`retry-policy.md`](../domains/agent/agent-orchestration/retry-policy.md)、[`session-concurrency-policy.md`](../domains/agent/agent-orchestration/session-concurrency-policy.md) **（单 session inbound/多 execution）** | [recovery.md](./recovery.md) **平台级**退避/队列 |
| 上下文预算、压缩、爆炸 | [`domains/agent/agent-context/overview.md`](../domains/agent/agent-context/overview.md) | [context-management.md](./context-management.md) |
| Prompt 注入与版本 | [`domains/admin/prompt-management/overview.md`](../domains/admin/prompt-management/overview.md) | 「**拉取/注入失败**」产品与验收 **链回 PM FR**；**Fallback **类型学 **vs **`prompts/`** **分层 ** → [`fallback-policy.md`](./fallback-policy.md) |
| 会话绑定、Deeplink、FR-T05 | [`domains/agent/onboarding/telegram-binding.md`](../domains/agent/onboarding/telegram-binding.md) | [sessions.md](./sessions.md) **执行态**交界 |
| HTTP、幂等、`operationId`、504 | [`design/api.md`](../../design/api.md) | [recovery.md](./recovery.md)、[persistence.md](./persistence.md) **需求语义** |
| 交易所 **上游**协议/码表/WS 格式（GitBook） | [`integrations/exchange/`](../integrations/exchange/overview.md) | [unknown-state.md](./unknown-state.md)、[reconciliation.md](./reconciliation.md)、[error-normalization.md](./error-normalization.md)、[failure-matrix.md](./failure-matrix.md)、[recovery.md](./recovery.md) — **平台如何应对** |
| LLM **上游** HTTP / SSE / `usage` 形状 | [`integrations/llm/`](../integrations/llm/provider-routing.md) | [error-normalization.md](./error-normalization.md)、[recovery.md](./recovery.md) |
| Telegram **上游** Bot API / Webhook `Update` | [`integrations/telegram/bot-api.md`](../integrations/telegram/bot-api.md) | [error-normalization.md](./error-normalization.md)、[sessions.md](./sessions.md) **交界** |
| 推送 **上游** APNs/FCM 载荷 | [`integrations/notifications/push-delivery.md`](../integrations/notifications/push-delivery.md) | [recovery.md](./recovery.md)、[error-normalization.md](./error-normalization.md) |
| 审计日志字段 SSOT | [`observability/overview.md`](../observability/overview.md)、[`observability/audit-log.md`](../observability/audit-log.md)（若存在） | [event-storage.md](./event-storage.md) **与 execution 关联键** |

**原则**：冲突时以 **域正文 + `design` +书面 OVERRIDE** 为准；本篇 **仅**导航。

---

**文档版本**：1.0.3 · **维护**：产品 + Agent Runtime owner · **本版**：交易所行 **同窗** **`failure-matrix`**。**承** 1.0.2。
