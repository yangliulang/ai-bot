# Evals · 写路径管线顺序（`eval.runtime.pipeline_write_order`）

**路径**：`specs/requirements/evals/pipeline-write-order.md`。

**职责**：用 **GWT** 验证 **写路径** **因果序** **不低于** [`Runtime/domain-model.md`](../Runtime/domain-model.md) **§4** 与 [`trade-via-agent` S1～S10](../flows/trade-via-agent.md)。**不** 替代 [`skill-contract.md`](./skill-contract.md)（槽位/分流 **仍** 走 **`eval.skill.*`**）。

**走读勾选 SSOT**：[`Runtime/pipeline-walkthrough-checklist.md`](../Runtime/pipeline-walkthrough-checklist.md)。

---

## 1. 登记表

| `evalSetId` | 版本 | 构造要点 | 映射 |
|-------------|------|----------|------|
| **`eval.runtime.pipeline_write_order`** | `0.1.0` | **主轴** `trade.spot.limit_order`；**Then** 事件序 **须** 满足 **§2** **五段序**；**负例 §3** · **同窗** **`eval.gateway.*`** | **SC-OBS08**、**SC-OBS11**、**SC-TA01**、[`domain-model` §4](../Runtime/domain-model.md)、**JV-07** · **INV-008** |

**登记宿主**：[`scenarios.md`](./scenarios.md) **§1** 表行。

---

## 2. 正例 GWT（限价写 · 标准）

**Given**：用户 **已绑定**、**FR-T02** 通过、**FEATURE_TRADING=ON**；**`read_skill_operation_spec`** 返回 **PUBLISHED** **`skill.spot.limit_order`**。

**When**：用户发起 **完整限价买** 话束并完成 **类型 A** 确认。

**Then**（**同一 `executionId`** **时间线或等价结构化日志**）：

1. **`execution.dispatched`**（或等价起票）**存在**。  
2. **`agent.skill.spec_read`** **`phase=success`** **且** **时间戳早于** **`confirmation.required`**。  
3. **`confirmation.required`** **早于** **首条** **交易所私域写**（**`trading.exchange_private`** / **`agent.tool.call`** **写类** **以所内枚举为准**）。  
4. **`user.confirmed`**（或等价）**早于** **上条写**。  
5. **用户可见终局** **不** 在 **UNKNOWN** 时 **报成交**。

**Admin Mock 下限**：`exec-aa11` — **`src/admin/src/data/mock.timeline.contract.test.ts`**。

---

## 3. 负例（须失败）

| 负例 | When | Then |
|------|------|------|
| **P-N1** | 编排 **跳过** 类型 A | **0** `call_exchange_write`；**SC-TA01** |
| **P-N2** | 人为 **将** `spec_read` **置于** `confirmation.required` **之后** | **契约/走读失败**；**SC-OBS11** |
| **P-N3** | **Kill 拒新写** 后 **仍** 起 **新交易写** | **FR-T05**；**`eval.runtime.global_pause_blocks_new_write`** |
| **P-N4** | **`eval.gateway.missing_qty_blocks_trade_type_a`** · **§1·Then**（**载货类型 A**） | **`fail`/0 载货确认** · **INV-008** · **`WRITE_PARAMETER_CONTRACT`** |
| **P-N5** | **`eval.gateway.missing_qty_blocks_exchange_write`** · ** Gateway 前断言** | **0 Ingress 成功写** · **`WRITE_PARAMS_INCOMPLETE`** |
| **P-N6** | **`eval.gateway.provenance_fallback_rejected`** | **`INVALID_PARAMETER_SOURCE`** · **0** **写** |
| **P-N7** | **`eval.gateway.sell_all_without_balance_read_fail`** / **`eval.gateway.metadata_normalize_empty_qty_no_default`** | **INV-009/010** · **同上 Taxonomy** |

**同窗全表**：[`scenarios.md` §1](./scenarios.md) **`eval.gateway.*`** **五行**。

## 4. B 阶段真跑

**所内** staging **须** 跑通 **§2** **并** 登记 **`evalSetId` 版本**。**本 Git** **`npm test`** **仅** 覆盖 **Mock 序**（**§2 第 2～4 步** 之子集）。

**派工**：[`MR-B-BFF-IMPLEMENTATION` §2 MR-B4](../skill-specs/MR-B-BFF-IMPLEMENTATION.md) · [`closure-remaining` OP-AO3 / SK-B02](../closure-remaining.md#cc-remaining-open-close-path)。

---

**文档版本**：0.1.1 · **维护**：产品 + QA · **本版**：§3 · P-N4～P7、`eval.gateway.*` **同窗**。承 0.1.0。
