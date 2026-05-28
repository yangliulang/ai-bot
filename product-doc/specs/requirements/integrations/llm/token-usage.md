# Integrations · LLM · Token Usage

**上游职责**：多数 LLM HTTP API 在 **响应体**（或非流式最后一帧）附带 **`usage`** 对象：`prompt_tokens`、`completion_tokens` 等；**字段名与是否在 stream 中返回** **因供应商而异**（以公开文档为准）。

## 协议约束（摘要）

- **形状**：常见为嵌套 JSON **`usage: { prompt_tokens, completion_tokens, total_tokens }`**；亦可能存在 **`reasoning_tokens`** 等扩展 — **以上游为准**。
- **缺失**：部分组合下 **`usage` 可能不存在或滞后** — **属上游行为事实**。
- **请求 ID**：部分供应商返回 **`id`** / **`x-request-id`** 类头 — **用于排障关联**，是否入库 → **`design`** / **`observability`**。

## 非目标

- **计费主键、配额耗尽 UX、是否对部分失败计费** — [`../../domains/admin/billing-management/overview.md`](../../domains/admin/billing-management/overview.md)、**`risk`**、**`Runtime/recovery`**。
- **用量表是否存 prompt 正文** — **`observability`** / 留存策略。

**连接**：[`provider-routing.md`](provider-routing.md)。
