# Integrations · Exchange · WebSocket API

**上游能力面**：用户私有推送通道 — 现货侧 [资产变动与订单更新](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/websocket-tui-song-zi-chan-bian-dong-yu-ding-dan-geng-xin)；合约侧 [合约订单仓位](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/websocket-tui-song-he-yue-ding-dan-cang-wei)。

## 协议约束（摘要，以外文档为准）

- **URL**：`wss://…` 路径以外文档为准（环境域名见 **`design`**）。
- **握手**：请求头携带 **`token`** 或 **`api-key`**（按文档两形态）；连接后发送 **`sub`** / **`unsub`**；合约示例含 **`broker`** 字段。
- **载荷**：正式业务消息为 **GZIP 压缩二进制**，需解压后解析 JSON。
- **心跳**：文档示例为周期 **`ping`** / **`pong`**（间隔以外文档为准）。
- **事件类型**：如现货 `outboundAccountPosition`、`executionReport`；合约 `ACCOUNT_UPDATE`、`order`、`trigOrder`、`SYSTEM` 等 — **字段语义以上游文档为准**。

**断线后平台是否 REST 拉齐、退避策略**：[`../../Runtime/reconciliation.md`](../../Runtime/reconciliation.md)、[`../../Runtime/recovery.md`](../../Runtime/recovery.md)。

**对内登记表**：[`../../../design/api.md`](../../../design/api.md)。
