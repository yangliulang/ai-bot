# Deeplink · 交易所 OpenAPI 参考

- **文档（GitBook）**：[Open API Basic Information](https://exchangedocsv2.gitbook.io/open-api-doc-v2)（`baseurl`、限频、`X-CH-APIKEY` / `X-CH-SIGN` / `X-CH-TS` 等）
- **开通页默认基准地址**：`https://openapi.coobit.cc`（对应 GitBook [OpenApi Basic Information](https://exchangedocsv2.gitbook.io/open-api-doc-v2) 中的 **`baseurl` `https://openapi.xxx.xx`** 占位范式；Coobit 实例以 **`openapi.` + 主域** 为惯例，**最终以所内网关/运维为准**）
- **实现注意**：真实验签在 **`/be`**；浏览器只传 `openapi_base_url` + Key，不落库 Secret
- **下单体**：`POST /sapi/v2/order` 的 JSON **`symbol`** 使用 **BASE/QUOTE**（如 **`BTC/USDT`**），与 [GitBook · New Order](https://exchangedocsv2.gitbook.io/open-api-doc-v2/spot.md) *Request Body* 一致；**`MARKET BUY`** 时 **`volume`** = 计价 **amount**
- **撤单 / 当前委托**：私有 **`POST /sapi/v2/cancel`**（Body **`symbol`**、**`orderId`**、可选 **`newClientOrderId`**）；私有 **`GET /sapi/v2/openOrders`**（Query **`symbol`**、**`limit`**）；签名见 GitBook **SIGNED**（GET 的 **`requestPath`** 含 **`?`** 及排序后的查询串）
- **现货市价/闪兑写**：私有 **`POST /sapi/v2/order`**（JSON body + **`X-CH-APIKEY` / `X-CH-SIGN` / `X-CH-TS`**）；字段见 [GitBook · Spot](https://exchangedocsv2.gitbook.io/open-api-doc-v2/spot.md)；Agent HTTP 封装：**`GET /api/v1/agent/trade/spot/quote`**、**`POST /api/v1/agent/trade/spot/flash-convert`**、**`POST …/limit-order`**、**`GET …/trade/spot/open-orders`**、**`POST …/trade/spot/cancel`**（见 **`server/docs/API_INTEGRATION_GUIDE.md` §4.3–4.3c**）