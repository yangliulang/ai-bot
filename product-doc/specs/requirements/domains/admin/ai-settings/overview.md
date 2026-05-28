# 域需求：AI Settings（后台 — Provider / Model / 网关参数）

| 项 | 内容 |
|----|------|
| **产品** | ChainUp AI Agent（Coobit 单所） |
| **文档** | `specs/requirements/domains/admin/ai-settings/overview.md` |
| **状态** | **V1 规划已展开**（OpenAPI 占位见 [`design/api.md`](../../../../design/api.md) **`admin/ai/*`** 与登记表 **模块四** 行 · **`CC-P0-01`**） |
| **PRD 位置** | **[`../management-console-v1-prd.md`](../management-console-v1-prd.md) · §7 模块四**（**FR-MC401～407**；**编排执行预算** **见 **`FR-MC408`** **与** [`functions.md`](functions.md)） |
| **互引** | [`integrations/llm/provider-routing.md`](../../../integrations/llm/provider-routing.md)；[`Runtime/recovery.md`](../../../Runtime/recovery.md)；[`design/api.md`](../../../../design/api.md)（**含** **编排执行预算** **专节**）；[`agent-orchestration/execution-lifecycle.md`](../../agent/agent-orchestration/execution-lifecycle.md) **§4**（**`FR-AO06`**）；[`agent-management/config.md`](../agent-management/config.md)（模板 `defaultModelRef`）；[`prompt-management/overview.md`](../prompt-management/overview.md)（拼装与 `modelId` 选用边界）；[`observability/overview.md`](../../../observability/overview.md) §2 / [`observability-management/functions.md`](../observability-management/functions.md) **FR-MC804**（`modelId` 同窗）；[`billing-management/overview.md`](../billing-management/overview.md)（计费 ≠ 本域改价）；[`contract-closure.md`](../../../contract-closure.md) **`CC-P0-01`**；[**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · **[§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path)；[`observability/audit-log.md`](../../../observability/audit-log.md)（`admin.audit`） |

---

## 1. 本域职责（摘要）

运营侧维护 **对外 LLM Provider 连接与模型目录**、**网关默认推理与安全边界**。**密钥仅通过 KMS / Secrets 引用**，控制台 **不写死** `baseUrl`+明文 Key。**Prompt Pack**（[`prompt-management`](../prompt-management/overview.md)）只消费 **允许的** `providerId` / `modelId` **集合**；不写 Provider 密钥进 Few-shot。**禁止**控制台长期展示或持久化完整 API Key。**审计**与 **模块八** / `admin.audit` 精神对齐。

### 1.1 Demo（`src/admin`）与域真源

[`/ai-settings`](../../../admin-console/demo-routing.md) 在 **后台 Demo** 中以 **两 Tab** 呈现（页眉仍统称 **模型配置**），**仅前端内存演示**，**非**生产 KMS/网关：

| Tab（界面文案） | 职责（Demo） |
|-----------------|---------------|
| **厂商与模型** | **厂商表可展开**：下属 **`modelId` 目录**与厂商 **一体化**维护（不再单独维护「全局模型表」）。**新建厂商**：表单 **「厂商」** 合并 **接入底座（catalogKind）** 与 **展示名**——选择 OpenAI / Anthropic / DeepSeek 时使用底座预设展示名；选 **暂无预置目录（自定义底座）** 时再录入自定义名称。**`providerId` 不落表单**：由展示名推导生成并保持唯一。**新建厂商须填 Base URL 与密钥引用**（控件标签「密钥」，不回显明文）。**添加模型**：**禁止手输 `modelId`**，仅从当前厂商接入底座对应的 **预置模型清单**中选择；**`modelId` 全局唯一**（已被任一厂商接入则不可再选）。 |
| **使用策略** | **Runtime 模型策略**（默认模型、分场景模型、Token/超时、降级模型、RPM 等）。**模型类下拉选项** **须来自** 上一 Tab 台账：**仅**「**启用**的厂商」下、「**启用**且 **未弃用**」的目录模型；选项展示建议区分厂商（如「模型展示名（厂商展示名）」）。台账 **增删改导致某策略字段所选 `modelId` 失效** 时，Demo **自动修正或清空**该字段，避免出现无效选中。 |

**Provider 台账、完整 `secretRef` 链路、网关参数与编排执行预算全量** 仍以 **本文 + [`functions.md`](functions.md) + [`design/api.md`](../../../../design/api.md) · `admin/ai/*`** 为契约 SSOT，与 [`admin-console/page-specs.md`](../../../admin-console/page-specs.md) **拆面**（Runtime 策略 vs Infra）一致。

---

## 2. SSOT 分层

| 层 | 文档 / 契约 | 职责 |
|----|-------------|------|
| **产品与 IA** | 本文 + [`functions.md`](functions.md)、[`config.md`](config.md)、[`flow.md`](flow.md)、[`rules.md`](rules.md) | **FR-MC401～408**、**SC-AI\*** |
| **对外 HTTP** | [`design/api.md`](../../../../design/api.md) **`admin/ai/*`** | 控制台 CRUD-lite、默认 profile、Health 触发 · **`CC-P0-01`** |
| **运行时路由 / 降级** | [`Runtime/recovery.md`](../../../Runtime/recovery.md)、[`integrations/llm/provider-routing.md`](../../../integrations/llm/provider-routing.md) | 网关从 **本域或配置服务快照** 读 **effective** 路由，**不经**浏览器直连私网 |
| **Token 计费** | [`billing-management`](../billing-management/overview.md) | 费率与扣费主体 · **FR-B02 / FR-MC502**；**禁止**在本域绕过或改价 |

---

## 3. V1 规划范围

| # | 主题 | 下限 |
|---|------|------|
| 1 | **Provider 台账**（**FR-MC401**） | `providerId`、`baseUrl`、`secretRef`、`healthStatus`、禁用位；**列表/详情无 Secret 明文** |
| 2 | **模型目录**（**FR-MC402**） | `modelId`、能力标签、上下文窗（只读或可配）、下架/弃用语义；**默认模型**与模板 `defaultModelRef` **同窗允许集** |
| 3 | **网关默认推理参数**（**FR-MC403～407**）与 **编排执行预算**（**FR-MC408** / **`FR-AO06`**） | Temperature 上下限与默认；Max output tokens 默认与硬顶；请求/流式 Timeout；RPM/并发类限流；Health 探测策略（周期、阈值、手动探针）；**`maxToolCallsPerExecution` / `maxOrchestrationStepsPerExecution` / 可选 `maxModelTurnsPerExecution`** — **OpenAPI** **`AiGatewayDefaults.orchestrationExecutionBudget`** |
| **非目标 · V1** | — | **不在本域**实现计费改价、Prompt Few-shot CRUD、Tool 矩阵 |

---

## 4. 契约与收口

- **登记表**：**「运营后台 · AI Settings（模块四）」** 行填 spec 后，须与本文及 [`functions.md`](functions.md) **对签**；**`CC-P0-01`**。
- **`modelId` / `providerId`**：须与 [`observability/overview.md`](../../../observability/overview.md) §2 及 **FR-MC804** **可追溯**。
- **`defaultModelRef` / 模板**：[`agent-management/config`](../agent-management/config.md) 仅允许引用 **本域 + design 冻结** 之模型集。

---

## 5. 里程碑

| 阶段 | 交付物 |
|------|--------|
| **M1** | Provider + Model **只读**列表 + `secretRef` 录入（无双明文落库） |
| **M2** | 默认参数 **profile** + `admin/ai/*` OpenAPI 初稿；**乐观锁** / `admin.audit` |
| **M3** | Health 探针与 [`Runtime/recovery`](../../../Runtime/recovery.md) **同窗**熔断/降级 **可演练** |

---

**文档版本**：0.2.1 · **维护**：平台 + Agent 网关 · **本版**：§1.1 与 `/ai-settings` Demo（厂商表单合并、策略下拉绑定台账）对齐。
