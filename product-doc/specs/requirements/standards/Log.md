# `standards/` 修订履历（Log）

## 适用范围（必读）

凡变更 **`specs/requirements/standards/`** 目录内 **任一 `.md` 文件**（含本 Log），须在 **同一合并请求（MR）或同一提交批次** 内，于本文 **顶部追加一条记录**（**最新在上**）。  
Git 历史仍为底层溯源；本文件提供 **人类可读的连续摘要**，便于评审与发布对照。

---

## 记录格式（复制后填空）

```markdown
### YYYY-MM-DD

- **摘要**：<一句话说明改了什么、为何>
- **涉及文件**：`<相对本目录的路径，如 prd-standard.md>`
- **关联**：<MR 编号 / Issue / 无>
```

同一自然日多次合并：可在同一日期标题下 **并列多条** `- **摘要**：…` 条目。

---

## 履历（最新在上）

### 2026-05-27

- **摘要**：`executionId` 冻结为 **纯数字 10～19 位**；OpenAPI `ExecutionId` 与 Web/Admin 演示数据对齐。
- **涉及文件**：`naming-standard.md`；同窗 `openapi/components/identity-schemas.yaml`
- **关联**：用户端账单 · 执行 ID 规则

### 2026-05-27

- **摘要**：`prompt-standard.md` 增补运营六段正文 vs Git 条文双层分工，链向 `prompts/governance-map.md`。
- **涉及文件**：`prompt-standard.md`
- **关联**：Prompt 治理升级 P0

### 2026-05-26

- **摘要**：`review-and-change-standard` §2 **Roadmap**：**须** **含** **`product/roadmap`** **「规格体系快照」L1～L7** **择要补丁**；§3 模板 Roadmap 行 **对齐**。**承** 本日 **上条**。
- **涉及文件**：`review-and-change-standard.md`、`Log.md`
- **关联**：`roadmap` 体系化 MR

- **摘要**：`review-and-change-standard` §2 增 **Roadmap** 勾选、§3 摘要模板增 Roadmap 行；**同窗** **`product/roadmap/README`** **维护约定**（需求变更 **须** 同步路线图及豁免）。
- **涉及文件**：`review-and-change-standard.md`
- **关联**：路线图同步惯例 MR

### 2026-05-25

- **摘要**：`interaction-flow-standard` §1 表增链 Telegram §2.8（STM 清空本会话 UX）。
- **涉及文件**：`interaction-flow-standard.md`
- **关联**：`memory-runtime` §13 / `telegram/overview` §2.8 同窗 MR
- **摘要**：`interaction-flow-standard` §1 表增链向 Telegram §2.7（跨会话记忆查看/撤销 UX）。
- **涉及文件**：`interaction-flow-standard.md`
- **关联**：`memory-runtime` §9 / `telegram/overview` §2.7 同窗 MR

### 2026-05-18

- **摘要**：**凡条文含 `contract-closure`、此前未显式链 `closure-remaining` 的入口** — **于首个二级标题（`##`）前补一行「关单余量（MR 首节）」：`§0` · `§6/§6.4` · `§6.4 问题→动作`**；覆盖 **`Runtime/*`、多域 `functions`/`rules`/`flow`、`exchange-agent`、`onboarding`、`flows/*`、`integrations/exchange`、`risk/*`、`observability/tracing`、`tools/tool-registry`、`prompts/system`、本目录多份索引标准**。**删除损坏之** **`_fix_closure_remaining.py`**。
- **涉及文件**：`api-standard.md`、`business-process-standard.md`、`interaction-flow-standard.md`、`naming-standard.md`、`prd-standard.md`、`review-process.md`、`STANDARDS-ADOPTION.md`；**并行** **`../Runtime/*`、并行 `../domains/`、`../flows/`、`../integrations/exchange/`、`../risk/`、`../observability/tracing.md`、`../tools/tool-registry.md`、`../prompts/system/system.md`** 等 — **详见同批次变更文件列表**。  
  **`Log.md`**
- **关联**：无

- **摘要**：**`README.md`** **推荐阅读** **与** **维护说明** **补** **`closure-remaining` §0 速链**（**与** **`contract-closure`** **同窗**：**契约收口语义** **与** **MR 粘贴缺锚**）。
- **涉及文件**：**`README.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`review-and-change-standard.md`** **篇首** **与** **§2 设计与收口** **补** **`closure-remaining` §0·§6** **自检条目**。
- **涉及文件**：**`review-and-change-standard.md`**；**`Log.md`**
- **关联**：无

### 2026-05-15

- **摘要**：**`prompt-standard.md`** **互引** **`prompts/library/`**（**可粘贴拼装库**：**`packs/`、`scenarios/registry.md`**），与 **`prompts/README`** **新增 **`library/`** **目录树** **同窗**。
- **涉及文件**：**`prompt-standard.md`**；**`Log.md`**
- **关联**：无

### 2026-05-14

- **摘要**：**`interaction-flow-standard.md`** **§1 表增补 §2.4**，**§5 **指向 **`telegram/overview` §2.4 **`effective_locale`****。**同窗 MR：** **`telegram/overview` §2.4、`prompts/system/system.md`、`prompts/shared/response-format.md`。**  
- **涉及文件**：**`interaction-flow-standard.md`**；**`Log.md`**  
- **关联**：无

### 2026-05-13

- **摘要**：**`naming-standard.md`** **§1**——**`userId`** 明示为 **Coobit 母账户（主账号）UID**，与 **`subUid`** 区分；**Coobit / Coolbit** 书写约定；版本 **1.2.1**。
- **涉及文件**：**`naming-standard.md`**；**`Log.md`**
- **关联**：无

### 2026-05-11

- **摘要**：**`interaction-flow-standard.md`**——**`telegram.md`** **→ **`telegram/overview.md`**（条文路径一致）；**§1** **开通/Billing** **锚 **§2.2～§2.5**；**自检表** **「见 telegram §」** **措辞统一**。
- **涉及文件**：**`interaction-flow-standard.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`prd-standard.md`** **§1 存放表**——**渠道必选能力条目**：**主链 **`telegram/overview.md`**（条文 SSOT）、**`README`** **仅目录索引**；**补充 **类型 A **`overview` §2.5.x** **指针**，与 **`interaction-flow-standard`** **分工一致**。
- **涉及文件**：**`prd-standard.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`interaction-flow-standard.md`** **§1·§3**——修正 **Telegram 渠道下限** **错误指向 **`README`** **的问题**：**改为 **`overview`、`telegram-binding`、`integrations/deeplink`** **同源分流**；**README** **仅作目录索引**。
- **涉及文件**：**`interaction-flow-standard.md`**；**`Log.md`**
- **关联**：无

---

- **摘要**：**`naming-standard.md`** **§1 增补**——**OpenAPI** 真源指针 **`openapi/components/identity-schemas.yaml`**（与 **§1 ID** 表同窗）。
- **涉及文件**：**`naming-standard.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`naming-standard.md`** **新增 §1**——**`executionId` / `scenarioId` / `sessionId` / 用户标识** 的 **语义、默认字符与形态、稳定性与互斥** 规则表；**与** **`routing-engine`、Runtime `execution`、Observability** **互引**。
- **涉及文件**：**`naming-standard.md`**；**`Log.md`**
- **关联**：无

### 2026-05-07

- **摘要**：**`tool-standard.md`** **修复** trade-assistance **外链** **全角括号** **至正文外**，**避免** **链接解析** **吞** **后续 `](...)`**；**`review-and-change-standard.md`** **Markdown** **清单** **示例** **改写**，**与** **正文** **§2** **「Markdown」** **条** **一致**（**消除** **易被** **链扫** **误捕获** **的** **占位写法**）。
- **涉及文件**：**`tool-standard.md`**、**`review-and-change-standard.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`review-and-change-standard.md`**：MR 清单 **增 **`risk/acceptance` `SC-RISK*`**、§3 摘要模板 **护栏行**、**Markdown 链卫生**；**与** **全库文档 Review** **收敛**。
- **涉及文件**：**`review-and-change-standard.md`**；**`Log.md`**
- **关联**：无

### 2026-05-06

- **摘要**：**`prompt-standard.md`** **补充 **`prompts/` **子目录 **`trading/README`**、**`analysis/README`** **与根 **`README` **文档版本约定** **指针**。
- **涉及文件**：**`prompt-standard.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`prompt-standard.md`** **对齐 **`prompts/` **MVP** **七目录**（**撤 **`fallbacks`/`policies` **prompt 子树**）；条文优先。
- **涉及文件**：**`prompt-standard.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`prompt-standard.md`** **对齐 **`prompts/` **重构**：**条文拆分 ** **+ ** **场景树 ** **+ **`fallbacks/`** **同窗 **`Runtime/fallback-policy`**；**`examples.md`** **须立项过闸**。
- **涉及文件**：**`prompt-standard.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`prompt-standard.md`** **对齐 **`prompts/` **协作策略**：以条文与按需草稿为主，禁止无需求提交对话示例占位。
- **涉及文件**：**`prompt-standard.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`integrations`** **回迁** **`specs/requirements/integrations/`**（保留 **`exchange/`**、**`telegram/`**、**`llm/`**、**`notifications/`** 分卷）；修正 **`integrations/`** 内相对 **`design`** / **`domains`** / **`flows`** 链；**`design/api`**、**`admin/`**、**`telegram`**、**`Runtime/recovery`**、**`domains/README`**、**`requirements/README`**、**`specs/README`**、**`workspace-layout`**、**`specify-rules`**、根 **`README`**、**Speckit Skill** 同窗刷新。
- **涉及文件**：**`../integrations/`**（迁入与内链）；**`../../design/api.md`**；**`domains/`**（多文件）；**`Runtime/recovery.md`**；**`../README.md`**；**`../../README.md`**；**`../../../README.md`**；**`../../../.specify/memory/workspace-layout.md`**；**`../../../.cursor/rules/specify-rules.mdc`**；**`../../../.cursor/skills/speckit-workspace-specs/SKILL.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`integrations`** 从 **`requirements/integrations/`** **迁至** **`specs/integrations/`**（`exchange/`、`telegram/`、`llm/`、`notifications/` 分卷）；原 **`llm-provider.md`** 并入 **`llm/provider-routing.md`**；全库互引、`requirements/README`、`specs/README`、**`workspace-layout`**、**`specify-rules`**、**Speckit Skill**、根 **`README`** 树同步刷新。
- **涉及文件**：**`../../integrations/`**（新建）；**`../`**（删 **`integrations/`** 旧稿；**`README`、`domains/README`、`Runtime/recovery`、多域 `admin/`、`design/api`**）；**`../../README.md`**（**`specs/README`**）；**`../../../README.md`**；**`../../../.specify/memory/workspace-layout.md`**；**`../../../.cursor/rules/specify-rules.mdc`**；**`../../../.cursor/skills/speckit-workspace-specs/SKILL.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`flows/trade-via-agent`**：概要 **`S1`～`S10`**、七段扩展 **`S11`～`S17`**；现货限价专节 **偏离带/OpenOrders** **去步号歧义**；合约/全仓 **专节加子路径编号声明**；**`STANDARDS-ADOPTION`** Wave F **`trade-via-agent`** 行与 **§4 Done**。
- **涉及文件**：**`../flows/trade-via-agent.md`**、**`STANDARDS-ADOPTION.md`**；**`Log.md`**
- **关联**：无

- **摘要**：Wave F 增量：**`flows/read-analyze-and-search-via-agent`**、**`automation-alerts`**、**`wealth-via-agent`** 主路径 **`S{n}`**；**`wealth`** **参与文档**去重；**`STANDARDS-ADOPTION`** Wave F 表与 **§4 Done**。
- **涉及文件**：**`../flows/read-analyze-and-search-via-agent.md`**、**`../flows/automation-alerts.md`**、**`../flows/wealth-via-agent.md`**、**`STANDARDS-ADOPTION.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**`Runtime`** 外链 **去「仅 README」**：**主链** 统一 **`Runtime/overview.md`（必要时加分卷 `execution`/`recovery`/…）**；**`README`** 仅为 **短入口**；刷新 **`spec.md`、`specs/README`、`requirements/README`、域名索引、编排/交易域、PRD/agent-management/prompt-management、Skill、workspace-layout、STANDARDS-ADOPTION（Wave R 去重）**。
- **涉及文件**：**`../spec.md`**、**`../../README.md`**、**`../README.md`**、**`domains/README.md`**、**`domains/agent/README.md`**、**`domains/agent/onboarding/overview.md`**、**`domains/agent/agent-orchestration/{overview,retry-policy,runtime-freeze,state-machine}.md`**、**`domains/agent/exchange-agent/{monitoring-tasks,overview-legacy-migration,boundaries}.md`**、**`domains/admin/{management-console-v1-prd,agent-management/overview,prompt-management/overview}.md`**、**`STANDARDS-ADOPTION.md`**、**`../../../.cursor/skills/speckit-workspace-specs/SKILL.md`**、**`../../../.specify/memory/workspace-layout.md`**、**`../../../.cursor/rules/specify-rules.mdc`**；**`Log.md`**
- **关联**：无

- **摘要**：**`Runtime/`** 按 **`overview` + `README` + 10 分卷**（`boundaries`、`execution`、`sessions`、`runtime-state`、`context-management`、`persistence`、`freeze-policy`、`locking`、`recovery`、`event-storage`）重组；**`fallback`/`retry` 等 stub** 并入 **`recovery.md`**；全库 **`Runtime/fallback.md`** 链改为 **`recovery.md`**；**`STANDARDS-ADOPTION`**（Wave R 表 **+** 文首/步骤 5 **`overview`** 指针）更新；**`workspace-layout`、`speckit-workspace-specs` Skill**、编排/后台 **同窗链** 刷新。
- **涉及文件**：**`STANDARDS-ADOPTION.md`**、**`Log.md`**；**`../Runtime/`**（多文件）；**`../design/api.md`**；**`../../integrations/`**；**`../domains/admin/ai-settings/`**、**`management-console-v1-prd.md`**；**`../domains/agent/agent-orchestration/runtime-freeze.md`**、**`retry-policy.md`**；**`../../../.specify/memory/workspace-layout.md`**；**`../README.md`**
- **关联**：无

- **摘要**：**`STANDARDS-ADOPTION`** Wave F 表中 **`user-onboarding.md`** 链改为 **`onboarding/overview.md`**，与 **`domains/agent/onboarding/`** 八文件切片一致。
- **涉及文件**：**`standards/STANDARDS-ADOPTION.md`**；**`Log.md`**
- **关联**：无

- **摘要**：**链文统一**：全库指向 **`exchange-agent/overview.md`** 的 **`exchange-agent.md` 链字** 改为 **`overview.md`**；**`trading-skills`** 统一为 **`trade-assistance`**（Skill 与 `trade-assistance.md` **职责段** **保留** **`trading-skills`** **历史指称**）；**`tool-standard.md`** 去重链、**`overview` §3** 增 **旧稿→分卷** 回迁表；**`contract-closure`** 闭环第 3～5 条 **链字** 对齐 **`overview`/`trade-assistance`**。
- **涉及文件**：**`standards/tool-standard.md`**、**`../tools/tool-registry.md`**、**`../contract-closure.md`**、**`../domains/agent/exchange-agent/overview.md`**、**多处 `flows/`、`design/`、`admin/`、`product/`、`observability/overview.md`**（见 diff）；**`Log.md`**
- **关联**：无

- **摘要**：**`domains/agent/trading-agent/` → `exchange-agent/`** 产品与路径重命名；**八卷**骨架（overview、intents、market-intelligence、portfolio-insight、risk-alerts、trade-assistance、monitoring-tasks、boundaries）；**`STANDARDS-ADOPTION`** Wave D 表 **`overview`/`trade-assistance`** 锚；库内 **`agent/trading-agent/*`** 路由 **批量**改 **`exchange-agent/*`**，`trading-skills`/`flow`/`runtime`/`risk`/`tools`/`metrics` **类旧链**分别 **导向** **`trade-assistance`/`trade-via-agent`/`overview`/`boundaries`**/**`metrics/trading-metrics.md`**。**`exchange-agent`** 行文 **≠** **`admin/trading-agent-config`**（后者 **保留**）。
- **涉及文件**：**`STANDARDS-ADOPTION.md`**、`../domains/agent/**`、`../product.md`、`**/flows/**`、`design/**`、`admin/**`、`../../README.md`、**`../../../.specify/memory/workspace-layout.md`**、**`../../../.cursor/skills/**`** 等（见提交 diff）；**`Log.md`**
- **关联**：无

- **摘要**：**`STANDARDS-ADOPTION`**：`agent-orchestration` / `agent-context` **示例锚** 迁至 **`domains/agent/agent-orchestration/overview.md`、`agent-context/overview.md`**（**删除** **`trading-agent/*.md`** 兼容路径）。
- **涉及文件**：**`STANDARDS-ADOPTION.md`**；编排/上下文 **锚** 迁至 **`domains/agent/agent-orchestration/overview.md`**、**`domains/agent/agent-context/overview.md`**（详见 diff）；**`Log.md`**
- **关联**：无

- **摘要**：删除 **`domains/admin/marketplace-management/`** 占位目录（技能市场在 PRD **V1 不建议做**）；更新 **`domains/README`**、**`.specify/memory/workspace-layout`**、**`product/roadmap`**；历史 **Log** 条目中「涉及文件」去掉对已删路径的引用。
- **涉及文件**：**删** **`../domains/admin/marketplace-management/`**；**`../domains/README.md`**、**`../../../product/roadmap.md`**、**`../../../.specify/memory/workspace-layout.md`**、**`Log.md`**
- **关联**：无

- **摘要**：**废弃 `domains/admin/agent-management/{config,overview,checklist,...}`**，**管理后台 V1 产品需求 SSOT** 改为 **[`../domains/admin/management-console-v1-prd.md`](../domains/admin/management-console-v1-prd.md)**；**`STANDARDS-ADOPTION`** A0 索引随 **PRD**；**`speckit-workspace-specs` Skill**、`spec.md`、**design/README**、全库链接 **批量**自 `config.md` 路径迁出；**`agent-management/`** 仅存 **README.md** 占位；**`.specify/scripts/_rewrite_paths.py`** 目标同步。
- **涉及文件**：**`../domains/admin/management-console-v1-prd.md`**（新）、**`../domains/admin/agent-management/README.md`**（新）、**删** 原 `agent-management` 多文；**`STANDARDS-ADOPTION.md`、`Log.md`**、**仓库内** 互引 **管理后台** 之 **`.md`/`mdc`**（见提交 diff）
- **关联**：无

- **摘要**：**`Config` 零残留收口（除本文履历中的历史措辞）**：**`product/roadmap`** 闭环与 **A0** 走查；**`design/README`、`design/architecture`**（在途表、契约收口条、**prompt-management** 相对链）；**`prompt-management/overview`** 去掉口语别名；**`speckit-workspace-specs` Skill** 域列表 **`config.md`**。
- **涉及文件**：`../../../product/roadmap.md`、`../../design/README.md`、`../../design/architecture.md`、`../domains/admin/prompt-management/overview.md`、`../../../.cursor/skills/speckit-workspace-specs/SKILL.md`、`Log.md`
- **关联**：无

- **摘要**：**`Config` 指称收尾（非 Log 叙事）**：**`billing-management/overview`** 全书 **「Config」→`config.md`/`config.md` §** 等；**`agent-management/{config,overview,checklist}`** 标题与互引；**`telegram/overview`** 表头 **`configKey`**；**`prompt-management`** 单列 **SSOT+口语**说明；**`standards/business-process-standard`** **前置条件**行。
- **涉及文件**：`../domains/admin/billing-management/overview.md`、`../domains/admin/agent-management/{config,overview,checklist}.md`、`../domains/admin/prompt-management/overview.md`、`../domains/agent/telegram/overview.md`、`business-process-standard.md`、`Log.md`
- **关联**：无

- **摘要**：**`Config`→`config.md`（SSOT 文件名）语义续扫**：**`flows/`**（`activate-trading-agent`、`trade-via-agent`、`consume-and-bill`）**契约收口与运营配置引用**；**`product.md`** 契约/提示词划界行；**`contract-closure`** **§5** 标题、**CC-P0-05** DoD、**§6** **prompt-management** 路径修正；**`billing-management/overview`** 内 **反引号 `Config`** 批量为 **`config.md`**；**`agent-management/checklist`、`standards/review-and-change-standard`** **§13/§14** 措辞。
- **涉及文件**：`../flows/activate-trading-agent.md`、`../flows/trade-via-agent.md`、`../flows/consume-and-bill.md`、`../product.md`、`../contract-closure.md`、`../domains/admin/billing-management/overview.md`、`../domains/admin/agent-management/checklist.md`、`review-and-change-standard.md`、`Log.md`
- **关联**：无

- **摘要**：**断链体检（续）**：**`llm-provider`** **`Runtime/`** 路径大小写；**`contract-closure`** **CC-P1-04** → **`domains/admin/prompt-management/overview.md`**（**`Config §1.3`→`config.md`§1.3**）；**`spec.md`、`business/README`、`product.md`** **`product/`→`../../../product/…`**；**`flow/trading-agent/runtime/metrics`**：**修复 `config.md#`、错配反引号导致的 Markdown 加粗断裂**，**`flow`** 表内 **`config.md` §** 与 **`domains/agent/telegram`** 等措辞；**`exchange-agent`** **契约行 / 脚注 / US-T04 / §6.1 索引行**。

- **涉及文件**：`../../integrations/llm/provider-routing.md`、`../contract-closure.md`、`spec.md`、`../business/README.md`、`../product.md`、`../domains/agent/exchange-agent/{flow,trading-agent,runtime,metrics}.md`、`Log.md`

- **关联**：无

- **摘要**：**`domains/agent/exchange-agent/`**：修复 **`trading-skills`** §8.5 **流程链** Markdown；**`\`Config\``** → **`\`config.md\``**（同目录多文）；**`\`channels\``** → **`\`domains/agent/telegram\``**。**`billing-management`**：**`flows` / `contract-closure` / `design`** → **`../../../…` / `../../../../design/`**（补正首轮替换笔误）；正文 **`Config §8.2`** → **`config.md`**。**`agent-management/config`**：**`design/*`、`product.md`** 深层链。**`prompt-management`**：**`flows`、`billing`、Telegram** `overview`。**`observability/overview`**：**`domains/admin/...` 与 `domains/agent/...`**。
- **涉及文件**：`../domains/agent/exchange-agent/`（多文）、`../domains/admin/billing-management/overview.md`、`../domains/admin/management-console-v1-prd.md`、`../domains/admin/prompt-management/overview.md`、`../observability/overview.md`、`Log.md`
- **关联**：无
- **摘要**：**原 `execution-plan`** 已并入 **`product/roadmap.md`** 后 **删除** **`product/roadmap/execution-plan.md`**；校正 **`checklist`**、`STANDARDS-ADOPTION`、`Log` 等引用；修正 **`domains/agent/telegram/overview.md`** 内大量错误相对路径（`../domains/…`、`flows`、`design`、`standards`、`contract-closure`）；全库 **markdown 链** 统一 **`Config.md` → `config.md`**（文件名小写）。
- **涉及文件**：`../../../product/`（`roadmap.md`、`roadmap/README`、`milestones`、`README`）、`../domains/admin/agent-management/checklist.md`、`../domains/agent/telegram/overview.md`、`STANDARDS-ADOPTION.md`、`Log.md`；`../../design/api.md`、各 `flows/`、`domains/` 等（**`Config.md` 链接批量改为 `config.md`**）
- **关联**：无
- **摘要**：目录重组后续收尾：**`channels/`** 用词统一为 **`domains/agent/telegram/`**；**`STANDARDS-ADOPTION`** Wave D/C 条目链更正；新增薄索引 **`prompt-standard` / `tool-standard` / `api-standard` / `naming-standard` / `review-process`**；**`standards/README`** 索引表更新。
- **涉及文件**：`prd-standard.md`、`business-process-standard.md`、`interaction-flow-standard.md`、`README.md`、`STANDARDS-ADOPTION.md`、`review-and-change-standard.md`、`prompt-standard.md`、`tool-standard.md`、`api-standard.md`、`naming-standard.md`、`review-process.md`、`Log.md`
- **关联**：无

- **摘要**：**`domains/` 按业务域重组**：`trading-agent/`、`onboarding/`、`admin/`（含 `billing-management`、`agent-management`、`prompt-management` 等）、`observability/`、`analytics-management/`；各域 **`README`**；重写根 **`domains/README`**；全局更新 **`spec`、`product`、`contract-closure`、`design`、`flows`、`domains/agent/telegram`、`Runtime`、`requirements/README`**、**`workspace-layout`、`specify-rules`、`speckit-workspace-specs`**、**`product/roadmap`、STANDARDS-ADOPTION** 中的域路径与本条 Wave D **`admin-console` → `admin/agent-management`** 清单行。
- **涉及文件**：`../domains/`（整树搬迁与新建 README）、`../spec.md`、`../product.md`、`../contract-closure.md`、`../README.md`、`STANDARDS-ADOPTION.md`、`Log.md`；`../../../.specify/memory/workspace-layout.md`、`../../../.cursor/rules/specify-rules.mdc`、`../../../.cursor/skills/speckit-workspace-specs/SKILL.md`；`../../../product/roadmap.md`；`../../design/`（链）、`../flows/`、`../domains/agent/telegram/`、`../Runtime/README.md` 等（路径替换批次）
- **关联**：无

- **摘要**：新增 **`specs/requirements/Runtime/`** 目录约定：撰写 **`../Runtime/README.md`**（与 `domains`/`design` 边界、互引规则）；同步 **`requirements/README`**、**`spec.md`**、根 **`specs/README`**、**`.specify/memory/workspace-layout`**、**`STANDARDS-ADOPTION`**（MR 步骤增补 **Runtime**、**Wave R**）、**`speckit-workspace-specs` Skill**、**`specify-rules.mdc`**、**`domains/README`**。
- **涉及文件**：`../Runtime/README.md`、`STANDARDS-ADOPTION.md`、`../README.md`、`../spec.md`、`../../README.md`、`../../../.specify/memory/workspace-layout.md`、`../../../.cursor/skills/speckit-workspace-specs/SKILL.md`、`../../../.cursor/rules/specify-rules.mdc`、`../domains/README.md`、`Log.md`
- **关联**：无

- **摘要**：新增 **`STANDARDS-ADOPTION.md`**（MR 固定动作与 Wave F/D/CH）；刷新 **`standards/README`**、**`requirements/README`**、**`product/roadmap`**、**`domains/README`**、**`spec`**；**`flows`** 对齐 **`business-process` §2**：**`activate-trading-agent`/`consume-and-bill`** **`S{n}`**、七条 **`flows` 文首摘要**；**`domains/agent/telegram/overview.md` §6**；**`flows/README`、`domains/agent/telegram/README`** 链入 adoption。
- **涉及文件**：`STANDARDS-ADOPTION.md`、`README.md`、`../README.md`、`../spec.md`、`../flows/`（多篇）、`../domains/agent/telegram/overview.md`、`../domains/agent/telegram/README.md`、`../../../product/roadmap.md`、`../domains/README.md`、`Log.md`
- **关联**：无

- **摘要**：三本核心规范定稿向优化：`prd-standard` 补齐 **§8**、**§3.2 product.md**、**§4.3 FR↔SC**、**§5** 术语与前缀说明、自检中性化、配置 Key 可选；`interaction-flow-standard` 弱化硬编码域引用、修正措辞、新增 **§10**（评审/`Log`）；`business-process-standard` 拆分 **§7 反模式**、软化自检与「终局」表述、**§11** 衔接 **`Log.md`**；`README` 增加 **「先规范后存量」工作流**。
- **涉及文件**：`prd-standard.md`、`interaction-flow-standard.md`、`business-process-standard.md`、`README.md`、`Log.md`
- **关联**：无

- **摘要**：（回溯）引入 **`Log.md`** 与 **`review-and-change`**、需求 **`requirements/README`**、**`spec.md`**、Skills 指针联动。
- **涉及文件**：`Log.md`、`README.md`、`review-and-change-standard.md`、`prd-standard.md`、`../README.md`、`../spec.md`；`.cursor/skills/speckit-workspace-specs/SKILL.md`、`product-manager/SKILL.md`
- **关联**：无

- **摘要**：（回溯）先前迭代：`review-and-change-standard`、三套 `*-standard.md` 多轮扩充、索引与 Skills 链入 **`review-and-change`**。
- **涉及文件**：`review-and-change-standard.md`、`prd-standard.md`、`interaction-flow-standard.md`、`business-process-standard.md`、`README.md`、`../spec.md`、`../README.md`；`.cursor/skills/` 多处
- **关联**：无
