# Tool Management · Runtime 契约（跨实现 SSOT）

**叙事 / 运营面**：[`overview.md`](overview.md)、[`functions.md`](functions.md)。  
**目的**：让 **Runtime、BFF、观测（`agent.tool.call`）** 对 **同一套** **工具调用语义** **可对签**；**不**替代 [`trade-assistance.md`](../../agent/exchange-agent/trade-assistance.md) **§8**（`toolId` 登记）、[`design/api.md`](../../../../design/api.md)（PATH 矩阵）、[`overview-legacy-migration.md`](../../agent/exchange-agent/overview-legacy-migration.md)（回迁与 **§10.x** 映射）。

---

## 1. Tool Invocation State Machine（调用状态机）

**目标**：日志与 Runtime **状态字段 1:1**，避免 **UI/协查** 与 **实际执行** **口径漂移**。

### 1.1 状态枚举

| `invocationState` | 含义 |
|-------------------|------|
| **VALIDATING** | 入参 Schema、**Template/Profile 引用**、**Prompt 绑定**、**幂等键** 等 **前置校验** **进行中**（**尚未** **对交易所/外网** **发真实 IO）。 |
| **EXECUTING** | **已通过** **VALIDATING**，**正在** **执行** **工具体**（**含** **子账户 HTTP**、**model 调用**、**外网 B/C** 等）。 |
| **RETRYING** | **EXECUTING** **内** **可恢复失败** **且** **策略允许** **自动重试** **的区间**（**见 §3**）；**仍属** **同** **`toolCallSeq`** **内** **逻辑段**（**不** **递增** **`toolCallSeq`** **除非** **实现** **显式** **定义为** **新一次调用** **`design`** **冻结**）。 |
| **SUCCESS** | **终态 · 业务成功**（**含** **业务码** **200** **但** **「无仓位」** **等** **空成功** — **以** **Result Contract §4** **`status`** **为准**）。 |
| **FAILED** | **终态 · 失败**（**校验失败**、**策略拒绝**、**交易所拒单**、**超时** **等**；**UNKNOWN** **闭合前** **`invocationState`** **可** **暂留** **EXECUTING** **或** **所内** **`PENDING_RECONCILE`** **—** **须** **与** [`observability` §2.2](../../../observability/overview.md) **`exchangeOutcome=unknown`** **对签**）。 |

### 1.2 允许迁移（节选）

```
VALIDATING → EXECUTING → SUCCESS
           ↘ FAILED

EXECUTING → RETRYING → EXECUTING → SUCCESS
                    ↘ FAILED

EXECUTING → FAILED
```

### 1.3 观测对齐（**`agent.tool.call`**）

**与** [`observability/overview.md`](../../../observability/overview.md) **§2.1** **对签**：

- **每条** **`agent.tool.call`**（**或** **同** **`toolCallSeq`** **之物化多事件** **`design`** **二选一冻结**）**须** **可推导** **`invocationState`**。  
- **兼容**：已有 **`phase`=`start`|`success`|`fail`** **映射建议**：  
  - `start` **且** **未完成 IO** → **VALIDATING** **或** **EXECUTING**（**细分** **`subphase`** **可选**）；  
  - `success`/`fail` → **SUCCESS**/**FAILED** **终态**；  
  - **RETRYING** **须在** `agent.tool.call` **或** `agent.execution.step` **上** **显式** `invocationState=RETRYING` **或** **等价** **`retryAttempt` + 状态** **组合**（**OpenAPI 冻结一种**）。  
- **SC-TM-OBS-RT01（建议）**：任抽 **`executionId`**，**Runtime 内存/队列状态** **与** **最后一条** **`agent.tool.call`** **之** **`invocationState`** **不得** **互相矛盾**（**测试** **或** **抽检** **门禁**）。

---

## 2. Tool Risk Level（工具风险等级 · V1）

**登记**：**每个** **`toolId`** **在** **`trade-assistance` §8** **或** **Registry 镜像** **须** **带** **`toolRiskLevel`**（**枚举** **LOW**|**MEDIUM**|**HIGH**）；**与** **[`boundaries.md`](../../agent/exchange-agent/boundaries.md)** **闸门** **可联合** **`design`** ** OVERRIDE**。

| Level | 示例 `toolId`（示意） | 说明 |
|-------|----------------------|------|
| **LOW** | `get_balance`、唯读行情/账户快照类 | **默认** **更宽** **自动 Retry（§3）**；**仍须** **子账户边界（§9）**。 |
| **MEDIUM** | `create_order`、改单前置查询组合 | **写路径** **但** **可** **撤销/对账**；**禁止** **无脑** **自动 Retry（§3）**。 |
| **HIGH** | `withdraw`、划转出金、`universal_transfer` **等非可逆高风险**（**以**矩阵 **§8.4** **为准） | **强门禁** · **Risk** **可加签** · **Sandbox（§6）** **Production** **须** **白名单**。 |

---

## 3. Idempotency Rules（幂等与自动 Retry）

**原则**：**自动 Retry** **仅** **对** **幂等读** **或** **明确定义** **为** **安全重放** **之** **操作**；**写** **须** **`idempotencyKey` / `clientOrderRef`** **与** [`overview.md`](../../agent/exchange-agent/overview.md) **FR-T01** **对签**。

| 工具（示例） | `toolRiskLevel` | **自动 Retry** | 说明 |
|-------------|-----------------|----------------|------|
| `get_balance` | LOW | **允许** | **退避** **+** **上限** **`design`** **冻结**；**状态** **RETRYING（§1）**。 |
| `create_order` | MEDIUM | **禁止** **自动 Retry** | **仅** **允许** **UNKNOWN/504** **路径** **之** **查单对账** **后** **由编排** **显式** **二次提交**（**人/策略** **不得** **默认** **for 循环** **重放** **同参** **下单**）。 |
| **其它写** | MEDIUM/HIGH | **默认禁止** **自动 Retry** | **与** **MEDIUM** **同** ** unless** **ADR** **登记** **某** **`toolId`** **安全重放条件**。 |

**扩展**：**按** **`toolId`** **逐条** **在** **`trade-assistance`** **或** **本域 Registry** **补** **`idempotencyClass`=`READ_SAFE`|`WRITE_ONCE`|`RECONCILE_ONLY`** **与** **上表** **合并** **`design`** **填链 PR**。

### 3.1 与单次执行预算（`FR-AO06`）之计数对齐

**同一 `executionId`** **之** **工具调用次数预算**（[`execution-lifecycle.md`](../../../domains/agent/agent-orchestration/execution-lifecycle.md) **§4**）**按** **逻辑调用** **粒度** **如下** — **`design`** **可** **细化为** **OpenAPI** **字段**：

- **同一 `toolCallSeq`** **内** **处于** **§1** **`RETRYING`** **之** **多次尝试** **计为** **一次** **预算占用**（**直至** **SUCCESS / FAILED** **终态**）。  
- **编排** **在** **UNKNOWN / 504** **闭合** **后** **发起** **「新一次显式提交」** **且** **`design`** **分配** **新** **`toolCallSeq`** **者** **计为** **新一次**（**与** **`create_order`** **禁止** **无脑** **同参** **for-loop** **重放** **一致**）。

---

## 4. Tool Result Contract（统一返回结构）

**Output Schema**（**JSON Schema / 字段说明**）**仍** **为** **`toolId`** **真源** **`trade-assistance`/OpenAPI**；** envelope** **由下式** **统一**，**便于** **Runtime、模型回填、计费 attribution**：

```json
{
  "status": "SUCCESS",
  "executionId": "",
  "data": {},
  "error": {}
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| **`status`** | `SUCCESS` \| `FAILED` \| `PARTIAL`（**可选**；**少用** **须** **`design`** **冻结**） | **与 §1 终态一致**：`SUCCESS`/`FAILED` **映射** **`invocationState`** **之子集**。**PARTIAL**：**多腿仅部分完成** **时** **`design`** **允许**。 |
| **`executionId`** | string | **与** **`billing`/observability** **同键**。 |
| **`data`** | object | **业务载荷**；须 **符合对应 `toolId` 之 Output Schema 子集**；敏感字段脱敏后入观测。 |
| **`error`** | object | **`status=FAILED`** **时** **非空**：**机器码**（**对齐** **`exchange-agent` FR-T05** **`billCode`/稳定码** **子集**）、**可选** **`message`、`retryable`、`details`**（**无** Secret）。**`SUCCESS`** **时** **`{}`** **或** **省略** **`design`** **二选一**。 |

---

## 5. Tool Runtime Permission Boundary（运行时权限校验链）

**单次** **`toolId`** **可被模板声明** ≠ **本次** **`executionId` 可调**。**必经链路**（**环节顺序** **`design`** **可微调**，**但下列能力域均不得跳过**）：

1. **Prompt**：拼装与治理 — **已 Resolve** 之 **`promptPack*`**、**`scenarioId`** **等**，见 [`prompt-management/runtime-injection.md`](../prompt-management/runtime-injection.md)。  
2. **Runtime**：实例/会话 **`FEATURE_*`**、**`agentState`**、**`executionId`** **有效**。  
3. **Tool Permission**：模板 **T05 · Tool Profile**、**`toolId`** **之** **`enabledOperational=true`** **[`FR-TM03`](functions.md)** IAM/场景策略（**落点**：BFF **或** Runtime **内闸门** — **`design`/`OpenAPI`** **冻结**）。  
4. **Risk Check**：**`toolRiskLevel`**、持仓/保证金/地域/产品线闸 — [`boundaries.md`](../../agent/exchange-agent/boundaries.md)。  
5. **Execute**：**仅当 1～4 全部通过** **后** **进入 §1：VALIDATING → EXECUTING**。

---

## 6. Tool Sandboxing（环境策略）

**与** **`FEATURE_AGENT_*`、测试网网关** **对签**（**`design`**）。**概要**：

| 环境 | 是否允许（默认口径） |
|------|---------------------|
| **Testnet** | ✅ **允许**（**HIGH** **亦** **默认可测**，**Production** **另见**下行） |
| **Production** | **条件允许** — **须** **`PATH`** **冻结** **+ Enable + 策略**，**HIGH** **另加** §6 **下表 **白名单** |

**按 `toolRiskLevel` 细化**（**`toolId` **级 **`Registry` override** **`design`** **登记**）：

| 环境 | HIGH | MEDIUM | LOW |
|------|------|--------|-----|
| **Testnet** | ✅ **允许**（**默认**） | ✅ | ✅ |
| **Production** | **条件允许** **（**模板白名单 **`+`** **Risk 签 **`+`** **HIGH** **ADR** **`或`** **等价** **） | **条件允许** **（PATH 冻结 **+** **Enable **`+`** **策略绑定**） | **条件允许** |

---

## 7. Tool Freeze Rule（停用 / 冻结语义）

**触发条件**：运营 **Disable** **`toolId`**（**`enabledOperational=false`**）**或** **合同/合规** **等价 FREEZE**。

| 对象 | 行为 |
|------|------|
| **新 Template（草稿保存/发布）** | **禁止绑定** **`toolId`**：**`SC-TM-09`**、[`flow §6`](flow.md)。 |
| **新 Runtime / 新建实例（模板快照仍含已禁用 tool）** | **创建/启动失败** **`422`** **`design`** **默认**；**或** **强制降配** **`design` 冻结**。 |
| **在飞 Runtime**（已 Resolve **`toolCallSeq`** **或** **处 EXECUTING**） | **V1 默认**：不强制中断 **当前 invocation**，允许跑至终态（SUCCESS/FAILED/UNKNOWN 闭合）；**禁止**对已 Freeze **`toolId`** **发起新的** **VALIDATING 起点**。合规硬停须 **ADR**，并与 **`management-console-v1-prd` · D-1 附录** 对签。 |

---

## 8. Tool Ownership（归属与后台权限）

| 对象 | Owner（责任域） |
|------|-----------------|
| **Tool Schema** | **平台**（架构 + 技能登记 MR） |
| **Tool Runtime**（adapter/executor） | **平台**（实现仓） |
| **Tool Permission**（`FR-TM03` 策略模型） | **平台**（安全/架构编修 · 运营执行） |
| **Tool Enable**（**运营开关**） | **平台运营**（**ToolOperator/RiskAdmin** **见** [`rules.md`](rules.md)） |

**Tool 管理权限**：**独立** **IAM 资源**（**如** **`tool.*`** **或** **所内** **`TOOL_ADMIN_BASE`** **包**）**须** **显式** **授予**；**默认** **任何** **角色** **不含** **模块三** **写/Enable** **能力**（**与** [`functions.md`](functions.md) **FR-TM-G01** **「** **不得** **弱化为** **单一超级管理员** **」** **一致** **—** **默认** **偏** **deny** **由** **安全** **开白**）。

---

## 9. Tool Runtime Isolation（子账户隔离）

- **交易所私有 API**：仅使用 **Agent 绑定子账户 scope** **之凭据**（[`exchange-agent/overview.md`](../../agent/exchange-agent/overview.md) **FR-T01**、[ `design/api.md`](../../../../design/api.md) 矩阵）。
- **禁止**：主账户 API Key / 母账本用于 **本条执行链** **之写**，或 **越权子账户**（**另行变更单** **除外**）。

**审计/日志**：可记 **`agentTradingApiKeyId`** **等公开 id**；**禁止**主账户 **Secret**。

---

## 10. 邻域自检

| 邻域 | 核对 |
|------|------|
| **observability §2.1** | **`invocationState`/`phase`** **映射** **§1.3** |
| **tool-management `functions`** | **FR-TM03/05**、**SC-TM-09**、**Enable** |
| **trade-assistance §8** | **`toolId`**、**未来** **`toolRiskLevel`/`idempotencyClass`** |
| **prompt-management** | **§5** 链 **第 1 步** |

---

**文档版本**：0.1.1 · **维护**：产品 + Runtime owner · **本版**：**§3.1** **与 **`FR-AO06`** **工具预算计数** **对齐** **`execution-lifecycle` §4**。
