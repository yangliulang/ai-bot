# Prompt Management · 功能清单、需求展开与验收

**叙事**：[`overview.md`](overview.md)；**产品模块**：[`../management-console-v1-prd.md` §5 模块二](../management-console-v1-prd.md)。

- **§1**：划界与核心对象  
- **§2**：FR-PM 细项与展开  
- **§3**：**FR-MC201～207** 映射 · **§3.1** 子项用例归因（测试挂载）  
- **§4**：**SC-PM**（V1 验收）  
- **§5**：错误码与 API 对齐  
- **§6**：邻域完整性自检  
- **§7**：已决议默认与工程约束  
- **Runtime 拼装/注入契约**（**Assembly / Variable / Tool / Budget**）：[`runtime-injection.md`](runtime-injection.md)  
- **AC-09 族闭环（派工 §7.2 · 检核 §7.4）**：[`closure-remaining` §7.2～§7.4](../../../closure-remaining.md#cc-ac09-closure-matrix) · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)** — **与** [`runtime-injection`](runtime-injection.md)、[`contract-closure` CC-P1-04](../../../contract-closure.md) **对读**

---

## 1. 划界与核心对象

| 主题 | 说明 |
|------|------|
| **本模块** | **交易所后台 · 模块二**：**系统 / 场景 Prompt 包** 的治理、版本、发布与回滚；**`promptPackVersion`** **单调可追溯**；与 **`scenarioId`、`observability`** 对签。**不**做 **Terminal 卡片模板**（[`telegram/overview` §2.5 · 类型 A；总则 §2～§2.6](../../agent/telegram/overview.md)）。 |
| **非本模块** | **模型路由 / API Key / Temperature** → [`ai-settings/overview.md`](../ai-settings/overview.md)、[`integrations/llm/provider-routing.md`](../../../integrations/llm/provider-routing.md)；**skill 正文** → [`trade-assistance.md`](../../agent/exchange-agent/trade-assistance.md)；**模板绑定 UI** → [`agent-management`](../agent-management/overview.md) **仅选 `promptPackRef`**（附录 **§1.3**）。 |
| **系统包** | 发布后 **`LOCKED`**：**禁止**原位改正文；**仅**新版本线（复制快照→编辑→发布）。 |
| **场景包** | **草稿 →（评审）→ 已发布 → 可回滚**；须挂 **`scenarioId`**（或与 [`agent-orchestration`](../../agent/agent-orchestration/overview.md) **寄存器**一致之 id）。**业务语义** **以寄存器绑定为第一维**：[`routing-engine`](../../agent/agent-orchestration/routing-engine.md)。 |

### 1.2 业务能力定义：**`scenarioId` 优先 · `promptPackKind` 不包办（MUST）

| 编号 | 约束 |
|------|------|
| **PM-C15** | **`promptPackKind` / `PromptPackType` 不得** **单独**承担 **业务能力全集**：**交易所 Agent 可按场景展开的能力矩阵** **须**在 **`scenarioId` 寄存器**、 **`flows`/Intent** **与 Tool 矩阵** **可对签**；**新版本线** **`promptPack` 可被多场景绑定/复用**。**仅靠** **`TRADING`** **与 **`ANALYSIS`** **无法覆盖全部业务时**——**不得**在未过 **`contract-closure`**／拼装语义 MR 前提下 **继续堆砌 **`PromptPackType` enum**。详见 [`config.md`](config.md) §1.1a、本节 **§1 表 · `scenarioId`**。 |

### 1.3 硬约束（MUST · V1）

| 编号 | 约束 |
|------|------|
| **PM-C01** | **用户/终端侧读模型**：**仅**返回 **`PUBLISHED`/`LOCKED` 且当前生效指针**所指版本；**草稿** **不得**混入 **对用户 BFF**。 |
| **PM-C02** | **`promptPackVersion`** **immutable after publish**：订正 **惟一**路径 **新版本线** **或** **回滚改指针**。 |
| **PM-C03** | **并发**：**推荐** **`If-Match`/`etag`** 或 **`contentHash`** 做 **乐观锁**；冲突 → **`PROMPT_VERSION_CONFLICT`**（见 **§7**）。 |
| **PM-C04** | **正文体积**：单次保存 **默认上限** **256 KiB**（整包 body + few-shot 序列化后——**可分字段限额**，**最终以 OpenAPI **`maxLength`/schema** **冻结）；超限 **`PROMPT_BODY_TOO_LARGE`**。 |
| **PM-C05** | **Few-shot**：**V1 默认** **属于场景包草稿/版本**；启用 **全局 Few-shot 池** → **MR + `contract-closure`**。**禁止**Few-shot **带可逆 Secret**。 |
| **PM-C06** | **沙箱**：**计费**不入 **生产**流水（或入账 **`SANDBOX`** **独立科目**，会签 **`billing`**）。 |
| **PM-C07** | **销毁策略**：已发布资源 **主流** **`deprecatedAt` + 保留履历**；**硬删**仅 **法务 OVERRIDE**。**模板仍引用 deprecate 包**→ **告警**（**agent-management T04** 口径）。 |
| **PM-C08** | **拼装顺序**：**SYSTEM → SAFETY → 场景策略正文（由 **`scenarioId` 解析，`promptPackType` ∈ **`TRADING`/`ANALYSIS`** 等与 OpenAPI同窗之场景族**）→ Few-shot → Runtime Context → Tool Spec → User Input**（**MUST**）。详 **[`runtime-injection.md` §1](runtime-injection.md)**。 |
| **PM-C09** | **变量注入闸**：**API Key / Secret / `internalConfig` 等** **禁止** **可逆注入**；未声明占位符 **拒绝**；**`{{…}}` denylist §2.3**。详 [`runtime-injection.md` §2](runtime-injection.md)。 |
| **PM-C10** | **会话冻结**：**一轮对话回合**内 **`resolvedPromptBinding`**（各包 **`promptPackVersion`**）**稳定**；**新 Publish** **下回合**生效。详 [`runtime-injection.md` §3](runtime-injection.md)。 |
| **PM-C11** | **Tool 注入**：**仅** **Registry JSON Schema SSOT**；**禁止** **手写参数表** **作为调用真源**。详 [`runtime-injection.md` §4](runtime-injection.md)。 |
| **PM-C12** | **发布前兼容闸**：**Tool 存在**、**Schema 兼容**、**Token/模型** **门槛** **blocking**（SAFETY **默认无豁免**）。详 [`runtime-injection.md` §5](runtime-injection.md) **与本节 §2.8**。 |
| **PM-C13** | **Runtime 分项预算**：**System / Few-shot / Runtime Context** **上限** **须** **OpenAPI 冻结**。详 [`runtime-injection.md` §6](runtime-injection.md)。 |
| **PM-C14** | **Safety 最高优先级**：**不得** **被 场景策略正文（§3 · `promptPackType` ∈ 场景族）/User 覆盖或省略**（**法务 OVERRIDE** 除外）。详 [`runtime-injection.md` §7～§7.1](runtime-injection.md)（**用语闸**）。 |

### 1.4 `CC-P1-04` · Prompt **全流程 DoD**（登记核对）

**完整关闭** **仍** **以** [`contract-closure.md`](../../../contract-closure.md) **§3** **为主表**；**合入前** **建议** **本域 MR** **逐项勾选**：

| # | 核对项 | 锚点 |
|---|--------|------|
| 1 | **登记表** **Prompt 行**：Spec + **Owner**（[`OWNERS.md`](../../../../openapi/OWNERS.md)） | [`design/api.md`](../../../design/api.md)、[`admin/prompt-management.yaml`](../../../../openapi/admin/prompt-management.yaml) |
| 2 | **`billing`** **与** **可计费/封印** **无口头分叉** | [`billing/overview.md`](../billing-management/overview.md)、[`consume-and-bill.md`](../../../flows/consume-and-bill.md) |
| 3 | **`telegram`** **变量/长度** **与** **拼装闸** | [`telegram/overview.md`](../../agent/telegram/overview.md) **§2.6/`callback_data`；§2.5 · 类型 A（总则 §2～§2.6 同窗）**、[`runtime-injection.md`](runtime-injection.md) |
| 4 | **`observability` §2.3** **`agent.prompt.binding_resolved` / `ResolvedPromptBinding`** | [`observability/overview.md`](../../../observability/overview.md) |
| 6 | **`contract-closure` §1.2 · §9** | **六款** **逐项** **MR** **自检** **与** **归档口径**（**CC-P0-01**） |

## 2. FR-PM · 需求细项与展开

| 编号 | 一级簇 | PRD FR-MC | 功能描述 |
|------|--------|-----------|----------|
| **FR-PM01** | 治理 / RBAC / 审计 | — | Prompt 模块 **独立资源前缀**（如 `prompt.*`/`pm.*`）；**须**有可区分审计类型；导出/拷贝 **受 RBAC**；与运营台其它模块 **不共享**粗放「超级写」在未授权时。**详见 §2.1**。 |
| **FR-PM02** | **系统** Prompt 包 | **201** | **`SYSTEM`** 类包：**列表、详情只读展示、版本履历**；新建版本 / 发布；**发布后 LOCKED**。 |
| **FR-PM03** | **Trading / 编排场景** Prompt 包 | **202** | **`TRADING`** / **`ANALYSIS`** / **`SCENARIO_TRADING`** 等（命名以 **`PromptPackType` OpenAPI 枚举**冻结为准）：**分析/行情等非交易写场景**单列 **`ANALYSIS`**；**同窗** **状态机/校验**与 **`TRADING`**（**须 `scenarioId`** 等）。 |
| **FR-PM04** | **Safety / 护栏** Prompt 包 | **203** | **`SAFETY`/`POLICY`** 类：同上；常用于 **风控话术、拒绝模板**；变更 **建议**走高风险审批路由（[`rules`](rules.md)）。 |
| **FR-PM05** | Few-shot 示例 | **204** | **示例库 CRUD**（或可版本化挂载到 **场景草稿**）；**绑定**场景包条目；导入导出 **脱敏评审**后可做。 |
| **FR-PM06** | 沙箱 / 测试 | **205** | **隔离环境**：用 **抽样 fixture** 或对 **staging 模型别名**跑一次；**禁止**绑定 **生产写**权限与 **真实用户密钥**；输入 **PII / 明文 Secret** **禁入**日志默认路径。 |
| **FR-PM07** | 发布 · 回滚 | **206～207** | **Publish**：`promptPackVersion` **+1** **单调**（同 **`promptPackId`**）；发布后 **运行时读「当前生效」**。**Rollback**：选定 **`promptPackVersion`** **复位生效指针**；**审计**区分 **`PROMPT_ROLLBACK`** / **`PROMPT_PUBLISH`**；实现 **指针回指 vs 新发「等价回滚版」`** **须在 OpenAPI 明示**。**详见 §2.7**。 |
| **FR-PM08** | 运行时生效读路径 | — | **`GET`/BFF**：按 **`scenarioId`/`promptPackId`/`locale`** 返回 **生效正文 + version**；**ETag**/短 **`Cache-Control`**；**失效**钩子 **Subscribe publish 事件**。**对用户响应**严禁 **草稿**。**详见 §2.9**。**PRD 无单行 MC**——**横切契约**，与 **`design/api` 登记表**绑定。 |

---

### 2.1 FR-PM01 · 治理 / RBAC / 审计

- **RBAC**：缺省矩阵见 [`rules.md`](rules.md) **§2**。**SAFETY 包**：**Approve** **Publish/Rollback**（**Approver**）；**TRADING/ANALYSIS/SYSTEM**：**可依 §7 「P0 免检」放宽**——**放宽时** Editor **须有** **`prompt.pack.publish`** 且 **Approver 行**在 IAM **显式移除**。**具体角色名**：所内 **`IAM`**。
- **审计（最低集）**：`PROMPT_DRAFT_SAVED`、`PROMPT_PUBLISHED`、`PROMPT_ROLLBACK`、`PROMPT_SYSTEM_VERSION_CREATED`、`FEWSHOT_MUTATED`、`SANDBOX_RUN`（占位名，与实现对签）；须含 **`promptPackId` / `promptPackVersion` / `actor` / `scenarioId`**（若有）/ **diff ref**（若存对象存储）。
- **Secret**：控制台与 API **never** Prompt 内含 **交易所 Key**；Few-shot **不得**录入 **可复制 Secret**。

### 2.2 FR-PM02 · FR-MC201 系统 Prompt 包

**列表**：`promptPackId`、类型=**SYSTEM**、**当前生效 `promptPackVersion`**、更新时间、锁定标记。**详情**：Markdown/结构化正文 **只读**（若 **`LOCKED`**）；**新版本**：从生效版 **快照复制**为新草稿。**发布**：通过后 **新版本生效**，旧版履历保留。

### 2.3 FR-PM03 · FR-MC202 Trading（场景家族）Prompt 包

与 **§2.2** 同 **状态机**，类型 **TRADING**（或等价枚举）；**必填/推荐**：**`scenarioId`**、**可选 `recommendedSkillSpecVersion`**（引用 **不拷贝** **`trade-assistance`** 正文）。

**扩展 `ANALYSIS`**（**行情分析 / 投研等非交易写链路**）：**同窗**本条 **生命周期与 Publish 必填**（如 **`scenarioId`**），枚举见 OpenAPI **`PromptPackType`**。

### 2.4 FR-PM04 · FR-MC203 Safety Prompt 包

同 **§2.2** 结构，类型 **SAFETY**；Publish **建议**走 **Approver**。

### 2.5 FR-PM05 · FR-MC204 Few-shot

- **挂载点**：每条示例 **隶属**某一 **场景包草稿** **或** 全局 Few-shot **池**（二选一会签，**默认** **跟场景草稿**）。
- **字段**：role / content / （可选）`name`、`tags`；**校验**超长与 **注入**风险提示。
- **版本**：Few-shot **随场景包发布会冻结**到新 **`promptPackVersion`**（不推荐「独立于包版本漂移」）。

#### 2.5.1 分析类包 · Market Narrative Few-shot（`FR-PM05` 扩展 · 非新 PM-C）

**宿主**：**`promptPackType=ANALYSIS`** **场景包**（**含 **`read.market.*`/`market.read_*`** **路由同窗**）。

**每包建议 1～3 条**，**须** **示范** **[`common-phrases` §8.6](../../../prompts/shared/common-phrases.md) **登记下限**：

- **Ticker + 锚句同窗**（**含 `lastPrice` + 一句盘感**）  
- **Funding 问句 + 费率数值 + `funding_*` 锚句**  
- **拒用客服腔 Bad vs Good 单轮对照**

**禁止**：Few-shot **复制 §8.2/§8.7 全表** **或** **替代 **`marketNarrativeHints`**。**Git 镜像（Publish 正文）** → [`library/packs/fewshot-narrative-analysis.zh-CN.md`](../../../prompts/library/packs/fewshot-narrative-analysis.zh-CN.md)（**评审索引** [`narrative-few-shot-specimens.md`](../../../prompts/analysis/narrative-few-shot-specimens.md)）。

### 2.6 FR-PM06 · FR-MC205 沙箱

- **入口**：场景草稿页 **试运行** Tab；独立 **Sandbox** 路由 **可选**。  
- **数据**：fixture **JSON**（用户消息序列、占位变量）；**须**明示 **不脱敏则用假数据**。  
- **模型调用**：可走 **staging `defaultModelAlias`**（[`ai-settings`](../ai-settings/overview.md)），**扣费**：**不得**计入生产账务（或由 **sandbox 账户**）。

### 2.7 FR-PM07 · FR-MC206～207 发布与回滚

**前置**：校验 **必填引用**完整（scenario、skillSpecRef 等）；**Tool/Prompt 占位符**不与 **`agent-orchestration`** **冲突**。  
**发布**：`promptPackVersion := max(previous)+1`；写 **`PUBLISHED`** 事件；**BFF/runtime 缓存** **失效**。  
**回滚**：从历史选 **≤ 当前生效**之一版本 **重新置顶**（实现可为 **新发一条「回滚版」`** 或直接 **指针回指** ——须在 **OpenAPI** 明示）；**审计**必选。

### 2.8 发布前校验清单（FR-PM07）

在 **允许点 Publish** 前 **须**（自动化或 **CI 闸门**）：

1. **`scenarioId`**：**`TRADING`** / **`ANALYSIS`** → **须**在 **`agent-orchestration` 寄存器** **存在**（若 **staging 专用 id**：**禁止**混入 **生产租户**链路，须在 **`contract-closure`**/**环境策略**单列）；**SAFETY**：按 **§2.4** 与 [`config.md`](config.md) **§1**。  
2. **占位符**：`body` **内 `{{var}}`** **须** **`variableSchema`** 可校验 **或** **通过内置 regex 白名单**；**且** **不得**命中 **`placeholder` denylist**（[`runtime-injection.md` §2.3](runtime-injection.md)）。  
3. **外部链接 / `tool` 宏**（若有）：**不得**突破 **`exchange-agent` FR-T05** **写路径**叙事。  
4. **Few-shot role**：**仅** `system`|`user`|`assistant`（或 **OpenAPI enum**）。  
5. **`skillSpecRef`**：若填则 **须在 `trade-assistance` §8** **可解析**。  
6. **Tool 与 Schema**：**`toolId`** **存在**；**若有** **示意性 tool 调用块** **须**与 **当前 JSON Schema** **一致**（**禁止** **平行真源**）——**[`runtime-injection.md` §4～§5](runtime-injection.md)**。  
7. **Token / 模型**：**分项 + 总上下文** **须**满足 **平台保留余量** 与 **`targetModelFamily`**（若有）——[`runtime-injection.md` §6](runtime-injection.md)。  
8. **Safety 用语闸**：**不得**命中 **`safetyPhrase` blocklist**（[**`runtime-injection.md` §7.1～§7.1.2**](runtime-injection.md)）；**revision** **`safetyPhraseBlocklistRevision`** **须** **与** **`design`** **对齐**；**扫描范围** **`safetyPhraseScanScope`** **默认** **`FULL_PACK`**。  
9. **Runtime 技能范围（`skillSpecRef` 门禁 · 非 Prompt 托管 Skill）**：**`publishRequired`** 条目 **须** 通过 [`skill-specs/scripts/check_skill_contract_complete.py`](../../../skill-specs/scripts/check_skill_contract_complete.py)；Publish 载荷 **=** Git [`skill-specs/<skillId>.md`](../../../skill-specs/PUBLISH.md) **全文**（**禁止** 截断增量段）；**`skillSpecVersion`** **单调** 且 **与** [`trade-assistance` §4](../../agent/exchange-agent/trade-assistance.md) **同窗**。**控制台** **不得** 在 Prompt 正文编辑 Skill Schema/Slot/Tool。

### 2.9 FR-PM08 · 运行时生效读路径

- **路由形态**（示例）：`GET /internal/prompts/effective?scenarioId=…&locale=…` **或** **`promptPackId` 直查**——**以登记表为准**。  
- **响应**：**min** `promptPackId`、`promptPackVersion`、`body`（或分段块）、`fewShots`、`etag`。**若** API **按块返回** **须** **与 [`runtime-injection.md` §1](runtime-injection.md) 顺序可对签**。  
- **缓存**：**CDN/BFF** **须** **Publish 后 purge 或** **短 TTL + ETag**——**不得** **>5min** **强缓存**且无 **版本键**（默认值，**可 OVERRIDE**）。  
- **失败**：包 **不存在 / 全下线** → **`FR-T05`** **拒答链** **或** **500 内部**（**禁止** **伪造成功执行**）；详见 **§7**。  


## 3. FR-MC201～207 映射

| FR-MC | FR-PM | 简述 |
|-------|-------|------|
| **201** | **FR-PM02** | 系统 Prompt 包 |
| **202** | **FR-PM03** | Trading / ANALYSIS 场景 Prompt 包 |
| **203** | **FR-PM04** | Safety Prompt 包 |
| **204** | **FR-PM05** | Few-shot |
| **205** | **FR-PM06** | 沙箱/测试 |
| **206～207** | **FR-PM07** | 发布 **+** 回滚、`promptPackVersion` |

---

### 3.1 FR-MC 子项展开（测试用例挂载建议）

**规则**：**FR-MC** = PRD 模块二条目；**FR-PM** = 域内挂载点。**PRD** 单行见 [`management-console-v1-prd.md` §5](../management-console-v1-prd.md)。

| FR-MC | FR-PM |
|-------|-------|
| 201 | FR-PM01（审计/RBAC）；FR-PM02 |
| 202 | FR-PM01；FR-PM03 |
| 203 | FR-PM01；FR-PM04 |
| 204 | FR-PM05 |
| 205 | FR-PM06 |
| 206～207 | FR-PM07；**FR-PM08**（读路径契约） |

**横切**：**FR-PM01**、**FR-PM08** **适用所有 FR-MC**（治理 + 运行时读）；**拼装 / 注入 / 会话冻结 / 预算 / Safety 优先** 见 **[`runtime-injection.md`](runtime-injection.md)**（**PM-C08～PM-C14** 与 **§2.8** 对签）。

---

## 4. 验收标准 SC-PM（V1）

| 编号 | Given | When | Then |
|------|--------|------|------|
| **SC-PM-01** | 系统包 **`LOCKED`** | 运营点 **原位保存**正文 | **拒绝**或非入口；须有 **新版本**路径 |
| **SC-PM-02** | 场景 **草稿** | 编辑 Prompt + Few-shot + 校验通过 | **可存盘**且无 **500** |
| **SC-PM-03** | 场景草稿 | **Publish** | **`promptPackVersion` 递增**且 **履历**可查 |
| **SC-PM-04** | 已有多版 | **Rollback** 到选定版 | **当前生效指针**指向该版；审计 **记录** |
| **SC-PM-05** | Few-shot ≥1 | **发布场景包** | 生效版 **可读**Few-shot **冻结快照** |
| **SC-PM-06** | 沙箱环境 | **Run**fixture | **不**写入生产订单；日志 **无痕**或可配置脱敏 |
| **SC-PM-07** | **Viewer**角色 | Publish/Rollback | **403**或无入口 |
| **SC-PM-08** | **模板 T04** 绑定 `promptPackRef` | Prompt 后端 **不可用/下线**（若定义） | **`agent-management`** 侧 **告警/阻断新发**语义成立（与该域 [`functions.md · T04`](../agent-management/functions.md) **对签**） |
| **SC-PM-09** | 一次执行 | **`observability`** 可查 | `promptPackVersion`（或等价）**可被 join** **`executionId`/session** |
| **SC-PM-10** | **`TRADING`/`ANALYSIS`** 草稿，`scenarioId` 空 | **Publish** | **拒绝** `PROMPT_SCENARIO_INVALID` **或**等价；**无「半发布」** |
| **SC-PM-11** | **`If-Match`** 过期 | **SaveDraft** | **`409`/`PROMPT_VERSION_CONFLICT`**；**无损**重读再提交 |
| **SC-PM-12** | **`GET` 生效**（用户链路） | **任意** | **响应** **无** `draft` **flag**泄露；**仅**已发布 **version** |
| **SC-PM-13** | 正文 **> PM-C04 上限** | 保存 | **`PROMPT_BODY_TOO_LARGE`** |
| **SC-PM-14** | **Publish**成功后 | Runtime **拉生效**（**新回合或未冻结会话**） | **≤1 个时钟步**内可读 **新版本** **或** **显式陈旧码**（**不得**静默混版）——**阈值** **`design`** **定 SLA**；**同回合内** **不因 Publish 切换**——**SC-PM-15** |
| **SC-PM-15** | **回合进行中** | 后台 **新发 Publish** **更高** `promptPackVersion` | **同回合** **仍** **使用** **解析时刻** **`resolvedPromptBinding`**（**PM-C10**）；**下一** **新回合** **切新**版 |
| **SC-PM-16** | 模型 **tools** 声明 | **任意** `toolId` | **parameters** **与** **Registry/OpenAPI SSOT** **一致**（**PM-C11**）；**控制台无**手写参数真源 |
| **SC-PM-17** | 正文含 **§2.3.1 denylist** 或 **未声明**之 **凭据/内部配置类**占位 | **Publish** | **`PROMPT_INJECTION_FORBIDDEN`** **或** **`PROMPT_VALIDATION_FAILED`**（[`runtime-injection.md` §2.3](runtime-injection.md)） |
| **SC-PM-18** | **Few-shot / System / Context** 超 **冻结预算** | **Publish** 或 Runtime 组装 | **`PROMPT_BUDGET_EXCEEDED`** **或** **等价拦截** |
| **SC-PM-19** | **`TRADING`/`ANALYSIS`** **草稿正文** **含 §7.1.1 越狱短语** | **Publish** | **`PROMPT_SAFETY_VIOLATION`** **或** **`PROMPT_VALIDATION_FAILED`**；**`observability` `admin.prompt.publish_blocked`** **可检索** |
| **SC-PM-20** | **任意** **`promptPack`** **Publish** **成功** | **读** **该** **`promptPackVersion`** | **元数据** **含** **`publishedWithPlaceholderDenylistRevision`** **与** **`publishedWithSafetyPhraseBlocklistRevision`**（**等于** **Publish 时刻** **平台当前** **两** **revision**） |
| **SC-PM-21** | **`TRADING`/`ANALYSIS`** 包 **`skillSpecRef`** 和/或 **写路径 `scenarioId`** | **Publish**（**所内**须真 API；**原型**见 `promptPublishGate`） | **`GET …/skills/effective`** **成功** 或等价 Runtime 读；否则 **`PROMPT_SKILL_REF_INVALID`** **阻断**（**§2.8 行 9**）；UI **叙事** **Runtime 技能范围（发布门禁）**，**非**「技能绑定」 |
| **SC-PM-22** | **一次回合 Prompt 已拼装** | **运营/调试** 查看 **Assembly Trace** | **每层来源**（Base / Scenario / Runtime 块 / Output contract）**可 join** **`executionId`** 或 **`agent.prompt.binding_resolved`**；**Demo** 侧栏 **示意表** **满足**「可见性占位」，**量产** **须** 真 Trace |

---

## 5. 错误码与 API 对齐（V1）

下列 **`code`** 为 **管理台语义建议**；**真源**：所内 OpenAPI **`design/api.md`** **登记表**。**前缀** **`PROMPT_`** 或并入 **`ADMIN_`**——**须全站冻结一种**。

| `code` | 典型触发 |
|--------|-----------|
| `PROMPT_PACK_LOCKED` | 对 **`LOCKED`** 包 **`PUT`**正文 |
| `PROMPT_VERSION_CONFLICT` | **乐观锁**/`If-Match` 冲突 |
| `PROMPT_SCENARIO_INVALID` | `scenarioId` **未**在编排寄存器登记 |
| `PROMPT_SKILL_REF_INVALID` | `skillSpecVersion` **未知**或未发布 |
| `PROMPT_VALIDATION_FAILED` | 占位符/schema **校验失败** |
| `PROMPT_SANDBOX_FORBIDDEN` | 绑定 **生产 Key**拒绝 |
| `PROMPT_ROLLBACK_UNAVAILABLE` | 目标版本 **不可回指** |
| `PROMPT_BODY_TOO_LARGE` | 超 **§1.1 PM-C04** |
| `PROMPT_DEPRECATED` | 包 **deprecated** —— **已绑定**模板仍可读但 **告警**（**或对** **新发** **阻断**——与 **agent-management** 一并冻结） |
| `PROMPT_EFFECTIVE_UNAVAILABLE` | **运行时读路径** **无生效版** |
| `PROMPT_INJECTION_FORBIDDEN` | **禁止类变量** **或** **未授权占位符** **进入** Runtime（[`runtime-injection.md` §2](runtime-injection.md)） |
| `PROMPT_TOOL_REF_UNKNOWN` | **`toolId`** **不在** SSOT |
| `PROMPT_TOOL_SCHEMA_MISMATCH` | 正文示意 **与** Schema **不一致** |
| `PROMPT_BUDGET_EXCEEDED` | [`runtime-injection.md` §6](runtime-injection.md) Token/条数/Context **超限** |
| `PROMPT_MODEL_INCOMPATIBLE` | **模型族 / 上下文窗** **不满足** |
| `PROMPT_SAFETY_VIOLATION` | **Safety** **越狱/绕过**短语（[`runtime-injection.md` §7.1](runtime-injection.md)）或 **省略 Safety 块** **被阻断** |

---

## 6. 邻域完整性自检

| 邻域 | 落点 |
|------|------|
| **agent-management T04/T03** | 仅 **绑定** `promptPackRef`；**T04**：不可用/deprecate → **告警/阻断新发**；**revision 掉队黄灯**见 [`functions.md · T04`](../agent-management/functions.md) **§1.1、SC-AM-24**。 |
| **agent-orchestration** | **`scenarioId` DAG / 寄存器**与场景包一致 |
| **trade-assistance** | **`skillSpecVersion`** **引用**，**不复制**正文；Git SSOT [`skill-specs/PUBLISH.md`](../../../skill-specs/PUBLISH.md) |
| **observability** | **`promptPackVersion`** **`executionId` join**；**下限** **`agent.prompt.binding_resolved`** / **§2.3**、**SC-OBS04**（[`observability/overview`](../../../observability/overview.md)）；**Publish 闸失败** **`admin.prompt.publish_blocked`** |
| **telegram** | **卡片模板不属于本模块** |
| **contract-closure CC-P1-04** | **`§1.1`～`§7`**、**[`runtime-injection.md`](runtime-injection.md)** 与 **OpenAPI 登记**、**billing/telegram** 会签 **对齐**后 **可关**（见 [`contract-closure.md`](../../../contract-closure.md)）。 |
| **runtime-injection** | **Assembly / 变量闸 / 冻结 / Tool SSOT / 预算 / Safety 优先 / 错误 Scope / Ownership** |

---

## 7. 已决议默认与工程约束（V1）

| 主题 | **默认** |
|------|----------|
| **Publish 审批** | **SAFETY `promptPackKind`** **须 Approver**；**TRADING/ANALYSIS/SYSTEM** **可** **P0 免检**——**若** **Editor 可直接 Publish** **须**在 **`contract-closure`** **单行备案**环境（**预发/所内**）。 |
| **Few-shot 挂载** | **随场景包版本**（**PM-C05**）；**无**全局池。 |
| **`scenarioId`（TRADING）** | **Publish 前 blocking 校验**：空则拒绝（**SC-PM-10**）。 |
| **回滚** | **指针回指** **优先于** **伪造新版本号**——**须** **审计** **`PROMPT_ROLLBACK`**。 |
| **缓存** | **Publish 事件** **须** **触发** **BFF purge** **或** **`max-age ≤ 60s`** **且** **带 `ETag`**（**§2.9** **可 OVERRIDE**）。 |
| **`FR-T05` 联动** | **`PROMPT_EFFECTIVE_UNAVAILABLE`** → **用户侧透明拒答** **主路径**（见 [`overview.md`](../../agent/exchange-agent/overview.md)）。 |
| **`rules` RBAC 对齐** | **`rules.md` §2** 为缺省；若启用 **P0 · Editor 可直接 Publish**，**须**在 **`contract-closure`** 备案 **并**同步 **改 RBAC 矩阵**（Approver 列）。 |
| **`safetyPhraseScanScope`（Safety 扫入）** | **`FULL_PACK`**（[`runtime-injection.md` §7.1.2](runtime-injection.md)）；**生产** **`TRADING_BODY_FEWSHOT`** **须** **`contract-closure`**。 |
| **Prompt 错误 Scope（V1）** | **GLOBAL / TEMPLATE** **可做**；**INSTANCE** **级** **差异化**——**禁止**（[`runtime-injection.md` §8](runtime-injection.md)）。 |

**文档**：与 [`config.md`](config.md) **IA**、[`flow.md`](flow.md) **主路径**、[`rules.md`](rules.md) **RBAC·合规**、[`runtime-injection.md`](runtime-injection.md) **拼装/注入/预算**同步维护；**工程默认**以 **§7** 为准迭代 **`config`/`flow`**。**闭环 / 派工·检核** → [`closure-remaining` §7.2～§7.4](../../../closure-remaining.md#cc-ac09-closure-matrix) · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)**。
