# 域需求：Observability Management（后台 — 日志与观测运营面）

| 项 | 内容 |
|----|------|
| **产品** | ChainUp AI Agent（Coobit 单所） |
| **文档** | `specs/requirements/domains/admin/observability-management/overview.md` |
| **状态** | **V1 规划已展开**（字段/SC **SSOT** 仍在 [`observability/overview.md`](../../../observability/overview.md)） |
| **PRD 位置** | **[`../management-console-v1-prd.md`](../management-console-v1-prd.md) · §11 模块八** |
| **互引** | [`../../../observability/overview.md`](../../../observability/overview.md)（事件下限）；[`../../../observability/tracing.md`](../../../observability/tracing.md)（**`executionId` / trace**）；[`../../../design/api.md`](../../../../design/api.md)；[`../../../observability/audit-log.md`](../../../observability/audit-log.md)；[`../billing-management/overview.md`](../billing-management/overview.md)；[`../management-console-v1-prd.md`](../management-console-v1-prd.md) **附录 A**；[`../../../contract-closure.md`](../../../contract-closure.md)；[**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · **[§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path) |

---

## 1. 本域职责（摘要）

管理后台中的 **对话 / 工具 / Runtime / 错误 / 审计 / 计费账务事件** 等 **检索、抽样、关联跳转、审计导出**（若与平台日志仓 **分体**，本域为 **SSO 嵌入式查询 + 权限与水印策略** 的 **产品面**）。**结构化事件名与必备字段** **不得低于** [`observability/overview.md`](../../../observability/overview.md)；**Prompt/响应全文默认不落或脱敏** 见 [`rules.md`](rules.md)。

---

## 2. SSOT 分层（禁止双轨）

| 层 | 文档 | 职责 |
|----|------|------|
| **事件与 join 下限** | [`observability/overview.md`](../../../observability/overview.md) **§2～§4** | **事件名**、**必备字段**、**`transitionTrigger`/§2.4 映射**、**`SC-OBS01～08`（§4）** |
| **后台产品面（本域）** | **本文** + [`functions.md`](functions.md)、[`config.md`](config.md)、[`flow.md`](flow.md)、[`rules.md`](rules.md) | **控制台 IA**、检索筛选项、**工单协查 UX**、导出权限、与 **模块一 L01～L03** **入口对位** |
| **实例侧入口** | [`agent-management/functions.md`](../agent-management/functions.md) **FR-AM-L01～L03**（**FR-MC114**） | 从 **模板/实例上下文** **深链** 到 **本域**（**预填** `userId`/`instanceId`/`executionId` **等**） |
| **账务 UI** | [`billing-management/`](../billing-management/) | **平台流水 · 导出**（**FR-MC504/507**）以 **账务域** **为主**；**本域** 侧重 **按 `executionId` 串起** **`billing.*`** 与 **`agent.*`/`trading.*`** |

---

## 3. V1 规划范围

| 主题 | V1 下限 | 互引 |
|------|---------|------|
| **联合协查** | 以 **`executionId`** 为主锚，**一键展开** 工具链、交易所私有调用、**计费** 事件；**主态边** **可** **与** **`transitionTrigger`** **（** **`OpenAPI`** **）** **对读** | **`FR-MC801～802`**、`observability` **§2**、**§2.4** |
| **计费 join** | **`billingTraceId`**、**`capabilitySkuId`**、**`idempotencyKey`** 与 **`billing.entitlement_debit_*` / `billing.skipped`** **可筛可查**；与 **FR-MC503** **同一键集** | [`billing-management/functions.md`](../billing-management/functions.md) **FR-MC503**；`observability` **§2 表** |
| **LLM/工具** | Token 摘要、**无默认全文**；**`invocationState`** 与 **`SC-OBS05`** 可读 | **`FR-MC803～804`** |
| **指标** | 只读嵌入或跳转（**必选其一** 产品定稿） | **`FR-MC805`** |
| **审计导出** | 管理台配置变更 **CSV**（**`admin.audit`** 链） | **`FR-MC806～807`**；[`observability/audit-log.md`](../../../observability/audit-log.md) |
| **显式非目标（V1）** | **不在本域**重做 **Billing 模块五** 财务报表/对账文件（**走** [`billing-management`](../billing-management/overview.md)）；**不**提供删库式「清日志」 | — |

---

## 4. 契约与收口

- **`design/api.md`**：**模块八登记行 +「运营 **`admin/observability/*`**」占位小节（时间线 · 搜索 · 工具/LLM · 审计导出）** **`CC-P0-01`** 同窗填链后 **方可**对外承诺控制台检索能力。
- **`executionId` / `traceId`**：产品主锚与 APM 分工见 [`tracing.md`](../../../observability/tracing.md)、[`config` §4](config.md)；**禁止**控制台 **默认向非 L2+ 暴露 **`traceId`** 检索**。
- **轨 B 协查**：协查 UI **须**链到 **同一** **`billingTraceId`** 语义（[`design/api.md`](../../../../design/api.md) **`internal/billing/entitlements/*`**、**`me/commerce`**、**`contract-closure` §8**）。

---

## 5. 里程碑（与 billing 并联）

| 阶段 | 交付物 |
|------|--------|
| **M1** | **执行视图**：`executionId` **钻取**、`userId`、`scenarioId`（若有）列 **对齐** `observability` **§2.1**；**推荐** **`transitionTrigger`** **或** **等价详情** **（** **`FR-MC801` / `SC-OM-04`** **）** |
| **M2** | **`billingTraceId`** **筛** + **`billing.entitlement_debit_*`** 与 **`trading.exchange_private`** **同窗时间线** · **FR-MC503 E2E** |
| **M3** | **审计导出** **`FR-MC806～807`** + **大批量导出 rate limit**（[`rules.md`](rules.md) §5）**可测** |

---

**文档版本**：0.2.3 · **维护**：产品 + SRE + 后台 · **本版**：**§3 计费 join 轨 B**、**§5 M2 事件名**。**承** 0.2.2。
