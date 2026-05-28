# 所内工单 / Issue 模板（复制即用）

**路径**：`specs/requirements/closure-work-item-templates.md`。

**用途**：在 **Jira / Linear / GitHub Issues** 建单时 **复制标题+正文**。**MR 技术全文** 仍以 [`closure-internal-sprint.md`](closure-internal-sprint.md) **§3** 为准。

---

## W1-RT · MR-RT-B4 编排接线

**标题**：`[W1][Runtime] MR-RT-B4 — 写路径管线 read_skill → 确认 → 写`

**正文**：

```text
阶段：B（实现）
规格 SSOT（产品文档仓）：
- specs/requirements/Runtime/domain-model.md
- specs/requirements/Runtime/pipeline-walkthrough-checklist.md
- specs/requirements/evals/pipeline-write-order.md

验收：
- trade.spot.limit_order staging 走读 checklist §2 ≥80%
- eval.runtime.pipeline_write_order 正例
- SC-OBS11 / SC-OBS08 时间线可导出

依赖：
- 可先 Mock GET …/skills/effective；SK-B3 合并后撤 Mock

MR 描述：复制 closure-internal-sprint.md §3.1 全文

证据回填：closure-staging-evidence-log.md §2
```

---

## W1-SK-B1 · 表 + import

**标题**：`[W1][BFF] SK-B01 — skill_operation_spec 表 + runtime-bundle import`

**正文**：

```text
DoD：
- 表结构见 skill-specs/schema/skill_operation_spec.v1.sql
- 可从 specs/.../published/runtime-bundle.json 导入全文（非摘要）
- import 脚本或一次性 migration 附在 MR

参考：MR-B-BFF-IMPLEMENTATION.md §2 MR-B1
阻塞：无（可与 MR-RT-B4 并行）
```

---

## W1-SK-B2 · Admin Publish API

**标题**：`[W1][BFF] SK-B02 — admin/skill-specs Publish API + contract gate`

**正文**：

```text
DoD：
- OpenAPI operationId 与 specs/openapi/admin/prompt-management.yaml 一致
- Publish 前跑 check_skill_contract_complete.py（或等价 CI）
- SC-SK-01～05 可在 staging 演示（至少 01/05）

参考：MR-B-BFF-IMPLEMENTATION.md §2 MR-B2
依赖：SK-B01
```

---

## W1-MEM · Memory / 澄清 stale+Resume（OP-MEM · 高优）

**标题**：`[W1][Runtime] MR-MEM-01 — STM §2.3/§14.6/§16 + Telegram 澄清全序`

**正文**：

```text
阶段：B（实现）
规格 SSOT：
- clarify-session.md v1.6 · session-concurrency-policy v1.0 · memory-runtime §14.6～§16
- design/memory-runtime-injection v0.5 · telegram/overview §2.6.1

DoD（摘要）：
- §2.3 每条 inbound 重意图 · §14.6 stale+Resume · §16 四原则 · §1.1 类型A×stale
- session-concurrency §2～§6 inbound 队列 · 在途写≤1 · D-1 · 改单链
- Webhook 幂等 · keys §2.1 + §2.2 SESSION_* configSnapshot

P0 eval 须绿：stm_governance_regression · idle_default_stale · resume_classifier_* · clarify.* · eval.session.* P0

用户旅程：product/journey-validation-checklist.md JV-13 + JV-14 全 Pass

完整粘贴块：product/internal-sprint-w1-issues.md § W1-MEM
阻塞：无（与 MR-RT-B4 并行）
```

---

## W2-SK-B3 · effective 读

**标题**：`[W2][BFF] SK-B03 — GET internal/skills/effective（仅 PUBLISHED）`

**正文**：

```text
DoD：
- 未发布 → PROMPT_SKILL_REF_INVALID
- ETag / 缓存策略所内终裁但须文档化
- 合并后通知 Runtime 撤 Mock

参考：MR-B-BFF-IMPLEMENTATION.md §2 MR-B3
```

---

## W2-GW · Gateway

**标题**：`[W2][Gateway] MR-GW-01 — CC-P1-07 Canonical 写路径`

**正文**：

```text
规格：design/canonical-trading-model.md、ADR-004
联调：trade.spot.limit_order 与 MR-RT-B4 同窗 staging
MR 描述：closure-internal-sprint.md §3.4
```

---

## W3-P0 · Hosted

**标题**：`[W3][Ops] CC-P0-01 — OpenAPI Hosted 或 release-* tag`

**正文**：

```text
勾选：specs/openapi/HOSTED-ROLLOUT-CHECKLIST.md
MR 描述：contract-closure.md §3.4（CC_P0_ID=CC-P0-01）
```

---

**文档版本**：0.1.0 · **维护**：产品 + 收口 owner
