# Observability · 审计日志（Admin Audit）

**路径**：`specs/requirements/observability/audit-log.md`。

**职责**：**管理台「谁在何时改了什么」** 的 **审计轨迹下限** — **与** **[`overview.md`](./overview.md) §2** **运行时结构化事件**（`billing.*`、`agent.*`、`trading.*`）**分层**：审计事件 **侧重** **`actor`、不可抵赖、导出合规**；运行时事件 **侧重** **`executionId` 串联与用户会话还原**。**互补**：同一 MR **可** **二次索引** **`executionId`/`instanceId`** **便于协查**，但 **不得** **用运行时日志替代** **法定审计字段缺失**。

---

## 1. 事件载体与命名

| 载体 | 说明 |
|------|------|
| **`admin.audit`** | **[`overview.md`](./overview.md) §2** 表中 **管理台写配置** 一行；**语义同窗** **[`domains/admin/management-console-v1-prd.md`](../domains/admin/management-console-v1-prd.md)** **附录 / 模块叙事** 中对 **`admin.audit`** **的引用**。 |
| **`admin.prompt.publish_blocked`** | Prompt **Publish** **被 Safety/占位符闸拦截** — **可与** **`admin.audit` 合并 schema** **（须** **子类型/`reasonCode` 可区分** **— OpenAPI 冻结）**。 |

**控制台导出**：**异步任务 + 水印 + 短时 URL** — **[`domains/admin/observability-management/functions.md`](../domains/admin/observability-management/functions.md) `FR-MC806～807`**，**同窗** [`billing-management/rules.md`](../domains/admin/billing-management/rules.md) **§5（导出）**。

---

## 2. 必备字段（下限）

下列字段 **须** **在所内 OpenAPI / `design`** **冻结**（**禁止** **仅存「一行文案」** **而无法检索**）：

| 字段 | 说明 |
|------|------|
| **`actor`** | **主体**：运营 SSO **`subject`** **或** **服务账号 id**（**禁止** **匿名写**）。 |
| **`actionType`** | **稳定枚举**：与 **`agent-management/rules.md`** **§1** **动作类型表** **同窗扩展**（例：`TEMPLATE_PUBLISHED`、`INSTANCE_OVERRIDES_UPDATED`、`RUNTIME_PAUSE`）。 |
| **`targetType` / `targetId`** | **对象**：如 **`promptPackId`**、**`templateId`**、**`instanceId`**、**`configKey`**。 |
| **`timestamp`** | **UTC** **或可排序绝对时间** **+** **所内单调 tie-break**（若有）。 |
| **`beforeRef` / `afterRef`**（**或** **`diffSnapshotId`**） | **变更前后**：**全文快照 ref** **或** **受控 diff id** — **禁止** **默认落 Secret / Prompt 明文**；与 **`prompt-management` SC-PM-09** **同窗**。 |
| **`reasonCode`**（**可选** **必填矩阵由 IAM 冻结**） | **高风险写** **须** **具备** **书面原因码**（例：**批次停机 `RUNTIME_BATCH_*`**）。 |
| **`requestId`**（**可选** **强烈建议**） | **与** **`coobitRequestId`/网关 trace** **同窗**，便于 **跨系统 ticket**。 |

**Agent 管理扩展条目**（**须覆盖** **≥** **[`agent-management/rules.md`](../domains/admin/agent-management/rules.md) §1** **表内类别**）：模板生命周期、实例绑定/参数、运行时命令、**`LOG_EXPORT_REQUESTED`** / **`LOG_SENSITIVE_VIEW`** **等**。

---

## 3. 留存与 IAM

- **留存**：**不低于** **[`overview.md`](./overview.md) §3**（**≥180 天** **或** **`config` 审计** **取长**）；**法务更长保留** **须** **单列策略** **不得压低本条**。  
- **读权限**：**运营只读** **vs** **审计导出角色** — **[`observability-management/rules.md`](../domains/admin/observability-management/rules.md)** **`READ_ONLY` / L2`** **同窗**。  
- **实例日志导出**：流程锚点 **[`agent-management/functions.md`](../domains/admin/agent-management/functions.md) §4** · **`LOG_EXPORT_REQUESTED`**。

---

## 4. 互引

| 文档 | 关系 |
|------|------|
| [`overview.md`](./overview.md) | **总则** · **`admin.audit` 行** · **留存 §3** |
| [`tracing.md`](./tracing.md) | **`requestId`/`traceId`** **可选 join** |
| [`domains/admin/observability-management/functions.md`](../domains/admin/observability-management/functions.md) | **`FR-MC806～807`** · **`SC-OM*`** |
| [`domains/admin/agent-management/rules.md`](../domains/admin/agent-management/rules.md) | **§1 审计动作枚举** |

---

**文档版本**：0.1.0 · **维护**：产品 + 合规 + SRE · **本版**：从占位 **落地** **字段下限** **与** **`agent-management` §1** **同窗**。
