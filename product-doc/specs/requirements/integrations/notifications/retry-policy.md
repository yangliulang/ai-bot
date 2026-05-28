# Integrations · Notifications · Retry Policy

本分卷 **不定义** 平台队列退避、DLQ、`max_inflight` 等政策 — 已与 **`integrations`**「仅上游契约」原则冲突。

**去向**：

- **通用重试、降级、UNKNOWN 叙事**：[`../../Runtime/recovery.md`](../../Runtime/recovery.md)。
- **编排 / Tool / 会话重试**：[`../../domains/agent/agent-orchestration/retry-policy.md`](../../domains/agent/agent-orchestration/retry-policy.md)。
- **推送供应商 HTTP 状态码 / 429**：**APNs/FCM 官方文档**（上游）；映射到平台 **`stableReason`**：[`../../Runtime/error-normalization.md`](../../Runtime/error-normalization.md)。

**上游通道形状**：[`push-delivery.md`](push-delivery.md)。
