# 域需求：Tool Management（后台 — 工具运营面）

| 项 | 内容 |
|----|------|
| **产品** | ChainUp AI Agent（Coobit 单所） |
| **文档** | `specs/requirements/domains/admin/tool-management/overview.md` |
| **状态** | **域内需求已展开（V1）**；**OpenAPI/**[`design/api.md`](../../../../design/api.md) **登记表「Tool/模块三」行**填满链后与 [`functions.md`](functions.md) **§5·§7**、[`runtime-contract.md`](runtime-contract.md)、[`config.md`](config.md) **§3～§5**、[`flow.md`](flow.md)、矩阵 **做一次对齐 PR**。 |
| **PRD 位置** | **[`../management-console-v1-prd.md`](../management-console-v1-prd.md) · §6 模块三**（**FR-MC301～305**） |
| **互引** | [`design/api.md`](../../../../design/api.md)；[`runtime-contract.md`](runtime-contract.md) **（运行时状态机、风险级、信封、权限链）**；[`../../../tools/README.md`](../../../tools/README.md)；[`../../agent/exchange-agent/trade-assistance.md`](../../agent/exchange-agent/trade-assistance.md) **§8**；[`../../../observability/overview.md`](../../../observability/overview.md) **§2.1 · SC-OBS05**；[`../observability-management/overview.md`](../observability-management/overview.md)；[`../agent-management/overview.md`](../agent-management/overview.md) **T05**；[`../../../contract-closure.md`](../../../contract-closure.md) **§1、CC-P1-02～03**；**关单 MR 模板** **[MR-E · CC-P1-03](../../../contract-closure.md#cc-p1-mr-e)**；[**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · **[§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path) |

---

### 小团队落地边界（[`LITE-MODE.md`](../../../LITE-MODE.md)）

- **登记表与 Enable**：**`design/api` 矩阵「Tool/模块三」行**、OpenAPI **`tool-management`/`trade-assistance` §8** **同窗对齐 MR** 未齐前，**不** 对外宣称「工具运营面 + 矩阵门禁」已生产收口；详见 **CC-P1-02～03**、[当前快照 · `product/release-notes.md`](../../../../../product/release-notes.md)。

---

## 1. 目的（摘要）

**后台 · 模块三**：**Tool Registry 镜像、`toolId`/矩阵状态运营视图**、**JSON Schema / 参数说明只读或可编辑边界**、**[`FR-TM03`](functions.md)** **调用权限策略**、**Enable/Disable 门禁（PATH 冻结 + 策略就绪 + CC-P1-02）**、**抽样日志 / 协查入口**（**`agent.tool.call` join**）。**运行时** **工具状态机、风险级、统一返回、子账户隔离** — **[`runtime-contract.md`](runtime-contract.md)**。**不**替代 **`design/api` + `trade-assistance` §8** 之 **登记真源**；**须**满足 **SC-MCV1-05**（**矩阵未冻结不得假开**）。详参 [`functions.md`](functions.md)。

---

## 2. 本版包含 / 不包含

| 判定 | 内容 |
|------|------|
| **包含** | **FR-TM-G01、FR-TM01～06**；**SC-TM-01～16**；**[`runtime-contract.md`](runtime-contract.md)**（**`invocationState`、**`toolRiskLevel`、Retry/幂等、Result 信封、权限链、Sandbox、Freeze、Ownership、隔离**）；**§2.4 Enable 门槛**；**§7 工程默认**；**FR-MC301～305**（[`functions.md`](functions.md) **§3**）；**[`config.md`](config.md)**；**[`flow.md`](flow.md)**；**[`rules.md`](rules.md)**。 |
| **不包含** | **Tool 服务端实现**、**未登记 `toolId` 的发明** → **登记 MR 先行**；**模型路由** → [`ai-settings`](../ai-settings/overview.md)；**全量 observability schema** → [`observability`](../../../observability/overview.md)。 |

---

## 3. FR / SC 索引

| 类型 | [`functions.md`](functions.md) |
|------|----------------|
| **FR-TM-G01、FR-TM01～06**、门槛 **§2.4**、**FR-TM03 展开 §2.25** | **§2** |
| **SC-TM-01～19** | **§4** |
| **错误码** | **§5** |
| **运行时契约** **`invocationState`/隔离/信封** | **[`runtime-contract.md`](runtime-contract.md)** |
| **§7 已决议默认**（**SC-TM-03 缺省策略**、同步、Admin 导出 …） | **§7** |
| **FR-MC301～305 映射** | **§3～§3.1** |

---

## 4. 文档索引（阅读顺序）

| 顺序 | 文档 |
|------|------|
| 0b | [`admin-console-tool-registry-reconciliation.md`](admin-console-tool-registry-reconciliation.md) | **运营台 `ai.tool-registry` 原型对齐快照**（**先读** 改 UI 时） |
| 1 | [`functions.md`](functions.md) |
| 2 | [`runtime-contract.md`](runtime-contract.md) **（Runtime / Observability 对签）** |
| 3 | [`config.md`](config.md) |
| 4 | [`flow.md`](flow.md)（**含 §6 · T05 / 在飞**） |
| 5 | [`rules.md`](rules.md) |

---

*维护：产品 + 后台 owner。*
