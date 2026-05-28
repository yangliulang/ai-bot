# Prompt Management · 配置与 IA

**需求 SSOT**：[functions.md](functions.md)；**拼装 / 注入 / 冻结 / 预算** 见 [runtime-injection.md](runtime-injection.md)（**对象字段协查** `config` §3）。

---

## 1. 核心对象


| 对象                            | 说明                                                                                                                                                                                                              |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `**promptPackId`**            | 稳定 id（**不因展示名改版而变**）                                                                                                                                                                                            |
| `**promptPackKind`**          | **SYSTEM / TRADING / ANALYSIS / SAFETY**（**`ANALYSIS`**：**场景族** Prompt，与 **`TRADING`** **同窗草稿/发布/回滚**；扩展以 `**design/api`/OpenAPI** `**PromptPackType` **枚举**为准）                                                             |
| `**promptPackVersion`**       | **单调递增**（同 `**promptPackId`**）；**发布后不可改号**                                                                                                                                                                      |
| `**lifecycle` / `lockState`** | **须与实现对签**。**推荐语义**：`SYSTEM` 包发布后 `**LOCKED` + `currentVersion` 指针**（见 [flow.md](flow.md) §2）；`**TRADING`/`ANALYSIS`/`SAFETY`** **场景/护栏族**草稿为 `**DRAFT`**；发布后 `**PUBLISHED**`（`**SYSTEM`** 已对签 **`**LOCKED**`**）；**语义不得混用**，OpenAPI `**enum` 须单一真源）。 |
| `**scenarioId**`              | **编排寄存器键**（`**[agent-orchestration](../../agent/agent-orchestration/overview.md)**`）；`**TRADING`/`ANALYSIS` V1：** **Publish 前必填**（与 **SC-PM-10** 同窗）；**SAFETY** 若绑场景亦必填 `**design**` **注明**。`**SYSTEM**` 常为 **可选/无**。          |
| `**skillSpecRef**`            | **Runtime 技能范围 · 发布门禁指针**（`**skillId@skillSpecVersion**`，引用 `**trade-assistance**` / 登记册，**不拷贝** Skill 正文）；**TRADING V1**：写路径场景 **建议必填** 或可由 **`scenarioId` 推断**（**SC-PM-21**）；**放行/拒绝** `**PROMPT_SKILL_REF_INVALID**` 由 `**design/api` + 本域校验表** 冻结。**控制台 MUST NOT** 将本字段叙事为「技能绑定 / Prompt 托管 Skill」。                                  |

### 1.1a `promptPackKind` vs `scenarioId`（职责分离 · **MUST**）

1. **`promptPackKind` / `PromptPackType`**：仅表达 **拼装槽位所属大类 + 与该大类同窗的生命周期/IAM**，**不是**业务能力 SKU 全集。  
2. **业务能力第一维**：**`scenarioId` 寄存器**（[`routing-engine`](../../agent/agent-orchestration/routing-engine.md)）及 **Orchestration/模板侧** **`promptPackRef` 绑定**；**新业务线优先**增补 **寄存器行 + 绑定引用**，参见 **PM-C15**（[`functions.md`](functions.md) §1.2）。  
3. **控制台 IA**：Prompt 列表/筛选 **须**可追溯 **`scenarioId`**（或与寄存器同窗之 Query），**不得**以「仅按 `promptPackType`」替代 **scenario 治理**。

### 1.1b Prompt 治理四层与 Runtime 分工（**MUST** · 控制台 / PRS 同窗）

**关系链**（正确方向）：`**scenarioId**` → **Runtime**（选 Skill · 读规范 · 门禁）→ **Prompt Assembly**（PRS 块 1～6）→ 模型。**禁止** 产品叙事 **Prompt 绑定 Skill 正文** 或 **Prompt = Skill Runtime**。

| 治理层（运营阅读） | `PromptPackType` | Prompt **只存** | **不存**（归它域） |
|--------------------|------------------|-----------------|-------------------|
| **Base** | `SYSTEM` | 全局行为、铁闸 | Skill §1～§6、Slot、Tool 绑定 |
| **Scenario** | `TRADING` | 场景叙事、澄清/确认规则 | 参数表、校验矩阵、API 字段 |
| **Analysis** | `ANALYSIS` | 解读/分析话术 | 同上 |
| **UX** | `SAFETY` | 护栏、遥测横幅 | 工作流编排 |

**运营发布包（V1 · 16 包 · 索引 SSOT）**：[`prompts/governance-map.md`](../../../prompts/governance-map.md) · 产品清单 [`product/prompt-governance-checklist.md`](../../../../../product/prompt-governance-checklist.md)。

| 槽位 | `promptPackId`（示例） | 绑定规则 |
|------|------------------------|----------|
| **SYSTEM · 内核** | `pp-system-core` | 全局；发布后 `LOCKED` |
| **SYSTEM · 澄清横切** | `pp-runtime-clarify` | 全场景 PRS 澄清块；**非**按 `scenarioId` 再拆包 |
| **SYSTEM · 输出横切** | `pp-runtime-output-contract` | clarify / intent 契约；**非** API Schema 真源 |
| **TRADING** | `pp-trading-*`（11 写路径） | **一 `scenarioId` → 一包**；`buy.md`/`sell.md` 等为 Git 评审下限，**≠** 各发独立运营包 |
| **ANALYSIS** | **`pp-analysis-core`（唯一）** | `market.read_*`、`research.*`、`portfolio.*`、`monitoring.*` 等 **共用**；`analysis/*` 四卷为能力语义分卷，**禁止**按主题拆 Publish |
| **SAFETY** | `pp-safety-global` | 护栏话术；条文见 `prompts/safety/*` |
| **拼装注入** | — | `confirmation/*`、`intents/*` 片段：**不**占独立 `promptPackId` |

**Publish 正文六段**（与 Demo [`promptBodyTemplates.ts`](../../../../../src/admin/src/data/promptBodyTemplates.ts) 同窗）：Identity → Scenario Context（TRADING 必填场景语义）→ Behavioral Rules → Capability Awareness（可选）→ Clarify Rules（可选；亦可由 `pp-runtime-clarify` 横切）→ Output Contract（可选；亦可由 `pp-runtime-output-contract` 横切）。**禁止**在正文写 Gateway / Billing / Canonical / Tool API 字段表。

**控制台 IA（V1 · 与 `src/admin` Demo 对齐）**（字段表；**§0 SSOT** [`admin-console-prompt-strategy-reconciliation.md`](admin-console-prompt-strategy-reconciliation.md)）：

| 元素 | 要求 |
|------|------|
| 列表列名 | **Runtime 技能范围**（**非**「技能绑定」）；单元格 **优先** `scenarioId` |
| 发布门禁 | Alert **发布门禁 · Runtime 技能范围**（**SC-PM-21**） |
| 拼装可见性 | **Demo**：编辑器侧栏 + 执行详情 **拼装追溯** — **须**展示 `pp-system-core`、`pp-runtime-clarify`、`pp-runtime-output-contract`、场景/分析策略包、`pp-safety-global`（**SC-PM-22**）；**量产**：`resolvedPromptBinding` / **`agent.prompt.binding_resolved`** |
| 远期（不阻塞 V1） | Validation Reject Trace、Canonical Inspector、 Skill Scope Viewer — **观测/调试** 入口，**非** Prompt 正文编辑 |

人类导读：[`product/end-to-end-guide.md`](../../../../../product/end-to-end-guide.md) **§1.2** · PRS [`prompt-runtime/README.md`](../../../prompt-runtime/README.md)。

### 1.1 模板绑定与本域 `**promptPackRef**`（不与模块一再造 SSOT）

- **模板侧** `**boundPromptPackRef**`：**引用** `**promptPackId**`；**是否钉 `promptPackVersion**` 由 `**[agent-management` T03/T04](../agent-management/functions.md)** 决定——本域产出 **可被引用的版本线**，**不写**模板钉版逻辑。
- `**agent-management` T04**：若包 `**下线`/`deprecated`/依赖断裂**，**告警 + 阻断新发 I02`** 与该域 **已对签**。

---

## 2. IA（V1）

**侧边栏**：**AI 治理** → **提示词治理**（页面 ID `ai.prompt-strategy`）+ **安全防护**（`ai.prompt-safety`）。路由与重定向 **以** [`admin-console/demo-routing.md`](../../../admin-console/demo-routing.md) **为准**。


| 路由（Demo） | 页面 ID | 视图 | 说明 |
|--------------|---------|------|------|
| `/prompts/strategy` | `ai.prompt-strategy` | **提示词治理**（列表 + 编辑器） | **统一列表**：`SYSTEM`（含 `pp-system-core`、`pp-runtime-clarify`、`pp-runtime-output-contract`）、`TRADING`、`ANALYSIS`（仅 `pp-analysis-core`）；**类型/场景筛选** 替代旧「系统/场景」双菜单 |
| `/prompts/safety` | `ai.prompt-safety` | **安全防护** | `pp-safety-global`；独立 IAM 可选 |
| `/prompts/system`、`/prompts/scenarios` | — | **重定向** | → `/prompts/strategy`（**不**再作对外菜单名） |

**列表 → 编辑器**：草稿 / 预览 / Few-shot / 沙箱 / Publish·Rollback；`SYSTEM` 已 `LOCKED` **无双击改号**。**Sandbox**：须在 **staging 模型上下文**明示 **水印/假数据**，**禁用**绑定生产 `**agentTradingApiKeyId`**。**权限**：独立 `**prompt.sandbox.run`** 或与 **Editor** 绑定（见 [rules.md](rules.md)）。

---

## 3. 字段词典（控制台 ↔ API）


| 字段                                               | 归属      | 说明                                                                                                                                                                  |
| ------------------------------------------------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `promptPackId`                                   | 包       | SSOT                                                                                                                                                                |
| `promptPackKind`                                 | 包       | SYSTEM / TRADING / ANALYSIS / SAFETY                                                                                                                                 |
| `promptPackVersion`                              | 版本      | **发布号**                                                                                                                                                             |
| `title`、`description`                            | 包/版本    | 运营可见简介                                                                                                                                                              |
| `body`/`blocks`                                  | 版本      | Prompt **正文载体**（JSON/Markdown 二选 `**design`** 冻结）                                                                                                                   |
| `scenarioId`                                     | TRADING · ANALYSIS | **场景键**（寄存器对齐）；**Publish 前** **须** **非空**（**`SYSTEM`/`SAFETY` 未绑场景** **除外**）                                                                                             |
| `skillSpecRef`                                   | TRADING · ANALYSIS | **发布门禁指针**；列表/详情 **展示名** **Runtime 技能范围**；见 **§1.1b**                                                                                                        |
| `fewShots[]`                                     | 版本      | Few-shot **快照**，随 **`promptPackVersion` 固化                                                                                                                          |
| `variableSchema`（可选）                             | 版本      | Prompt 占位符 **JSON Schema**；**服务端发布前校验**；与 [`runtime-injection.md` §2.3](runtime-injection.md) **denylist / 白名单** **协查**（**Slug 语义**优于 **仅用 schema**）                |
| `placeholderDenylistRevision`（可选 · 响应头/元数据）      | 治理      | `**{{…}}` denylist** **修订号**（[`runtime-injection.md` §2.3.4](runtime-injection.md)）                                                                                 |
| `safetyPhraseBlocklistRevision`（可选 · 响应头/元数据）    | 治理      | `**§7.1` 越狱用语表** **修订号**（[`runtime-injection.md` §7.1](runtime-injection.md)）；**Publish 校验器** **与控制台** **须** **对齐**                                                 |
| `safetyPhraseScanScope`（可选）                      | 版本      | `**FULL_PACK`** **或** `**TRADING_BODY_FEWSHOT`**（[`runtime-injection.md` §7.1.2](runtime-injection.md)）；**默认** `**FULL_PACK`**                                      |
| `publishedWithPlaceholderDenylistRevision`（快照）   | 版本      | **Publish 成功** **时** **固化** **当时** `**placeholderDenylistRevision`**                                                                                                |
| `publishedWithSafetyPhraseBlocklistRevision`（快照） | 版本      | **Publish 成功** **时** **固化** **当时** `**safetyPhraseBlocklistRevision`**                                                                                              |
| `targetModelFamily`、`minContextTokens`（可选）       | 版本      | **模型兼容闸**（[`runtime-injection.md` §5](runtime-injection.md)）；**OpenAPI** 冻结                                                                                         |
| `resolvedPromptBinding`（概念 · Runtime）            | 会话/回合   | **非**控制台编辑字段：**回合开端**解析的 **SYSTEM/SAFETY/场景策略正文（对应 `scenarioId` 与场景族 **`promptPackType`）`promptPackId+Version` + Few-shot 快照**（[`runtime-injection.md` §3](runtime-injection.md)）；**实现名** **以 OpenAPI 为准** |
| `contentHash`、`etag`（可选）                         | 版本      | **乐观锁**/缓存；冲突策略见 [`functions.md`](functions.md) **§7**                                                                                                              |
| `deprecatedAt`、`deprecationNotice`（可选）           | 包或版本    | **软下线**≠删；绑定侧 **告警**                                                                                                                                                |
| `createdAt`、`publishedAt`、`publisher`            | 元数据     | **审计/UI**                                                                                                                                                           |


**控制台 UX**：列出 **「当前生效版」Badge**；**草稿**须有 **明示 Tab**。**读失败**（Runtime）：见 `**functions`** **§7** **降级**与 [`runtime-injection.md` §8](runtime-injection.md) **Scope**。  

**命名**：OpenAPI `**snake_case`** 与控制台 **camelCase copy** —— `**design/api`** SSOT。**填登记表后**与本表 **对齐 PR**。

---

## 4. 与 `management-console` / 模块一对齐

- **附录 A §1.3**：**模块二**为本域；**模块一** **模板绑定** `**boundPromptPackRef`** → `**prompt-management` 发布物**（参见 [`agent-management/config.md`](../agent-management/config.md)）。
- **模型**：本域表单 **不出现** `**apiSecret`**；**试跑模型**下拉 **只吃** `**ai-settings` 可读别名**列表。

