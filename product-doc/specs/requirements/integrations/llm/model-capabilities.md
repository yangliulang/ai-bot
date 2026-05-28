# Integrations · LLM · Model Capabilities

**上游职责**：各供应商 HTTP API 对 **`model`**（或等价）暴露的 **能力差异** — 上下文上限、`max_tokens`、是否接受 **`tools`/function calling**、是否接受 **vision / 多模态部件** 等，**以供应商文档 + `ai-settings` 模型目录快照为准**。

**配置 SSOT**：[`../../domains/admin/ai-settings/overview.md`](../../domains/admin/ai-settings/overview.md)。  
**Prompt 拼装**：[`../../domains/admin/prompt-management/overview.md`](../../domains/admin/prompt-management/overview.md)。

## 协议约束（摘要）

- **请求侧**：常见可选字段包括 **`temperature`**、**`top_p`**、**`stop`**、**`response_format`**（是否支持视模型）；**必填 / 禁止组合** 以上游为准。
- **工具调用**：若上游支持 **tools/functions**，请求与响应中的 **tool_calls** 结构 **遵循该供应商 schema**（**`design`** 可冻结子集）。
- **超长输入**：上游返回 **400 类错误**与错误 JSON — **载荷形状**归 **`integrations`**；是否映射为平台归因 → [`../../Runtime/error-normalization.md`](../../Runtime/error-normalization.md)。

## 非目标

- 网关 **是否在出站前预估 token**、是否剥离 tools — **Runtime / `risk`** / **`exchange-agent`**（依场景）。

**出站连接**：[`provider-routing.md`](provider-routing.md)。
