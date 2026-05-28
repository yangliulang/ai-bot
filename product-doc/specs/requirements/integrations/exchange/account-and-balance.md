# Integrations · Exchange · Account & Balance

**上游能力面**：子账户 — [子账户](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/zi-zhang-hu)；万向划转 — [万向划转](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/qian-bao)；通用错误形状见 [错误码](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/cuo-wu-ma)。

## 协议约束（摘要）

- **母账户接口**：列子账户、创建虚拟子、`authority`/IP 白名单、母↔子划转等 — **路径与 body 字段以外文档为准**。
- **子账户接口**：子向母划转、查询记录；**`accountType`**（现货/逐仓/全仓/场外/合约）等取值为 **上游文档枚举**。
- **响应包裹**：部分接口返回 **`code`/`msg`/`data`** 包裹 — **属上游响应语义**。

**绑定、`CHANNEL`、`subUid` 产品语义**：[`../../domains/agent/onboarding/overview.md`](../../domains/agent/onboarding/overview.md)、**`trading-agent-config`**。  
**对内 PATH 登记表**：[`../../../design/api.md`](../../../design/api.md)。
