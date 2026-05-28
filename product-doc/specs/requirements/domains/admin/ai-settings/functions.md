# AI Settings · 功能需求与验收

**模块四 PRD**：[`../management-console-v1-prd.md`](../management-console-v1-prd.md) **§7**。**HTTP 占位**：[`design/api.md`](../../../../design/api.md) **「运营侧 AI Settings API」**、登记表 **模块四**。

---

## 1. 功能需求（FR-MC401～408）

| FR | **When** | **Then** | 邻域 |
|----|----------|----------|------|
| **FR-MC401** | 运营在 **Provider** 页登记或更新连接 | **须**持久化 `providerId`、`baseUrl`、`secretRef`（KMS/Secrets **仅引用**）、`healthStatus`、启用/禁用；**响应体与列表项不得**含 Secret 明文；**须**可 **手动触发** Health（见 **FR-MC407**） | [`integrations/llm/provider-routing.md`](../../../integrations/llm/provider-routing.md)；[`rules.md`](rules.md) §1 |
| **FR-MC402** | 运营维护 **模型目录** 或 **默认路由** | **须**可配置 `modelId`、所属 `providerId`、能力标签、上下文窗（只读镜像或所内可配）、**deprecated** 语义；**模板** [`agent-management/config`](../agent-management/config.md) **`defaultModelRef` 仅允许**引用 **已启用** 模型 | [`prompt-management`](../prompt-management/overview.md)；**观测** **FR-MC804** |
| **FR-MC403** | 运营调整 **Temperature** 策略 | **须**可设 **默认**与 **min/max 硬边界**（网关拒参或裁剪策略 **`design` 冻结**） | — |
| **FR-MC404** | 运营调整 **Max output tokens** | **须**可设 **默认**与 **硬顶**（防滥用）；与 Provider 实际窗 **`design` 可对签** | — |
| **FR-MC405** | 运营调整 **Timeout** | **须**可设 **首字/整次** 或 **统一 ms**（所内二选一 **OpenAPI 冻结**） | [`Runtime/recovery.md`](../../../Runtime/recovery.md) |
| **FR-MC406** | 运营调整 **Rate limit** | **须**可设 **RPM / 并发** 等运营级默认（与 **per-user** 若有 **`design` 分校**） | — |
| **FR-MC407** | 运营配置 **Health** 或 **触发探针** | **须**可设 **探测周期、连续失败阈值**；**须**有 **手动探针** + 结果写回 `healthStatus`；**连续失败** **可**驱动 [`Runtime/recovery`](../../../Runtime/recovery.md) **叙事中的降级**（实现落 **网关 + Runtime**） | **FR-MC401**；**观测** 可挂 **告警**（产品定 **SLO**） |
| **FR-MC408** | 运营在 **网关默认 profile** 中维护 **编排执行预算** | **须**可配置 **`maxToolCallsPerExecution`、`maxOrchestrationStepsPerExecution`**（**整数** **≥ 1**）；**可选** **`maxModelTurnsPerExecution`**（**`null`** **表示** **不设** **回合顶**）；**与** [`execution-lifecycle.md`](../../../domains/agent/agent-orchestration/execution-lifecycle.md) **§4 `FR-AO06`**、[`design/api.md`](../../../../design/api.md) **编排执行预算** **同窗**；**Runtime** **须**读 **effective** **配置** **并** **enforce** | [`runtime-contract.md`](../tool-management/runtime-contract.md) **§3.1**（计数） |

**注**：**FR-MC403～407** 在 **产品面** 可 **合并为单一「网关默认 profile」** 资源；**拆解列** 用于验收对签，**OpenAPI** 终裁 **不得弱化** 上表 **Then** 下限。**FR-MC408** **对象** **嵌于** **该 profile**（**见 `ai-settings-schemas` · `OrchestrationExecutionBudget`**）。

### 1.1 控制台 Demo 对齐（`src/admin` · `AiSettingsPage`）

以下 **便于评审与走查**，**不替代** 上表 FR/SC 与 OpenAPI；细节以 [`overview.md`](overview.md) **§1.1** 为准。

- **厂商与模型**：**FR-MC401 / FR-MC402** 的 **台账形态** — Provider 下属嵌套模型；**新建** 厂商时 **`providerId` 仅服务端生成**，表单侧不落字段。
- **模型接入**：新增目录项 **须** 来自 **接入底座对应的允许清单**（与 **`catalogKind`** 同窗），**禁止**运营任意字符串充当 **`modelId`**（降低配置漂移）；**全局 **`modelId`** 唯一**。
- **使用策略**：默认 / 分场景 / 降级等 **`modelId` 下拉** **须仅列出** **台账生效子集**（**启用厂商** + **模型启用且未弃用**）；台账变更导致选项失效时 **须校正策略表单**，避免出现无效引用。

---

## 2. 验收主题（SC-AI · 占位）

| SC | 主题 |
|----|------|
| **SC-AI-01** | **任意** Provider/Model **读 API** **不**返回完整 API Key / Secret |
| **SC-AI-02** | **`defaultModelRef`** 解析失败或 **引用已禁用模型** → **模板保存** **须** **400** 类可解释错误（与 **I02** **同窗策略**由 [`agent-management`](../agent-management/functions.md) **终裁**） |
| **SC-AI-03** | **写路径**（Provider/Model/profile）**须** **审计**（`admin.audit` 键集与 **模块八** **同窗精神**） |
| **SC-AI-04** | **`modelId`** 在同一 **`executionId`** 内与 [`observability` §2.3](../../../observability/overview.md) 及 **FR-MC804** 一致（降级后模型变更须事件链可辨） |
| **SC-AI-05** | **`orchestrationExecutionBudget`**：**读 defaults** **须** **与** **OpenAPI `OrchestrationExecutionBudget`** **同窗**；**调低** **至** **小于** **当前** **P99 单执行** **工具/步数** **须** **走** **变更评审**（**容量** **同窗**） |

## 3. 簇索引（快速）

| 簇 | FR |
|----|-----|
| Provider + Health 入口 | **401**、**407** |
| Model 目录 + 默认 | **402** |
| 推理默认（温 / tokens / 超时 / 限流） | **403～406** |
| 编排执行预算（**`FR-AO06`**） | **408** |
