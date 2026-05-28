# Integrations · Exchange · Futures API

**上游能力面**：合约 REST — [合约交易](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/he-yue-jiao-yi)；通用协议见 [OpenApi 基本信息](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2?fallback=true)。

## 协议约束（摘要）

- **鉴权**：与基本信息中 **`TRADE`** / **`USER_DATA`** 一致。
- **标识字段**：响应中可能同时出现 **`contractId`**、`contractName`、`symbol` / 别名等 — **均为上游载荷事实**；平台选用哪一字段作主键 → **`design`** / **`exchange-agent`**。
- **私有 WS**：订单/仓位推送形态见 [合约订单仓位 WS](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/websocket-tui-song-he-yue-ding-dan-cang-wei)（**帧格式、订阅、`broker` 等上游事实**见 [`websocket-api.md`](websocket-api.md)）。

**对内 PATH 登记表**：[`../../../design/api.md`](../../../design/api.md)。  
**平台运行时**：[`../../Runtime/reconciliation.md`](../../Runtime/reconciliation.md)。
