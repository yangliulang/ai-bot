# Prompt Management · Runtime 注入与拼装契约（Assembly / Injection）

**所属体系**：**[PRS（Prompt Runtime System）](../../../prompt-runtime/README.md)** — 本篇为 **拼装契约 SSOT**。**改什么去哪** → **[PRS §4](../../../prompt-runtime/README.md#prs-where-to-edit)**（**块 5 读侧** → [**MNRA**](../../../market-narrative-runtime/README.md)）。

**叙事与治理**：[`overview.md`](overview.md)、[`functions.md`](functions.md)。  
本文定义 **单次模型调用前**，平台如何将 **SYSTEM / SAFETY / 场景策略正文（由 `scenarioId` 解析，`promptPackType` ∈ `TRADING`/`ANALYSIS` 等与 OpenAPI 同窗之场景族）**、**Few-shot**、**运行时上下文**、**Tool 形态**与 **用户输入** 组装为 **最终 messages**（或等价结构），以及 **变量注入风控**、**版本冻结**、**发布前兼容校验**与 **预算**。**不**替代 **LLM 供应商 Key**、**模型路由**（→ [`ai-settings`](../ai-settings/overview.md)、[`integrations/llm/provider-routing.md`](../../../integrations/llm/provider-routing.md)）。

---

## 1. Prompt Assembly Contract（拼装顺序）

**MUST**：Runtime **按以下顺序**构造 **发往模型的逻辑块**（实现可映射为多段 `system` / 单条 `system` 拼接，但 **语义顺序不得颠倒**）。**SAFETY** 块在 **语义上** **不可被后续块撤销或覆盖**（见下文 **§7**）。

| 顺序 | 块名 | 来源（真源） |
|:----:|------|----------------|
| 1 | **SYSTEM** | 已发布 **`promptPackKind=SYSTEM`** 生效版正文（[`functions` FR-PM02](functions.md)） |
| 2 | **SAFETY** | 已发布 **`SAFETY`** 生效版正文（[`functions` FR-PM04](functions.md)） |
| 3 | **场景策略正文** | 当前 **`scenarioId`** **与** **`promptPackRef` 绑定** 解析到的 **`TRADING`/`ANALYSIS` 等场景族包**生效版（[`functions` FR-PM03](functions.md)、[`routing-engine`](../../agent/agent-orchestration/routing-engine.md)） |
| 4 | **Few-shot** | 随 **§3 场景策略包** **冻结快照**之示例序列（[`functions` FR-PM05](functions.md)；**插在**本轮 **User** 之前） |
| 5 | **Runtime Context** | 运行时注入的 **结构化上下文**（会话摘要、`agentContext`、行情摘要等——**须经 §2 变量闸**） |
| 6 | **Tool Spec** | **§4**：**JSON Schema（及描述）单一 SSOT** 注入；**禁止**手写参数表替代 Schema |
| 7 | **User Input** | 当前用户 **本轮** 消息（多模态若有，以 OpenAPI 为准） |

**说明**：

- **Orchestration** 可在 **§6 分项预算**内对 **Runtime Context** 做 **裁剪/摘要**，但 **不得** **删除或后置** **SAFETY** 相对 **USER** 的 **约束语义**（见 **§7**）。  
- **Telegram 卡片模板** **不属于**本拼装链（[`telegram/overview` §2.5 · 类型 A；总则 §2～§2.6](../../agent/telegram/overview.md)）。  
- **与读路径对签**：解析 **`promptPackVersion`** 须与 [`functions` §2.9](functions.md)、**`observability`** 字段 **一致**。

---

## 2. Runtime Variable Injection Rules（变量注入 · Prompt 风控）

### 2.1 原则

- **允许注入**的变量 **仅** 来自：**(a)** 包内 **`variableSchema` 声明** 且 **通过发布前校验**；**(b)** **平台内置**只读上下文键（白名单，**以 OpenAPI `enum`/登记行为准**）。  
- **默认拒绝**：未在 schema/白名单出现的占位符 → **Publish 侧** **`PROMPT_VALIDATION_FAILED`**；**Runtime 侧**若仍出现非法键 → **`PROMPT_INJECTION_FORBIDDEN`** **或** **脱敏剔除**（**须** **`observability`** 可观测，**禁止**静默当成功）。

### 2.2 禁止注入（MUST NOT · 非穷举）

| 类 | 示例 | 说明 |
|----|------|------|
| **凭据 / Secret** | **API Key**、**HMAC Secret**、**子账户签名密钥**、**refresh token** | **永不得**写入 Prompt 正文、Few-shot、Runtime Context **可逆明文** |
| **内部配置真源** | **`internalConfig`**、**未脱敏网关路由**、**内部服务 admin 端点** | **防**：提示词诱导 **带出**运维面；**Runtime** 仅用 **已为终端设计**的 **摘要字段** |
| **可执行码 / 指令注入** | 要求模型 **忽略 Safety 护栏**、**泄露 system 全文** | **策略 + 输出闸**（与 **§7**、[`exchange-agent` FR-T05](../../agent/exchange-agent/overview.md) 对签） |

**与邻域对齐**：[`rules.md`](rules.md) **Secret/PII**；[`tool-management`](../tool-management/overview.md) **Schema 日志**。**占位符 denylist** 的 **下限键名/模式** **见 §2.3**；完整表 **须**在所内 **`design`/配置中心冻结** **`denylistRevision`** 并可审计；与 **`variableSchema` 校验**并行 **blocking** Save/Publish。

### 2.3 占位符 denylist（V1 下限 · `{{…}}` 内键名）

**适用范围**：**`body`**、**Few-shot `content`**、**沙箱 fixture** 中 **一切** `{{` + `}}` 形式占位符（含 `{{ var }}` **去空白** 后比对）。**比对规则**：对 **slug**（`{{` 与 `}}` 之间）做 **大小写不敏感**匹配；**任一**命中 **§2.3.1** **字面子串** → **拒绝 Save/Publish**（**`PROMPT_INJECTION_FORBIDDEN`** **或** **`PROMPT_VALIDATION_FAILED`**），**除非** **§2.3.3** **Override**。

#### 2.3.1 须拦截的字面子串（slug 内包含即拦截 · 非穷举）

以下 **为仓库内 V1 下限**；所内 **可增不可减**（**减项**须 **`contract-closure`** + 安全评审）。

| 触发子串（不分大小写） | 意图 |
|------------------------|------|
| `APIKEY`、`API_KEY`、`ACCESS_KEY`、`SECRET`、`SECRET_KEY`、`HMAC`、`SIGNING`、`PRIVATE_KEY` | **凭据 / 签名材料** |
| `REFRESH_TOKEN`、`BEARER`、`AUTH_TOKEN`、`PASSWORD`、`PASSWD`、`CREDENTIAL` | **令牌 / 口令** |
| `WEBHOOK_SECRET`、`CLIENT_SECRET` | **对称 / OAuth 秘钥** |
| `INTERNAL_CONFIG`、`INTERNALCONFIG`、`INTERNAL_API`、`ADMIN_URL`、`DEBUG_TOKEN` | **内部真源 / 运维面** |
| `SUBACCOUNT_SECRET`、`TRADING_API_SECRET`、`AGENT_TRADING_KEY` | **子账户 / Agent 交易**对称秘钥 **语义** |

**说明**：**公开运行时 id**（如 **`agentTradingApiKeyId`**）**允许**出现在 **platform 白名单上下文** **或** **`variableSchema`** **明确为非 Secret 的摘要字段**——**禁止**用 **`{{…}}`** 承载 **可复制 Secret**；**slug** **含 §2.3.1 子串** **一律** **拒绝**。**`AGENT_KEY`** **等笼统键名** **建议默认拦截**，**放行**须在 **`contract-closure`** **单列**并完成 **Approver**。

#### 2.3.2 Slug 规范化（实现 MUST）

1. `{{ a_b }}` → **`A_B`**（trim + upper 仅用于 **比对**；**落库**保存原貌 **可**）。  
2. **禁止** **空 slug**、**仅空白**、**嵌套 `{{`**（语法错误 → **`PROMPT_VALIDATION_FAILED`**）。  
3. **Unicode homoglyph** **不**作首版硬要求；**所内** **可**追加 **NFKC 归一化**（**MR** 记入 **`design`**）。

#### 2.3.3 与 `variableSchema` 的关系

- **即使** `variableSchema` **声明**某键，**若** slug **命中 §2.3.1**，**仍** **拒绝**（**Secret 不得入 Prompt 正文链**）。  
- **未命中 denylist** **且** **未**在 **schema / 平台白名单**：**仍**按 **§2.1** **`PROMPT_VALIDATION_FAILED`**。

#### 2.3.4 版本字段

- 控制台 / 审计 **可选** 暴露 **`placeholderDenylistRevision`**（整数单调）——**须**与 **配置中心当前修订** **一致**后 **校验**才 **通过**（**防** **旧节点** **漏拦**）。

---

### 2.4 对用户话术闸门字段（与 Prompt Library / Telegram 同窗）

**用途**：编排 / 网关 / `error-normalization` **在注入 Runtime Context（§1 顺序 · 块 5）** 时，可附带 **已定稿或已定性的用户可见信息**，供模型 **与** **[`prompts/library/ASSEMBLY`](../../../prompts/library/ASSEMBLY.md)**、**[`fragment-errors-user-visible`](../../../prompts/library/packs/fragment-errors-user-visible.zh-CN.md)** **对签**。**JSON 形状真源** **以所内 OpenAPI**（例：`agentContext` / 编排信封 **扩展字段**）**为准**；下表为 **仓库内 V1 下限键名** — **增删键名** **须** **`contract-closure` MR** **同窗** 更新本文 + **`prompt-management` CI 白名单**（§2.1）。

| 键（camelCase · 下限） | 类型（示意） | **MUST** |
|------------------------|--------------|----------|
| **`user_visible_message`** | `string` · **可选** | **若存在**：模型 **须** **保留语义与事实走向**，**仅** 按 **`effective_locale`** **润色** — **禁止** 把 UNKNOWN 改成确定失败等。**同窗** [`library` L2](../../../prompts/library/packs/fragment-errors-user-visible.zh-CN.md)、[`Runtime/error-normalization`](../../../Runtime/error-normalization.md)。 |
| **`requires_main_site`** | `boolean` · **可选**；默认 **`false` 或未出现** | **`true`** **仅当** 能力在 [**`exchange-agent/boundaries`**](../../agent/exchange-agent/boundaries.md) **等处冻结**、**且无 Telegram 等价闭环**。**为真** 时 **方可在本条用户气泡末尾**附 **官方 Deeplink**，且 **仍须**说明回到对话后的下一步 — [`shared/response-format` §1](../../../prompts/shared/response-format.md)。 |

**说明**：实现 **可**将上述键挂在 **`agentContext`**、**`executionEnvelope`** 或与 **`executionId`** **同窗**之结构；**占位符** **`{{…}}`** **形态** **不必**与键名相同 — **须**在 **Publish / Runtime** **映射层** **显式绑定** **勿静默丢字段**。**禁止**把 **`user_visible_message`** **用于**承载 Secret / 原始上游 JSON。

### 2.4.1 行情只读：`userVisibleMarketData` · `marketInsightData`（产品下限）

**宿主**：[`exchange-agent/market-runtime-payload.md`](../../agent/exchange-agent/market-runtime-payload.md) — **`userVisibleMarketData`**（典型绑定 **`market.read_quote`**；**ticker 字段映射** **§3.3**）与 **`marketInsightData`**（典型绑定 **`market.read_deep_analysis`**）之 **camelCase 字段下限**、**对用户 MUST NOT**。Runtime 向 **块 5 · Runtime Context** 注入等价结构时：**OpenAPI/`agentContext` 形状仍为 SSOT**；**须在 Publish 映射层**对齐键名 **`variableSchema`/白名单**（**同窗** **`market-runtime-payload`**、[`prompts/library/ASSEMBLY`](../../../prompts/library/ASSEMBLY.md)）。**跨会话 Semantic Narrative**（**若解冻**）→ [`memory-runtime` §9](../../../Runtime/memory-runtime.md) **`semanticNarrativeBlock`** **等** **须** **同窗映射** **且** **默认 OFF** — **OpenAPI** [`memory-runtime-schemas.yaml`](../../../../openapi/components/memory-runtime-schemas.yaml) **`AgentRuntimeMemoryContext`**。**市场叙事 hints**（**草案**）→ [`market-runtime-payload` §3.4](../../agent/exchange-agent/market-runtime-payload.md) **`marketNarrativeHints`**；**OpenAPI** → [`market-runtime-schemas.yaml`](../../../../openapi/components/market-runtime-schemas.yaml) **`MarketNarrativeHints`/`AgentRuntimeMarketContext`**；**锚句 SSOT** → [`common-phrases` §8](../../../prompts/shared/common-phrases.md) **§8**（**非** **`TRADER_PHRASE` pack**）。

---

## 3. Prompt Freeze Rule（会话内版本冻结）

**已定义**：**`promptPackVersion`** **单调 immutable**（[`functions` PM-C02](functions.md)）。  
**补充（MUST · V1）**：

1. **解析时刻**：Orchestration / Runtime **在「一轮可计费对话回合」开端**（**首条 user 进线**或**明确定义的 session start**）解析 **SYSTEM / SAFETY / TRADING** 的 **`promptPackId` + `promptPackVersion`**（及 **Few-shot 快照**），写入 **本轮 session 的 `resolvedPromptBinding`**。**JSON 形状** **以** OpenAPI **`components/prompt-management-schemas.yaml` · `ResolvedPromptBinding`** **为 SSOT**（**场景策略槽位** `trading*` **亦承载 `ANALYSIS` 族** 之已发布包 **id/version**；与 [`observability/overview.md`](../../../observability/overview.md) **§2.3** **字段同窗**）。  
2. **回合内稳定**：**同一回合**内 **禁止**因 **后台 Publish** **自动切换**至 **更高 `promptPackVersion`**，**除非** **显式产品行为**「用户触发新开回合」**且** **auditable**。**防止**同轮 **混版**（**SC-PM-15**）。  
3. **新 Publish 生效**：**下一** **新回合**（新 session 或 **显式 reset**）**拉取** **当前生效指针**。  
4. **观测**：**`observability`** **须**能关联 **`resolvedPromptBinding`** 与 **`executionId`**（与 **SC-PM-09** 对签）。

---

## 4. Tool Injection Contract（Tool Schema → Prompt）

**MUST**：

1. **唯一 SSOT**：注入到模型侧 **tools / function declarations** 的 **名称、描述、parameters（JSON Schema）** **须**来自 **登记 toolchain 真源**：[`design/api`](../../../../design/api.md) **矩阵（PATH 冻结项）** + [`trade-assistance.md`](../../agent/exchange-agent/trade-assistance.md) **§8**（**`toolId`**）；**[`tool-management`](../tool-management/overview.md)** 为 **镜像与运营视图**，**不**自定 Schema。  
2. **禁止手写 Tool 参数**：Prompt 正文 **不得**内含 **平行于 Schema 的参数表 / 必填表** **作为调用真源**；若须 **行文说明**，**须**标明 **「以 Registry Schema 为准」** **且** **Publish CI** **校验**正文 **不与 Schema 冲突**（见 **§5**）。  
3. **占位符**：若 **`scenarioId`/编排** **绑定** **`toolId` 列表**，仅 **注入** **已启用**且在 **矩阵已冻结**行之工具（与 **SC-MCV1-05** 对齐）。  
4. **变更**：Registry **晋级** Schema **须在** **`contract-closure`** **与 Prompt 兼容闸**联动（§5）。

---

## 5. Prompt Compatibility Check（发布前校验 · 扩充）

**在 [`functions` §2.8](functions.md) 清单之上**，**还须**满足（**blocking** Publish，**或可配置为 Approver 豁免**——**SAFETY 禁止默认豁免**）：

| # | 校验项 | 失败码（建议） |
|---|--------|----------------|
| 1 | **Tool 存在性**：正文/`tool` 宏引用的 **`toolId`** **均在** **§4 SSOT** **可解析** | `PROMPT_TOOL_REF_UNKNOWN`（与 [`functions.md` §5](functions.md) **冻结同名**） |
| 2 | **参数兼容**：Prompt 内 **若**含 **结构化 tool 调用示例**，**须**与 **当前 Schema** **required / types** **一致**（**不得**多传未定义字段为「真源」） | `PROMPT_TOOL_SCHEMA_MISMATCH` |
| 3 | **Token 长度**：**§6** 分项预算 **加总**（粗估或 tokenizer）**须** ≤ **目标模型上下文窗口** 的 **平台保留余量**（**具体阈值** **`design`/`ai-settings` 冻结**） | `PROMPT_BUDGET_EXCEEDED` |
| 4 | **模型兼容**：包元数据 **`targetModelFamily`/`minContext`**（若有）**须**与 **拟发布环境默认模型** **兼容** | `PROMPT_MODEL_INCOMPATIBLE` |

**CI 闸门**：与 **`FR-PM07`**、**CC-P1-04** 对签；**登记表** **须**列 **兼容闸** **输入**（例如 **tools 清单来源**）。失败码 **`code`** **真源**仍归 **[`functions.md` §5](functions.md)**，**禁止**控制台与文档 **同名异义**。

---

## 6. Prompt Runtime Budget（分项预算）

**默认上限** **须**在 **所内 OpenAPI / `design`** **冻结数值**；下表为 **V1 需求形状**（**未填数** = **TBD**）。

| 项 | 限制维度 | 说明 |
|----|----------|------|
| **System Prompt** | **Max Token**（或 **MaxChars** 衍生） | **仅** **SYSTEM 块**；与 **PM-C04** **整包上限** **协查** |
| **Few-shot** | **Max Count**（条数）+ **单条 Max Token** | **超出** → **拒绝 Publish** **或** **截断策略**（**须** **书面**选一种并写 **`contract-closure`**） |
| **Runtime Context** | **Max Length**（字符或 token） | **摘要失败** → **降级** **可观测事件** **+** **不得** **注入 §2.2 禁止类** |

**运算**：**总上下文** **尚须**为 **User + 模型输出** **预留** **余量**——**由 `ai-settings`/Runtime 横切** **定默认**。

---

## 7. Safety Priority Rule（Safety 最高优先级）

**MUST**：

1. **拼装位序**：**SAFETY** 在 **TRADING / Few-shot / User** **之前**（见 **§1**）。  
2. **语义**：**任何** **TRADING / SYSTEM / User** **内容** **不得** **声明覆盖、撤销或忽略** **SAFETY** 中 **平台强制策略**；**Runtime** **须** **拒绝** **将 SAFETY 块整体省略**（**除** **法务 OVERRIDE** **登记**）。  
3. **检测**：若 **Publish 校验** 命中 **§7.1 用语闸**（**维护黑名单 + 修订号**）→ **`PROMPT_VALIDATION_FAILED`** **或** **`PROMPT_SAFETY_VIOLATION`**。  
4. **与 FR-T05**：无法注入 Safety（包缺失）→ **不得** **伪造安全**；走 **拒答/不可用**（[`functions` §7](functions.md)）。

### 7.1 越狱 / 绕过护栏用语闸（V1 下限）

**范围**：**`scanText`** **的** **块覆盖** **由** **`safetyPhraseScanScope`**（**§7.1.2**）**冻结**。**`TRADING`** 包 **自身** **`body`** **与** **`fewShots[].content`** **始终** **参与** **子串匹配**；**是否** **并入** **SYSTEM/SAFETY** **正文** **见** **§7.1.2**。**默认** **`FULL_PACK`**——**防止** **仅** **TRADING** **干净但** **SYSTEM** **含越狱锚点**。

**匹配规则（MUST）**：

1. **归一化**：**拉丁** **`scanText`** **子串** **可先** **NFKC**（**推荐**）再 **转小写** 后比对；**中文** **段落** **不经** **小写**，**原样** **子串**匹配。  
2. **子串**：对 **§7.1.1** **每条** **短语** **做** **包含**检测；**拉丁** **短语** **以小写形式** **与** **归一化后** **`scanText`** **比对**；**命中** → **blocking** Publish。  
3. **修订**：**`safetyPhraseBlocklistRevision`** **单调**；**与** **`placeholderDenylistRevision`** **独立**。**所内** **`design`** **须** **可回滚** **配置**。  
4. **日志**：命中 **仅** **记** **`matchedRuleId` + revision**（[`observability` §2.3](../../../observability/overview.md) **`admin.prompt.publish_blocked`**），**禁止** **默认** **落** **命中句全文**。

#### 7.1.1 仓库内 V1 下限短语表（可增不可减）

| # | 短语（**拉丁** · 小写比较） | 意图 |
|---|---------------------------|------|
| 1 | `ignore previous instructions` | **忽略前置** |
| 2 | `ignore the above` / `disregard the above` | **否定上文** |
| 3 | `bypass safety` / `bypass the safety` | **绕过安全** |
| 4 | `you are now in developer mode` | **模式劫持** |
| 5 | `jailbreak` / `dan mode` | **越狱** |
| 6 | `reveal your system prompt` / `show your system prompt` | **套取 system** |
| 7 | `没有安全限制` / `忽略安全策略` / `绕过护栏` / `无视风控` / `取消内容策略` | **中文绕过** |

**误杀**：**须** **走** **草稿内** **「申请豁免」**（**单条规则 id**）**或** **改文案**；**不得** **静默** **关闸**。

#### 7.1.2 `safetyPhraseScanScope`（扫描纳入范围 · OpenAPI 冻结）

**字段**： **`safetyPhraseScanScope`** —— 挂在 **`promptPackVersion`** 元数据（**或**包级 **默认**，**优先级** **`design`** 定）。

| 值 | `scanText` **纳入内容** |
|----|--------------------------|
| **`FULL_PACK`（默认）** | **`SYSTEM` + `SAFETY` + `TRADING` 各包 `body`** + **本条 TRADING 包** **`fewShots[].content`**（与 **§7.1** **范围**一节 **一致**） |
| **`TRADING_BODY_FEWSHOT`** | **仅** **当前 **`TRADING`** 包** **`body` + Few-shot**，**不包含** SYSTEM/SAFETY **正文扫描** |

**规则（MUST）**：

1. **`FULL_PACK`** **为** **生产租户** **默认值**；**Runtime** **仍须** **按** **§1** **组装** **注入** SYSTEM/SAFETY（**不因** **`TRADING_BODY_FEWSHOT`** **省略注入**）。  
2. **`TRADING_BODY_FEWSHOT`** **仅允许** **预发/沙箱**，**或** **生产** **须 **`contract-closure`** **单行备案** + **`Approver`**（**安全风险**：SYSTEM/SAFETY **或未扫块** **可能**藏 **越狱锚点**）。  
3. **Publish** **须** **持久化** **当时** **`safetyPhraseBlocklistRevision`**（见 **`config`** **`publishedWith*Revision`**）。

---

## 8. Prompt Runtime Error Handling（Scope）

**错误 / 降级** **作用域** **V1** **定义**：

| Scope | 说明 |
|-------|------|
| **GLOBAL** | **全平台** **默认策略**（例：`PROMPT_EFFECTIVE_UNAVAILABLE` → **FR-T05**）；**配置**在 **全局配置 / Runtime** |
| **TEMPLATE** | **模板级** **覆盖**（[`agent-management`](../agent-management/overview.md) **绑定** `promptPackRef` **时** **可选** **降级策略**——**须** **不弱于** GLOBAL **安全底线**） |
| **INSTANCE** | **实例级** **差异化策略**：**V1 禁止**。首版 **不**提供 **按用户实例改写 Prompt 运行时错误语义** 的 **产品入口**（运营 API / IAM）；后续 **须** **MR + `contract-closure`** |

---

## 9. Prompt Runtime Ownership（谁可改）

**对象** 与 **默认属主**（**运营组织意义**；**技术强制** **靠 IAM**）：

| 对象 | 默认 **内容属主** | **说明** |
|------|-------------------|----------|
| **System Prompt** | **平台**（所内 **平台 / 产研** 角色） | **LOCKED** 发布后 **仅** **新版本线** |
| **Safety Prompt** | **平台** | **Suggest** **Approver**；**见 [`rules` RBAC](rules.md) |
| **Trading Prompt** | **平台**（或 **平台授权之「场景运营」**；**所内定名**） | **须** **scenarioId** **登记** |
| **Few-shot** | **平台运营**（**PromptEditor** 域；**与 TRADING 包** **同事务版本**） | **PM-C05** **默认随场景包** |

**IAM（MUST）**：

- **修改 / 删除** **须** **独立 permission**（例：`prompt.pack.edit`、`prompt.pack.delete`、`prompt.fewshot.edit` —— **所内命名冻结**）。  
- **默认**：**无** **写/删** **权限**；**仅** **显式授予** 后 **可操作**。  
- **与 [`rules.md` §2](rules.md)**：**PromptEditor** 为 **能力包模板**；**实际** **以 IAM 细粒度** **为准**。

---

## 10. 与 `functions.md` 条目映射（便于验收）

| 主题 | PM / 条目 |
|------|-----------|
| **拼装顺序 / Safety 优先** | **PM-C08**、**PM-C14**（[`functions.md` §1.3](functions.md)；**Safety§7.1～7.1.2**） |
| **变量闸 / denylist / Tool SSOT** | **PM-C09**、**PM-C11**（[`functions.md` §1.3](functions.md)，**§2.3 denylist**） |
| **`user_visible_message` / `requires_main_site`** | **§2.4** ↔ **[`prompts/library/ASSEMBLY`](../../../prompts/library/ASSEMBLY.md)** §2、[`response-format` §1](../../../prompts/shared/response-format.md) |
| **会话冻结** | **PM-C10** |
| **Safety 扫入范围** | **§7.1.2** `safetyPhraseScanScope` ↔ [`functions.md` §7](functions.md) |
| **发布兼容闸 / 预算** | **PM-C12**、**PM-C13**、[`functions.md` §2.8](functions.md) |
| **运行时错误 Scope** | **§8**（本文 **Prompt Runtime Error Handling**）+ [`functions.md` §5](functions.md) **`PROMPT_*`** |

---

**文档版本**：1.0.2 · **维护**：与 **`design/api` 登记表**、**`trade-assistance` §8**、**`agent-orchestration`** **同步**（**产品 + Agent Runtime owner**）；变更 **拼装顺序** **须** **ADR + `contract-closure`**。**AC-09 检核** → [`closure-remaining` §7.2～§7.4](../../../closure-remaining.md#cc-ac09-closure-matrix) · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)**。
