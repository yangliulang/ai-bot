# 域需求：Agent Management（后台 — 模板 / 实例 / 运行控制 / 运行日志）


| 项          | 内容                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **产品**     | ChainUp AI Agent（Coobit 单所）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| **文档**     | `specs/requirements/domains/admin/agent-management/overview.md`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| **状态**     | **域内需求展开**（与 PRD §4、**FR-MC101～114** 会签；细表与验收草案见 [functions.md](functions.md)）                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **PRD 位置** | **[PRD · 模块一 §4](../management-console-v1-prd.md)**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| **互引**     | [management-console-v1-prd.md](../management-console-v1-prd.md) **附录 A**（`configKey`、`agentState`、`FR-M01` 等）；[contract-closure.md](../../../contract-closure.md)；[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)；[access-control/config.md](../access-control/config.md) **§4**（**I02** 前置链第 2 步、`AGENT_*` **code**）；[exchange-agent/overview.md](../../agent/exchange-agent/overview.md)；[agent-orchestration/overview.md](../../agent/agent-orchestration/overview.md)；[billing-management/overview.md](../billing-management/overview.md) §2；[Runtime/overview.md](../../../Runtime/overview.md)、[Runtime/execution.md](../../../Runtime/execution.md)、[Runtime/README.md](../../../Runtime/README.md)；[observability/overview.md](../../../observability/overview.md)；[observability-management/overview.md](../observability-management/overview.md)；[prompt-management/overview.md](../prompt-management/overview.md)；[tool-management/overview.md](../tool-management/overview.md)；[ai-settings/overview.md](../ai-settings/overview.md)；[trading-agent-config/overview.md](../trading-agent-config/overview.md) |


---

## 1. 本域职责（摘要）

本域聚合 **交易所管理后台「模块一」** 与用户侧 Trading Agent **模板—实例—运行—日志** 直接相关的控制台能力。**用户侧编排、计费边界、单次执行语义**仍以 **[flows/](../../../flows/README.md)**、[exchange-agent/overview.md](../../agent/exchange-agent/overview.md)、**附录 A** 为准；本域写的是 **谁在后台做什么、看见什么数据、写入什么审计**。


| 能力                      | 职责（展开）                                                                                                                                                                                                                                                    | SSOT / 备注                                                                                     |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Template Management** | 平台维护 **可被创建的 Agent 蓝图**：名称与业务描述（面向运营）、**绑定**已发布的 Prompt 包、符合矩阵的 Tool Profile、`ai-settings` 中的默认模型引用、以及与 **全局护栏**相容的模板级风控默认；模板 **启用**才可被新发实例选中，**停用**则阻断「创建」路径（存量行为见 [rules.md](rules.md)）。                                                              | Prompt `**prompt-management`**；Tool `**design/api` + trade-assistance**；模型 `**ai-settings`**。 |
| **Agent Instance**      | 按 **用户 + 模板版本** 管理运行实体：创建、列表与检索、详情（含 **只读**绑定信息）、**子账户 / API 绑定关系**（never Secret）、**白名单内**实例参数、删除。创建与绑定须同时满足 **准入、计费、全局 FEATURE、模板可用** 等条件。                                                                                                               | 门禁 `**access-control`**；全局键 **附录 A §5.1**；开户 `**agent/onboarding`**。                          |
| **Runtime Control**     | 对 **单实例**下发 **Start / Pause / Resume / Stop**（实现上 Resume 可与 Start 合并，但 **审计类型**须区分），并展示 **Runtime 摘要**与 **与附录 A `agentState` 一致或可推导** 的状态。与 **全站 `GLOBAL_AGENT_SWITCH`、OPS 级暂停** 的 **叠加规则**见 [rules.md](rules.md)。                                      | **Runtime** 文档；`**agentState`** 枚举 **附录 A §9**。                                               |
| **Agent Logs**          | 在 **实例上下文**内提供 **对话 / Tool / 错误** 三类日志的 **默认运营视图**（时间窗、会话、`**executionId`** 等过滤）；**字段定义、保留、采样、导出、强脱敏** 不在本域重复定义，**一律**与 [observability/overview.md](../../../observability/overview.md) / [observability-management/overview.md](../observability-management/overview.md) 对签。 | 本域负责 **入口 IA 与过滤维度**与实例一致。                                                                    |


**说明**：一次用户消息触发的 **可计费执行**以 `**executionId`** 贯穿；`**scenarioId` / `promptPackVersion**` 等与观测、回归相关字段须 **可 join**，见 **exchange-agent / observability**。本域 **不把**「一个实例 = 一台常驻 OS 进程」写死，**调度与队列**由 Runtime 实现。

---

## 2. 关键概念


| 概念                      | 含义                                                                                                                                         |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Template（模板）**        | 平台侧 **类定义**；含版本线（`templateId` + 单调增的发布版本）。用户 **不**编辑模板正文，只 **选用**模板创建实例。                                                                   |
| **Template Version**    | 一次 **发布**生成的不可变快照；实例创建时 **钉死**某一 `templateVersion`（**FR-AM-I07** 若后续允许「运营升级实例到新模板版本」，须有单独迁移审计与兼容性策略）。                                      |
| **Agent Instance（实例）**  | 某 `userId` 下挂载到 **某一 `templateVersion`** 的运行配置与绑定关系载体；Runtime 命令 **作用在该实例维度**（非「全局用户维度」笼统一条 unless 产品设计如此）。                                |
| `**agentState`（门禁聚合态）** | 附录 A 给出的 **用户/Agent 是否在业务上可被调度**的聚合原因之一；控制台 **可同时展示**：**实例 Runtime 机电状态** + `**agentState` / `lastProductBlockReason`**（运营摘要下限见附录 A §8.2）。 |
| **OPS 全局 Pause**        | **全站或分批**的运营熔断，与 **单实例 Pause** 叠加时取 **严格**规则（通常为「任一暂停则不接单」），须在实现与 `**agentState`** 展示上一致（见 [rules.md](rules.md)）。                        |


---

## 3. 参与者（谁使用本模块）

**V1 缺省**：**以运营后台为主**——**交易所运营 / 风控 / 技术支持**经 **IAM** 使用管理控制台；与用户端 **同源 API**、**分立 RBAC**（见 [functions.md](functions.md) **§8「已决议默认」**、[rules.md](rules.md) **§10**）。若主站另有「我的 Agent」等 **用户自助**路径，须在 **产品与 RBAC** 中 **单列**：**哪些能力与后台同源 API、哪些是后台专有**。**任一**路径下，**审计、Secret 不可见、附录 A 门禁** 均须成立。


| 参与者      | 典型目标                             |
| -------- | -------------------------------- |
| **运营**   | 配模板、帮用户建实例、排障、看日志摘要、Pause/Resume |
| **风控**   | 查绑定与状态、配合封禁/解冻、核对审计              |
| **技术支持** | `executionId` 协查、错误日志跳转、与用户工单对齐  |


---

## 4. 与相邻模块的职责分工


| 主题                     | **本模块**                                 | **不负责（SSOT 在）**                                |
| ---------------------- | --------------------------------------- | ---------------------------------------------- |
| Prompt 正文、发布锁定         | 仅 **选择与绑定**引用 id                        | `**prompt-management`**                        |
| Tool 是否在矩阵内可用          | 仅 **选择与展示** Profile；校验「未冻结不可声称可用」       | `**design/api`、`tool-management`**             |
| 模型目录与 Key              | 模板 **默认模型引用**                           | `**ai-settings`**                              |
| 全所交易默认、 SYMBOL、全局价格偏离等 | 模板风控 **在下层合并**；不写全局键取值                  | `**trading-agent-config`、附录 A**                |
| 计费计划、消耗/配额              | 实例创建时的 **计费资格**校验入口可在此触发；账务主体 **不在此定义** | **`billing-management`、`commerce-model`**          |
| 白名单 VIP、合规封禁           | 创建实例 **须读门禁**                           | `**access-control`**                           |
| 日志 schema、导出合规         | **过滤与下钻入口**                             | `**observability`、`observability-management`** |


---

## 5. 模块一 · 明确不包含（非目标 · V1）

与 PRD **§12** 一致方向，本域 **不**承担：

- **Marketplace** 模板上架/分成/评分。
- **多 Agent 协同编排**（一用户多实例策略若仅「允许多条实例记录」则仍属本域；**跨实例工作流**不属本域）。
- 用户 **自定义任意 Prompt/模型**（仅 **实例白名单参数** 与 **模板已定义** 能力）。
- **Workflow Builder**、**Fine-tuning** 平台。

---

## 6. 文档索引（阅读顺序）


| 顺序  | 文档                             | 内容                                                                                 |
| --- | ------------------------------ | ---------------------------------------------------------------------------------- |
| 1   | [functions.md](functions.md) | FR-AM；**SC-AM-01～23**；**§7.1 错误码**；**§6** FR-MC 映射；**§8** 已决议默认                    |
| 2   | [flow.md](flow.md)           | **G01/T09/I08/R06** 流程、模板/实例门禁 **mermaid**、状态机、审计锚点                                |
| 3   | [config.md](config.md)       | **Banner**、多选/批量、详情 **§8.2 字段**、`batchId`、页面与表单                                    |
| 4   | [rules.md](rules.md)         | 审计（含 **CLONED/BATCH/EXPORT**）、**RBAC**、**§6 模板停用默认**、**§8 全局门禁**、**§10 V1 形态**、错误码 |


