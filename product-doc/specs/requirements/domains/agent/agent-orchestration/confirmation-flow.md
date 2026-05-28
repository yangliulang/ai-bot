# 确认流 · 写路径步骤与 `SC-TA*`

**职责**：**类型 A 确认卡先于 Coobit 写**（ADR-001）在 **编排步骤序** 上的 **产品表达**；**条文主宿主** **仍** **在** [`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **§2**。**Telegram 卡面条目（§2.5.x）** → [`../telegram/overview.md`](../telegram/overview.md)。

**互引**：[`overview.md`](overview.md) **FR-AO01、FR-AO04**、**§3 `SC-AO-01`/`SC-AO-04`**；**Production Runtime** [`skill-specs/production-runtime.md`](../../../skill-specs/production-runtime.md)；[`runtime-invariants INV-008～010`](../../../Runtime/runtime-invariants.md)；[`../../../../design/adr/001-telegram-confirm-before-coobit-write.md`](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)；[`../telegram/overview.md`](../telegram/overview.md) **§2.5.x · 类型 A；总则 §2～§2.6**。**步骤 4 之后（交易所私域写）同窗** **Intent→Canonical→Gateway→Adapter**：[`canonical-trading-model.md`](../../../../design/canonical-trading-model.md)、[`ADR-004`](../../../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../exchange-agent/trade-assistance.md)；[`CC-P1-07`](../../../contract-closure.md#cc-p1-07)；[`requirements-review` §7.5](../../../../../product/requirements-review.md#cc-adr004-review-checklist)；[`Runtime/execution` §1 步 7](../../../Runtime/execution.md)。**契约开放面 / 走读缺口** → [`closure-remaining` §7](../../../closure-remaining.md#cc-remaining-open-items) · **[§7.1](../../../closure-remaining.md#cc-remaining-gap-paste)** · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)**。

**对上 Coobit**：**步骤 4**（`call_exchange_write` **等私域读写**）**对上交易所 HTTP**：出站默认 **`openapi-ai`/Skill**，**制品须 pin**。**不改变** ADR-001、类型 A、[ **`trade-assistance` §2**](../exchange-agent/trade-assistance.md)、[**`design/api`**](../../../../design/api.md)、[**`agent-coobit-api-allowlist`**](../../../integrations/exchange/agent-coobit-api-allowlist.md)。综述 [**`integrations/exchange/overview`**](../../../integrations/exchange/overview.md)。


---

## 0. 写路径 · 概念管线与风险闸（对签索引）

**十步口语**（含 **Risk Check** 归并 **R1～R4**、**Receipt/Timeline 三轨**、**`executionId` 与 S5 顺序**）→ **[`Runtime/domain-model.md`](../../../Runtime/domain-model.md)**。**本节 §1 五步** **仍** **为** **确认流 SSOT**。

---

## 1. 标准步骤序（原 overview §6.4 / FR-AO01）

以 **`trade.spot.limit_order`** **为** **主轴**（其它写场景 **同构** **除非** **流程专节** **另行规定**）：

**扩展**：**`trade.spot.oco` / `trade.spot.bracket`** **在** **`design/api`** **子账户矩阵** **对应 PATH 冻结** **且** **[`product.md`](../../../product.md) §非目标** **已解除** **「OCO/bracket Agent 暂不交付」** **后** **与** **主轴** **同序**（**步骤 3 类型 A** **可** **多腿摘要** **但** **须** **单次用户确认语义** **所内终裁**）；**矩阵书面延期未解冻**，**或** **`product.md` §非目标** **仍禁止交付 OCO/bracket 时**，**不得** **执行** **步骤 4** **交易所写**。详见 [`trade-via-agent.md`](../../../flows/trade-via-agent.md) **专节 · 现货限价**、[`routing-engine.md`](routing-engine.md) **§2**。

1. **`read_skill_operation_spec`**（或等价）— **FR-AO04 / FR-T11**  
2. **参数校验 / 偏离带 / 槽位补全** — **FR-T07 / FR-AO02**；**Runtime 硬闸** **[`runtime-invariants` §0、INV-008～010](../../../Runtime/runtime-invariants.md)** — **未** **同时** **满足** **写槽** **齐备**、**系统校验通过**、**写参** **`provenance`** **合法** **时** **不得** **发出** **携带** **`call_exchange_write`** **将使用** **之** **参数的** **Telegram §2.5 类型 A**（**纯澄清、无** **可执行写参包** **之** **上轮** **话术** **不在此禁**）。**Typical 违例**：**`WRITE_PARAMS_INCOMPLETE`**、**`INVALID_PARAMETER_SOURCE`** → **`FR-T05`/`stableReason`**（**所内** **登记**）— **同窗** [`runtime-error-taxonomy` `WRITE_PARAMETER_CONTRACT`](../../../Runtime/runtime-error-taxonomy.md)。**澄清链 LLM/规则/组合** → [`prompts/shared/clarify-user-visible` §0](../../../prompts/shared/clarify-user-visible.md#clarify-execution-split)；**跨轮 session / `cl:*`** → [`clarify-session.md`](../clarify-session.md)。  
3. **Telegram · §2.5 · 类型 A 确认**（[`../telegram/overview.md`](../telegram/overview.md)）  
4. **`call_exchange_write`** — **可为单笔** **或**（**逻辑改单**）**经同一步骤 3 授权后** **顺序多笔**，**中间不插入第二次类型 A**；详见 **[`trade-via-agent.md`](../../../flows/trade-via-agent.md)** **专节 · 逻辑改单** **与** [**ADR-001**](../../../../design/adr/001-telegram-confirm-before-coobit-write.md) **决策 §5**。  
5. **用户可见摘要与错误解释** — **FR-T05 族**

---

## 2. **SC-TA01、SC-TA02**

- **完整定义与抽检口径** → [`../exchange-agent/trade-assistance.md`](../exchange-agent/trade-assistance.md) **§2、§8**。  
- **编排验收**：**任一** **`agent.orchestration.step`** **标榜写路径** **须** **在** **`routing-engine.md`** **寄存器** **有键** **且** **步骤序** **不满足** **上节** **即** **为** **契约不达标**。**依赖 / 并行 / 失败出口** **另受** [`runtime-freeze.md`](runtime-freeze.md) **§3** **（** **§3.1～§3.11** **）** **最小编排表** **约束** — **与** **寄存器** **键** **同窗** **见** **`routing-engine` 文首** **「写路径 · 编排下限对签」**。

---

## 3. 理财与子站回退

- **不可用 API 模板落地之写** → **`WEALTH_ACTION_REQUIRES_WEB`** **等** — [`../exchange-agent/boundaries.md`](../exchange-agent/boundaries.md)、[`../../flows/wealth-via-agent.md`](../../../flows/wealth-via-agent.md)。

---

**文档版本**：1.1.11 · **维护**：产品 + Agent Runtime owner · **本版**：**步骤 2** **同窗** **`runtime-invariants` INV-008～010**。承 **1.1.10**。
