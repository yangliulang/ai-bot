# Integrations · Exchange · Order Lifecycle（上游语义）

**职责**：**交易所文档中的**订单状态、推送事件含义与字段角色 — **不是**平台会话状态机、不是 REST 兜底策略。

**对外文档**：现货 [币币交易](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/bi-bi-jiao-yi)、杠杆 [杠杆交易](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/gang-gan-jiao-yi)、合约 [合约交易](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/he-yue-jiao-yi)；枚举 [ENUM](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/enum)；现货 WS [资产变动与订单更新](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/websocket-tui-song-zi-chan-bian-dong-yu-ding-dan-geng-xin)、合约 WS [合约订单仓位](https://exchangedocsv2.gitbook.io/open-api-doc-v2/jian-ti-zhong-wen-v2/websocket-tui-song-he-yue-ding-dan-cang-wei)。

## 上游订单状态（ENUM 摘录）

文档列举包括但不限于：`NEW`、`PARTIALLY_FILLED`、`FILLED`、`CANCELED`、`PENDING_CANCEL`、`REJECTED` — **以后续 GitBook 为准**。

## 上游推送（现货示例语义）

- **`executionReport`**：文档定义字段如事件时间、订单 ID、`X` 当前状态等 — **语义以上游表为准**。
- **文档注明**：市价单 **可能不推送** `executionReport` — **属上游行为事实**；平台补救 → **`Runtime/reconciliation.md`**。

## 上游推送（合约示例语义）

- **`order` / `trigOrder` / `ACCOUNT_UPDATE`** 等通道与字段 — **以上游文档为准**。

**平台 UNKNOWN、对账次序、用户确认流**：[`../../Runtime/unknown-state.md`](../../Runtime/unknown-state.md)、[`../../Runtime/reconciliation.md`](../../Runtime/reconciliation.md)、[`../../domains/agent/agent-orchestration/confirmation-flow.md`](../../domains/agent/agent-orchestration/confirmation-flow.md)。

**对内 PATH**：[`../../../design/api.md`](../../../design/api.md)。
