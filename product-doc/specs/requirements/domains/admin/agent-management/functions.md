# Agent Management · 功能清单、需求展开与验收草案

**叙事**：[overview.md](overview.md)；**产品汇总**：[management-console-v1-prd · §4](../management-console-v1-prd.md)。

- **§7** SC-AM **01～24**；**§8** **已决议默认**（评审收口）；**§9** 完整性自检；**§10** 清单对照。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. Template Management — 平台定义「可创建哪些 Agent」

负责 **交易 Agent 模板** 的全生命周期：**停用**后 **不可再创建**新实例（存量策略见 [rules.md](rules.md)）。


| 域内编号          | 一级功能             | 二级功能      | 功能描述                                                                                             | 会签备注                                |
| ------------- | ---------------- | --------- | ------------------------------------------------------------------------------------------------ | ----------------------------------- |
| **FR-AM-T01** | Template 列表      | 查看模板      | 展示 **全部** Agent 模板（含版本/状态摘要）                                                                     | 须支持筛选、排序、与 **启用状态** 联合过滤            |
| **FR-AM-T02** | 创建 Template      | 创建模板      | **创建**一条新的交易 Agent 模板                                                                            | 创建即写 **审计**                         |
| **FR-AM-T03** | 编辑 Template      | 修改模板      | **编辑**已有模板                                                                                       | **已发布·冻结**态走 **新版本**路径              |
| **FR-AM-T04** | Prompt 绑定        | Prompt 配置 | 绑定 **Prompt 包 / 场景**                                                                             | 仅 **已发布**；**健康** **与** **[`prompt-management`](../prompt-management/overview.md) revision/scope** **对签**（**§1.1**） |
| **FR-AM-T05** | Tool 绑定          | Tool 配置   | 绑定 **Tool Profile**                                                                              | **禁止**未冻结 PATH                      |
| **FR-AM-T06** | 默认模型             | Model 配置  | 模板 **默认 LLM**                                                                                    | 须在运营白名单内；下线策略 **§8**                |
| **FR-AM-T07** | 默认风控             | 风控配置      | 模板级 **默认风控 / 护栏**                                                                                | **合并**：全局为底、模板 **可收紧不可放宽**，见 **§8** |
| **FR-AM-T08** | Template 状态      | 启用 / 停用   | 控制 **是否允许创建**                                                                                    | 存量：`**[rules](rules.md)` §6**       |
| **FR-AM-T09** | Template 克隆      | 复制为新模板    | 基于 **指定模板（某 `templateVersion`）** 生成 **新 `templateId`** 的 **草稿**，复制 Prompt/Tool/模型/风控引用           | **不**复制发布/启用状态；**须**审计；名称 **须**防冲突  |
| **FR-AM-T10** | Template 删除 / 归档 | 删除草稿或归档策略 | `**DRAFT` 且无 FK 阻断**可 **删除**；**已发布**走 **T08 停用**，**不按物理删除主路径**；合规强掩码 → `**contract-closure`** MR | FK / 计费 **实现对签**                    |


### 1.1 需求展开（Template）

**T01 列表**：默认按 **更新时间倒序**。筛选项至少：**启用状态**、**模板名称关键字**、`templateId` 精确、依赖引用（可选高级筛）。每条展示：**名称、templateId、当前发布版本号、启用/停用、最近发布时间与操作者**。支持进入 **版本履历**（只读时间线）。

**T02 创建**：创建后默认 **草稿**态。必填：**内部名称**（运营可见）、**对外展示名**（是否与用户端一致由产品定）。可选：**描述、标签**。创建成功进入 **编辑页**，记 **审计：created**。

**T03 编辑**：**草稿**可改配置；**已发布**仅允许（a）**新建版本**（复制快照为新草稿，旧版只读）；（b）若存在 **元数据热更白名单**则仅限该集合（默认 **无热更**）。**禁止**不 bump 版本而直接改 Prompt/Tool/模型/风控引用。

**T04 Prompt**：下拉/搜索 **已发布** `promptPack`（或场景 id），保存 **引用 id + 展示标签**。**向导 Step 2** **须** **只读展示** **当前绑定** **`promptPackVersion`**、**`deprecatedAt`**（若有）、**[`prompt-management` `publishedWith*Revision` / `safetyPhraseScanScope`](../prompt-management/config.md) **快照**（**若** **读模型** **返回**）：**当** **平台** **当前** **`placeholderDenylistRevision`/`safetyPhraseBlocklistRevision`** **高于** **包内** **固化快照** **时** → **黄灯** **「闸规则已升级，建议复核或重发 Prompt 版」**——**V1 默认** **不** **单独** **阻断** **模板发布**（**可** **`contract-closure`** **升为** **硬闸**）。若包 **后续不可用**：列表/详情 **显式告警**；**阻断**新发 **I02** 直至模板 **改绑可用包或发新版**。**存量**：**默认继续跑**，由运营按需 **Pause / 迁移**（与 [rules.md](rules.md) **§6** 路径 A 一致）。

**T05 Tool**：`toolProfileRef` **解析** **`toolId[]`**；**逐项须** **`enabledOperational`、PATH 已冻结（非 `TBD`）**。**对签**：[`tool-management/functions` §4 SC-TM-09](../tool-management/functions.md)、[`tool-management/flow` §6](../tool-management/flow.md)；**任一**禁用或 **`TBD`** → **阻止发布**并列缺失项（**SC-MCV1-05 · SC-AM-04**）。

**T06 模型**：`defaultModelRef` 从 **ai-settings 可用模型**选择；模型 **下线**时 **告警**；**阻断**基于该模板的 **新发 I02**；运营须 **改绑模型并发版**（T03 新版本路径）。**不**采用「静默回退到平台默认模型」以免 **不可预期行为**（见 **§8**）。

**T07 风控**：存 **引用 + 模板级参数**；建议默认合并规则：**全局为底、模板可收紧不可放宽**；若业务要放宽须 **风控签批**。

**T08 状态**：**停用**须二次确认 + 原因码；**立即禁止新发**。**启用**：若依赖曾变更须 **重新过发布校验**。存量实例见 [rules.md](rules.md) 规则 6。

**T09 克隆**：入口：**模板列表行操作「克隆」**或详情页。**行为**：（1）运营输入 **新内部名/展示名**（必填，命名 **防冲突**）；（2）后端复制 `**templateVersion`** 所选 **快照**的配置引用（**首选已发布版本**）；若源 **尚无发布版**：**允许克隆当前草稿快照**→ **新 `templateId`**、**草稿**；（3）**不**自动发布、**不**继承 **启用**；（4）**审计 `TEMPLATE_CLONED`**，含 **源 templateId/templateVersion（或草稿 token） + 新 templateId**。**禁止**：克隆到 **同一 `templateId`**。

**T10 删除/归档**：**草稿**：列表/详情提供 **删除**（二次确认）；若 **仍被依赖**（如挂单/FK）**禁止**硬删。**已发布**：UI **不提供「删除」按钮**→ **T08 停用**。**列表隐藏**：**V1 默认不做**「停用即从运营列表移除」——停用在列中 **可读**；（若合规要强掩码，**单独立项** `**contract-closure`** + MR）。**审计**：`TEMPLATE_DRAFT_DELETED`；归档类事件名以 **实现对签**为准。

---

## 2. Agent Instance — 用户运行中的 Agent


| 域内编号          | 一级功能       | 二级功能        | 功能描述                                         | 会签备注                                         |
| ------------- | ---------- | ----------- | -------------------------------------------- | -------------------------------------------- |
| **FR-AM-I01** | Agent 列表   | 查看实例        | 用户 **实例列表**                                  | 与 Runtime 状态联动筛                              |
| **FR-AM-I02** | 创建 Agent   | 创建实例        | **基于启用模板**创建                                 | 准入+计费+模板                                     |
| **FR-AM-I03** | Agent 详情   | 查看详情        | **详情页**                                      | **Secret 不可见**                               |
| **FR-AM-I04** | 绑定子账户      | Sub Account | **关联子账户**                                    | **FR-T01** scope                             |
| **FR-AM-I05** | Agent 配置   | 参数配置        | **白名单** `instanceOverrides`                  | 不突破 **FEATURE_***                            |
| **FR-AM-I06** | 删除 Agent   | 删除实例        | **销毁**                                       | 在途风险策略                                       |
| **FR-AM-I07** | 模板版本       | 版本钉扎 / 升级   | 创建 **钉死** `templateVersion`；新发模板版 **不自动迁**存量 | **V1**：**无**控制台「升级到新版」向导→ **§8**             |
| **FR-AM-I08** | Agent 列表导出 | CSV / 异步导出  | 在 **当前筛选条件**下导出实例列表 **非敏感列**                 | **禁止**导出 Secret；大数据量 **异步任务 + 下载链接**；**须**审计 |


### 2.1 需求展开（Instance）

**I01 列表**：展示 `instanceId`、`userId`（可脱敏）、`templateId`+`templateVersion`、`agentState` 摘要、**实例 Runtime 机电状态**、**子账户绑定状态**、**最近活跃时间**。筛选项：`userId`、`templateId`、状态、时间范围、**渠道**（若实例有 `channel` / Telegram 绑定，见 [config.md](config.md)）。**默认列、单行关键字检索维度、联系掩码（邮箱/手机）是否出现** 以 **[config.md](config.md) §3.1** 为控制台 IA SSOT。**`src/admin` 演示**另含 **多选 / R06 批量条**、**I08 导出**按钮占位、**G01** 横幅（读 `globalGateConfigKeys`）；**§3.1 结构化筛选**（用户 UID、模板 id、`agentState`、机电态、最近活跃 UTC 日期区间、子账户列表态、Telegram 渠道）与 **单行关键字**并存。

**I02 创建**：前置检查建议顺序：（1）`GLOBAL_AGENT_SWITCH`；（2）[access-control](../access-control/config.md) **§4**：封禁/VIP/**灰度（本域事实源）**；（3）**计费**；（4）模板 **启用**且依赖完整；（5）**每用户实例配额**（若有）。失败返回 **可行动**码并与 **附录 A `agentState` / block reason** 展示一致（如 `AGENT_GLOBAL_OFF`、`AGENT_USER_BLOCKED`、`AGENT_ROLLOUT_BLOCKED`、`AGENT_MEMBERSHIP_BLOCKED`、`AGENT_BILLING_BLOCKED`、`AGENT_TEMPLATE_DISABLED` 等）；**§7.1 + OpenAPI** **须同名冻结**。

**I03 详情**：分区：**基础信息**、**绑定**（无 Secret）、**运行**（命令按钮 + 状态 + `lastProductBlockReason`）、**参数**、**日志入口**与 **observability-management** 深链。**详情内默认不外显**模板展示名 / `templateId` / `templateVersion`（与 **[config.md](config.md) §3.2**）；**绑定分区是否含顶层「运营提示」类醒目区块** 亦以 §3.2 为 IA SSOT。

**I04 子账户**：仅 **Agent 专用 scope**子账户。未开通时 **展示引导态**与 **可读 Deeplink**（**Key/onboarding** → **Agent 产品线绑定页** URL **产品定**；其它归因同窗 **`initialization-flow`**）。**换绑**：二次确认 + 审计；**V1 默认**（见 **§8**）：换绑过程中 **Pause 新执行**直到绑定成功（实现可 **配置关闭**）。

**I05 参数**：`instanceOverrides` **键集与白名单表**同步维护；服务端 **合并**模板默认与全局并 **拒绝**越权字段，**字段级错误**返回。

### 2.2 `instanceOverrides` 键白名单（与 OpenAPI 同步）

以下为 **允许的键下限示意**。**契约 SSOT**：所内 `**Agent Instance`** 写路径在 `**[design/api.md](../../../../design/api.md)**` **「OpenAPI / 登记表」** 增补一行并指向 **Swagger/工件**；`instanceOverrides`、`runtimeInstanceState` **JSON Schema / 枚举** **以该 OpenAPI** 冻结为准。本文 `**§2.2`** 与 `**config` §5 字段表** 须在 **登记表填链后**做一次 **对齐 PR**。


| 键（示例）                   | 说明      | 约束                                   |
| ----------------------- | ------- | ------------------------------------ |
| `preferredLanguage`     | 回复语言偏好  | **不得**绕过内容安全策略                       |
| `cooldownPreferenceSec` | 用户侧冷却偏好 | **≤** global `AGENT_COOLDOWN_SEC` 上限 |
| `symbolPreference`（若允许） | 偏好交易对列表 | **须** ∩ `SYMBOL_POLICY` **白名单**      |
| `voiceOutputEnabled`    | 语音播报开关  | **须** ∩ `FEATURE_VOICE`              |


**新增键**：须 **RFC + 风控**；**禁止**客户端私增未登记键。

**I06 删除**：默认倾向 **软删**或 **异步清理**；**硬删**条件由 **risk/exchange-agent** SSOT（无在途订单/持仓/未完成关键执行等）。拒绝须 **结构化原因**。

**I07**：**创建**即 **钉死** `templateVersion`；新发模板版 **不自动迁存量**。`**FR-MC112` 在 V1 的落地**：本条 **仅存钉扎语义**——**不包含**控制台「选中实例升级到模板最新版」向导；该类能力后置 **MR**（须 **差异预览 / 审计 / 可选 Pause**）。手工 **Pause + 建新实例删旧实例**仍为 **运维 Runbook**，不替代产品化迁移。

**I08 导出**：**列**：默认含 `instanceId`、`userId`（**导出列**可对 `userId` 使用运营约定掩码形态，**≠** 邮箱掩码）、`templateId`、`templateVersion`、`agentState`、`runtimeInstanceState`、`subAccountBindingStatus`、`createdAt`、`lastActiveAt`；**邮箱/手机掩码列** **仅当** OpenAPI **显式登记为可导出字段** 时方可纳入默认导出，否则 **省略**（同窗 **[config.md](config.md) §3 / §5**）；**不含**任何 Key/Secret。**范围**：**与列表当前筛选一致**；若全量过大 → **异步导出**（任务 id、进度、**水印**文件名）。**权限**：**独立** `INSTANCE_LIST_EXPORT` 或与 **Ops** 绑定（见 [rules.md](rules.md)）。**拒绝**：无权限 **403**；超时 **降载**提示。

---

## 3. Runtime Control — 当前运行状态


| 域内编号          | 一级功能       | 二级功能            | 功能描述                                 | 会签备注                                                         |
| ------------- | ---------- | --------------- | ------------------------------------ | ------------------------------------------------------------ |
| **FR-AM-R01** | 启动 Agent   | Start           | 冷启动或 Stopped → 可调度                   | 与 R05：审计类型 **须可分**（见 **§3.1**）                               |
| **FR-AM-R02** | 暂停 Agent   | Pause           | 实例级暂停                                | 与 OPS 划界                                                     |
| **FR-AM-R03** | 停止 Agent   | Stop            | 停止                                   | 终局或可重启                                                       |
| **FR-AM-R04** | Runtime 状态 | Runtime Status  | **状态展示**                             | 对齐 **附录 A**                                                  |
| **FR-AM-R05** | 恢复 Agent   | Resume          | Pause → 可执行                          | 可与 R01 同 API                                                 |
| **FR-AM-R06** | 批量 Runtime | 批量 Pause / Stop | 对 **多选实例**（同屏勾选或导入 id 列表）下发 **相同命令** | **部分失败**须 **明细表**；**须**审计 **批次 id**；与 **全局 OFF** 规则同 **单实例** |


### 3.1 需求展开（Runtime）

**幂等**：重复 **Start**/**Resume** 在已满足态下 **无副作用**，返回 **当前态**。

**全局关断**：`GLOBAL_AGENT_SWITCH` **关闭**时 **禁止**实例级 Start/Resume **产生例外接单**（除非附录 A 书面白名单）。UI **禁用**并展示 **全局原因**。

**叠加**：**OPS_SUSPENDED** 与 **实例 Pause** **并列展示**两层原因（[rules.md](rules.md)）。

**R01/R05**：共实现时审计类型须分 `RUNTIME_START` / `RUNTIME_RESUME`。**从 Stop 再起**记 **Start**。

**R02**：生效后 **新执行**不得进入可计费成功路径；在飞请求遵循 **附录 A D-1** 类策略（[exchange-agent](../../agent/exchange-agent/overview.md) SSOT）。

**R03**：**V1**（与 **§8** 一致）：Stop → Stopped 后 **允许**再次 **Start**；若产品将来定义 **終局 Stop**，须在 **状态机 + UI** 同步禁用 Start，并 **修订 §8**。

**R04**：展示 **机电状态**、`agentState`、`lastProductBlockReason`（§8.2 子集）、**最近心跳/错误摘要**（若有）。

**R06 批量**：**入口**：实例列表 **多选** + 工具栏 **批量 Pause / 批量 Stop**（**不建议**批量 Start/Resume：易误触）。**前置**：二次确认 + **原因码**；校验 **RBAC**。**执行**：**逐条**或 **批 API**；**默认**：**部分成功 + 失败明细**（`instanceId` + `code` + message）。**全局 OFF**：**仅允许** **Pause / Stop** 类命令（与 **§5.1 G01** 冻结一致）；**禁止**批量 **Start/Resume**；**不得**整批「无操作」拒绝合法 Pause/Stop。**审计**：`RUNTIME_BATCH_PAUSE` / `RUNTIME_BATCH_STOP`，含 **batchId**、成功/失败计数。

---

## 4. Agent Logs — 运行日志


| 域内编号          | 一级功能             | 二级功能      | 功能描述        | 会签备注               |
| ------------- | ---------------- | --------- | ----------- | ------------------ |
| **FR-AM-L01** | Conversation Log | 对话日志      | **对话**轨迹    | 默认脱敏               |
| **FR-AM-L02** | Tool Log         | Tool 调用日志 | **Tool** 记录 | join `executionId` |
| **FR-AM-L03** | Error Log        | 错误日志      | **错误**条目    | observability      |


### 4.1 需求展开（Logs）

**查询**：实例详情内 **过滤** = 时间窗、`executionId`、会话 id、`traceId`、工具/错误维度；**分页/游标**与 `**[observability](../../../observability/overview.md)`** API 一致。

**详情（单条钻取）**：点击行 **展开**或 **侧栏** 展示 **该条完整可展示字段**（Conversation：脱敏全文走 **二次授权**；Tool/Error：参数摘要、堆栈 **按角色**）。**无**独立「日志详情页」亦可，**须有**可复核的 **单行视图**。

**导出**：**范围** = 当前 Tab + 当前过滤器（或勾选行）；**跳转/嵌入** [observability-management](../observability-management/overview.md) **审批导出**；水印、保留期 **observability SSOT**；**权限**见 **SC-AM-12**。审计 `**LOG_EXPORT_REQUESTED`**（见 [rules.md](rules.md)）。

**入口**：实例详情 **三 Tab**（或等价）；默认时间窗 **最近 24h**，更长跨度 **服从 observability API 上限**。**Conversation** 默认截断/哈希；**原文**二次授权。**Tool** 入出参 **摘要**、无 Secret。**Error** 归一码与 **用户可见话术**（若有）分列。

---

## 5. 全局门禁横幅（FR-AM-G01 · 跨块）

运营在 **模块一任一主要页面**（模板列表、实例列表、实例详情——**Logs 若仅占位在详情内则随详情**）须 **共识地**看见 `**GLOBAL_AGENT_SWITCH`（及只读展示的关联 config 摘要）** 状态：**ON / OFF**。  


| 域内编号          | 一级功能 | 二级功能      | 功能描述                                                                                                                              |
| ------------- | ---- | --------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **FR-AM-G01** | 全局门禁 | 只读横幅 / 徽章 | `**GLOBAL_AGENT_SWITCH` OFF** 时顶栏/固定 **Banner**；**无永久关闭**；**可「当日不再显示」**（UTC 日复位；详见 **§5.1**）；文案链 `**trading-agent-config`** 或运维外链 |


### 5.1 需求展开（G01）

- **不写**全局键值：**仅读取**门禁结果与 **简短原因字段**（若后端提供）；**Toggle 不在本模块**（改键属 **Trading Agent Config / 运维** SSOT）。  
- `**GLOBAL_AGENT_SWITCH` = OFF（冻结规则，与 R06 / I02 一致）**：  
  - **须禁用 / 须拒绝**：**新建实例（I02）**、**Start**、**Resume**（含任何「恢复可计费接单」语义）、UI 上 **灰显**对应按钮。  
  - **须仍允许**（运营 **降载 / 止损**）：**Pause**、**Stop**、**R06 批量 Pause / 批量 Stop**（与单实例 **同一后端策略**；**不得**因「全局 OFF」整批 **自动拒绝** Pause/Stop，除非 **另设**合规开关——默认 **无**）。  
  - **不得**产生 **已启动可接单** 的虚假成功态；**详见** [rules.md](rules.md) **§8**、**§10**。
- **频控**：状态 **轮询**或 **SSE** 由实现定；默认 **≤30s** 刷新或页面 **焦点**触发刷新。
- **Banner 收纳（V1 冻结）**：**无**「永久关闭」；**仅** **当日不再显示**（`localStorage`/Cookie，键名实现定），**日历日翻转**默认按 **UTC 00:00** 复位；站点数据清空后 **须恢复展示**。若租户须 **交易所运营时区** 换日边界，须在 `**contract-closure`** 单列 **多时区**条目（极少见）。

---

## 6. FR-MC101～114 映射草案


| FR-MC   | 建议覆盖（FR-AM）                  | 简述                                          |
| ------- | ---------------------------- | ------------------------------------------- |
| **101** | T01                          | 模板列表与筛选                                     |
| **102** | T02, T03, T09, **T10**（仅草稿删） | 创建/编辑/**克隆**/**草稿删除**                       |
| **103** | T08                          | 启用/停用与存量联动                                  |
| **104** | T04                          | Prompt 绑定与健康                                |
| **105** | T05                          | Tool 绑定与矩阵校验                                |
| **106** | T06                          | 默认模型与下线策略                                   |
| **107** | T07                          | 模板风控与全局合并                                   |
| **108** | **G01**                      | **全局门禁只读横幅**（亦可在 **PRD** 单列 MR）             |
| **109** | I01, I02, **I08**            | 实例列表/创建/**导出**                              |
| **110** | I03, I04, I05                | 详情、绑定、参数                                    |
| **111** | I06                          | 删除与在途校验                                     |
| **112** | I07                          | **钉扎**（V1 **无**「升级实例到新 templateVersion」产品化） |
| **113** | R01～R05, **R06**             | 单实例与 **批量** Runtime                         |
| **114** | L01～L03                      | 三类日志入口与权限                                   |


### 6.1 FR-MC 子项展开（与 PRD §4.1 同步 · 用例归因）

**规则**：**FR-MC** = PRD 条目号；**FR-AM** = 域内细项与 **测试用例默认挂载点**。PRD 表见 [management-console-v1-prd · §4.1](../management-console-v1-prd.md)。


| FR-MC | FR-AM 子项（建议一条用例或一组场景）   |
| ----- | ----------------------- |
| 101   | T01                     |
| 102   | T02；T03；T09；T10         |
| 103   | T08                     |
| 104   | T04                     |
| 105   | T05                     |
| 106   | T06                     |
| 107   | T07                     |
| 108   | G01                     |
| 109   | I01；I02；I08             |
| 110   | I03；I04；I05             |
| 111   | I06                     |
| 112   | I07                     |
| 113   | R01；R02；R03；R04；R05；R06 |
| 114   | L01；L02；L03             |


---

## 7. 验收标准 SC-AM（V1）


| 编号           | Given                    | When                          | Then                                                                                |
| ------------ | ------------------------ | ----------------------------- | ----------------------------------------------------------------------------------- |
| **SC-AM-01** | 有多版本模板                   | 打开模板列表                        | 可见启用/停用、当前发布版本，筛选生效                                                                 |
| **SC-AM-02** | 模板有效                     | 新建实例                          | 成功且 **钉死 templateVersion**                                                          |
| **SC-AM-03** | 模板停用                     | 新建实例                          | **拒绝**，原因明确                                                                         |
| **SC-AM-04** | Tool 含 TBD               | 发布模板                          | **阻止**并列项                                                                           |
| **SC-AM-05** | `defaultModelRef` 模型下线   | 基于该模板 **新发 I02**              | **拒绝**（`AGENT_TEMPLATE_DEP_UNMET` 类等）；控制台 **告警**；**不回退**静默改模型                       |
| **SC-AM-06** | 计费阻断                     | 新建实例                          | **拒绝**，状态与附录 A 一致                                                                   |
| **SC-AM-07** | 全局 OFF                   | Start/Resume                  | **拒绝**，无「已启动」误判                                                                     |
| **SC-AM-08** | 实例 Pause                 | 新用户消息                         | 不进入计费成功闭环（与 exchange-agent SC 联动）                                                    |
| **SC-AM-09** | Pause 后 Resume           | 查审计                           | 事件类型可区分，含操作者与原因                                                                     |
| **SC-AM-10** | 不满足删除条件                  | 硬删                            | **拒绝**结构化原因                                                                         |
| **SC-AM-11** | 打开详情                     | —                             | **无** Secret/私钥明文                                                                   |
| **SC-AM-12** | 只读角色                     | 日志原文/导出                       | **拒绝**或无入口                                                                          |
| **SC-AM-13** | 给定 executionId           | 三类日志检索                        | **可串联**定位（字段与 observability 一致）                                                     |
| **SC-AM-14** | 已绑子账户                    | 运营摘要                          | 含附录 A §8.2 **已有字段子集**                                                               |
| **SC-AM-15** | **已发布**模板 **或** **仅存草稿** | 克隆                            | **新 templateId + 草稿**；审计含 **源标识**（`templateVersion` 或草稿）；**不**继承发布/启用               |
| **SC-AM-16** | 全局 OFF                   | 打开实例列表/详情                     | **G01 Banner 可见**且 Start/Resume **不可用**                                             |
| **SC-AM-17** | 有导出权限                    | 导出当前筛选 CSV                    | **无 Secret**；文件名 **含水印**或与策略一致                                                      |
| **SC-AM-18** | 勾选 5 实例其中 2 不满足 Pause    | **批量 Pause**                  | **明细**标示 成功 3 / 失败 2 + **原因码**                                                      |
| **SC-AM-19** | **纯草稿**模板、无 FK 阻断        | **删除草稿**                      | **成功**且审计 `**TEMPLATE_DRAFT_DELETED`**；若 **已发布**则无「删除」仅 **停用（T08）**                 |
| **SC-AM-20** | **全局 OFF**               | **批量 Pause** 合法选中集            | **请求被接受**（逐条或因单实例原因失败），**不因**全局 OFF **整批拒绝**；Start/Resume **仍禁用**                   |
| **SC-AM-21** | 全局 OFF、Banner 可见         | 用户点「当日不再显示」                   | **按 §5.1**：**当日剩余时间**隐藏；**次日 UTC 复位**后 **须再显示**（或等价 **localStorage TTL**）；**无**永久关闭 |
| **SC-AM-22** | 模板已 **停用（T08）**          | 对该 `templateId` **I02**       | **拒绝** `AGENT_TEMPLATE_DISABLED`（或统一码），与列表 **告警**一致                                 |
| **SC-AM-23** | 模板绑定的 Prompt **变为不可用**   | **存量 Running**实例 + **新发 I02** | 存量 **不自动 Pause**（默认）；新发 **拒绝**直至模板修复                                                |
| **SC-AM-24** | 模板 **已绑定** **某** `promptPackVersion`；平台 **全局** **`placeholderDenylistRevision`/`safetyPhraseBlocklistRevision`** **已** **高于** **包快照**（[`prompt-management/config`](../prompt-management/config.md)） | 打开模板 **向导 Step·Prompt** **或** **依赖摘要** | **可见** **黄灯**提示（**语义** **`functions` §1.1 T04**）；**V1** **不** **因**本条 **alone** **禁止**模板 **发布**/保存（**除非** **`contract-closure`** **升格**） |


### 7.1 创建与门禁错误码（BFF/UI 对齐用）

下列 `**code`** 为 **V1** **管理台语义契约**（与 `**design/api`** 注册之后端 **须在 OpenAPI enum / 示例中一致冻结**）；与 **附录 A `agentState` / `lastProductBlockReason`** **对签**（前缀可 `**AGENT_`** 或沿用 `**ADMIN_**` 网关规范——**全站统一一种**）。


| `code`                      | 典型触发                          |
| --------------------------- | ----------------------------- |
| `AGENT_GLOBAL_OFF`          | `GLOBAL_AGENT_SWITCH` OFF     |
| `AGENT_OPS_SUSPENDED`       | OPS 全局暂停                      |
| `AGENT_COMPLIANCE_RESTRICTED` | **合规凌驾** · [`access-control/eligibility-runtime`](../access-control/eligibility-runtime.md) **§3** |
| `AGENT_USER_BLOCKED`        | **封禁** · [`access-control/functions.md`](../access-control/functions.md) **FR-MC603**           |
| `AGENT_REGION_BLOCKED`      | **地域/管辖区** · [`access-control/eligibility-runtime`](../access-control/eligibility-runtime.md) **§1～§2** |
| `AGENT_KYC_REQUIRED`        | **KYC/测评未达标** · [`eligibility-runtime` §1](../access-control/eligibility-runtime.md)；与 `AGENT_KYC_INSUFFICIENT` 由同窗 OpenAPI **`enum`** 二选一 **或并排登记**（**`SC-AC-08`**） |
| `AGENT_KYC_INSUFFICIENT`    | **KYC 不足之备选码**（若与上行并存则须在 MR 收口文档说明分界） |
| `AGENT_ROLLOUT_BLOCKED`      | **灰度/白名单未命中** · [`access-control/functions.md`](../access-control/functions.md) **FR-MC601～602** |
| `AGENT_BILLING_BLOCKED`     | 计费 / 欠费                       |
| `AGENT_MEMBERSHIP_BLOCKED`  | VIP / 会员不达标                   |
| `AGENT_TEMPLATE_DISABLED`   | 模板停用                          |
| `AGENT_TEMPLATE_DEP_UNMET`  | Prompt/Tool/Model 依赖不可用       |
| `AGENT_QUOTA_EXCEEDED`      | 实例数配额                         |
| `AGENT_SUBACCOUNT_REQUIRED` | 未绑定或未就绪                       |
| `AGENT_BATCH_PARTIAL`       | **R06** 部分失败（附带 `failures[]`） |


---

## 8. 已决议默认（评审收口 · V1）

下列项 **按默认执行**；若与 **监管/所规**冲突，在 `**contract-closure`** 或 **法务签批**中单行 OVERRIDE，**不**在本表 silent 改行为。


| 主题                          | **V1 默认**                                                                                          | 文档                               |
| --------------------------- | -------------------------------------------------------------------------------------------------- | -------------------------------- |
| **模板停用 → 存量实例**             | **仅禁止新建**（路径 A）；**不自动**批量 Pause；若需 **联动 Pause** 须 **独立运营任务/开关**                                    | [rules.md](rules.md) §6        |
| **Stop 后是否可再起**             | **可**：Stop → Stopped → **Start** 允许（除非 **PRD MR** 明确「終局 Stop」并改状态机）                                | §3.1                             |
| **换绑子账户**                   | 换绑过程中 **默认 Pause 新执行**至绑定 **成功**（可配置关闭）                                                            | §2.1 I04                         |
| **用户自助 vs 后台代客**            | **V1 控制台以运营能力为主**；若主站 **自助**与本模块 **同源 API**，须在 **IAM 按渠道/角色**隔离（见 [overview.md](overview.md) §3） | overview §3                      |
| **Prompt 包后续不可用**           | **告警**列表/详情；**阻断**新发 **I02**；**存量默认继续运行**直至人工干预                                                    | `**rules`** §6 路径 A、`§1` **T04** |
| `**defaultModelRef` 模型下线**  | **阻断**新发；**告警**；**须**模板 **新版本**换模型；**不**静默平台默认回退                                                   | `**§1` T06**、**SC-AM-05**        |
| **仅从草稿克隆（无发布版）**            | **允许**；新 `templateId` **草稿**；审计含 **源草稿快照 id**（若可分）                                                 | `**§1` T09**                     |
| **停用模板列表可见性**               | **默认**停用模板仍 **可见**（Badge 停用）；不强掩码                                                                  | `**§1` T10**                     |
| **实例升级到新版模板**               | **不交付**控制台向导；仅存 **运维 Runbook / 后置 MR**                                                             | `**§2` I07**、`§6` **FR-MC112**   |
| `**instanceOverrides` 白名单** | **Keys** ≤ `**[design/api.md](../../../../design/api.md)`** **OpenAPI**；私增 keys **419/422**        | `**§2.2`、`config`** §5           |


**仍为外部签批（非本模块能单独改字）**：`GLOBAL` / OPS / billing 等与 **附录 A** 一致的 **法务合规话术**正文。

---

## 9. 模块与功能完整性自检

### 9.1 与 PRD **§4 模块一** 结构对照


| PRD 叙述                         | 本域落点                                                                                               | 完备性                                                          |
| ------------------------------ | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ |
| Template                       | **§1** FR-AM-T01～**T10** + `config` 向导                                                             | **完整**（含 **克隆、草稿删除**；**已发布**以 **停用**代硬删）                     |
| Instance                       | **§2** FR-AM-I01～**I08** + `flow` §2                                                               | **完整**（含 **列表导出**）                                           |
| Runtime（Start·Pause·Stop + 状态） | **§3** FR-AM-R01～**R06**；**Resume=R05**，**批量=R06**                                                 | **完整**                                                       |
| Agent Logs（对话/Tool/错误）         | **§4** FR-AM-L01～L03                                                                               | **完整**（深度 schema 在 `observability`）                          |
| **全局横幅**                       | **§5 FR-AM-G01**、`config`、`flow`                                                                   | **已立项**                                                      |
| **FR-MC101～114**               | **§6 / §6.1**；**PRD §4.1**                                                                         | **已拆条**（PRD §4.1 + 本域 §6.1）                                  |
| 附录 A · `agentState` / 全局闸      | **§2 I02**、**§3**、**§5 G01**、[rules.md](rules.md) **§8**                                         | **规则 + 展示**                                                  |
| 附录 A · §8.2 运营摘要               | **§2 I03**、**SC-AM-14**、`§9.4`、[PRD §8.2](../management-console-v1-prd.md)、`**design/api`** 用户摘要契约 | `**§9.4**` 表 = **控制台验收勾选**；**HTTP 契约**以 **登记表 + OpenAPI** 闭合 |


**结论（结构层）**：**四大子模块**与 PRD 模块一 **一致**；**Resume** 为 PRD 一句话未显式写出但 **运营必备**，本域已覆盖。

---

### 9.2 与「业务功能清单」四表对照（逐项）

**Template Management**


| 一级               | 二级                | FR-AM   |
| ---------------- | ----------------- | ------- |
| Template 列表 / 查看 | 全部模板              | T01     |
| 创建 Template      | 创建模板              | T02     |
| 编辑 Template      | 修改模板              | T03     |
| Prompt 绑定        | Prompt 配置         | T04     |
| Tool 绑定          | Tool 配置           | T05     |
| 默认模型             | Model 配置          | T06     |
| 默认风控             | 风控配置              | T07     |
| Template 状态      | 启用/停用             | T08     |
| **克隆为独立模板**      | 新 `templateId` 草稿 | **T09** |


**Agent Instance**


| 一级             | 二级          | FR-AM   |
| -------------- | ----------- | ------- |
| Agent 列表       | 查看实例        | I01     |
| 创建 Agent       | 创建实例        | I02     |
| Agent 详情       | 查看详情        | I03     |
| 绑定子账户          | Sub Account | I04     |
| Agent 配置       | 参数配置        | I05     |
| 删除 Agent       | 删除实例        | I06     |
| （跨能力）模板版本钉扎/升级 | —           | I07     |
| **列表导出**       | CSV / 异步    | **I08** |


**Runtime Control**


| 一级                | 二级             | FR-AM   |
| ----------------- | -------------- | ------- |
| 启动                | Start          | R01     |
| 暂停                | Pause          | R02     |
| 停止                | Stop           | R03     |
| Runtime 状态        | Runtime Status | R04     |
| 恢复（清单外常漏项）        | Resume         | R05     |
| **批量 Pause/Stop** | 多选实例           | **R06** |


**Agent Logs**


| 一级               | 二级      | FR-AM |
| ---------------- | ------- | ----- |
| Conversation Log | 对话日志    | L01   |
| Tool Log         | Tool 调用 | L02   |
| Error Log        | 错误日志    | L03   |


**结论（功能表层）**：原四表功能点均已覆盖；增补 **T09、I08、R05、R06**，且 **§5 G01** 承担全局横幅。

---

### 9.3 可选增强（域外依赖 · **无**本域 FR 编号直至依赖域立项）

下列能力 **本域不增 FR-AM 编号**——依赖域未交付前 **不得**在本模块 sprint **占 P0**：接入后由各域 **增补 FR**，本域只做 **索引**：


| 能力                       | 说明                                                                |
| ------------------------ | ----------------------------------------------------------------- |
| **实时日志 tail / SSE**      | 依赖 `**observability`** 能力；接入后 `**observability-management**` 定 FR |
| **实例 / 模板 Webhook / 工单** | **integrations**，本域不写                                             |
| **模板 JSON 批量导入导出**       | 与 **合规**绑定；若要 V1 → 另增 **FR-AM-T11** MR（**勿与 T10 草稿删除冲突**）         |


---

### 9.4 附录 A §8.2 字段 · 展示与验收（SC 打勾用）

以下为 **控制台宜展示的运营摘要下限**（与 [management-console-v1-prd.md](../management-console-v1-prd.md) **附录 A §8.2** 对齐）。**集成 / 测试**请 **逐行**勾选：**展示 / 脱敏 / 无数据时行为**。


| 字段（附录 A）                       | 建议承载                                    | 无数据时    | 仅 Viewer |
| ------------------------------ | --------------------------------------- | ------- | -------- |
| `vipTier`（**母账号**）、`agentMinVipTier` | 实例详情 **概览** 或链出用户                       | 显示「—」   | 只读       |
| `agentSubAccountId` / 绑定类      | **绑定** Tab                              | 「未绑定」   | 只读       |
| `agentSubAccountStatus`（可选）    | **绑定** Tab                              | 「—」     | 只读       |
| `agentTradingApiBindingStatus` | **绑定** Tab                              | 明确空态    | 只读       |
| `agentTradingApiKeyId`（可选）     | **绑定** Tab，**never Secret**             | 「—」     | 只读       |
| `agentState`                   | 页头 Badge + `**lastProductBlockReason`** | 仍须展示聚合态 | 只读       |


---

### 9.5 SC-AM · 增补项状态

**§7** 现为 **SC-AM-01～23**（**V1**：含 **Banner 收纳** SC-21、模板/Prompt/I02 SC-22～23 等）。

---

### 9.6 总评


| 维度                              | 结论                                                             |
| ------------------------------- | -------------------------------------------------------------- |
| **模块划分（4 块）**                   | **完整**，与 PRD 模块一 **对齐**                                        |
| **与你的五项清单（§10）**                | **通过**                                                         |
| **可签 PRD 的 FR-MC 正文**           | **§4.1 + §6.1** 已可作 **验收归因**；详参仍以 **FR-AM 展开**为准               |
| **运营增强（克隆/批量/横幅、tail/Webhook）** | **克隆/导出/批量/横幅**→ §1～5 + §7 **SC-15～23**；**tail/Webhook**→ §9.3 |


---

## 10. 与你的清单逐项对照（检查结果）


| #     | 你的要求                            | **是否具备** | **FR-AM / 说明**                                                                          |
| ----- | ------------------------------- | -------- | --------------------------------------------------------------------------------------- |
| **1** | Template **新增、编辑、删除**           | **具备**   | **新增**=T02；**编辑**=T03；**删除**= **T10**（**草稿**可删；**已发布**不按「物理删除」主路径，用 **T08 停用** + 记录保留）  |
| **2** | Prompt、Tool、默认模型、默认风控、**启用/停用** | **具备**   | T04、T05、T06、T07、T08                                                                     |
| **3** | Agent **列表、创建、绑子账户、详情、删 Agent** | **具备**   | I01、I02、I04、I03、I06（**可选** I05 参数、I08 列表导出）                                             |
| **4** | **启动、暂停、恢复、停止、当前状态**            | **具备**   | R01、R02、R05、R03、R04；（**附加** R06 **批量** Pause/Stop）                                      |
| **5** | **对话/工具/错误**三类 + **查询、详情、导出**   | **具备**   | L01～L03；**§4.1**：**查询**（筛选/分页）、**详情**（行展开/侧栏单行视图）、**导出**（observability-management + 权限） |


