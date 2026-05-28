# Agent Management · 配置与 IA

> **全局 `configKey`**：`GLOBAL_AGENT_SWITCH`、`FEATURE_*`、`CHANNEL_*`、`AGENT_MIN_VIP_TIER` 等仍以 **[附录 A §5.1](../management-console-v1-prd.md)** 为 SSOT。本节描写 **控制台布局、字段展示与交互**，供设计与前端对齐。

---

## 1. 信息架构（V1 · 冻结）

侧边栏 **`Agent`**（或等价一级菜单）**仅二级导航**：

| 路由片段（示例） | 名称 | 说明 |
|------------------|------|------|
| `/agents/config` | 智能体配置 | **单页**：本所主 Agent 绑定（无列表；数据键同 API `templateId`，演示为 `PRIMARY_AGENT_TEMPLATE_ID`）；旧 `/agents/templates` **重定向** |
| `/agents/instances` | Agent Instance | 实例列表 + **详情壳** |

**不包含（V1 明确不做）**：**不设** **`/agents/runtime` 一级菜单**——单实例 Runtime 仅在 **实例详情**；**批量 Pause/Stop** 仅在 **实例列表多选工具栏（R06）**。**不设一级 `/agents/logs` 聚合页**——Agent Logs（L01～L03）**仅**在 **实例详情内三 Tab**。若后置需要 **聚合日志入口** → **单列 MR**，并补 **IAM + IA**。

### Demo（`src/admin`）与正式 FR

为收窄演示路由，**`/agents/config`**、**`/agents/config/:configId`**、**`/agents/templates`**、**`/agents/templates/:templateId`** **统一重定向至** **`/agents/instances`**：**无**「智能体配置」单页、**无** §2 所述模板列表/编辑向导。**原型 ↔ 文档 SSOT**：[`admin-console-agent-instances-reconciliation.md`](admin-console-agent-instances-reconciliation.md) **§0**。**演示与 §3·§1.1·§3.0 对齐（已实现）**：**G01** 横幅（`GLOBAL_AGENT_SWITCH` Demo=`false` 时可验 OFF + 「当日不再显示」UTC）；列表 **Start / Resume** 在 OFF 时禁用；**R06** 多选 + **批量 Pause / Stop**；**I08** 导出按钮（演示 Modal）；**§3.1** 默认列 + **完整筛选器**（用户 UID、模板、门禁、机电态、**最近活跃日期区间**、子账户状态、渠道 × **单行关键字**）；实例详情 **页头副区仅 `userId`**、各 Tab **不外显模板**；**创建者**；绑定 Tab **无**顶层运营提示；预览抽屉 **实例 ID + userId**；**`?tab=`** 深链日志。**正式验收**仍以 **§1.1** 全文及 [`rules.md`](rules.md)、[`functions.md`](functions.md) 为准。

### 1.1 全局门禁横幅（FR-AM-G01）

**位置**：**智能体配置** **与** **实例** **列表** **页顶**（固定在 **filters 上方**）；**实例详情**页顶 **次级条**（不遮挡原有标题操作区）。  

**文案要素**：`GLOBAL_AGENT_SWITCH` **ON/OFF**；OFF 时 **主色告警** + **一句话**（与后端 **`reason`/附录 A** 对齐）+ **「查看配置」**链到 [`trading-agent-config`](../trading-agent-config/overview.md)（只读/编辑 **依 RBAC**）。OFF 时可加 **次要链**「运维说明」（外链由所内定）。

**收纳**：**不得**提供「一键永久关闭」。**可**提供「**当日不再显示**」，**UTC 日历日**边界复位后再显（[`functions.md`](functions.md) **§5.1**、**SC-AM-21**）。

**交互**：OFF 时 **实例列表**工具栏 **灰显** **Start / Resume**（若存在快捷入口）；**批量 Pause / Stop** **须仍可用**（[`functions`](functions.md) **G01**、[`rules`](rules.md) **§8**）；**禁止**「全局 OFF → 禁用批量 Pause/Stop」且无 **合规 OVERRIDE**。

---

## 2. Template Management · 页面与列表

> **控制台产品名**：**智能体配置**；**实现路由** **`/agents/config`**（**单页**、无多配置列表；旧 **`/agents/templates`** **须重定向**）。**OpenAPI / 持久化** 仍使用 **`templateId`** 与路径 **`/api/v1/admin/agents/templates`**。

### 2.1 模板列表页

**工具栏**：新建模板、**导出 CSV**（模板列表 **可选**·敏感列须审）、帮助链到本文档。

**列（默认）**：

| 列 | 内容 |
|----|------|
| 模板名称 | 主标题 + `templateId` 小字灰 |
| 发布版本 | 当前 **最新已发布** `templateVersion`，无则显示「未发布」|
| 状态 | **启用 / 停用** Badge |
| 依赖摘要 | Prompt / Tool Profile / Model 三图标 **绿黄红** |
| 更新时间 | **最后发布或最后草稿保存** |
| 操作 | 编辑、**克隆（T09）**、启用/停用、版本履历、**草稿删除（T10）** |

**行内点击**：进入 **模板编辑向导**。

### 2.2 创建/编辑向导（建议 Steps）

| Step | 内容 |
|------|------|
| **1 基础** | 内部名、展示名、描述、标签 |
| **2 Prompt** | 搜索选择 `promptPackRef`；展示 **`promptPackVersion`、LOCKED、deprecate、`publishedWith*Revision`/`safetyPhraseScanScope`（若 API 返回）**；**闸 revision 落后于平台** → **黄灯**（见 [`functions.md`](functions.md) **§1.1 T04**） |
| **3 Tool** | 选择 `toolProfileRef`；**校验报告**内嵌 |
| **4 模型** | `defaultModelRef` 下拉 + **健康**指示 |
| **5 风控** | 模板级护栏表单（字段与 `trading-agent-config` **不冲突**） |
| **6 确认** | **Diff 摘要**（相对上一发布版）+ **发布** / 存草稿 |

### 2.3 版本履历抽屉

**时间线**：版本号、操作者、时间、**变更摘要**（自动生成：Prompt/Tool/Model/风控 diff tag）、**回滚仅运营**（若支持：创建 **基于历史版本**的新草稿）。

---

## 3. Agent Instance · 页面与列表

### 3.0 列表工具栏与批量区

- **多选列**：首列 **checkbox**；「**全选**」**V1 = 当前页勾选**。**全选筛选结果全集**（跨页、`O(n)` API）→ **非 V1**；后置须 **异步任务边界 + UX 警示 + MR**。  
- **批量操作条**：选中 ≥1 时展开 **批量 Pause**、**批量 Stop**（**FR-AM-R06**）；**禁用**条件：**仅有**「无 **`RUNTIME_BATCH_*`** / R06 **RBAC**」等 **正当理由**。**`GLOBAL_AGENT_SWITCH` 为 OFF** 时 **不单独**禁用批量 Pause/Stop（与 **G01** 冻结一致；个案失败以 **明细**呈现）。  
- **导出**：**导出实例列表**（**I08**）→ 应用 **当前筛选**；无 **`INSTANCE_LIST_EXPORT`** 则 **隐藏**。

### 3.1 实例列表页

**列（默认）**：

| 列 | 内容 |
|----|------|
| 实例 ID | `instanceId` 可复制 |
| 用户 UID | **`userId`**（与 API 同源）；邮箱/手机掩码 **仅当** OpenAPI **明确提供对应字段** 时可作 **次要展示**。**未提供时**：本列 **仅** `userId`，且 **单行关键字筛选不得**按邮箱命中 |
| 模板 | `templateId` v`templateVersion` |
| 聚合门禁 | `agentState` + **简短 block 原因**（附录 A） |
| 机电态 | **Running / Paused / Stopped / Error**（与 R04 一致） |
| 子账户 | **已绑 / 未绑 / 异常** |
| 渠道 | **Telegram** chat id 掩码、或「—」（若 V1 无则隐藏列） |
| 最近活跃 | 时间 |
| 操作 | 详情、**日志**、Runtime 快捷（可选） |

**筛选器**：用户 UID、模板 id、**agentState**、机电态、时间范围、子账户状态、渠道。**单行关键字**（若有）：`instanceId`、`userId`、`agentSubAccountUid`（模糊）；**不含**邮箱（与上表「用户 UID」列 **无字段则不外显**一致）。

### 3.2 实例详情页 · 布局

**页头**：**标题** `instanceId`；**状态 Badge 组**（机电态 + `agentState`）；**副区**（若有）**仅** `userId`，与列表 **同源**。**实例详情内各 Tab** **默认不外显**模板展示名 / `templateId` / `templateVersion`（页头 **亦不**重复）；模板信息 **仅供** **实例列表**（§3.1）、**I08 导出** 或 **后台专用检索** 使用。邮箱/手机掩码 **未在契约提供时** **不外显**（与 §3.1 一致）。**右侧**：**Start / Pause / Resume / Stop**（按态 **禁用**），**删除**（危险操作二次确认）。

**Tabs 或折叠分区**：

1. **概览**：创建时间、创建者、**配额占用**（若有）；**附录 A §8.2 摘要**：`vipTier`、`agentMinVipTier`（若有）、`agentState`、`lastProductBlockReason`（与列表 **同源**避免矛盾）。  
2. **绑定**：`agentSubAccountId`（或 `subAccountBindingRef` 展示名）、`agentSubAccountStatus`、`agentTradingApiBindingStatus`、`agentTradingApiKeyId`（可选）、**换绑**、**无 Secret 声明**。**不**提供绑定 Tab **顶部**「运营提示」类醒目区块（如顶层 Alert）；绑定快照内若仍有备注类字段，**不作为**控制台首屏展示要件（可走审计/工单等链路）。  
3. **参数**：`instanceOverrides` 表单 + **Effective 只读 JSON**（折叠）。  
4. **日志**：内嵌 **Conversation / Tool / Error** 三子 Tab（见 §4）。  
5. **审计**（可选）：本实例相关 **最近 N 条**审计流水。

---

## 4. Agent Logs · 视图规范

| 子 Tab | 默认列 | 默认排序 |
|--------|--------|----------|
| **Conversation** | 时间、会话 id、方向（user/agent）、**摘要**、executionId | 时间倒序 |
| **Tool** | 时间、toolId、PATH 摘要、耗时、状态、executionId | 时间倒序 |
| **Error** | 时间、级别、错误码、摘要、executionId、traceId | 时间倒序 |

**通用**：时间范围选择器、**刷新**、**复制 executionId**、**在 observability-management 中打开**（深链，带 query）。

**分页**：游标分页优先（大数据量）；页大小 **与 observability API** 一致。

---

## 5. 对象字段词典（控制台与 API 对齐用）

| 字段 | 所属 | 说明 |
|------|------|------|
| `templateId` | 模板 | 稳定 id；**不可**因改名而变 |
| `templateVersion` | 模板/实例 | 单调；**实例创建时复制** |
| `templateStatus` | 模板 | `DRAFT` / `PUBLISHED` / `DISABLED` 等枚举 **会签冻结** |
| `boundPromptPackRef` | 模板 | 指向 `prompt-management` 发布物 |
| `toolProfileRef` | 模板 | 指向运营 Tool Profile |
| `defaultModelRef` | 模板 | 指向 `ai-settings` 模型 |
| `templateRiskProfileRef` | 模板 | 风控配置引用或内嵌 JSON **二选一会签** |
| `instanceId` | 实例 | 全局唯一 |
| `userId` | 实例 | 所内用户 UID |
| `createdByDisplay`（或等价，`actor`/审计 subject） | 实例 | **可选**；概览「创建者」；未返回时控制台 **「—」** |
| `userEmailMasked`（或等价邮箱掩码字段） | 实例 | **可选**；OpenAPI **未登记或未返回** 时：列表、详情、关键字筛选 **均不得依赖**；**`src/admin` 演示 `AgentInstance` 可不包含该键** |
| `bindingSnapshot.operatorNote`（或等价） | 实例 | **可选**；**不得**要求控制台以绑定 Tab **顶层运营提示**形式展示 |
| `subAccountBindingRef` | 实例 | 子账户绑定关系 id |
| `instanceOverrides` | 实例 | **白名单** map（键集合与 [`functions.md`](functions.md) **§2.2**、`design` OpenAPI **须一致冻结**） |
| `runtimeInstanceState` | 实例 | **机电态**（与 `agentState` 区分命名；**枚举/嵌套字段**以 **后端 OpenAPI** 为 SSOT，本表为 **控制台对齐用**快照） |
| `lastRuntimeCommandAt` | 实例 | 最近运行命令时间（可选） |
| `batchId` | 批操作 | **R06** 返回，用于审计与客服协查 |

**命名**：若后端已有 **snake_case** 字段，控制台 **展示用 copy** 由 i18n 表维护。**API 契约 SSOT**：[`design/api.md`](../../../../design/api.md) **登记表**（须含 **Agent 模板/实例/Runtime**）；OpenAPI **填链后**须与本表 **`instanceOverrides` / `runtimeInstanceState`** 做一次 **对齐 PR**。

---

## 6. Runtime 控制台展示（摘要区）

当 **独立 Runtime 页**存在时，可含：**全局开关只读状态**（链到 `trading-agent-config`）、**队列深度**（只读数）、**最近 N 次实例级命令失败率**（链 observability）。**详细仪表盘**不属本文件范围。

---

## 7. 国际化与时区

- **时间**：默认 **UTC 存储**、控制台 **按运营偏好时区**展示（用户设置或租户默认）。  
- **文案**：所有 **门禁拒绝原因** 须有 **中英文**键（或与产品 i18n 策略一致）。
