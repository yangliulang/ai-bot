# Tool Management · 配置与 IA

**需求 SSOT**：[`functions.md`](functions.md)。

---

## 1. IA（V1）

**运营后台（`src/admin` Demo）· 原型已对齐（非生产 API）**：

| 路由 | 页面 ID | 说明 |
|------|---------|------|
| **`/ai/tool-registry`** | **`ai.tool-registry`** | **技能与工具**：A/B/C 登记镜像 + **Git §1～§6 抽屉解析** + **启用/停用**（localStorage）；**非**生产 Registry API / **非** Runtime Publish UI |
| `/ai/skill-specs` | — | **重定向** → `/ai/tool-registry` |
| `/tools`、`/tools/registry`、`/ai/tool-policies` | — | **重定向** → `/ai/tool-registry` |

**实现**：[`ToolRegistryPage`](../../../../src/admin/src/pages/tools/ToolRegistryPage.tsx) · 登记单源 [`skillRegistryCatalog`](../../../../src/admin/src/pages/tools/skillRegistryCatalog.ts)（同窗 `manifest.yaml` + `trade-assistance` §4/§8.2）。**对齐 SSOT**：[`admin-console-tool-registry-reconciliation.md`](admin-console-tool-registry-reconciliation.md) **§0** · 低保真 [`page-specs.md`](../../../admin-console/page-specs.md) **`ai.tool-registry`**。

**需求与 OpenAPI SSOT** 仍见 [`functions.md`](functions.md)、[`admin/tool-management.yaml`](../../../../openapi/admin/tool-management.yaml)。**导航与路由** 见 **[`admin-console/demo-routing.md`](../../../admin-console/demo-routing.md)**。

**说明**：下文 **§2 列表列** 为 **生产 Registry API 目标态**；**Demo 列** 以 **page-specs** 与 `skillRegistryUiCopy.ts` 为准。

**V1 目标态（未在 Demo 拆子路由，可后续迭代）**：

| 路由示例 | 视图 | 说明 |
|----------|------|------|
| `/tools/registry/:toolId/schema`（或详情 Tab） | **Schema** | 参数表、Schema JSON **折叠**、`TBD` **Banner**。 |
| `/tools/registry/:toolId/policy`（或策略 Tab 行内展开） | **调用策略** | **FR-TM03**：白名单维度（角色、租户、scenario…）。 |
| `/tools/logs`（可选聚合）或 **Registry 内链** | **协查** | 跳 **`observability-management`**，预填 **`toolId`**。 |

---

## 2. 列表列（默认）

| 列 | 内容 |
|----|------|
| `toolId` | 稳定标识；可复制 |
| **域 / 类型** | e.g. `exchange_read`、`tool.web.*`、`model` |
| **PATH / 网关** | 摘要或 **「TBD」** |
| **矩阵** | **FROZEN / TBD / DEFERRED**（枚举 **`design`** 对齐） |
| **启用** | Badge |
| **策略** | **已绑定 / 缺失**（**门禁**：缺失则 **§2.4** **不得** Enable，见 [`functions.md`](functions.md) **§7**） |
| **风险** | **A/B/C**（与 **`trade-assistance`** 一致若有） |
| **Owner** | 所内责任人 |

---

## 3. 调用权限策略模型（FR-TM03 · BFF/OpenAPI）

**UI SSOT**：[`functions.md`](functions.md) **§2.25、§7**。

| 字段 / 概念 | 说明 |
|-------------|------|
| `policyId` / `toolPolicyId` | **每 `toolId`（或前缀/域模板）至少一条可审计策略头** |
| `denyByDefault` | **`true`**（**缺省**）；无显式 allow 之主体会话 **策略引擎不归因通过** |
| `allowedIamRoles[]` **或** `allowedGroups[]` | **与 §2.25** 「IAM 角色 / 组别」 **枚举对齐** |
| `allowedScenarioIds[]`（可选） | **`scenarioId`** 交集 **非空** **才放行** |
| `toolDomain` / `toolIdPrefix`（可选） | **冗余**校验 · **防错绑** |
| `effectiveFrom` / `revision`（建议） | **回滚 · 审计** `TOOL_POLICY_UPDATED` **对齐** |

**注意**：租户维（若 FR 需）**占位**在所内 **`Tool Admin`/BFF** spec **枚举**后与 **本节**一起做 **对齐 PR**。

---

## 4. 镜像字段契约

| 字段 | 说明 |
|------|------|
| `toolId` | SSOT **`trade-assistance`/`design`** |
| `toolRiskLevel`（建议） | **LOW \| MEDIUM \| HIGH** **[`runtime-contract.md`](runtime-contract.md) §2**；**镜像** **自 **`trade-assistance` **或 **`design`** **填链 PR** |
| `matrixStatus` | 派生自 **登记表 + 矩阵** |
| `pathSummary` | **不得**长于 OpenAPI **requestPath** 真值 **虚构** |
| `enabledOperational` | **FR-TM04** **与** **`matrixStatus`** **联合推导** |

**OpenAPI**：所内 **`Tool Admin`/`BFF`** spec **填入** [`design/api.md`](../../../../design/api.md) **登记表**后，与本节 **对齐 PR**。

---

## 5. Tool Profile 与模板 T05（`agent-management`）

**需求对签**：[`../agent-management/functions.md`](../agent-management/functions.md) **T05** · **SC-AM-04**；本域 **`toolProfileRef`（或等价）解析出的 `toolId[]`**：**逐项须** **`enabledOperational` ∧ `matrixStatus=FROZEN`** **方可写入**模板 **`allowed`** 集 —— **阻断语义**：**[`functions.md`](functions.md) SC-TM-09** · **[`flow.md`](flow.md) §6**。

---

## 6. 外链索引

- **仓库工具目录**：[`../../../tools/README.md`](../../../tools/README.md)（资产索引 **≠** **运行时 SSOT**）。  
- **矩阵**：[`design/api.md`](../../../../design/api.md)。  
