# Tools（Tool Calling 索引）

**PATH / `operationId` 终裁**：[`../../design/api.md`](../../design/api.md)。  
**`toolId` / A·B·C 登记与 §8 分卷**：[`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md)。  
**对上 Coobit 的 B/A 工具执行 HTTP**：**默认经** **`openapi-ai` 官方宿主**（[`integrations/exchange/overview.md`](../integrations/exchange/overview.md)）；**`skillId`/`toolId` SSOT 不因更换宿主而拆分**。

**运行时契约**（`invocationState`、`toolRiskLevel`、Result 信封、权限链）：[`../domains/admin/tool-management/runtime-contract.md`](../domains/admin/tool-management/runtime-contract.md)。

本目录 **不** 另造工具 SSOT，只提供 **仓库内导航 + 片段 Schema 载体**。

| 文档 | 用途 |
|------|------|
| [`tool-registry.md`](tool-registry.md) | **`skillId`/`toolId`** 与 §8 / `schemas/` / 流程 **对照索引** |
| [`permission-matrix.md`](permission-matrix.md) | **类 A/B/C · 运营 Profile · 风险级** 摘要（矩阵仍以 **`design` + `exchange-agent`** 为准） |
| [`schemas/README.md`](schemas/README.md) | JSON Schema **片段目录**；与 OpenAPI **冲突以 `design/api` 为准** |
| [`../standards/tool-standard.md`](../standards/tool-standard.md) | 书写规范 **薄索引** |

**`trade-assistance` §8 锚**（引用宿主）：[§8.1 类定义](../domains/agent/exchange-agent/trade-assistance.md#ta-81) · [§8.2 A 写表](../domains/agent/exchange-agent/trade-assistance.md#ta-82) · [§8.3 B 类只读](../domains/agent/exchange-agent/trade-assistance.md#ta-83) · [§8.4 C 类](../domains/agent/exchange-agent/trade-assistance.md#ta-84) · [§8.5 自动化](../domains/agent/exchange-agent/trade-assistance.md#ta-85)。

**编排 / 流程**：[`../domains/agent/agent-orchestration/routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md)、[`../domains/agent/agent-orchestration/execution-lifecycle.md`](../domains/agent/agent-orchestration/execution-lifecycle.md)、[`../flows/trade-via-agent.md`](../flows/trade-via-agent.md)、[`../flows/read-analyze-and-search-via-agent.md`](../flows/read-analyze-and-search-via-agent.md)。

## 维护约定

1. **新增或改名 `toolId`/`skillId`**：先改 **`design/api.md` 登记表** 与 **`trade-assistance` §4 / §8**（**同行数/顺序** 与 **FR-TS07** 对签），再视需要更新本目录 **`tool-registry`** 与 **`schemas/`**。  
2. **JSON Schema 片段**：仅作 Codegen/内省补充；字段以 **OpenAPI** 冻结为准，**冲突删片段或标 TBD**。  
3. **权限 / 风险**：运营 **`FR-TM03` / Tool Profile** 见 **`tool-management/functions`**；**`toolRiskLevel`、Retry** 见 **`runtime-contract`**。

## 未来拆分（可选）

若 **B 类只读** 或 **C 类外网** 条文过长，可增设 `market-data.md`、`external-tools.md` 等 **从本 README 链出**，**登记表仍不归此类文件独有**。
