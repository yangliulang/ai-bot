# Runtime · 不变式（Invariants · **宪法**）

**路径**：`specs/requirements/Runtime/runtime-invariants.md`。

**职责**：**单笔 `executionId` 主轨迹** **上** **绝对不能违反** **的规则**（**编号 INV**）。**逐边允许/触发/守卫** **以** [`execution-transition-matrix.md`](./execution-transition-matrix.md) **§2.2** **为 SSOT**；**本条** **不** **替代** **矩阵全文**。

---

## 0. Runtime 执行闸（速查 · Enforcement Matrix）

**用途**：把 **INV-008～010** **落到**「**哪一阶段须断言**」，**与** [`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md) **§1 步骤 2～4**、[`execution.md`](./execution.md) **§1** **步 6～7** **对读**。**实现** **须在** **Gateway / Adapter 入口** **保留** **最后一道熔断**（与 **Prompt 是否写清** **无关**）。

| **阶段** | **须成立（摘要）** | **主要 INV** |
|----------|-------------------|--------------|
| **进入 `waiting_confirmation` 且将推「写」类型 A** | **L0 skill 登记之** **写参数** **`required` 已齐**、**已过** **校验规则**、**每笔写参数字段血缘** **在白名单** **或** **可归一为** **交易所元数据规范化** | **INV-008**、**INV-009** |
| **`call_exchange_write` / Gateway 前** | **载参与** **用户已确认包** **一致**；**重申** **无缺参、无非法血缘** | **INV-008** |
| **语义** **「清仓/全部/买满」** **等** | **仅经** **获准只读** **（** **余额/持仓/可用** **）** **或** **用户明确数字** **收敛为定量**；**禁止** **解析器/适配器** **默认占位** | **INV-010**、**INV-009** |

**违例处置**：**Stop**（**不** **扩张** **Coobit 私有写**）；**Taxonomy** **`WRITE_PARAMETER_CONTRACT`** — [`runtime-error-taxonomy.md`](./runtime-error-taxonomy.md)；**处置索引** — [`failure-matrix.md`](./failure-matrix.md) **§2**。**典型实现枚举**（**所内须登记并映射** **`FR-T05`/`stableReason`**）：**`WRITE_PARAMS_INCOMPLETE`**、**`INVALID_PARAMETER_SOURCE`** — [`error-normalization.md`](./error-normalization.md)。**抽检 Eval**：[`evals/scenarios.md` **`eval.gateway.*`** 五行](../evals/scenarios.md) · [`pipeline-write-order` §3 负例](../evals/pipeline-write-order.md)。

---

## 1. 不变式（MUST NOT / MUST）

| **ID** | **规则** |
|--------|----------|
| **INV-001** | **`completed` / `failed` / `cancelled`** **为终局主态**：**同一** **`executionId`** **下** **不可逆** **迁回** **`planning` / `executing` / `settling`**（**子态 RETRYING** **不** **抬主行**）。 |
| **INV-002** | **`unknown_pending`** **不得** **在** **计费/核销叙事或用户话术** **中被** **当作** **`completed` / 已成交**；**PER_EXECUTION_FINAL** **成功 `ENTITLEMENT_DEBIT`** **仅** **在** **可采信终局闭合** **之后** — **同窗** [`consume-and-bill.md`](../flows/consume-and-bill.md) **S4～S5**。 |
| **INV-003** | **触及** **`call_exchange_write`** **的写路径** **不得** **绕过** [`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md) **/ ADR-001** **类型 A**（**除非** **矩阵 §2.1** **登记** **且** **flow** **明示** **之** **等价门禁**）。 |
| **INV-004** | **风险/护栏/编排预算** **等** **已** **`risk_rejected`/拒答** **之** **结果** **不得** **导致** **在无新用户确认与合规叙事下** **进入** **会扩张** **Coobit 私有写** **的** **`executing`** **（** **只读/无害工具** **`executing`** **不受此限** **—** **见** **矩阵** **`planning→failed`** **与** **S5.1** **）**。 |
| **INV-005** | **同** **`executionId`** **内** **子态 Retry** **不得** **突破** **幂等/**`runtime-contract` **§3** **边界**（**尤其** **禁止** **`create_order`** **等** **无脑自动重试** **同参下单**）。 |
| **INV-006** | **Replay** **（** **恢复语义** **）** **默认** **须** **新开** **`executionId`** **或** **ADR** **登记之** **显式 replay**；**禁止** **默示** **终局后** **在同 id** **下** **重启** **主扩张**。 |
| **INV-007** | **交易所** **`partial_filled`** **等** **部成** **仅** **子态/观测维** **—** **不得** **单独立** **附录 A** **新主行** — [`trade-via-agent.md`](../flows/trade-via-agent.md) **S5.1**。 |
| **INV-008** | **写参数完备性（Write Parameter Completeness）**：**任何** **可能产生** **交易所侧写副作用** **之** **`executionId`** **轨迹** **不得** **在** **下列** **未** **同时** **满足** **时** **发出** **携带** **将被 `call_exchange_write` 使用** **之** **载荷** **的** **Telegram §2.5 类型 A**，**亦不得** **调用** **`call_exchange_write`**：（1）**当前** **`skillId`/L0 契约** **登记之** **`required` 写槽** **已齐备** **且** **经** **系统校验**（**含** **minNotional/stepSize/tick** **等**，**以** **工具/元数据** **为准**）；（2）**拟提交字段** **与** **卡面展示** **可对账** — **同窗** **[`trade-via-agent` S11、S13～S14](../flows/trade-via-agent.md)**、[`confirmation-flow.md`](../domains/agent/agent-orchestration/confirmation-flow.md) **§1 步骤 2～3**。**纯澄清话术**（**不** **含** **可执行写参包**）**不受** **「禁发类型 A」** **字面值约束**，**但** **仍不得** **顺带** **扩张** **私有写**。**与** **INV-003** **正交**（**INV-003** **管** **确认门**；**本条** **管** **参数可否** **进入** **确认门**）。 |
| **INV-009** | **写参数血缘（Parameter Provenance）**：**凡** **将进入** **`call_exchange_write`** **之** **每笔** **业务参数字段**（**如** **`quantity`/`quoteQty`/`price`/合约张数** **等** **以** **L0 skill** **为准**）**须** **附带** **`provenance.source`** **血缘字段** **（**所内** **BFF/编排** **结构化字段** **或** **等价观测摘要**）。**合法字面** **仅** **`user_input`**（**用户字面**）、**`confirmation_echo`**（**与** **已确认类型 A** **逐项一致** **之** **回显**）、**`runtime_read_balance`** **/ `runtime_read_position`**（**获准子账户只读** **且** **与用户可见卡面** **同源**）、**`exchange_metadata_normalize`**（**仅** **tick/step/minNotional** **等** **规范化** **不产生** **新** **经济意图**）。**Runtime MUST NOT** **接受**：**`fallback_default`**、**`parser_autofill`**、**`adapter_placeholder`**、**`llm_inferred_unconfirmed`** **等** **未** **经** **上列** **合法源** **对齐** **之** **占位或臆测数量/价格**。**同窗** [`memory-runtime`](./memory-runtime.md) **FR-MEM04** **（** **叙事** **不得** **单独** **当** **写参来源** **）**。**违例** → **Stop** + **`INVALID_PARAMETER_SOURCE`** **族**（**映射** **`FR-T05`** — **§0**）。 |
| **INV-010** | **语义满仓/清仓 Intent**：**自然语言** **「全部卖出/清仓/用全部 U 买入」** **等** **须** **先** **归类为** **可执行语义**，**再** **仅经** **INV-009** **准许** **之** **来源** **（** **通常** **`runtime_read_balance`** **/ `runtime_read_position` + 用户确认** **）** **落实** **为** **定量** **后** **方得** **满足** **INV-008**。**禁止** **以** **LLM** **槽位** **单独** **填满** **经济敏感字段** **而** **跳过** **获准只读** **或** **用户** **明示** **数字**。**流程专节** → [`trade-via-agent` S11.1](../flows/trade-via-agent.md#trade-inv-010-semantic-full-book)；**执行体分工** → [`clarify-user-visible` §0](../prompts/shared/clarify-user-visible.md#clarify-execution-split)；**同窗** [`sell`](../prompts/trading/sell.md) **§1**、[`buy` §1.1](../prompts/trading/buy.md)、[`skill.spot.flash_convert` §4.1](../skill-specs/spot/skill.spot.flash_convert.md)、[`clarify-user-visible` §2](../prompts/shared/clarify-user-visible.md)。 |

**其它强制条**（**不** **另占编号**）：**合法单步迁移** **仅** **矩阵** **§2** **✓/✓†**；**主态行** **仅** **编排宿主** **持久化** — [`locking.md`](./locking.md) **§2**；**持久化** **不** **双计费** — [`persistence.md`](./persistence.md)。

---

## 2. 审计顺序

1. [`execution-transition-matrix.md`](./execution-transition-matrix.md) **§2.2**  
2. 本篇 **§1**  
3. [`runtime-state-machine.md`](./runtime-state-machine.md) **§4**

---

**文档版本**：2.1.1 · **维护**：产品 + Agent Runtime owner · **本版**：**§0** **同窗** **`eval.gateway.*`**。**承** 2.1.0。
