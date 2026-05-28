# Observability Management · 功能索引

**模块八 PRD**：[`../management-console-v1-prd.md`](../management-console-v1-prd.md) **§11**；**观测域（事件 SSOT）**：[`../../observability/overview.md`](../../../observability/overview.md)；**HTTP 占位**：[`../../../design/api.md`](../../../../design/api.md) **「运营侧 Logs & Observability API（`admin/observability/*`）」**。**计费协查对齐**：[`../billing-management/functions.md`](../billing-management/functions.md) **FR-MC503**。**实例日志入口**：[`../agent-management/functions.md`](../agent-management/functions.md) **FR-AM-L01～L03** · **FR-MC114**。

---

## 1. FR-MC801～807（控制台能力 · V1）

| FR | 对象 | Then（下限） | 观测/账务互引 |
|----|------|--------------|----------------|
| **FR-MC801** | 运营支持 | **按 `executionId` 检索**：**时间线视图**聚合 **`agent.execution.step`**、**`agent.skill.spec_read`**（写路径）、`agent.tool.call`、`trading.exchange_private`、**`billing.entitlement_debit_*`**（**可计费执行**）**等同执行事件**（**字段集** **`observability` §2.1～2.2**）；**须** **兼容** **[`observability-schemas`](../../../../openapi/components/observability-schemas.yaml) · `ObservabilityTimelineEvent`** **之** **`transitionTrigger`（可选）** **及** **`summary`** **键** — **语义** **不得低于** **[`observability/overview.md`](../../../observability/overview.md) **§2.4**（**主态边** **与** **[`execution-transition-matrix.md`](../../../Runtime/execution-transition-matrix.md) **§2.2.1** **对读**）；**UI** **须** **以** **列** **或** **事件详情区** **之一** **可读** **展示** **（** **若** **响应** **携带** **该字段** **）**，**禁止** **静默吞** **`transitionTrigger`** · **执行记录主列表** **OpenAPI** **`listObservabilityExecutions`** / **`ObservabilityExecutionSummary`** **同窗** **`admin/observability.yaml`**（**不** **替代** **时间线** **PATH**） | `SC-OBS01～03`、`SC-OBS05`、**`SC-OBS08`**、**`SC-OBS11`**、**`§2.4`** |
| **FR-MC802** | 运营支持 | **`userId` + 时间窗** 检索；**支持与 L01～L03 深链**：从 **实例上下文** **预填** 筛选项 | **FR-MC114**、`agent-management` **§4** |
| **FR-MC803** | L2+（见 rules） | **工具日志**：**`toolId`**、**`toolCallSeq`**、**`invocationState`**、**`methodPathSummary`**（若有）；**禁止**默认列 **完整 Prompt/外链凭证** | **§2.1、`SC-OBS05`** |
| **FR-MC804** | L2+ | **LLM 日志**：**`modelId`**、**`inputTokens`/`outputTokens`** **摘要**；**无 body 默认列** | **`observability` §2.3（计量 join）** |
| **FR-MC805** | Ops / 运营只读 | **指标**：SLI 看板 **只读嵌入** **或** **外链 SSO**（**二选一须在 IA 冻结**） | **`observability/metrics.md` §2、[`runtime-monitor.md`](../../../observability/runtime-monitor.md)** · infra **详情 **不写 **`overview` §2** |
| **FR-MC806** | 审计/Audit | **管理台变更** **异步导出**：时间窗、`actor`、`resource`、`action`（**`admin.audit` 字段**与同域 [`audit-log.md`](../../../observability/audit-log.md) **同窗**） | `config.md` **§15.4** |
| **FR-MC807** | 审计 | **导出水印 / 文件名策略 / 短时 URL** — **同窗** [`billing-management/rules.md`](../billing-management/rules.md) **§5（导出）** | 同上 |

---

## 2. 计费协查字段（控制台 **须**支持与 **FR-MC503** **同一键跳转**）

以下为 **控制台筛选项与时间线列之下限**（**语义 SSOT**：[`observability/overview.md`](../../../observability/overview.md) **§2 计费表**；**账务 HTTP**：[`design/api.md`](../../../../design/api.md) **`internal/billing/entitlements/*`、运营 `FR-MC503`**）。

| 键 | 用途 |
|----|------|
| **`executionId`** | 串联 **运行时 + 计费** **主锚** |
| **`billingTraceId`** | **`billing.entitlement_debit_*`**（**主链**）**↔** **账务流水** **`traceKey`** 口径（[`billing-management/overview.md`](../billing-management/overview.md) **FR-B06**） |
| **`capabilitySkuId`** | **核销归因** · **与** **`BILLING_CAPABILITY_MAP`** **同窗** |
| **`idempotencyKey`** | 与 **`billing` FR-T01/FR-B05** **同窗**（**建议** **`:rail-b:entitlement-debit`**） |
| **`userId`** | **平台侧** **`FR-MC503`** **协查三联** **`userId` + `executionId` + `billingTraceId`** **之一可查因** |
| **`commercialSettlementType`** | **默认** **`ENTITLEMENT_DEBIT`**；**轨 A `CHARGE`** **仅** **历史对读** |

**执行详情 · 计费镜像（下限）**：**须** **展示** **`billingTraceId`**、**核销状态**（**SUCCESS/INSUFFICIENT/FAILED/skipped**）、**`capabilitySkuId`**；**Token/USDT 金额** **若展示** **须** **标为 Metering** **非** **结算主列**。

**退款（轨 A 对读）**：时间线 **若存在** **`billing.charge_*`** **与** **`REFUND`** **须** **可 join**（**`originalBillingTraceId`**）；**Agent S5 主链** **无** **默认退款 UI**。

---

## 3. SC-OM · 验收（后台产品面 · 占位）

| ID | Then |
|----|------|
| **SC-OM-01** | 给定 **`executionId`**（**可计费**）：**可见** **`billingTraceId`**、**`capabilitySkuId`**、**核销状态**（**`billing.entitlement_debit_*`** **或** **同窗 API**）**并可** **跳到** **`billing`/`commerce` 协查（FR-MC503）或同窗 URL** |
| **SC-OM-02** | **不含**计费/核销事件的执行：**不出现**伪造 **`entitlement_debit_success`/`charge_success`** UI；**`billing.skipped`** **原因**可读（**`observability` §2**） |
| **SC-OM-03** | **大批量导出**：触发 **429/排队** UI（[`rules.md`](rules.md) **§5**） |
| **SC-OM-04** | **`FR-MC801` 时间线**：当 **`OpenAPI` 响应** **含** **`transitionTrigger`** **或** **`summary`** **键** **已满足** **`observability` §2.4** **某 Trigger 行** **下限时**，**控制台** **须** **可读** **展示** **（** **列** **或** **抽屉/展开** **）**；**抽检** **同窗** **`SC-OBS08`**（**不** **替代** **后端** **须** **先** **落字段**） |
| **SC-OM-05** | **Production Runtime · 读规范**：写路径演示 **`executionId`**（**如** **`exec-aa11`**）**时间线** **须** **含** **`eventName=agent.skill.spec_read`** **行**（**标签/摘要** **可读**）；**总览** **须** **展示** **`skillId` / `skillSpecVersion` / `phase` / `specDigest`（若有）** — **同窗** [`skill-specs/production-runtime` §4](../../../skill-specs/production-runtime.md)、**`SC-OBS11`** |

**扩展**：全局 **SC-MCV1** 「计费可 join」— [`management-console-v1-prd.md`](../management-console-v1-prd.md) **§13**。

---

**文档版本**：0.2.5 · **维护**：产品 + 后端 + SRE · **本版**：**§2 轨 B 协查字段**、**SC-OM-01/02 核销语义**。**承** **0.2.4**。
