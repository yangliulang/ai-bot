# Observability · tracing（分布式追踪与执行主锚）

**总则与事件下限**：[`overview.md`](./overview.md) **§2**。  
**控制台 API 占位**：[`design/api.md`](../../design/api.md) 「**运营侧 Logs & Observability API（`admin/observability/*`）**」。  
**后台 IA**：[`../domains/admin/observability-management/config.md`](../domains/admin/observability-management/config.md) **§4**。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 1. 目标

在仍以 **`executionId`** 为 **产品主执行键**（[`exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md) **FR-T01**）的前提下，允许用 APM（Tempo / Jaeger / 云厂商等）的 **`traceId` / `spanId`** 做多服务排障。**运营协查** 默认入口须是 **`executionId`**，并能串起同一次执行的计费、工具与交易所相关事件（[**`FR-MC801`**](../domains/admin/observability-management/functions.md)）。**主态边审计**（**`ObservabilityTimelineEvent.transitionTrigger`** **与** **总则** [**§2.4**](./overview.md) **对签**、**`SC-OBS08`**）**须** **与** **时间线同窗** — **不** **以** **`traceId`** **视图** **替代** **§2.4** **下限**。

---

## 2. 关系（须同窗实现）

| 概念 | 职责 |
|------|------|
| **`executionId`** | **业务锚**：单次可计费 Agent 执行；[`overview` §2](./overview.md) 所列相关事件须携带；**BFF / 控制台主筛**。 |
| **`traceId`** | **基础设施锚**：分布式请求树根 id（例如由 W3C **`traceparent`** 解析）；可选经 HTTP/gRPC 头透传。 |
| **`spanId`** | **基础设施锚**：树内单段调用；是否一一映射到 **`agent.execution.step`** 或 **`agent.tool.call`** 由 **`design`/OpenAPI** 冻结。 |

**规则**：

1. **自分配 `executionId` 起**的网关根 span 须带 **`executionId`** 标签或等价属性（不含 Secret）。
2. **禁止**以 **`traceId`** 替代 **`executionId`** 作为计费、账务或对用户承诺的主锚；[`contract-closure.md`](../contract-closure.md) **轨 B 关单（§8）** **与** **`billing` / `runtime`** **同窗**。
3. **控制台**：默认仅 **`executionId`** 检索暴露给常规运营；**`traceId`** 仅对 **L2+ / 排障** 角色开放——[`observability-management/rules.md`](../domains/admin/observability-management/rules.md)。

---

## 3. OpenAPI（占位）

[`design/api.md`](../../design/api.md) 中 **`GET .../admin/observability/search`** 可支持可选查询参数 **`traceId`**，须与索引能力与 IAM 同窗评审。

---

## 4. 与域内分卷

**审计**：[`audit-log.md`](./audit-log.md)；**SLI / 看板**：[`metrics.md`](./metrics.md)；**网关队列健康**：[`runtime-monitor.md`](./runtime-monitor.md)；**输出阻断协查**：[`hallucination.md`](./hallucination.md)。

---

**文档版本**：0.1.4 · **维护**：SRE + Agent 网关 · **本版**：**§1** **同窗** **`FR-MC801` · §2.4 · `transitionTrigger`。**承** **0.1.3**。
