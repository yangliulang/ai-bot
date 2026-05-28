# Integrations · Exchange · Spot API

**上游能力面**：币币（现货）REST — 详见 [币币交易](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/bi-bi-jiao-yi)；术语与订单枚举见 [ENUM](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/enum)；通用协议见 [OpenApi 基本信息](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2?fallback=true)。

## 协议约束（摘要，以外文档为准）

- **鉴权类型**：交易 / 账户读接口一般为 **`TRADE`** / **`USER_DATA`**（见基本信息中的鉴权类型表）。
- **参数位置**：`GET` → query string；`POST` → JSON body；`Content-Type: application/json`。
- **签名**：`TRADE`/`USER_DATA` 使用 **`X-CH-SIGN`** / **`X-CH-TS`** / **`X-CH-APIKEY`**（算法与拼接串见基本信息）。
- **幂等能力**：文档支持 **`newClientOrderId`**（及长度约束）— **字段存在性与约束属于上游**；平台如何用该键属于 **`design`** / **`Runtime`**。
- **限频**：按接口标注的 **IP/UID 权重**（见基本信息与各接口说明）。

**对内 PATH 登记表**：[`../../../design/api.md`](../../../design/api.md)。  
**平台运行时（未知态、对账、归因）**：[`../../Runtime/overview.md`](../../Runtime/overview.md)。
