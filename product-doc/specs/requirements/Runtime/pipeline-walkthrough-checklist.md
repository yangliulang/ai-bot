# Runtime · 写路径管线走读清单（可复制）

**路径**：`specs/requirements/Runtime/pipeline-walkthrough-checklist.md`。

**用途**：把 [`domain-model.md`](./domain-model.md) **§2～§4** **落成** **MR/工单/所内集成测** **可勾选表**。**不** 新造 FR/SC；**关单 B** **仍须** [`contract-closure`](../contract-closure.md) **§2～§3** + [`closure-remaining` §7.6](../closure-remaining.md#cc-closure-exec-checklist)。

**同窗**：[`trade-via-agent` S1～S10](../flows/trade-via-agent.md) · [`MR-B-BFF-IMPLEMENTATION` §2 MR-B4](../skill-specs/MR-B-BFF-IMPLEMENTATION.md) · [`evals/pipeline-write-order.md`](../evals/pipeline-write-order.md) · [`flow/e2e-closed-loop` Goal-PIPE](../../../flow/e2e-closed-loop.md#goal-pipe-pipeline-write-order) · **所内 3 周派工** [`closure-internal-sprint.md`](../closure-internal-sprint.md)。

---

## 1. 适用范围

| 项 | 说明 |
|----|------|
| **主轴 `scenarioId`** | **`trade.spot.limit_order`**（其它写键 **同构**，**专节例外** 见 `trade-via-agent`） |
| **环境** | staging **或** 所内沙箱；**禁止** 用生产用户真下单 **冒充** 走读通过 |
| **主键** | 全程保留 **`executionId`** 供协查 |

---

## 2. 走读勾选（写路径 · 交易）

**Legend**：`[ ]` 未验 · `[x]` 已验（MR 中 **须** 附 **证据**：时间线导出 / 日志片段 / 用例 id）

### 2.1 输入与路由（S1～S2）

- [ ] **S1** Telegram `Update` **已归因** `sessionId` / 用户 / 实例（**无** 匿名写）
- [ ] **S2** 主 **`scenarioId` ≤ 1**；**非法键** → 澄清或 **FR-T05**（**非** 静默写）

### 2.2 风险闸束 R1～R2（S3 · 起票前配置）

- [ ] **R1** **FR-T02**：子账户+Key、**FEATURE_TRADING**、VIP、计费闸 — **写前** 已判（**拒答可读**）
- [ ] **R2** **`configVersion` / Kill·Pause**：**拒新写** 时 **无** `executionId` **误承诺可下单**

### 2.3 起票与读规范（S4～S5 · Skill Runtime）

- [ ] **S5** **`executionId`** **已分配**（**非** 仅用 `message_id`）
- [ ] **S4 / 5b** **`read_skill_operation_spec` success**；观测 **`agent.skill.spec_read`** **含** `skillId` + `skillSpecVersion`（**SC-OBS11**）

### 2.4 槽位与校验（S6 · Parameter + Validation）

- [ ] **FR-T07** 必填槽位 **齐** 或 **澄清轮**（**0** 臆测写）
- [ ] **`runtime-invariants` INV-008、INV-009**：**无** **`fallback_default`/`parser_autofill`/占位 **`quantity`**；**不发**「将写交易所」类型 A **`WRITE_PARAMS_INCOMPLETE`/`INVALID_PARAMETER_SOURCE`**（**映射** **`FR-T05`**）
- [ ] **FR-T12 / SYMBOL_POLICY**（若适用）：偏离带 **拒答** 或 **二次确认** **已文档化**

### 2.5 确认前限额（R3 · S7 前半）

- [ ] **FR-T09** 单笔/单日限额：**超限拒答**，**无** 类型 A

### 2.6 类型 A（Confirmation）

- [ ] **首张类型 A** **在** **R3 通过后**、**在** **首条** `call_exchange_write` **之前**
- [ ] 卡面 **含** 交易对/方向/价量（**§2.5.x** 下限）；**用户未确认** → **0** 写

### 2.7 执行（Execution）

- [ ] **S8** **仅** 子账户 scope **私有写**；**Gateway** 路径 **与** `design/api` **矩阵** 一致（**CC-P1-07** 实现仓抽检）
- [ ] **504/UNKNOWN**：**无** 对用户 **SUCCESS/已成交**（**SC-OBS03** 方向）

### 2.8 用户回执（Receipt · S9）

- [ ] **FR-T05** 摘要 **与** 交易所终局 **一致**；**在途/部成** **≠** **`executionId` 产品终局**（**S5.1.1**）

### 2.9 时间线与计费（Timeline · S10）

- [ ] **Timeline**（**FR-MC801**）：**自起票起** 有事件；**`spec_read` 序 < `confirmation.required` < 写工具事件**（**SC-OBS08/11**）
- [ ] **S10** 计费 **与** [`consume-and-bill`](../flows/consume-and-bill.md) **无结构性矛盾**

### 2.10 编排下限（横切）

- [ ] **`runtime-freeze` §3** 对应 **`scenarioId`** 小节：**依赖/并行/失败边** **未违反**
- [ ] **FR-AO06** 预算：**未** 无限工具环

---

## 3. 负例快检（须 0 通过写）

| # | 注入 | 预期 |
|---|------|------|
| N1 | 跳过类型 A 直写 | **拒** · **SC-TA01** |
| N2 | 缺数量进类型 A | **0** 类型 A · **`eval.skill.missing_qty_no_confirm`** |
| N3 | Adapter/解析层 **默认填充** **`quantity`/`quoteQty`**（非法 `source`） | **0** 写 · **INV-009** · **`WRITE_PARAMETER_CONTRACT`** |
| N4 | `spec_read` 在确认之后 | **契约失败** · **SC-OBS11** |
| N5 | Kill 开仍起新写 | **FR-T05** · **`eval.runtime.global_pause_blocks_new_write`** |

---

## 4. MR 描述粘贴块（所内 Runtime · 首节）

**完整 GitHub 稿（含 DoD / 依赖 / 负例）** → [`closure-internal-sprint.md` §3.1](../closure-internal-sprint.md#mr-rt-b4-pipeline)。

**短节选（工单摘要）**：

```markdown
## 管线对拍（写路径）· MR-RT-B4

- SSOT：domain-model §2～§4 · pipeline-walkthrough-checklist §2
- 主轴：`trade.spot.limit_order` · staging executionId: ___
- 勾选：§2.1～2.10（附时间线/日志链接）
- Eval：`eval.runtime.pipeline_write_order`（GWT 见 evals/pipeline-write-order.md）
- 观测：SC-OBS08 + SC-OBS11
- 全文粘贴：closure-internal-sprint.md §3.1
```

---

## 5. Admin 原型门卫（本 Git）

```bash
cd src/admin && npm test -- mock.timeline.contract
```

**映射**：`eval.obs.timeline_transition_contract` + **`eval.runtime.pipeline_write_order`**（Mock 下限）。

---

**文档版本**：0.1.1 · **维护**：产品 + Agent Runtime owner · **本版**：**INV-008/009** 勾选 · **N5**。承 0.1.0。
