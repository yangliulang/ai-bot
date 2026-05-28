# 设计（Design）

在需求基线之上描述 **系统如何满足需求**（非实现代码）。

| 文件 / 目录 | 说明 |
|-------------|------|
| [overview.md](overview.md) | **入口重定向** → 以 `architecture.md` 为主 SSOT |
| [architecture.md](architecture.md) | **逻辑架构**：C4 语境/容器、信任边界、**504 / 对账 / D-1**、主数据流；**「与通用 Agent 栈之对照」**（Runtime / Gateway / 意图中心 vs Prompt+Tool-only） |
| [canonical-trading-model.md](canonical-trading-model.md) | **统一交易语义（设计 SSOT · 草案）**：Intent → Canonical → Gateway → Adapter · `venue`；**ADR** [**ADR-004**](adr/004-intent-centric-execution-and-canonical-trading-model.md)；**同窗** `architecture` **文档地图** |
| [deployment.md](deployment.md) | **逻辑部署**：环境、发布原则、部署单元；物理拓扑 **Infra 回填** |
| [api.md](api.md) | 对外/对内接口与事件契约要点；**所内登记表、填写清单**、**子账户 endpoint 矩阵**、**API 执行边界**；**Telegram Bot API** 见 §「Telegram Bot API」，详 **[domains/agent/telegram/overview.md §2.5 · 类型 A、§2～§2.6](../requirements/domains/agent/telegram/overview.md)** |
| [OWNERS.md](../openapi/OWNERS.md) | **B 阶段** **登记表 Owner 花名**回填表（与 **`api.md` 登记表** **对签**） |
| [runtime-architecture.md](runtime-architecture.md) | 运行时 **组件级** 展开 **挂载点**（与 `architecture.md`、`deployment.md`、`Runtime/*`、`exchange-agent` 对签后充实；篇首 **已锚需求边界**） |
| [market-narrative-runtime.md](market-narrative-runtime.md) | **MNRA 设计面** · PhaseRules v0（**阈值占位**）；需求总入口 [`market-narrative-runtime/README`](../requirements/market-narrative-runtime/README.md) |
| [memory-runtime-injection.md](memory-runtime-injection.md) | **Memory · STM/LTM 召回/四原则硬闸/裁剪管线 v0**；同窗 **`memory-runtime` §9～§16**、**`keys` §2.1**、**`memory-runtime-schemas.yaml`** |
| [sub-account-isolation.md](sub-account-isolation.md) | 子账户隔离设计切片 |
| [tool-calling-sequence.md](tool-calling-sequence.md) | 工具调用时序切片 |
| [requirements-daily-report-feishu.md](requirements-daily-report-feishu.md) | **产品视角 · 需求与范围日报 → 飞书群**：模版、Owner、对齐口径；技术实现见篇末附录（非群发正文） |
| [adr/](adr/README.md) | **ADR**：**ADR-001**（Telegram 确认先于写）、**ADR-004**（意图中心 · Canonical · Gateway）、**ADR-002～003** — [`adr/README`](adr/README.md) |

需求侧 SSOT：`../requirements/product.md` 与 `../requirements/domains/`。**运行时横切需求**：[`Runtime/overview.md`](../requirements/Runtime/overview.md)。**契约收口索引**（矩阵 TBD → 可对签、**[`management-console-v1-prd.md` §13](../requirements/domains/admin/management-console-v1-prd.md)**、解冻 MR）：[`contract-closure.md`](../requirements/contract-closure.md)（**文档侧收尾登记**：**§8**）。**Open 项总表 / 闭环路径 / MR 勾选**：[`closure-remaining.md`](../requirements/closure-remaining.md)（**[§7](../requirements/closure-remaining.md#cc-remaining-open-items)** · **[§7.5](../requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../requirements/closure-remaining.md#cc-closure-exec-checklist)**）。
