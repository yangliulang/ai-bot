# Tool Schemas（JSON 片段目录）

**主契约与登记表**：[`../../../design/api.md`](../../../design/api.md)。  
**`toolId` / 类定义**：[`../../domains/agent/exchange-agent/trade-assistance.md`](../../domains/agent/exchange-agent/trade-assistance.md) §8。

**规则**：此处文件为 **节选**；若与 **OpenAPI / 矩阵** **不一致**，以 **`design/api` MR** 为准，**更新或删除**本目录对应片段，并在 MR 说明 **差异原因**。

| 文件 | 用途 | `toolRiskLevel`（示意） |
|------|------|-------------------------|
| [`get-balance.schema.json`](get-balance.schema.json) | **B 类** 账户只读 · 余额族（矩阵名 **`operationId`** 终裁） | LOW |
| [`get-position.schema.json`](get-position.schema.json) | **B 类** 仓位/持仓只读（示意） | LOW |
| [`create-order.schema.json`](create-order.schema.json) | **A 类写** 下单入参 **形状示意** | MEDIUM |
| [`cancel-order.schema.json`](cancel-order.schema.json) | **A 类写** 撤单入参 **形状示意** | MEDIUM |

**Meta**：草案 [**JSON Schema 2020-12**](https://json-schema.org/draft/2020-12/schema)；**`$id`** 未分配 URI — **OpenAPI 合入**时可同步注册。

**导航**：[`../tool-registry.md`](../tool-registry.md)、[`../permission-matrix.md`](../permission-matrix.md)。
