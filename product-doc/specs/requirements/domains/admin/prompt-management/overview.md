# 域需求：提示词管理（交易所后台 — Prompt Governance）

| 项 | 内容 |
|----|------|
| **产品** | ChainUp AI Agent（Coobit 单所） |
| **文档** | `specs/requirements/domains/admin/prompt-management/overview.md` |
| **状态** | **评审中（V1）** — **域内需求与** **`runtime-injection`** **已** **可** **对照实现**；**全流程 DoD（`CC-P1-04`）**：**模块二** **与** **`billing`/`telegram`/`observability` Prompt join** **同窗 MR** + **登记表 Prompt 行** [**`admin/prompt-management.yaml`**](../../../../openapi/admin/prompt-management.yaml) **+** [`OWNERS.md`](../../../../openapi/OWNERS.md) **具名**；**未齐** **不得** **标 Prompt B 已关**。 |
| **权威位置** | **Coobit 交易所主后台 · 模块二**：独立 **「Prompt / 提示词管理」** 导航；与管理台 **`management-console-v1-prd` §5** 对签。 |
| **互引**：[**PRS 总入口 · 改什么去哪 §4**](../../../prompt-runtime/README.md#prs-where-to-edit)；[`management-console-v1-prd.md`](../management-console-v1-prd.md) **附录 A §1.3**（与模块一 [`agent-management`](../agent-management/overview.md) **划界**）；[`routing-engine.md`](../../agent/agent-orchestration/routing-engine.md)（**scenario 产品 SSOT · 与 Prompt 绑定**）；[`runtime-injection.md`](runtime-injection.md)；[`../../agent/agent-orchestration/overview.md`](../../agent/agent-orchestration/overview.md)；[`../../agent/exchange-agent/trade-assistance.md`](../../agent/exchange-agent/trade-assistance.md)；[`../../agent/telegram/overview.md`](../../agent/telegram/overview.md)（**§2.5 · 类型 A；总则 §2～§2.6**）；[`../../../observability/overview.md`](../../../observability/overview.md) **§2.3 · SC-OBS04**；[`../../../Runtime/context-management.md`](../../../Runtime/context-management.md)、[`../../../Runtime/overview.md`](../../../Runtime/overview.md)、[`../../../Runtime/README.md`](../../../Runtime/README.md)；[`../../../contract-closure.md`](../../../contract-closure.md) **CC-P1-04**；[**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · **[§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path) |

---

### 小团队落地边界（[`LITE-MODE.md`](../../../LITE-MODE.md)）

- **已具备**：本域正文 + [`runtime-injection.md`](runtime-injection.md) + OpenAPI 可对照实现；表首 **「评审中（V1）」** 表示 **条文与实现对齐可并行**，**不等于** **CC-P1-04（B 阶段 / 多模块会签）已关**。  
- **AC-09 族闭环**（**派工 §7.2 · 检核 §7.4**；**需求侧索引**，**非**替代 **CC-P1-04 DoD**）：[**§0 速链**](../../../closure-remaining.md#closure-remaining-quicklinks) · **[§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path) · [`closure-remaining` §7.2～§7.4](../../../closure-remaining.md#cc-ac09-closure-matrix) — **须**与 [`runtime-injection`](runtime-injection.md)、[`contract-closure` **CC-P1-04**](../../../contract-closure.md) **对读**。  
- **未关闭项闭环路径**（**与 AC-09 / MR 勾选同窗**）：[`closure-remaining` §7.5](../../../closure-remaining.md#cc-remaining-open-close-path)。  
- **MR 关单勾选**（**与 §9/§2.1 同窗编排**）：[`closure-remaining` §7.6](../../../closure-remaining.md#cc-closure-exec-checklist)。  
- **未闭合前**：**不** 在对外材料中称「交易所后台 Prompt 管理已等同生产契约收口」；详见 [`contract-closure.md`](../../../contract-closure.md) **CC-P1-04**、[当前快照 · `product/release-notes.md`](../../../../../product/release-notes.md)。

---

## 1. 目的（摘要）

**系统 / 场景 Prompt** **版本化治理** + **运行时拼装契约**（[`runtime-injection.md`](runtime-injection.md)）：系统包 **`LOCKED` 发布后只读**，仅 **新版本线**演进；场景包 **草稿 →（评审）→ 发布 → 回滚**；**`promptPackVersion`** **单调可追溯**；**会话内 `resolvedPromptBinding` 冻结**（**PM-C10**）；运行时 **`scenarioId`、`promptPackVersion`** 与结构化事件 **`agent.prompt.binding_resolved`**（**`observability` §2.3**；**绑定快照 JSON** **SSOT**：[`specs/openapi/components/prompt-management-schemas.yaml`](../../../../openapi/components/prompt-management-schemas.yaml) · **`ResolvedPromptBinding`**）须与 **`agent-orchestration`** **可对签**。**不**承载 **Telegram 卡片模板正文**。详参 [`functions.md`](functions.md)。

### 业务模式：`scenarioId` 优先与 **`promptPackKind` 边界**

| 层级 | SSOT | 说明 |
|------|------|------|
| **业务能力 / 意图** | [**`scenarioId` 寄存器**](../../agent/agent-orchestration/routing-engine.md)、**`flows`/Intent**、**Tool 矩阵** | **现货/合约/理财/自动化等** **在此展开**；Orchestration **命中场景**后解析 **`promptPackId`+Version**。**不得**单靠 `promptPackKind` 枚举穷尽业务。 |
| **Prompt 资产 + 大类** | 本域 **`promptPackId`**、`promptPackKind`（OpenAPI `PromptPackType`） | **`kind` 仅表达** **拼装与治理大类**，见 [`config.md`](config.md) §1.1a。 |
| **实例/模板引用** | **`agent-management`** **`boundPromptPackRef`** | **绑定**本域发布物；**场景→默认包** **由编排/寄存器附属列或等价配置维护**（OpenAPI/`contract-closure` 终裁）。 |

---

## 2. 本版包含 / 不包含

| 判定 | 内容 |
|------|------|
| **包含** | **FR-PM01～08**（[`functions.md`](functions.md)）；硬约束 **`PM-C01～15`**（**§1.3** + **§1.2 PM-C15**）；**[`runtime-injection.md`](runtime-injection.md)**（**Assembly · 占位符 denylist · Safety §7.1 · 冻结 · Tool · 预算 · 错误 Scope · Ownership**）。**FR-MC201～207** · **映射 §3**。 |
| **不包含** | 模型路由、供应商 Secret、Temperature 等 → [`ai-settings/overview.md`](../ai-settings/overview.md)、[`integrations/llm/provider-routing.md`](../../../integrations/llm/provider-routing.md)；**skill 正文** → [`trade-assistance`](../../agent/exchange-agent/trade-assistance.md)；**模板向导里选包** UI → **`agent-management` T03/T04**（本域只管 **可被引用之发布物**）。 |

**Git 协作区（非 SSOT）**：[`prompts/README`](../../../prompts/README.md) — MVP 七目录，单根 [`system/system.md`](../../../prompts/system/system.md)；叙事核心 [`intents/README`](../../../prompts/intents/README.md)、[`confirmation/README`](../../../prompts/confirmation/README.md)。写 / 读场景索引导航 [`trading/README`](../../../prompts/trading/README.md)、[`analysis/README`](../../../prompts/analysis/README.md)。不设 `fallbacks/`、`policies/`、`monitoring/`、`onboarding/` 独立 prompt 子树。Publish 仍以本域与 `design/` 为准。降级同窗 [`Runtime/fallback-policy`](../../../Runtime/fallback-policy.md)。

---

## 3. FR / SC 索引（SSOT：`functions.md`）

| 类型 | 位置 |
|------|------|
| **FR-PM01～08**、**PM-C**、**[`runtime-injection`](runtime-injection.md)**、**§7** 默认、`FR-MC` 映射 | [`functions.md` §1～§3.1 · §7](functions.md) |
| **SC-PM-01～22**（V1；**22** 拼装 Trace **量产** 对签 **观测**） | [`functions.md` §4](functions.md) |
| **错误码草案** | [`functions.md` §5](functions.md) |

---

## 4. 文档索引（阅读顺序）

| 顺序 | 文档 | 说明 |
|------|------|------|
| 1 | [`functions.md`](functions.md) | **FR/SC/API 语义 SSOT** |
| 2 | [`runtime-injection.md`](runtime-injection.md) | **拼装顺序**、**denylist §2.3**、**Safety §7.1**、**会话冻结**、**Tool Schema**、**兼容闸**、**分项预算**、**错误 Scope**、**Ownership/IAM** |
| 3 | [`config.md`](config.md) | **IA·对象·字段** |
| 4 | [`flow.md`](flow.md) | **草稿→发布→回滚** · 系统 **`LOCKED`** |
| 5 | [`rules.md`](rules.md) | RBAC · 话术 · **合规边界** |
| 6 | [`prompts/README.md`](../../../prompts/README.md) | **可选**：Git MVP 七目录条文（**非**线上 SSOT）；场景索引 [`trading/README`](../../../prompts/trading/README.md)、[`analysis/README`](../../../prompts/analysis/README.md)；版本约定见根 README |

*维护：产品 + 交易所后台 owner。*
