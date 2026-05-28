# Integrations · LLM · Provider Routing

**上游职责**：Agent 网关经 **HTTPS** 调用各 LLM / 中转商 HTTP API（路径族以 **`design`** **`admin/ai/*`** 与服务商公开文档为准）。

**运营配置 SSOT**（非上游正文）：[`../../domains/admin/ai-settings/overview.md`](../../domains/admin/ai-settings/overview.md)（Provider、`modelId`、`baseUrl`、`secretRef`、Health）。

## 协议约束（摘要）

- **传输**：TLS；请求体多为 **JSON**（具体 schema 因供应商而异，**以内 OpenAPI 登记表为准**）。
- **鉴权**：常见形态为 **`Authorization: Bearer …`** 或 **`api-key` 类请求头** — **以供应商文档 + `design` 为准**；浏览器 **不得**持有 Secret（属 **`ai-settings`/`secrets`** 叙事，非 HTTP 语法）。
- **路由参数**：请求级 **`model`** / **`modelId`**（字段名因供应商而异）用于选用模型 — **上游载荷事实**。
- **流式**：若启用 **SSE / chunked JSON**，帧边界与结束条件 **以供应商文档为准**；**平台如何在半截响应时计费 / 中断** → [`../../Runtime/recovery.md`](../../Runtime/recovery.md)、[`token-usage.md`](token-usage.md)（仅 **上游是否返回 usage**）。

## 非目标（本分卷）

- Health 探针策略、熔断阈值、降级链路、超时档位 — **`Runtime/recovery.md`**、**`ai-settings` FR**。
- **`stableReason`**、trace 字段矩阵 — [`../../Runtime/error-normalization.md`](../../Runtime/error-normalization.md)、[`../../observability/overview.md`](../../observability/overview.md)。

**能力与字段语义**：[`model-capabilities.md`](model-capabilities.md)、[`token-usage.md`](token-usage.md)。  
**对内登记表**：[`../../../design/api.md`](../../../design/api.md)。
