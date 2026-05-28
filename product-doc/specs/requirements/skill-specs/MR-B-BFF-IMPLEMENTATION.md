# MR-B · Skill Runtime Publish · 所内实现清单（规格 / 原型已对齐）

**路径**：`specs/requirements/skill-specs/MR-B-BFF-IMPLEMENTATION.md`。

**用途**：供 **所内** prompt-management BFF 与 Agent Runtime 实现 `read_skill_operation_spec` **生产链路** 时的拆单、DoD 与验收。**契约 SSOT** 仍为 Git + OpenAPI。

**本规格仓已完成（可对评审）**：**规格对齐** + **Admin 原型对齐** — 见 [`requirements-closure.md` §3.6](./requirements-closure.md#36-runtime-publish--原型与规格对齐非生产实现)。**下文 §2～§7 为所内 MR，非本仓交付承诺。**

**同窗**：[`PUBLISH.md`](./PUBLISH.md) · [`requirements-closure.md` §4](./requirements-closure.md#4-b-阶段开放项不阻塞-a-但阻塞全闭环--对客-b) · [`admin/prompt-management.yaml`](../../openapi/admin/prompt-management.yaml)。

---

## 1. 本仓 · 原型与规格对齐（非生产实现）

| 交付物 | 层级 | 说明 |
|--------|------|------|
| **`published/runtime-bundle.json`** | 规格 | 11 篇 §1～§6 全文 + `specDigest` · CI `--check` · **供所内 import 参考** |
| **FR-TM06 / SC-TM-13～16、SC-PM-21** | 规格 | 控制台与 Prompt Publish 门禁条文 |
| **OpenAPI 草案** | 规格 | `skill-operation-spec-schemas` + `admin/skill-specs/*` |
| **`/ai/tool-registry` Demo** | 原型 | 登记 + 规范解析 + Publish **交互**（本地状态） |
| **Prompt `skillSpecRef` 提示** | 原型 | `SkillSpecRefPublishAlert` / `promptPublishGate` |
| **`schema/skill_operation_spec.v1.sql`** | 规格 | 所内 DDL **草案** |
| **`src/admin` 辅助代码** | 原型可选 | 含 localStorage、Vitest、**可选** Dev Mock — **不** 视为生产服务 |

**评审用原型**：`cd src/admin && npm run dev` → `/ai/tool-registry`、Prompt 编辑器。

---

## 2. 所内 MR 拆单（建议）

| MR | 范围 | 退出条件 |
|----|------|----------|
| **MR-B1 · 存储** | `skill_operation_spec` 表 + 生效指针 | 可从 `runtime-bundle.json` import；**禁止** 仅存摘要 |
| **MR-B2 · Admin API** | `GET/POST /api/v1/admin/skill-specs/*` | 与 OpenAPI **operationId** 一致；Publish 门禁 `check_skill_contract_complete` |
| **MR-B3 · Runtime 读** | `GET /api/v1/internal/skills/effective` | **仅 PUBLISHED**；未知版 **`PROMPT_SKILL_REF_INVALID`**；ETag |
| **MR-B4 · 编排接线** | `read_skill_operation_spec` | **FR-T11** · 类型 A 前加载全文 · `agent.skill.spec_read`；**步骤序** **对拍** [`Runtime/domain-model.md` §4](../Runtime/domain-model.md)（**禁止** 先确认后读规范） |
| **MR-B5 · Prompt 绑定** | Trading **`skillSpecRef`** Publish 校验 | **复现** **SC-PM-21**（原型见 `promptPublishGate`） |

---

## 3. 数据模型（最低字段）

见 [`schema/skill_operation_spec.v1.sql`](./schema/skill_operation_spec.v1.sql)。

---

## 4. API 行为（与 OpenAPI 对齐）

| operationId | 要点 |
|-------------|------|
| `listSkillOperationSpecs` | 列表含 `lifecycle`、`contractComplete` |
| `getSkillOperationSpec` | 当前 **effective** 指针摘要 |
| `getSkillOperationSpecVersions` | 履历降序 |
| `getSkillOperationSpecVersionBody` | 指定版 **全文** |
| `publishSkillOperationSpec` | **单调** `skillSpecVersion` · 全文快照 |
| `getEffectiveSkillOperationSpec` | Runtime 读 · **仅 PUBLISHED** |

**错误码**：[`prompt-management/functions` §5](../domains/admin/prompt-management/functions.md) — `PROMPT_SKILL_REF_INVALID` 等。

---

## 5. Runtime / 编排 DoD（所内）

1. 写路径 **`scenarioId` → `skillId` + `skillSpecVersion`**（[`trade-assistance` §4](../domains/agent/exchange-agent/trade-assistance.md)）。  
2. **类型 A 前** 加载规范全文（**不**内嵌进 Prompt 包 — [`rules`](../domains/admin/prompt-management/rules.md)）。  
3. 未发布 → **`PROMPT_SKILL_REF_INVALID`** / **FR-T05** 链。  
4. 观测 **`agent.skill.spec_read`**（[`observability` §2.1](../observability/overview.md)）。

---

## 6. 验收（SC-SK · 所内真跑）

| 编号 | Given | When | Then |
|------|--------|------|------|
| **SC-SK-01** | Git `contract-complete` | `POST …/publish` | DB **全文** + `specDigest` |
| **SC-SK-02** | 未发布版本 | `GET …/effective` | **`PROMPT_SKILL_REF_INVALID`** |
| **SC-SK-03** | 已发布 | 写路径类型 A 前 | 上下文含确认规则（抽检） |
| **SC-SK-04** | Trading 包 `skillSpecRef` | Prompt Publish | 引用版 **已 PUBLISHED**（**SC-PM-21**） |
| **SC-SK-05** | 已有多版 | 再 Publish | 单调；回退版 **400** |

**Eval**：[`evals/skill-contract.md`](../evals/skill-contract.md) P0 — **SK-B03** staging。

---

## 7. 写路径管线走读（MR-B4 同窗）

**勾选表**：[`Runtime/pipeline-walkthrough-checklist.md`](../Runtime/pipeline-walkthrough-checklist.md) **§2**。

**MR 首节粘贴**：同文 **§4**。

**验收 Eval**：[`evals/pipeline-write-order.md`](../evals/pipeline-write-order.md) · **`eval.runtime.pipeline_write_order`**（staging 真跑；本仓 Mock → `src/admin` **`mock.timeline.contract.test.ts`**）。**Gateway 负例** **同窗** **§9** **与** [`evals/scenarios.md`](../evals/scenarios.md) **`eval.gateway.*`**。

**所内 3 周节奏 · MR 粘贴全文** → [`closure-internal-sprint.md`](../closure-internal-sprint.md) **§1～§3**（**W1** 可与 **MR-B4** 并行）。

---

## 8. Import 与 CI 衔接（规格仓）

```bash
python3 specs/requirements/skill-specs/scripts/check_skill_contract_complete.py
node specs/requirements/skill-specs/scripts/build_runtime_publish_bundle.mjs --check
```


---

## 9. Execution Gateway · BFF 硬断言（Write Barrier）

**宿主 Law**：[`runtime-invariants` §0、INV-008～010](../Runtime/runtime-invariants.md)。**Taxonomy 出口**：[`WRITE_PARAMETER_CONTRACT`](../Runtime/runtime-error-taxonomy.md)；**`FR-T05`/`stableReason`** **所内登记表** **映射**。

**任一** **`call_exchange_write`** **或可等价** **`trading.exchange_private`** **Ingress** **之前**（**建议在** **Intent→Canonical 冻结后、HTTP 出站前**），**所内编排** **MUST** **顺序断言**：

| **断言标识**（实现字段名可对齐） | **须成立（摘要）** |
|----------------------------------|--------------------|
| **`required_fields_complete`** | **当前 **`skillId`** **之** **L0 `required`** **写槽齐备** · **已过** **业务/交易所规则校验**（**minNotional/stepSize/tick** **等**） |
| **`parameter_provenance_valid`** | **每笔** **经济敏感字段** **`provenance.source` ∈** **`user_input`** / **`confirmation_echo`** / **`runtime_read_balance`** / **`runtime_read_position`** / **`exchange_metadata_normalize`**（**INV-009**）；**黑名单** **`fallback_default`/`parser_autofill`/… → Stop** |
| **`confirmation_snapshot_matches_payload`** | **Canonical 载荷** **与** **用户已点确认** **之** **快照** **逐项一致** |
| **`validation_passed`** | **本条** **为** **`required_fields_complete`** **之** **再断言位** · **占位**：**任何** **校验器** **`validationStatus≠pass`** → **同上 Stop** |

**失败统一语义**：**不** **扩张** **交易所写**；**观测/`stableReason`** **归一** **`WRITE_PARAMETER_CONTRACT`**；**典型枚举** **`WRITE_PARAMS_INCOMPLETE`**、**`INVALID_PARAMETER_SOURCE`** — **同窗** **`runtime-invariants` §0**。

**本仓可选契约对签小样（TypeScript · 非量产实现 SSOT）**：[`executionGatewayWriteBarrier.ts`](../../../src/admin/src/productionRuntime/executionGatewayWriteBarrier.ts)（Gateway 四断言）、[`tradeWriteResolverGate.ts`](../../../src/admin/src/productionRuntime/tradeWriteResolverGate.ts)（闪兑与**现货限价**缺参列表、`build*ResolverOutput`、载货类型 A 门）、[`internalTradeResolverAdapter.ts`](../../../src/admin/src/productionRuntime/internalTradeResolverAdapter.ts)（`postInternalAgentOrchestrationTradeResolver`）、[`tradeResolverTypes.ts`](../../../src/admin/src/productionRuntime/tradeResolverTypes.ts)；**OpenAPI 同窗** [`openapi/components/orchestration-runtime-schemas.yaml`](../../openapi/components/orchestration-runtime-schemas.yaml)、[`openapi/internal/agent-orchestration.yaml`](../../openapi/internal/agent-orchestration.yaml)；索引 [`productionRuntime/README.md`](../../../src/admin/src/productionRuntime/README.md)。**正式 BFF/Runtime 由所内开发团队实现**；本段 **仅** 便于 MR 评审与表达与 Law 一致。

**抽检 Eval（须于 staging / 网关回归跑红）**：[`evals/scenarios.md`](../evals/scenarios.md) **`eval.gateway.*`** **五行** · **同窗** [`pipeline-write-order.md` §3](../evals/pipeline-write-order.md) **P-N4～P7**。

---

## 10. 上级

[`PUBLISH.md`](./PUBLISH.md) · [`closure-remaining` · OP-SKILL](../closure-remaining.md#cc-remaining-open-close-path) · [`Runtime/domain-model`](../Runtime/domain-model.md)

---

**文档版本**：1.3.0 · **维护**：产品 + Agent Runtime owner · **本版**：**§9 Gateway/BFF Write Barrier**。承 1.2.0。
