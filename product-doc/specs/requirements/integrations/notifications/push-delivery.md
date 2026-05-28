# Integrations · Notifications · Push Delivery

**上游职责**：各移动推送通道的 **供应商 HTTP API / SDK 载荷形状**（典型：**APNs**、**FCM HTTP v1**）。**整页字段表**以 Apple/Google 官方文档与 **`design/api.md`** 登记表为准。

## 协议约束（摘要）

- **APNs**：HTTP/2 至 Apple 提供的主机；**development vs production** **端点不同** — **环境混用属集成配置错误**，登记表须在 **`design`** 区分。
- **FCM**：HTTP v1 至 **`fcm.googleapis.com`**（路径与 OAuth 凭据见 Google 文档）。
- **设备标识**：APNs **`device token`**、FCM **`registration token`** — **二进制/字符串编码**以上游为准。
- **载荷**：JSON **`aps`** / **`data`**（APNs）或 **FCM `message`** 结构 — **字段约束以上游为准**。

## 非目标

- **退避、DLQ、`notificationId` 幂等打扰** — [`../../Runtime/recovery.md`](../../Runtime/recovery.md)（通用队列语义）+ **`design`**。
- **载荷内是否带 `stableReason`、营销 opt-out** — [`../../Runtime/error-normalization.md`](../../Runtime/error-normalization.md)、**`risk`**、**`billing`**。
- **站内信降级** — **产品 / `design`**。

**重试**：[`retry-policy.md`](retry-policy.md)。
