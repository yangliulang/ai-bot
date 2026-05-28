# Integrations · Exchange · Error Codes（上游）

**职责**：**交易所文档中的**错误表达方式 — HTTP 语义摘要、`{ "code": int, "msg": string }` 载荷形状、文档给出的错误码表。**不**包含 **`stableReason`** 映射、**不**包含平台 recovery 策略。

**对外文档**：[错误码](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/cuo-wu-ma)、[OpenApi 基本信息](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2?fallback=true)（HTTP `4xx`/`5xx`、`504`/`429`/`410`/`418` 等 **文档说明**）。

## 上游载荷形状

- **业务错误**：JSON `code`（整数）+ `msg`（字符串），见基本信息示例。
- **HTTP 与 JSON 并存**：网关实现需同时理解两层 — **如何实现 / 如何映射** → [`../../Runtime/error-normalization.md`](../../Runtime/error-normalization.md)。

## 文档中的分类（示意）

GitBook 将错误分为「通用服务器与网络错误」「请求内容问题」等 — **可重试与否须结合文档描述与 HTTP 语义逐条判断**；平台级「可重试清单」→ **`Runtime/recovery.md`**，不在本分卷重复展开。

**对内登记表**：[`../../../design/api.md`](../../../design/api.md)。**平台 `stableReason` 字面 + Runtime Taxonomy** → **`api.md` 附录**；**叙事** [`../../../Runtime/runtime-error-taxonomy.md`](../../../Runtime/runtime-error-taxonomy.md)、[`../../../Runtime/error-normalization.md`](../../../Runtime/error-normalization.md)。
