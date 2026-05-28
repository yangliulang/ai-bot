# Integrations · Exchange · Margin API

**上游能力面**：杠杆 REST — [杠杆交易](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/gang-gan-jiao-yi)；枚举见 [ENUM](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/enum)。

## 协议约束（摘要）

- **鉴权**：一般为 **`TRADE`** / **`USER_DATA`**（见基本信息）。
- **路径与字段**：与 **现货 REST 分流**（具体 PATH 以外文档与 **`design`** 为准）；`symbol` 表示形态（如是否含 `/`）**以上游示例为准**，归一化策略 **不属于**本分卷。

**对内 PATH 登记表**：[`../../../design/api.md`](../../../design/api.md)。
