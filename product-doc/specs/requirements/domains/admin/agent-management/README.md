# Agent Management（`admin/agent-management/`）

**聚合 PRD**：[`../management-console-v1-prd.md` §4](../management-console-v1-prd.md)

**与 `standards/Log` 历史条**：本目录 **`config.md` 等** 为 **模块一** **现行有效** **需求**；[`standards/Log.md`](../../../standards/Log.md) 中 **曾记**「仅 README」**之** **批次** **已被** **后续** **恢复** **建档** **覆盖** — **以** **本表** **与** **PRD** **为准**。

| 文件 | 内容（已展开） |
|------|----------------|
| [`overview.md`](overview.md) | **职责四章**深度说明、**关键概念表**、**参与者**、**与相邻模块分工**、**非目标**、阅读顺序 |
| [`functions.md`](functions.md) | FR-AM + **`§8`/`§9`/`§10`** · SC-AM **01～23** · **§7.1 错误码契约** |
| [`flow.md`](flow.md) | 含 **G01 横幅**、**T09 克隆**、**I08 导出**、**R06 批量**（**全局 OFF** 与 G01 **冻结一致**） |
| [`config.md`](config.md) | **§3 实例列表/详情 IA**（默认列、单行关键字、页头副区、绑定 Tab **不含**顶层运营提示等）、**Banner**、实例 **多选/批量条**、附录 A §8.2 **详情字段**、`batchId`、**§5** 字段–OpenAPI 对齐 |
| [`rules.md`](rules.md) | **审计矩阵**、删除、Pause/OPS、密钥、**RBAC**、日志边界、**§8 全局门禁**、**§10 IAM/V1 形态**、错误码 |

**建议阅读**：`overview` → `functions`（业务真值）→ `config`/`flow`（实现与 UX）→ `rules`（合规模块）。
