# Tool Management · 功能清单、需求展开与验收

**叙事**：[`overview.md`](overview.md)；**产品模块**：[`../management-console-v1-prd.md` §6 模块三](../management-console-v1-prd.md)。

- **§1**：划界  
- **§2**：FR-TM 细项（**含 FR-TM-G01 治理**）  
- **§3**：**FR-MC301～305** 映射 · **§3.1** 测试挂载  
- **§4**：**SC-TM**（V1）  
- **§5**：错误码  
- **§6**：邻域自检  
- **§7**：已决议默认与工程约束（V1）  

**登记真源**：[`design/api.md`](../../../../design/api.md) **矩阵 + 登记表**；[`trade-assistance.md`](../../agent/exchange-agent/trade-assistance.md) **§8**（`toolId`、B/C 类、**`FR-TS07`**）。**运行时工具契约**（**状态机、风险级、幂等、返回信封、隔离**）：[`runtime-contract.md`](runtime-contract.md)。本域 **不**替代上述 SSOT。

**Registry SSOT 与实现镜像（`CC-P1-03`）**：[`ADR-002`](../../../../design/adr/002-tool-skill-registry-ssot.md) 定义 **登记表** 与 **`design/` registry** **及** **DB 镜像** **的形态**；**关闭 DoD**：实现侧 **`toolId`/`skillId` 枚举** **须**与 **本域 Registry 镜像 + `trade-assistance` §4·§8** **幂等可对**（**同窗 MR** **登记** **关闭条件**）。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. 划界

| 主题 | 说明 |
|------|------|
| **本模块** | **交易所后台 · 模块三**：对 **已登记工具** 做 **Registry 镜像、Schema 运营视图、调用权限策略、启用/停用、抽样日志入口**；支持 **SC-MCV1-05**（**矩阵未冻结不得「假开」**）。 |
| **非本模块** | **PATH/矩阵格终裁、OpenAPI 填链** → **`design/api`**；**`toolId` 语义、技能登记** → **`trade-assistance` §8**；**Tool 原文实现** → 实现仓；**全量日志 schema** → [`observability`](../../../observability/overview.md)。**Runtime 侧** **工具状态机、返回信封、子账户隔离** → [`runtime-contract.md`](runtime-contract.md)（**与** **`observability` §2.1 `invocationState`** **对签**）。 |
| **与模块一** | 模板 **T05** 选 **Tool Profile** 时，**须**能反映 **本域启用态 + 矩阵冻结态**（与 [`agent-management`](../agent-management/functions.md) **SC-AM-04** 精神一致）。 |

---

## 2. FR-TM · 需求细项与展开

| 编号 | 簇 | PRD | 功能描述 |
|------|----|-----|----------|
| **FR-TM-G01** | 治理 / RBAC / 审计 | — | **独立资源**（如 `tool.*`）；**不得**弱化为单一「超级管理员全开」且无审计。**详见 §2.1**。 |
| **FR-TM01** | Registry 镜像 | **301** | **只读或可编辑边界内**镜像 **`design/api` + trade-assistance** 已出现的 **`toolId`、域标签（exchange_read / model / `tool.web.*` 等）、PATH 摘要、矩阵状态（**`FROZEN` / `TBD` / `DEFERRED`**）**；支持 **按域/风险级**过滤与 **Owner** 展示。 |
| **FR-TM02** | Schema 运营视图 | **302** | **参数说明**、**JSON Schema / 安全壳**（maxLength、enum、PII 标记）**展示**；**可编辑范围** **须**与 **`trade-assistance`/ADR** 一致——**禁止**在后台 **扩大**写路径 **超越**矩阵已登记能力；**TBD 行** **禁止**标为「已配置完成」。 |
| **FR-TM03** | 调用权限策略 | **303** | **角色 / 租户 / 场景**（与 `scenarioId` 可选挂钩）**可调用子集**；**默认拒绝**未显式允许之组合；**C 类外网工具** **须**满足 [`contract-closure`](../../../contract-closure.md) **CC-P1-02** 与 **`agent-context`** 预算叙事。 |
| **FR-TM04** | 启用 / 停用 | **304** | **运营开关**：**启用**前 **须**满足 **§2.4 冻结门槛**；**停用**后 **新编排/新模板绑定** **不得**选用（**在飞会话** 策略见 **`exchange-agent`/`runtime`**）。 |
| **FR-TM05** | 日志抽样与协查 | **305** | **管理台入口**：按 `toolId`、`userId`、`executionId`、时间窗 **跳转/嵌入** [`observability-management`](../observability-management/overview.md) **或** 直连 observability API（**权限**独立）；**join** **`agent.tool.call`**（见 **observability §2.1**）。 |
| **FR-TM06** | 技能与工具登记镜像 | **306** | **页面** `ai.tool-registry`：与 [`trade-assistance` §4·§8.2](../../agent/exchange-agent/trade-assistance.md)、[`skill-specs/manifest.yaml`](../../../skill-specs/manifest.yaml) **同窗**；**A 类** **须** 可查看 **Git L0** 解析（§1～§6）；**禁止** 控制台成为第二套正文 SSOT；**Demo UI** → [`admin-console-tool-registry-reconciliation.md`](admin-console-tool-registry-reconciliation.md) **§0**；**生产** Registry API **另轨** **FR-TM01**（**B**）。 |

---

### 2.1 FR-TM-G01 · 治理 / RBAC / 审计

- **RBAC**：**Viewer**：Registry+Schema **只读**、日志 **摘要**；**ToolOperator**：**启用/停用**（受 **矩阵门槛**约束）、**权限策略**编辑；**RiskAdmin**：**C 类**工具 **放行/收紧**；**Admin**：**Registry/策略/日志可读** **+** **配置导出（若有）** —— **细粒度** **`rules` §4** **表**；**Admin** **是否** **含** **Enable** **等** **运维 Override** **`design`** **冻结**。**IAM 真源**：所内权限中心。  
- **审计（最低集）**：`TOOL_POLICY_UPDATED`、`TOOL_ENABLED`、`TOOL_DISABLED`、`TOOL_SCHEMA_VIEWED`（敏感）、`TOOL_LOG_DRILLDOWN`；须含 **`toolId`**、**actor**、**before/after** ref。  
- **矩阵优先**：**任何**导致「终端可调用」的 **Enable** **须**在审计中 **可证明**当时 **PATH 非 TBD**（或 **书面延期**与 **矩阵备注**一致，见 **`design/api` §4**）。

### 2.2 FR-TM01 · Registry（FR-MC301）

- **数据源**：定期/事件 **同步**自 **登记 SSOT**（实现可为 **拉取 OpenAPI 元数据 + skills 表**）。  
- **展示**：`toolId`、**R/W**、**PATH 摘要**（或 **「未登记」**）、**矩阵首版列**、**Owner**、**最后矩阵变更 PR**。  
- **禁止**：手工在 UI **新增** **`design/trade-assistance` 不存在的 `toolId`** 并声称 **已交付**（**登记 MR 先行**）。

### 2.25 FR-TM03 · 调用权限策略（FR-MC303）

- **模型**：**一条策略记录** **绑定** **一个** **`toolId`**（**或** **按 `toolId` 前缀/域** **批量模板**——**OpenAPI** **须** **二选** **冻结**）；**默认** **`denyByDefault=true`**：**未**显式 **allow** 之 **主体会话** **不得** **经策略引擎** **放行**（**Runtime** **最终** **仍**受 **Enable + 矩阵** **约束**）。  
- **维度（V1 下限）**：

| 维度 | 说明 |
|------|------|
| **IAM 角色 / 组别** | 运营、只读风控、Automation Runner 等（**所内** **枚举冻结**） |
| **scenarioId**（可选） | **与** [`agent-orchestration/routing-engine`](../../agent/agent-orchestration/routing-engine.md) **寄存器** **交集** **非空** **才允许** |
| **`toolDomain` / `toolId` 前缀** | **冗余**校验（**防**策略 **错绑** **跨域**工具） |

- **变更**：**须** **`TOOL_POLICY_UPDATED`** **审计**；**须** **可回滚**（**before/after** ref）。  
- **C 类**：**Enable** **前** **仍** **须** **CC-P1-02**；策略 **收紧** **不** **豁免** ADR。

### 2.3 FR-TM02 · Schema（FR-MC302）

- **只读模式**：默认；**可写**字段（如 **运营可见描述、deprecated 标记**）**若有**须 **单独 FR** 或在 **`contract-closure`** 备案。  
- **与 TBD 对齐**：矩阵格 **`TBD`** → Schema 区 **固定展示「未冻结」Banner** + **禁用**「完成配置」类 **误导 CTA**。

### 2.4 FR-TM04 · 启用门槛（FR-MC304 核心）

**Enable 前置（全满足）**：

1. **`toolId`** 在 **`trade-assistance` §8** 或 **`design/api` 登记表** **有行**；  
2. **涉及交易所写/子账户** 的：对应 **矩阵 PATH** **非 `TBD`** **或** 有 **合规延期备注**；  
3. **FR-TM03** 权限策略 **已配置**（至少 **默认安全**模板）；  
4. **C 类**：**CC-P1-02** **ADR** 状态 **已关闭或已链接**。

**否则**：UI **仅**允许 **Disabled** 或 **「申请矩阵解冻」**链到 **`design/api`** 责任人。

### 2.5 FR-TM05 · 日志（FR-MC305）

- **不进**本域 **重复定义** observability schema；**只定**：**入口、过滤维度、权限、跳链**。  
- **脱敏**：**默认**不展示 **用户 Secret、完整 request body**（与 [`rules.md`](rules.md) 一致）。

---

## 3. FR-MC301～305 映射

| FR-MC | FR-TM | 简述 |
|-------|-------|------|
| **301** | **FR-TM01** | Registry 镜像 |
| **302** | **FR-TM02** | Schema 运营视图 |
| **303** | **FR-TM03** | 调用权限策略 |
| **304** | **FR-TM04** | 启用 / 停用 |
| **305** | **FR-TM05** | 日志抽样 / 协查入口 |

### 3.1 子项展开（测试挂载建议）

| FR-MC | FR-TM |
|-------|-------|
| 301 | FR-TM-G01；FR-TM01 |
| 302 | FR-TM-G01；FR-TM02 |
| 303 | FR-TM-G01；FR-TM03 |
| 304 | FR-TM-G01；FR-TM04 |
| 305 | FR-TM-G01；FR-TM05 |

---

## 4. 验收标准 SC-TM（V1）

| 编号 | Given | When | Then |
|------|--------|------|------|
| **SC-TM-01** | 矩阵 PATH **`TBD`** | 运营打开工具详情 | **「未冻结」**明示；**无**「已上线」误导文案 |
| **SC-TM-02** | 同上 | 点 **启用** | **拒绝**或 **无入口**；审计 **无**「已启用」假状态 |
| **SC-TM-03** | PATH **已冻结** + **`FR-TM03`** **零配置 / 仅有不可调用之缺省** | **Enable** | **拒绝** **直至** **存在可调用的权限策略绑定**（**与 §7 「SC-TM-03 缺省策略」默认**一致；**豁免**须经 **`design` 书面 OVERRIDE**） |
| **SC-TM-04** | **ToolOperator** | 改 **调用白名单** | **审计** `TOOL_POLICY_UPDATED` |
| **SC-TM-05** | 工具 **Disabled** | 模板 **T05** 保存 | **不可选**或 **保存失败**并 **可行动**码（与 **agent-management** 对签） |
| **SC-TM-06** | **Viewer** | Enable/Disable | **403** |
| **SC-TM-07** | 存在 **`agent.tool.call`** | 按 **`executionId` 过滤** | **可定位**至单次调用（与 **observability** 一致） |
| **SC-TM-08** | **C 类**工具 | **Enable** | **无** ADR/CC-P1-02 关闭 → **拒绝** |
| **SC-TM-09** | **模板 T05 · Tool Profile** **含** **已 Disable** **或** **矩阵 `TBD`** 之 **`toolId`** | **保存/发布模板** | **阻断** **`409`/`422`** + **`TOOL_DISABLED`** **或** **`TOOL_MATRIX_TBD`**（**条目级** **`failures[]`** **须** **`design`** **冻结是否**）；**与** **`agent-management` SC-AM-04** **对签** |
| **SC-TM-10** | 已上报 **`invocationState`** **或 **`phase`** | 按 **`executionId`/`toolCallSeq`** **协查** | **`invocationState`** **生命周期** **与 Runtime **可对账**，**参见** **[`runtime-contract.md`](runtime-contract.md) §1.3**、[`observability` SC-OBS05](../../../observability/overview.md) |
| **SC-TM-11** | **工具返回值进入编排/模型回填** | **Registry 内 `toolId`** | **`status`/`executionId`/`data`/`error` 外层须符合 [`runtime-contract.md`](runtime-contract.md) §4；`data` 为 Output Schema 子集 |
| **SC-TM-12** | **走 Coobit 子账户私有 API 之工具** | **Execute** | **仅用 Agent 绑定子账户凭据；禁止主账户 Key** — [`runtime-contract.md`](runtime-contract.md) **§9** |
| **SC-TM-13** | **A 类** `skillId` **在 §4 已登记** 且 **有** Git 正文 | 运营打开 **`/ai/tool-registry`** 该行 | **可** 打开抽屉查看 **用户流程、下单方式、对话与下单要求**（§1～§6 解析）；**技能编号** 可复制 |
| **SC-TM-14** | **`publishRequired`** 技能正文 **contract-complete** | 查看 **对话与下单要求** Tab | **须** 展示 **参数 / 校验 / 确认 / 缺槽 / 拒答 / 对接交易所** 分节（**非** 原始 Markdown 墙） |
| **SC-TM-15** | **`matrixStatus=tbd`** 或 **无** L0 正文（OCO/Bracket/划转） | 打开该技能 | **明示** **暂未开放** 或 **仅备案** 说明（**`specNote`**）；**不得** 空白或工程错误码直出 |
| **SC-TM-16** | **Demo 预览** | 切换 **运营启用** 开关 | **仅** 影响 **本浏览器** 本地状态；**文案** **须** 说明 **非** 生产配置（**FR-TM06**） |
| **SC-TM-17** | **`publishRequired`** + **contract-complete** | 抽屉内 **「发布到 Runtime」**（**所内 / 接 BFF 后**） | **生产** 写入 **PUBLISHED** 快照；**`src/admin` Demo** **不展示** 该按钮（固定登记册 + **启用开关** 表达可用性 · [`PUBLISH` §7.1](../../../skill-specs/PUBLISH.md#71-admin-原型--交付边界srcadmin)） |
| **SC-TM-18** | 该技能 **已在 Runtime 生效** | 再次打开抽屉（**所内**） | **「发布到 Runtime」** **禁用** 或 **已发布** 标签；**不得** 暗示已写生产库 |
| **SC-TM-19** | **绑定无效** 或 **未知 `skillSpecVersion`** | **Prompt** 点 **Publish**（**TRADING**） | **阻断** **`PROMPT_SKILL_REF_INVALID`**；**Demo** 校验 **登记册 + Git 版本**（非 localStorage Runtime）· **`promptPublishGate`** |

---

## 5. 错误码（V1 · 建议）

**真源**：OpenAPI + BFF；前缀 **`TOOL_`** 或 **`ADMIN_`** **全站统一**。

| `code` | 典型触发 |
|--------|-----------|
| `TOOL_MATRIX_TBD` | **Enable** 时 PATH 仍 TBD |
| `TOOL_POLICY_MISSING` | **Enable** 时 **`FR-TM03`** **无可调用之策略绑定**（**SC-TM-03**） |
| `TOOL_NOT_REGISTERED` | `toolId` **不在** SSOT |
| `TOOL_DISABLED` | 运营 **停用** |
| `TOOL_FORBIDDEN_BY_POLICY` | **FR-TM03** 拒绝 |
| `TOOL_C_CLASS_NOT_APPROVED` | **CC-P1-02** 未满足 |

---

## 6. 邻域自检

| 邻域 | 核对 |
|------|------|
| **agent-management T05** | 发布前 **Tool 矩阵**校验 — **SC-AM-04** |
| **contract-closure §1** | **toolId/PATH** 承诺与 **矩阵**一致 |
| **observability §2.1 · SC-OBS05** | **`agent.tool.call`** 之 **`invocationState`/`phase`** — **`runtime-contract` §1** |
| **`runtime-contract` / `exchange-agent/overview` `FR-T01`** | **子账户隔离**、幂等 **`SC-TM-12`** |
| **prompt-management** | **无**直接依赖；**编排**层 **同时**引用 **工具+Prompt** 时 **版本独立**；**Prompt** **tool 正文** **须** **Registry Schema SSOT**（[`prompt-management/runtime-injection.md`](../prompt-management/runtime-injection.md) **§4**） |
| **skill-specs / PRS L0** | **FR-TM06** **不得** 替代 **Publish**；**正文 SSOT** [`skill-specs/requirements-closure.md`](../../../skill-specs/requirements-closure.md) |

---

## 7. 已决议默认与工程约束（V1）

| 主题 | **默认** |
|------|----------|
| **SC-TM-03 缺省策略** | **未配置可调用的权限策略绑定 → 拒绝 Enable**（与 **§2.4** 第 3 条一致）；不得在 PATH **已冻结**但**零策略**时静默开放全域调用。 |
| **Registry 同步** | **事件驱动** **优先**（**矩阵 PR 合并 / `trade-assistance` MR**）+ **兜底**定时 **≤15min**（**阈值** **`design`** **可 OVERRIDE**） |
| **Tool Profile（T05）** | **`toolProfileRef`** **解析出** **`toolId[]`** —— **逐项** **须** **`enabledOperational` ∧ matrixStatus=FROZEN`** **方** **可入** **模板** **`allowed` 集**（**SC-TM-09**）。 |
| **Admin 导出** | **配置导出**（**若有**）**须** **`Admin`** **角色** **+** **`TOOL_EXPORT`** **类权限** **+** **审计**。 |

---

与 [`config.md`](config.md)、[`flow.md`](flow.md)、[`rules.md`](rules.md)、[`runtime-contract.md`](runtime-contract.md) **同步维护**；**工程默认**以 **§7** **及 **`runtime-contract` §10** **邻域自检**为准迭代 **`config`/`flow`**。
