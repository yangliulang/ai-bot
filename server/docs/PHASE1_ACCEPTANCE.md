# Phase 1 收口验收清单（本仓 `server/` 可实现范围）

> **用途**：给 **`/pm` / QA / 联调** 做 **小而明确** 的 Phase1 闭环核对；**不等价于**产品全量 FR（路线图 §2 交易写盘、完整 observability YAML 等 **不在本清单验收范围内**）。  
> **实现真源**：[`BACKEND_SPEC.md`](BACKEND_SPEC.md)、[`API_INTEGRATION_GUIDE.md`](API_INTEGRATION_GUIDE.md)、[`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`](API_ADMIN_OBSERVABILITY_EXECUTIONS.md)。  
> **产品路线图**：`product-doc/product/roadmap.md`（Phase 1 HTTP 对照见遗留 `product-doc/development-roadmap.md` §「第一阶段」）。  
> **产品-doc 增量对照**：§**8**（**`AC-09a`～`AC-09r`**）供 **`/be`** 标注 **新增 / 改已实现 / 已满足 / 部分 / N/A**，与 Phase1 §1～§6 **并行**，**不替代** Phase1 收口勾选。

**前缀约定**：**AC** = Acceptance Criterion；勾选表示该项在当前环境 **已验证通过**。

---

## 0. 前置条件（任何验收前先满足）

- [ ] **AC-00a**：生产或联调库已执行 **`alembic upgrade head`**（至少含 **`0002_tatb`** … **`0017_admin_ai_model_api_model`**、**`0018_spot_trade_trading_prompt_seed`**、**`0019_remove_phase1_prompt_identifiers`**（存量库 **`prompt_pack_id` / 平台 `scenario_id` 去 `phase1` 段**）；以仓库当前迁移链为准）。种子包示例：**`pack_platform_system_v1`**、**`pack_trading_chat_faq_v1`**；平台场景 **`agent.runtime.platform_system`** / **`platform_safety`**。
- [ ] **AC-00b**：**`CHAINUP_AGENT_DATABASE_URL`** 指向 **实际联调库**；Admin / Webhook / Deeplink 与共库一致。
- [ ] **AC-00c**：**`uv run pytest`** 全绿（CI 门槛）。

---

## 1. 路线图 §1.1 — 子账户与绑定（不做「自动开立」）

- [ ] **AC-01a**：**`POST /api/v1/agent/api-binding/validate`**（不落库）能对合法 OpenAPI 凭证返回 **200**；缺 **`sub_account_id`** 或探针交叉校验失败返回约定 **`4xx`**（见 **`BACKEND_SPEC` §11**）。
- [ ] **AC-01b**：配置 **`CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY`** 后，**`POST /api/v1/agent/api-binding/confirm`** **200** 落库 **`telegram_agent_trading_binding`**，并 **upsert** **`agent_instance`**（**`instanceId`** 前缀 **`inst_`**）。
- [ ] **AC-01c**：**`POST /api/v1/me/agent/bindings/trading-api`**（camelCase）与 confirm **语义等价**（联调 Deeplink 主路径）。
- [ ] **AC-01d**：**`GET /api/v1/agent/api-binding/status?userId=<tg_id>`** 命中绑定则为 **`BOUND`**，否则 **`NONE`**。
- [ ] **AC-01e**：**`GET /api/v1/agent/subaccount/status?userId=<tg_id>`**：**`subaccountReady`** 与是否存在托管绑定一致；**`agentSubAccountId`** Phase1 **恒 `null`**（与设计一致）。
- [ ] **AC-01f**：**`POST /api/v1/agent/onboarding/initiate`**：无绑定时 **`nextStep=bind_trading_api`**；已绑定时 **`complete`**。
- [ ] **AC-01g**：**`POST /api/v1/agent/subaccount/create`** **恒** **`accepted=false`**、**`DEFERRED_EXCHANGE_CONSOLE`**，错误码 **`AGENT_SUBACCOUNT_CREATE_PHASE1_NOT_AUTOMATED`**（明确 **不提供自动开立**）。

---

## 2. 路线图 §1.2 — Telegram Webhook

- [ ] **AC-02a**：**`POST /webhook/telegram/{botToken}`**：path token 与 **`CHAINUP_AGENT_TELEGRAM_BOT_TOKEN`** **不一致** → **404**；未配置 token → **503** **`TELEGRAM_WEBHOOK_NOT_CONFIGURED`**。
- [ ] **AC-02b**：合法请求：**HTTP 200** 先行；出站 **`sendMessage`** 在 **后台任务**完成（默认）；异常时仍有兜底话术（见 **`BACKEND_SPEC` §3.1**）。
- [ ] **AC-02c**：**未绑定**会话：回复含绑定引导；**`CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL`** 为 **公网 https** 时可带 **InlineKeyboard** URL。
- [ ] **AC-02d**：**已绑定**（DB 或 **`CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST`**）：走门禁 → 意图 → 只读路由 / **`chat.faq`** LLM；**不**在正文附带运行时调试块（**`tg_id`** 等）。
- [ ] **AC-02e**：运维：**`GET|POST|DELETE /api/v1/admin/channels/telegram/webhook`** 可查询/登记/删除 webhook（Bot token 不在响应明文泄漏）。

---

## 3. 路线图 §1.3 — 意图与路由（Phase1 关键字 + 只读执行）

- [ ] **AC-03a**：**`POST /api/v1/agent/intent/recognize`**：**200**，返回 **`scenarioId` / `confidence` / `candidates`**（关键词占位）。
- [ ] **AC-03b**：**`GET /api/v1/agent/scenarios`**：**200**，目录含 **`read.market.ticker`**、**`chat.faq`** 等（**`readiness`**：**`chat.faq`** 等为 **`ready`**（LLM 拼装）；其余 **`stub`** 可为占位）。
- [ ] **AC-03c**：**`POST /api/v1/agent/routing/execute`**：**已绑定**前提下，**`read.market.ticker`**（含 **`symbol`**）与 **`read.account.balance`** 调交易所 **只读**摘要；其它 **`scenarioId`** **200** 占位 **`note`**（**非**真实下单）。

---

## 4. 路线图 §1.4 — 门禁（Phase1 已实现子集）

- [ ] **AC-04a**：**`POST /api/v1/agent/access/evaluate`**：**200** **`EligibilityEnvelope`**（camelCase）；未绑定且无放行名单 → **`allowed=false`**，码 **`AGENT_SUBACCOUNT_REQUIRED`**（或等价阻断）。
- [ ] **AC-04b**：**`CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED=true`** → **`AGENT_GLOBAL_OFF`**。
- [ ] **AC-04c**：**`CHAINUP_AGENT_AGENT_RUNTIME_OPS_SUSPENDED=true`** → **`AGENT_OPS_SUSPENDED`**。
- [ ] **AC-04d**：**`GET /api/v1/agent/access/reasons`**：**200**，常见 **`AGENT_*`** 码可查。
- [ ] **AC-04e（Phase1 明示不包含）**：路线图列举的 **VIP 实时校验 / 计费阻断 / 地区合规** 等 **未声称在本清单验收**——若环境侧仅为占位或后续迭代，验收备注 **N/A** 并由 **`/pm`** 另立条目。

---

## 5. 路线图 §1.5 — 可计费执行骨架（持久化）

- [ ] **AC-05a**：**`POST /api/v1/agent/execution/accept`** → **200**，返回 **`executionId`**；表 **`agent_execution`** 可见 **`ACCEPTED`** 行。
- [ ] **AC-05b**：**`POST /api/v1/agent/execution/finalize`**（**`SUCCESS`/`FAILED`/`CANCELLED`**）→ 行状态 **`SUCCEEDED`/`FAILED`/`CANCELLED`**（与实现映射一致）。
- [ ] **AC-05c**：**`GET /api/v1/agent/execution/{executionId}`**：存在 **200**，不存在 **404**。
- [ ] **AC-05d**：Telegram **已绑定且门禁通过** 的一轮用户文本：触发 **`accept→finalize`** 并 **`commit`**（**`source=telegram_webhook`**）；**门禁拒绝** → **无** execution 行。
- [ ] **AC-05e（Phase1 明示不包含）**：**按量扣费 / `effectiveMinChargeUsdt` 真实入账** **不在本清单验收**——仅要求 **`executionId` 锚点**可用。

---

## 6. Admin · Phase1 控制台（与联调）

- [ ] **AC-06a**：**`POST /api/auth/login`**（env 或 database 模式）可用。**database**：首张账号可走 **`POST /api/auth/register`**（空库、口令≥8）；或 **`chainup-agent-seed-admin`**。
- [ ] **AC-06b**：**AI Settings**：**`GET|PATCH …/admin/ai/*`** 可按 **`BACKEND_SPEC`** 管理 Provider / Model / defaults（删除 Provider **204**、模型冲突 **409** 等契约行为符合文档）。
- [ ] **AC-06c**：**Agent 实例**：**`GET /api/v1/admin/agents/instances*`** **200**，无 Secret 泄漏。
- [ ] **AC-06d**：**绑定运维**：**`GET /api/v1/admin/agent/trading-bindings`** 列表无密钥列（掩码/省略符合 schema）；**`DELETE …/trading-bindings/{bindingId}`** **204** 硬删整行，不存在 **404**。
- [ ] **AC-06e**：**执行记录**：**`GET …/admin/observability/executions*`** 列表/详情与 **`agent_execution`** 一致；**`DELETE …/{executionId}`** **204**，二次删除 **404**（见 **`API_ADMIN_OBSERVABILITY_EXECUTIONS.md`**）。
- [ ] **AC-06f**：生产或预发：**配置** **`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET`**（≥16）后，所有 **`/api/v1/admin/*`** **须**带 **`Authorization: Bearer <login.access_token>`**：无头 **401** **`ADMIN_CONSOLE_AUTH_REQUIRED`**；损坏令牌 **401** **`ADMIN_CONSOLE_ACCESS_TOKEN_INVALID`**。**本地纯联调**可不配 Secret（Admin 路由不强制 Bearer，但 **`access_token`** 亦不可服务端校验）。**`/api/v1/agent/*`**、Webhook、**`/api/v1/me/*`** **不在**本条强制范围内。

---

## 7. Phase1 收口「不包含」（避免验收范围膨胀）

以下 **不要求** 在本清单勾选通过即可宣称 Phase1 全局完结：

- **第二阶段及以后**：真实 **现货/合约写盘**、撤单、条件单等（路线图 §2+）。
- **完整 Observability**：**`…/timeline`**、**`…/tool-calls`**、**`…/llm`**、联合 search（**`openapi/admin/observability.yaml`** 余下路径）——依赖额外埋点与表，**另行立项**。
- **Agent management 写路径**：**`POST/PATCH/DELETE …/instances*`**（OpenAPI I02/I04/I05/I06）**未实现**不阻塞本条 Phase1 **运行时 + 绑定 + 执行锚点**收口。

---

## 8. 产品-doc 规格增量对照（`AC-09a`～`AC-09r`）

**性质**：与 `product-doc` 近期 SSOT（Prompt Library、`runtime-injection`、Telegram/overview、话术对齐等）对齐，供 **`/be`** 逐项标明 **`新增` / `改已实现` / `已满足` / `部分` / `N/A`**（可在 PR / 工单备注）。**OpenAPI / `design/api.md` 登记表** 终裁冲突时以契约为准。

**路径前缀**：下表 **`规格`** 列均为 **单体仓内 `product-doc/` 相对路径**。

### 8.1 对照表（映射 PM 清单 **A1～F2**）

| ID | 原映射 | 验收要点（后端） | 规格（相对 `product-doc/`） | **BE 结论**（`server/` · Phase1） |
|----|--------|------------------|-----------------------------|----------------------------------|
| **AC-09a** | A1 | Runtime 拼装 **语义顺序** 与 **`runtime-injection` §1** 一致（SYSTEM→SAFETY→场景→Few-shot→Context→Tool Spec→User）；SAFETY **不可被后续块撤销** | `specs/requirements/domains/admin/prompt-management/runtime-injection.md` §1 | **部分**：**`agent_prompt_assembly`** — **`chat.faq`**（OpenAI **messages** / Ark **扁平 transcript**）与 **Intent NLU**（前置 SYSTEM/SAFETY + 输出 Schema 块）按 §1 **顺序**；**非**所有 **`scenarioId`** 通用 assembler |
| **AC-09b** | A2 | Tool：**仅** JSON Schema（及描述）SSOT 注入模型上下文，**禁止**手写参数表顶替 Schema | `specs/requirements/domains/admin/prompt-management/runtime-injection.md` §1 | **部分**：**`exchange_tool_schema_registry`** → **`chat.faq`** Tool Spec 块（只读工具 JSON Schema）；Intent NLU **输出形状** **`INTENT_NLU_OUTPUT_JSON_SCHEMA`** — **禁止** prose 参数表作为调用真源 |
| **AC-09c** | A3 | SYSTEM 侧与 **`library/ASSEMBLY.md`** + **`library/scenarios/registry.md`** 的 **C/E/S/IT\|IA\|IM/A** 一致（写路径 **必选类型 A**） | `specs/requirements/prompts/library/ASSEMBLY.md`、`specs/requirements/prompts/library/scenarios/registry.md` | **部分**：平台 **SYSTEM/SAFETY** 种子包语义对齐 **ASSEMBLY** L1/L3 **意图**（非 Git 全文镜像）；**未**搬运 L2/L4/L5 Markdown 片段；寄存器仍以 **`agent_scenario_catalog`** 为准 |
| **AC-09d** | A4 | **`scenarioId` ↔ registry ↔ routing-engine** 可对签（可与 CI 脚本同语义） | `specs/requirements/prompts/library/scenarios/registry.md`、`specs/requirements/domains/agent/agent-orchestration/routing-engine.md` | **改已实现**：**`AGENT_SCENARIO_CATALOG`** / **`registered_scenario_ids()`** 与 **`GET /api/v1/agent/scenarios`**、意图裁决、`publish`（**`PROMPT_SCENARIO_INVALID`**）同源；产品 **`check_registry_*.py`** 属 **`product-doc/`** MR 自检（≠ **`server/` CI**）。 |
| **AC-09e** | A5 | Few-shot **插在「本轮 User 之前」**；Orchestration 裁剪 **不得**破坏 SAFETY 相对 USER 的约束 | `specs/requirements/domains/admin/prompt-management/runtime-injection.md` §1 | **部分**：**`chat.faq`** TRADING 包内 **user/assistant** 示例位于 **Runtime Context / Tool Spec** 之前、**末条 User** 之后插入逻辑之前；**未**实现 Orchestration **动态裁剪** |
| **AC-09f** | B1 | 变量注入 **仅** `variableSchema`（发布校验）+ **平台内置白名单**（OpenAPI/登记） | `specs/requirements/domains/admin/prompt-management/runtime-injection.md` §2.1 | **部分**：**`admin_prompt_pack.variable_schema_json`**；**`PATCH …/prompt-packs/{id}`** 可选 **`variableSchema`**；**非空对象**时 **`{{…}}`** 须为 **schema 键 ∪ Phase1 平台白名单**（**`effective_locale`、`scenario_id`…**）否则 **422** **`PROMPT_VALIDATION_FAILED`**；未配置 **variableSchema**（空/缺省）仍仅 **§2.3.1 denylist**（兼容存量包）。**`GET …/internal/prompts/effective`**、包详情返回 **`variableSchema`** |
| **AC-09g** | B2 | Publish：非法占位符 → **`PROMPT_VALIDATION_FAILED`**（或契约同名码） | `specs/requirements/domains/admin/prompt-management/runtime-injection.md` §2.1 | **改已实现**：**`PATCH`/`publish`** 前 **`{{…}}`** denylist §2.3.1 → **`PROMPT_VALIDATION_FAILED`**；**`variableSchema` 非空**时追加 **未声明占位符** → 同码 |
| **AC-09h** | B3 | Runtime：非法键 → **`PROMPT_INJECTION_FORBIDDEN`** 或剔除且 **可观测**，**禁止静默成功** | `specs/requirements/domains/admin/prompt-management/runtime-injection.md` §2.1 | **部分**：**`agent.runtime.intent_nlu`** system 文本 **`prompt_runtime_substitution`**：**enforce** **`variableSchema`** 下 **`PROMPT_INJECTION_FORBIDDEN`** → **不静默 LLM**：跳过网关、`error` 日志、`keyword_v1` 回退；**skip**（无 schema 对象）→ 未知占位符 **`warning`** 剔除。**HTTP **`intent/recognize`** 本条仍 **200**（非 403） |
| **AC-09i** | B4 | **`ASSEMBLY.md` §2** 占位符与 **`runtime-injection` §2.4** 下限一致（`effective_locale`、`scenario_id`、`prompt_pack_version`、`requires_main_site` 等） | `specs/requirements/prompts/library/ASSEMBLY.md` §2、`specs/requirements/domains/admin/prompt-management/runtime-injection.md` §2 | **部分**：**`intent/recognize`**：**`effectiveLocale`**；execution 观测 **`promptPackVersion`**；**intent NLU**/**assembly** **`{{…}}`** 注入；**chat.faq** 拼装链注入 **`promptPackVersion`** echo；Git **ASSEMBLY** 全文对齐仍为 **gap** |
| **AC-09j** | C1 | 可关联 **`scenarioId` / `promptPackVersion` / `resolvedPromptBinding`**（或等价字段） | `specs/requirements/prompts/library/README.md` §2、`specs/requirements/observability/overview.md` §2.3（互链） | **改已实现**：**`agent_execution`** 持久化 **`prompt_pack_version`**、**`resolved_prompt_binding`**；**Admin `GET …/observability/executions*`**、**`GET …/agent/execution/{id}`** 返回 **`promptPackVersion`/`resolvedPromptBinding`** |
| **AC-09k** | C2 | **`promptPackVersion`** 日志/DB/API **与实跑包版本**一致 | `specs/requirements/domains/admin/prompt-management/runtime-injection.md` §1（读路径对签） | **改已实现**：执行行与 **effective** 读路径同源（无包则 **`null`**）；Telegram **`ROUTE_CHAT_FAQ`** 当轮 Timeline 追加 **`prompt.snapshot`**（**`intent_nlu`**）与 **`llm.chat.faq`**（含 **`promptPackVersion`** / 网关 **`gatewayModelId`**） |
| **AC-09l** | D1 | **Telegram 内闭环**；**`requires_main_site`** **仅**窄口子且与 **`exchange-agent/boundaries`** 一致 | `specs/requirements/prompts/library/README.md`、`specs/requirements/prompts/shared/response-format.md` | **部分**：**`POST …/access/evaluate`** 可选 **`requiresMainSite`**：**`true`** ⇔ **`AGENT_SUBACCOUNT_REQUIRED`**（须走 H5/绑定）；**`false`** ⇔ **`allowed`** 且（**Phase1 放行名单**会话 **或** **DB **`bindingVerified=true`**）；其它阻断常为 **`null`/`undefined`。与产品 **boundaries** 全车对签仍为 **gap** |
| **AC-09m** | D2 | **`effective_locale` 三桶**（`zh-Hans`/`zh-Hant`/`en`）与 **`telegram/overview` §2.4**、占位符一致 | `specs/requirements/domains/agent/telegram/overview.md`、`prompts/library/ASSEMBLY.md` §2 | **改已实现**：**`POST …/intent/recognize`** 响应 **`effectiveLocale`**（由 **`locale`** 映射；未知语种回退 **`en`**） |
| **AC-09n** | D3 | **类型 A / 提交后话术** 与 **`order-confirmation`**、**`response-format`**、**`telegram-and-cards`** **同窗** | `specs/requirements/prompts/confirmation/order-confirmation.md`、`prompts/shared/response-format.md`、`product/telegram-and-cards.md` | **改已实现**：现货 **闪兑/限价** Telegram **Type-A**（**`callback_data`**、`agent_telegram_pending_confirm`、Timeline **`transitionTrigger`**）与 **`BACKEND_SPEC`** §3.1 / 修订 **2026-05-14** 一致；**其余 `scenarioId`** 未同窗条文。 |
| **AC-09o** | E1 | **开通欢迎语**：触发、多语言 **configKey**、回退链、**幂等（每 userId 一次）** | `specs/requirements/domains/agent/telegram/overview.md` §2.1.1 | **N/A**：无 §2.1.1 专用欢迎语落库/幂等键；与 **AC-02** 通用绑定引导并存 **gap**。 |
| **AC-09p** | E2 | **卡片模板** **不属于** **`ASSEMBLY`/拼装链**（与 **`runtime-injection`** 一致） | `specs/requirements/domains/admin/prompt-management/runtime-injection.md` §1、`specs/requirements/domains/agent/telegram/overview.md` | **已满足**：InlineKeyboard / Type-A 与 LLM **`messages`** 拼装分离（**`chat.faq`** 出站不含 SYSTEM 拼装卡片正文）。 |
| **AC-09q** | F1 | CI/MR：**`check_registry_vs_routing_engine.py`** **或等价对签** | `specs/requirements/prompts/library/scripts/check_registry_vs_routing_engine.py` | **部分**：**`server/tests/test_product_doc_registry_check.py`** 对本仓 **`product-doc/.../check_registry_vs_routing_engine.py`** 做 **`subprocess`** 回归（脚本缺失则 **skip**）；与 MR 独立跑脚本 **同语义** |
| **AC-09r** | F2 | Runtime **仅已发布** Prompt 包；Git library → 管理台发布 → 版本可追溯 | `specs/requirements/prompts/library/README.md` §2 | **改已实现**：**`get_published_pack_for_scenario`** / **`GET …/internal/prompts/effective`** 仅 **`lifecycle=PUBLISHED`**；**`publish`** 递增 **`promptPackVersion`**；Git library → 控制台 **全自动语义对齐**仍 **N/A**（依赖运营发布与寄存器手工对齐）。 |

### 8.2 BE 勾选（可选：打印贴 PR）

对 **`AC-09a`～`AC-09r`** 逐项勾选左侧表示 **已完成对照**（§**8.1** 末列已填 **BE 结论**）。结论取值：**`新增` / `改已实现` / `已满足` / `部分` / `N/A`** —— 本轮 **`/be`** 标注如下。

- [x] **AC-09a**：拼装语义顺序（映射 **A1**）。→ **部分**（**chat.faq** / Intent NLU §1 顺序块）
- [x] **AC-09b**：Tool Spec 仅 Schema（**A2**）。→ **部分**（JSON Schema SSOT Tool Spec / NLU 输出 Schema）
- [x] **AC-09c**：ASSEMBLY + registry 片段链（**A3**）。→ **部分**（platform SYSTEM/SAFETY 语义；未镜像 Git L2/L4/L5）
- [x] **AC-09d**：registry ↔ routing-engine（**A4**）。→ **改已实现**
- [x] **AC-09e**：Few-shot 位置与 SAFETY（**A5**）。→ **部分**（**chat.faq** 示例对白位置；无动态裁剪）
- [x] **AC-09f**：变量注入白名单（**B1**）。→ **部分**（**`variableSchema`** + runtime **`{{…}}`**；非全部场景拼装）
- [x] **AC-09g**：Publish **`PROMPT_VALIDATION_FAILED`**（**B2**）。→ **改已实现**（denylist §2.3.1）
- [x] **AC-09h**：Runtime **`PROMPT_INJECTION_FORBIDDEN`** 或可观测剔除（**B3**）。→ **部分**（**intent NLU** enforce：**错误码 + 日志**，HTTP 仍为 **200**/keyword）
- [x] **AC-09i**：占位符下限一致（**B4**）。→ **部分**（见 §8.1）
- [x] **AC-09j**：观测字段 scenarioId / promptPackVersion / resolvedPromptBinding（**C1**）。→ **改已实现**
- [x] **AC-09k**：promptPackVersion 与实跑一致（**C2**）。→ **改已实现**
- [x] **AC-09l**：Telegram 优先 + **`requires_main_site`** 窄口子（**D1**）。→ **部分**（**`evaluate`** **`requiresMainSite`**；产品与 **boundaries** 全文仍有 gap）
- [x] **AC-09m**：**`effective_locale`** 三桶（**D2**）。→ **改已实现**（**`effectiveLocale`**）
- [x] **AC-09n**：类型 A / 话术同窗（**D3**）。→ **改已实现**（闪兑/限价 Type-A；其余 scenario 未对齐条文）
- [x] **AC-09o**：开通欢迎语 §2.1.1（**E1**）。→ **N/A**
- [x] **AC-09p**：卡片不在拼装链（**E2**）。→ **已满足**
- [x] **AC-09q**：registry 脚本或等价 CI（**F1**）。→ **部分**（**`server/tests/test_product_doc_registry_check.py`**；依赖 `product-doc` 脚本是否存在）
- [x] **AC-09r**：仅已发布包 + 版本追溯（**F2**）。→ **改已实现**（DB 发布链；Git→控制台全自动对齐仍缺）

**本轮无一项标为「新增」**：§**8** 条文相对既有 **`server/` Phase1** 多为扩充对照或缺口声明。**（2026-05-19：§8 AC-09a～e 等与 **`agent_prompt_assembly_phase1`** / **`0013`** 对齐；§8.1/§8.2 已更新）**

### 8.3 不计入后端「功能缺口」核对（避免误判）

| 原映射 | 说明 |
|--------|------|
| **G1** | **`product-doc/src/admin` Tool Registry Demo** — 仅原型与 `specs/requirements/admin-console/*` 路由叙事；**非** `server/` Phase1 必选。 |
| **G2** | **Telegram overview 版号/Markdown 清理** — 以 **AC-09m / AC-09o / AC-09p** 行为对照为准。 |

---

## 9. 修订记录

| 日期 | 说明 |
|------|------|
| 2026-05-20 | **§2.1/§2.2 Telegram**：现货 **当前委托 / 撤单** 绑定用户直查/直撤；**限价 Type-A** **`lcp`/`lcx`** pytest 回归（含复用 **`executionId`** 不重复 quote）。**§8**：**`0018`** TRADING 种子 **`trade.spot.flash_convert`** / **`trade.spot.limit_order`** 入 **`PHASE1_TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`** |
| 2026-05-21 | **§0（AC-00a）**：**`0016_read_account_balance_wealth_trading_prompt_seed`** · TRADING **`read.account.balance`** / **`wealth.holdings_read`** + **`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_ACCOUNT_BALANCE`** / **`…WEALTH_HOLDINGS_READ`** · 时间线 **`llm.read.account.balance`** / **`llm.wealth.holdings_read`** |
| 2026-05-18 | **§8（AC-09a 续）**：**`0014`**（**`read.market.ticker`** TRADING + **`NARRATE_TICKER`**）；**`0015`**（**`read.market.depth`** / **`read.market.trades`** TRADING + **`NARRATE_DEPTH`/`TRADES`**）；**`PHASE1_TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`**；时间线 **`llm.read.market.*`** · **`AC-00a`** |
| 2026-05-19 | **§8（AC-09a 收口半步）**：**`assemble_phase1_trading_llm_payload`** + **`PHASE1_TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS`**（当前仅 **`chat.faq`**）；**`invoke_llm_chat_for_telegram(scenario_id=)`**；**`chat.faq`** **`GET /scenarios`** **`readiness`**=`ready` · **`AC-03b`** 勾选措辞更新 |
| 2026-05-19 | **§8 AC-09a～e（部分）**：Prompt Assembly 链 · **`0013_phase1_prompt_assembly_seed`** · **`agent_prompt_assembly_phase1`** / **`phase1_exchange_tool_schema_registry`** |
| 2026-05-18 | **§8（续）**：**AC-09h** Intent NLU **runtime** **`{{…}}`**；**AC-09i** 占位符注入（NLU）；**AC-09l** **`access/evaluate`** **`requiresMainSite`** · 见 **`BACKEND_SPEC`** §**3** |
| 2026-05-19 | **§8 AC-09f（部分）**：**`variableSchema`** 落库（**`0012_prompt_pack_variable_schema`**）；**`PATCH`/`publish`** 占位符 ∪ 平台白名单校验；**`GET …/internal/prompts/effective`** / 包详情含 **`variableSchema`** |
| 2026-05-18 | **§8.1～§8.2**：逐项填入 **`/be`** **BE 结论**（**改已实现**：**AC-09d**、**AC-09n**（部分）、**AC-09r**（DB 发布链）；**已满足**：**AC-09p**；余 **N/A**）；**§8.2** 勾选列为已对照 |
| 2026-05-18 | **§8**：新增 **`AC-09a`～`AC-09r`** 产品-doc 增量对照表 + BE 勾选清单；原「修订记录」顺延为 **§9** |
| 2026-05-13 | **AC-06f**：**`ADMIN_CONSOLE_JWT_SECRET`** 非空时 **`/api/v1/admin/*`** Bearer 强制（JWT）；Secret 空则沿用旧联调 |
| 2026-05-13 | 初版：Phase1 可勾选验收 + 明确不包含项 |
