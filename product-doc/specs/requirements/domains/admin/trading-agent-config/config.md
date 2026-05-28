# Trading Agent Config · 配置与 IA

**需求 SSOT**：[`functions.md`](functions.md)。**键枚举**：[`keys.md`](keys.md)。

---

## 1. Tab 与 `configKey` 映射

| Tab | 对应 keys 节 | 内容 |
|-----|----------------|------|
| 全局闸 | [keys §1](keys.md) | `GLOBAL_AGENT_SWITCH`、`OPS_GLOBAL_AGENT_PAUSE` |
| 特性矩阵 | [keys §2](keys.md) | `FEATURE_*`、`CHANNEL_*` |
| **Memory / STM** | [keys §2.1](keys.md) | **`STM_*`**、**`RESUME_*`**、**`WARM_EXECUTION_INDEX_TTL_SEC`** — **idle/TTL stale · Resume 门控 · 温索引 · L0 窗口**（**[`memory-runtime` §14.6](../../../Runtime/memory-runtime.md)**） |
| 交易护栏 | [keys §3](keys.md) | `SYMBOL_*`、`AGENT_*` |
| 渠道管理（含 Telegram 等） | [keys §4](keys.md) | **键** 仍锚 §4（后端真源）；**控制台** 为 **渠道列表 + 分渠道详情**（运营语义），**不显式** 暴露 §4.2 key 表 / secretRef 路径；Bot/Webhook 叙事详 **[`telegram/admin-bot-config.md`](../../agent/telegram/admin-bot-config.md)** |

### 1.1 控制台拆面（全局参数 · Demo）

以下与 **管理台侧栏** **全局参数** 分组下：**Demo** 仅 **`sys.channels` 渠道管理** 独立页；**`GLOBAL_AGENT_SWITCH` / G01（keys §1）**、**`FEATURE_*`（keys §2）** **无** 独立运营页，由 **agent-management 横幅**、**配置 bundle / API**、Runtime freeze 叙事对签。**交易护栏 / 计费边界键**（keys §3、§5）**不设独立运营页**，由 **运行场景、准入、计费域** 等 **业务 IA** 承接或 **仅 API/配置中心** 写入。**键真源** 仍以 [`keys.md`](keys.md) 为准。

| 页面 | **应放置** | **不应放置** | keys 主要锚点 |
|------|------------|--------------|----------------|
| **渠道管理** | **Agent Interaction Channel 列表与分渠道详情**：接入状态、用户规模（演示）、Bot/Webhook/语言/菜单等业务字段；**不**以 configKey 为主表。 | 交易护栏数字、总闸键、`FEATURE_*`（无独立 Demo 页）。 | [§4 渠道 · Telegram](keys.md)（后端键；**控制台不显式暴露**） |
| **（无独立页 · §1）** | **全局闸**：`GLOBAL_AGENT_SWITCH`、运维并行熔断；与 **G01**、**`GLOBAL_OFF`** / **`OPS_SUSPENDED`** 归因对签（**agent-management**、Runtime）。 | 单渠道 Bot 参数、产品线 `FEATURE_*` 表、交易护栏数值。 | [§1 全局闸](keys.md) |
| **（无独立页 · §2.1）** | **Memory / STM**：**§2.1 键** **由** **全局 bundle / 配置中心 API** **写入**；**Demo** **无** **独立 Tab**（**与 §2 特性矩阵** **同窗 bundle** **或** **运维 JSON**）。**Runtime 步 2** **须** **观测生效快照**（**OpenAPI **`MemoryRuntimeConfigSnapshot`**）。 | **`cl:*` 键盘文案**、**Prompt 正文**。 | [§2.1 Memory/STM](keys.md#21-runtime--memory--stmfr-stm--产品默认-v0) |
| **（无独立页 · §2）** | **特性矩阵**：`FEATURE_*`、`CHANNEL_TELEGRAM` 等；由 **bundle/API** 写入。 | `GLOBAL_AGENT_SWITCH`（易与总闸混淆）、`TELEGRAM_*` 运行参数（**属渠道页**）。 | [§2 特性矩阵](keys.md) |
| **（无独立页 · §3/§5）** | **`AGENT_*`、`SYMBOL_*`、BILLING 边界键** 等：由 **AI Runtime 治理**（运行场景、人工确认、安全防护、准入、计费）与 **后端 bundle** 分工展示/写入；**避免** 再挂「平台默认策略」类 **Config Center 页** 与治理分层冲突。 | — | [§3 交易护栏](keys.md)、[§5 `BILLING_*`](keys.md) |

**与 Demo 控制台**：`ChannelConfigPage` 为 **渠道列表 + `/system/channels/:channelId` 详情**（运营语义）；`/system/global-gate`、`/system/feature-flags` **重定向** 至 **`/runtime/executions`**；`telegramChannelConfigKeys` 等 **仅** 留在 **`mock`** / API 对齐，**不**再作为页内主表。

---

## 2. 版本化写入（FR-MC707）

对齐 [`management-console`](../management-console-v1-prd.md) §7.2 · §8.4、[design/api.md](../../../../design/api.md) **「运营后台 · 全局配置写入」**：

- **分 Tab 提交** 或 **单次 bundle**：由 **OpenAPI / `design`** 冻结；单次请求原子。
- **`If-Match`** 与 **`configVersion`** 冲突 → **409**、`ADMIN_OPS_CONCURRENT`。
- **BFF**：Dry-run / Diff 预览、`ETag` **是否必选** 由 **`design`/OpenAPI** 冻结。

---

## 3. **导出**（灾备）

**JSON/YAML**；**受限 RBAC**；**不含 Secret**。

---

## 4. **用户级覆盖**

若某键允许 **用户级 override**，须在 **PRD 附录 A** 与 [`access-control`](../access-control/overview.md) **对签后** 方可在本模块 UI 暴露。

---

## 5. **与 Billing / Prompt 划界**

`BILLING_*` 透出边界见 [`keys` §5](keys.md)；账务专属阈值、Prompt 变量 **不属于** 本 Tab **除非** 产品与域 owner **书面豁免 MR**。

---

与 [`flow.md`](flow.md)、[`rules.md`](rules.md) **同步维护**。
