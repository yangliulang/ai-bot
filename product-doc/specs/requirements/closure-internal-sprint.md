# 所内执行冲刺 · 派工与 MR 粘贴稿（≈2 人 · 3 周）

**路径**：`specs/requirements/closure-internal-sprint.md`。

**用途**：把 **[`closure-remaining` §7.5～§7.6](closure-remaining.md#cc-remaining-open-close-path)** **落成** **可开工单**。**不** 替代 [`contract-closure.md`](contract-closure.md) **DoD**；**P0 全稿** **仍** **[§3.4](contract-closure.md#cc-p0-mr-github-full)**。

**规格仓 A 已闭合**：[`Runtime/domain-model.md`](Runtime/domain-model.md) · [`pipeline-walkthrough-checklist.md`](Runtime/pipeline-walkthrough-checklist.md) · Admin **`npm test -- mock.timeline.contract`**。

---

## 1. 三周节奏（建议）

| 周 | 轨道 A（Runtime / 编排） | 轨道 B（BFF / Publish / Registry） | 共同出口 |
|:--:|--------------------------|-------------------------------------|----------|
| **W1** | **MR-RT-B4** 编排接线（可 **Mock** `effective`） | **MR-SK-B1** 表 + import bundle · **MR-SK-B2** Admin API | staging **`trade.spot.limit_order`** **走读 §2 勾选 ≥80%** |
| **W2** | **Gateway** 切片（**CC-P1-07**）· **R1～R3** 门禁联调 | **MR-SK-B3** `GET …/effective` · **MR-SK-B5** Prompt `skillSpecRef` | **`eval.runtime.pipeline_write_order`** **真跑 1 条** |
| **W3** | **runtime-freeze §3** 轨迹/单测 · **OP-AO3** 证据 | **SK-B03** `eval.skill.*` staging · **MR-E** 幂等（可并行） | **P0-01** Hosted/tag **或** **release-*** **首条**（运维+实现） |

**W4（可选）**：**MR-PROMPT-B**（CC-P1-04）· **Memory/NAR** 实现 Eval 真跑。

**并行纪律**：**勿** 单 MR 堆 **P0+P1+Runtime**；**每 MR 首节** **标** **A 或 B**（[`contract-closure` §3.0](contract-closure.md#cc-p1-doc-vs-b)）。

**完成度一览** → [`closure-completion-matrix.md`](closure-completion-matrix.md)。

---

## 2. 工单勾选（复制到 Jira/Linear）

**Issue 标题+摘要** → [`closure-work-item-templates.md`](closure-work-item-templates.md) · **staging 证据回填** → [`closure-staging-evidence-log.md`](closure-staging-evidence-log.md)。

**合并前自检（规格仓）** → 仓库根 **`scripts/closure-preflight.sh`**。

### W1

- [ ] **MR-RT-B4** — 正文 **[§3.1](#mr-rt-b4-pipeline)** · 走读 **[`pipeline-walkthrough-checklist` §2](Runtime/pipeline-walkthrough-checklist.md)** · 证据 **[`closure-staging-evidence-log` §2](closure-staging-evidence-log.md)**
- [ ] **MR-MEM-01** — **OP-MEM** · [`clarify-session`](domains/agent/agent-orchestration/clarify-session.md) v1.6 · P0 eval · **JV-13** — **粘贴块** [`product/internal-sprint-w1-issues.md`](../../product/internal-sprint-w1-issues.md) · **勾选表** [`journey-validation-checklist.md`](../../product/journey-validation-checklist.md)
- [ ] **MR-SK-B1** — [`MR-B-BFF-IMPLEMENTATION` §2](skill-specs/MR-B-BFF-IMPLEMENTATION.md) · `runtime-bundle.json` import
- [ ] **MR-SK-B2** — OpenAPI `admin/skill-specs/*` 与 **Publish 门禁** 脚本

### W2

- [ ] **MR-SK-B3** — `GET /api/v1/internal/skills/effective` **仅 PUBLISHED**
- [ ] **MR-GW-01** — Execution Gateway **DoD B**（所内工程仓 · **CC-P1-07**）
- [ ] **Eval** — **`eval.runtime.pipeline_write_order`** staging 证据（时间线导出链接 ______）

### W3

- [ ] **MR-P0-01** — **[contract-closure §3.4](contract-closure.md#cc-p0-mr-github-full)** · Hosted **或** tag URL ______
- [ ] **SK-B03** — [`evals/skill-contract.md`](evals/skill-contract.md) P0 **真跑** ≥4 条
- [ ] **回填** — [`closure-remaining` §7.6 B 组](closure-remaining.md#cc-closure-exec-checklist) **OP-AO3 / OP-SKILL**

### Billing · Phase 2（轨 B · 同窗本仓 [`productionRuntime`](../../src/admin/src/productionRuntime)）

- [ ] **MR-BILL-B1** — 正文 **[§3.7](#mr-bill-b1)** · **`runConsumeAndBillS2CommerceGate`** · staging ______
- [ ] **MR-BILL-B2** — 正文 **[§3.8](#mr-bill-b2)** · **`runConsumeAndBillS5Settlement`** · staging ______

---

<a id="mr-rt-b4-pipeline"></a>

## 3. MR 粘贴稿

### 3.1 MR-RT-B4 · 写路径管线（所内 Agent Runtime）

**建议标题**：`feat(runtime): write-path pipeline — read_skill before confirm — MR-B4`

**建议仓库**：所内 **Agent Runtime**（**非** 本规格仓）。

```markdown
## 所内 Runtime · MR-B4 · 写路径管线对拍

### 阶段
- [x] **B · 实现 MR**（**不** 宣称 P0 全关 / **不** 升格 `spec.md` §5.1）

### 规格 SSOT（产品文档仓）
- [`domain-model.md`](https://github.com/…/specs/requirements/Runtime/domain-model.md) §2～§4
- [`pipeline-walkthrough-checklist.md`](https://github.com/…/specs/requirements/Runtime/pipeline-walkthrough-checklist.md) §2
- [`eval.runtime.pipeline_write_order`](https://github.com/…/specs/requirements/evals/pipeline-write-order.md)

### 实现 DoD
- [ ] **`scenarioId=trade.spot.limit_order`** 写路径：**S3 FR-T02** → **S5 executionId** → **read_skill** → **S6 槽位** → **S7 限额+类型 A** → **S8 写**
- [ ] **`agent.skill.spec_read`**：`phase=success`，**早于** `confirmation.required`（**SC-OBS11**）
- [ ] **风险闸 R1～R3** **无** 推迟到确认之后（见 domain-model §2）
- [ ] **类型 A 前** **无** `call_exchange_write`（**ADR-001** / **SC-TA01** 负例）
- [ ] **504/UNKNOWN** **无** 对用户 SUCCESS 话术（**SC-OBS03** 方向）
- [ ] **主态边** 时间线可还原 Trigger（**SC-OBS08**）

### 走读证据（staging）
- **executionId**：`________________`
- **时间线导出 / 日志**：`________________`
- **走读勾选**：pipeline-walkthrough-checklist §2.1～2.10（附截图或链接）

### Eval
- [ ] **`eval.runtime.pipeline_write_order`** §2 正例 **通过**
- [ ] 负例 **P-N1 / P-N2** **拒绝**（见 pipeline-write-order §3）

### 依赖 / 阻塞
- [ ] **MR-SK-B3** `GET …/effective` **已合并** **或** **本 MR 注明 Mock 范围与截止日**
- [ ] **CC-P1-07** Gateway：**本 MR 仅编排序** **或** **同窗 Gateway MR**：`________________`

### 邻域第五步
- 编排 **对拍** [`runtime-freeze` §3.1](…)（限价写）；**Walkthrough** Goal-PIPE / `trade.spot.limit_order`
```

---

### 3.2 MR-SK-B1～B3 · Skill Publish 链（所内 BFF）

**建议标题**：`feat(bff): skill operation spec publish + effective read — SK-B01～B03`

**规格 SSOT**：[`MR-B-BFF-IMPLEMENTATION.md`](skill-specs/MR-B-BFF-IMPLEMENTATION.md) **§2**。

```markdown
## Skill Runtime Publish · SK-B01～B03

### 阶段
- [x] **B · 实现**（规格+原型 A 已在 Git：`requirements-closure` §3）

### DoD（按 MR 拆或同窗）
- [ ] **B1** `skill_operation_spec` 表 + **全文** import（`runtime-bundle.json`）
- [ ] **B2** `POST/GET admin/skill-specs/*` · `check_skill_contract_complete` 门禁
- [ ] **B3** `GET internal/skills/effective` · **仅 PUBLISHED** · `PROMPT_SKILL_REF_INVALID` · ETag

### 验收 SC-SK
- [ ] **SC-SK-01～05**（见 MR-B §6）· staging 链接 ______

### 阻塞 Runtime
- [ ] **合并后** 通知 Runtime 轨 **撤 Mock** · 接 **MR-RT-B4**
```

---

### 3.3 MR-P0-01 · Hosted / tag（运维 + 实现）

**勿重写** — **整段复制** [`contract-closure` §3.4](contract-closure.md#cc-p0-mr-github-full)，**`【CC_P0_ID】`= CC-P0-01**。

**运维勾选表** → [`openapi/HOSTED-ROLLOUT-CHECKLIST.md`](../openapi/HOSTED-ROLLOUT-CHECKLIST.md)。

**建议排期**：**W3**（**不阻塞** W1 **管线走读**）。

---

<a id="mr-gw-gateway"></a>

### 3.4 MR-GW-01 · Execution Gateway（CC-P1-07 · 所内工程仓）

**建议标题**：`feat(gateway): canonical trading execution — CC-P1-07`

**规格 SSOT**：[`canonical-trading-model.md`](../../design/canonical-trading-model.md)、[`ADR-004`](../../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)。

```markdown
## Gateway · CC-P1-07 · DoD B

### 阶段
- [x] **B · 实现**（文档 A 已在规格仓）

### DoD
- [ ] **Intent → Canonical → Gateway → Adapter** 对拍 **trade-assistance` §2.6**
- [ ] **写路径** **仅** **矩阵已冻结 PATH** + **openapi-ai pin**
- [ ] **与 MR-RT-B4** **同窗联调**：`trade.spot.limit_order` **staging 一笔**
- [ ] **504/UNKNOWN** **不** 向上冒泡为 SUCCESS

### 证据
- 实现 MR：______
- PATH 断言日志 / 集成测：______
- [`requirements-review` §7.5](../../../product/requirements-review.md#cc-adr004-review-checklist) 勾选

### 依赖
- [ ] **SK-B03** effective **或** 编排 Mock 范围已声明
```

---

### 3.5 MR-PROMPT-B · Prompt Runtime（CC-P1-04）

**建议标题**：`feat(runtime): prompt assembly chain — CC-P1-04`

**派工** → [`closure-remaining` §7.2～§7.4](closure-remaining.md#cc-ac09-closure-matrix)。

```markdown
## Prompt Runtime · CC-P1-04

### DoD（节选）
- [ ] **09a～09e**：SYSTEM→…→User 拼装 + Tool JSON Schema + Few-shot + variableSchema
- [ ] **09f**：denylist / 修订号 Publish 闸
- [ ] **SC-OBS04**：`resolvedPromptBinding` 可 join
- [ ] **functions` §1.4** 核对表 MR 勾选
- [ ] （若宣称 B）Hosted/生产 Prompt API 实测

### 证据链
- MR：______
- 样例 executionId + 绑定快照：______
```

---

### 3.6 OP-MEM / OP-NAR（W4 · 可与 W2 并行）

| OP | Eval 真跑 | 规格 |
|----|-----------|------|
| **OP-MEM** | `eval.memory.session_clear_stm` 等 | [`evals/memory-runtime.md`](evals/memory-runtime.md) |
| **OP-NAR** | `eval.market.narrative_*` | [`evals/market-narrative.md`](evals/market-narrative.md) |

---

<a id="mr-bill-b1"></a>

### 3.7 MR-BILL-B1 · Phase 2 · S2 商业额度门禁

**建议标题**：`feat(billing): commerce entitlement S2 gate — MR-BILL-B1`

**规格 SSOT**：[`consume-and-bill.md`](flows/consume-and-bill.md) **S2** · [`commerce-model.md`](domains/admin/billing-management/commerce-model.md) · [`internal/billing-entitlements.yaml`](../openapi/internal/billing-entitlements.yaml)。

**对照小样（规格仓）**：`src/admin/src/productionRuntime/consumptionBillingHost.ts` · `billingCapabilityMap.ts` · `commerceEntitlementS2Evaluate.ts` · **`writePathConsumeAndBillOrchestrator.ts`**（**`runWritePathConsumeAndBill`** · S2→S5 一键）。

```markdown
## Billing · Phase 2 · MR-BILL-B1 · S2 宿主接线

### 阶段
- [x] **B · 实现 MR**（**不** 扩写 **CC-P0-03** · **不** 对外宣称轨 B 生产已关单）

### DoD
- [ ] **`PHASE2_COMMERCE_RAILS_ENABLED`** 配置注入（默认 **false**）
- [ ] **`INTERNAL_BILLING_BASE_URL`** + mTLS/内网 **Headers**（若架构要求）
- [ ] **FR-T02 序内**：**`scenarioId → capabilitySkuId`**（**`BILLING_CAPABILITY_MAP`** 真源）→ **`GET …/entitlements/balance`** → **remaining ≤ 0 阻断**
- [ ] **阻断** 映射 **`FR-T05`** / **`stableReason=BUDGET_OR_QUOTA`**（或 Taxonomy 同窗名）
- [ ] **HTTP 5xx/DNS** **不** 静默放行（所内策略 + Runbook 一句）

### 验收
- [ ] **SC-B21** staging：**Capability 剩余 0** → **新可计费写被拦** + **升级/买包引导**
- [ ] **开关关**：**零 balance 请求**（**S2 跳过轨 B 门禁** — **非**「回退轨 A 扣 Agent 费」；**所内 Runbook** 一句）

### 证据
- staging **userId** + **scenarioId**：`________________`
- balance 响应截屏 / 日志：`________________`
- **MR URL**：`________________`
```

---

<a id="mr-bill-b2"></a>

### 3.8 MR-BILL-B2 · Phase 2 · S5 轨 B 核销

**建议标题**：`feat(billing): consumption settlement entitlement debit — MR-BILL-B2`

**规格 SSOT**：[`commerce-model.md` §4～§5.1](domains/admin/billing-management/commerce-model.md) · **SC-B20** · **FR-B21**。

**对照小样**：`consumptionBillingHost.ts` · `commerceEntitlementS5Settle.ts` · `internalBillingEntitlementsAdapter.ts` · **`writePathConsumeAndBillOrchestrator.ts`**。

```markdown
## Billing · Phase 2 · MR-BILL-B2 · S5 宿主接线

### 阶段
- [x] **B · 实现 MR**（**须** **`contract-closure` §8** 登记 **轨 B MR** 后 **方可** 生产宣称）

### DoD
- [ ] **S4 终局后**：**`POST …/entitlements/debit`**（**`{executionId}:rail-b:entitlement-debit`**）→ **SUCCESS** → **`billingTraceId`**
- [ ] **debit `INSUFFICIENT`** → **终止** · **不得** **扣 Token / charge**（**FR-B19 / FR-B21 / SC-B20**）
- [ ] **重复回调** **安全重放** **得等价** **`billingTraceId`/状态**
- [ ] **观测**：**核销 trace** **可 join** **`executionId`**（**D-5**）

### 验收
- [ ] **SC-B20** staging **≥1** **`executionId`**
- [ ] **仅 B** 路径 **日志样例** **≥1**

### 证据
- **executionId**：`________________`
- debit 流水 join：`________________`
- **MR URL**：`________________`
```

---

## 4. 合并后回填（规格仓）

| 动作 | 位置 |
|------|------|
| 勾选 **OP-AO3 / OP-SKILL 所内** | [`closure-remaining` §7.6 B 组](closure-remaining.md#cc-closure-exec-checklist) |
| **§8 顶行** 登记 MR URL | [`contract-closure` §8](contract-closure.md) |
| **Hosted/tag** | [`openapi/README`](../openapi/README.md) |
| **走读缺口行** 改「已闭环」 | [`closure-remaining` §7.1](closure-remaining.md#cc-remaining-gap-paste) |

---

## 5. 上级索引

| 文档 | 关系 |
|------|------|
| [`closure-remaining.md`](closure-remaining.md) | §7.6 总勾选 |
| [`skill-specs/MR-B-BFF-IMPLEMENTATION.md`](skill-specs/MR-B-BFF-IMPLEMENTATION.md) | B1～B5 技术拆单 |
| [`contract-closure.md`](contract-closure.md) | P0/P1 DoD 主表 |
| [`LITE-MODE.md`](LITE-MODE.md) | 小团队日常节奏 |

---

**文档版本**：0.1.1 · **维护**：产品 + 收口 owner · **本版**：**§3.7～3.8 MR-BILL-B1/B2 粘贴稿**。**承** **0.1.0**。
