# ADR-002：`toolId` / `skillId` 登记表逻辑 SSOT


| 字段           | 内容                                    |
| ------------ | ------------------------------------- |
| **状态**       | 已接受（**文档草案**）                         |
| **日期**       | 2026-05-07                            |
| **决策 owner** | 产品 + 架构接口 owner + Agent Runtime owner |


## 上下文

`[trade-assistance.md](../../requirements/domains/agent/exchange-agent/trade-assistance.md)` §6 与 `[contract-closure.md](../../requirements/contract-closure.md)` **CC-P1-03** 追问：**登记表** 长期可能落在 `**design/api` 文档**、**本文分卷表** **或** **运行时 DB/registry** — **须** **单一逻辑 SSOT** **与演进策略**。

## 决策

1. **逻辑 SSOT（与人类评审入口）**：`**[design/api.md](../api.md)` 子账户 / 工具表** + `**trade-assistance` §4 / §8** — **须同窗**；**OpenAPI `operationId` / PATH** **以矩阵为终裁**（`[contract-closure` §1.2](../../requirements/contract-closure.md)）。
2. **镜像与 DB**：**运行时可** **维护** **registry 表**（性能/Prompt 绑定/cache）；**须** **与 (1)** **幂等对齐** — **差异** **视为** **缺陷** **或** **迁移中短时状态**（**须** **带版本与审计**）。
3. **变更门闸**：**任** `**skillId`/`toolId` 增删改** **须** **同一 MR 或合并窗口** **更新** **(1)** **两处表**（§4/§8 与矩阵行）**并** **递增** `**design/api` 脚注**（**FR-TS07**）。
4. **ADR 演进**：若未来 **强制** **仅 DB** **为唯一写入**：**须** **新 ADR** **废止本条 (1)** **并** **迁移** `**contract-closure` §4** **核对清单**。

## 后果

- **CC-P1-03**：**文档侧** **已有裁断**；**实现** **选用 DB** **不** **推翻** **(1)** **为评审 SSOT**。
- **工具运营域**：`[tool-management](../../requirements/domains/admin/tool-management/overview.md)` **镜像** **仅** **投影**，**不** **另造** **第三套 ID**。

## 引用

- `[trade-assistance.md](../../requirements/domains/agent/exchange-agent/trade-assistance.md)` §4～§8
- `[contract-closure.md](../../requirements/contract-closure.md)` **CC-P1-03**
- **[`closure-remaining` §0](../../requirements/closure-remaining.md#closure-remaining-quicklinks)** · **[§6 / §6.4](../../requirements/closure-remaining.md#cc-exec-solve-path)**（关单余量 / MR 首节）

