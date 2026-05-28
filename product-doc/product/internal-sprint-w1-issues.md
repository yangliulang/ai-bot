# 所内 W1 工单 · 复制即用（2026-05-27 批次）

**来源**：[`closure-internal-sprint.md` §2](../specs/requirements/closure-internal-sprint.md) · [`closure-work-item-templates.md`](../specs/requirements/closure-work-item-templates.md) · **自查批次 OP-MEM 增补**。

**规格仓 preflight**：`./scripts/closure-preflight.sh` → **OK**（含 `runtime-bundle.json` 同步）

**MR 全文粘贴** → `closure-internal-sprint.md` **§3**；**staging 证据** → [`closure-staging-evidence-log.md`](../specs/requirements/closure-staging-evidence-log.md)

---

## W1-RT · MR-RT-B4 编排接线

**标题**：`[W1][Runtime] MR-RT-B4 — 写路径管线 read_skill → 确认 → 写`

```text
阶段：B（实现）
规格 SSOT（产品文档仓 · trading-agent Git）：
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

## W1-MEM · OP-MEM Memory / 澄清 stale+Resume（与 RT-B4 并行 · 高优）

**标题**：`[W1][Runtime] MR-MEM-01 — STM §2.3/§14.6/§16 + Telegram 澄清全序`

```text
阶段：B（实现）
规格 SSOT：
- specs/requirements/domains/agent/agent-orchestration/clarify-session.md v1.6
- specs/requirements/domains/agent/agent-orchestration/session-concurrency-policy.md v1.0
- specs/requirements/Runtime/memory-runtime.md §14.6～§16
- specs/requirements/design/memory-runtime-injection.md v0.5
- specs/requirements/domains/agent/telegram/overview.md §2.6.1
- specs/openapi/components/memory-runtime-schemas.yaml

实现 DoD（摘要）：
- 每条 inbound：clarify-session §2.3 重意图（寒暄/只读/放弃/stale）
- session-concurrency §2 inbound 串行/合并 · §3 在途写≤1 · §5 D-1
- idle/TTL 先达 → lifecycleState=stale + WarmExecutionEpisode
- ambiguous → ResumeClassifier（conf≥0.75）· episodePickReason
- §16 四原则硬闸 · §2.5 Normative 去重
- §1.1：pending_confirm 存活时 stale 不得废类型 A
- Webhook update_id 幂等 + cl:* / cf:* 分层（Telegram §2.6.1）
- keys §2.1 + §2.2 SESSION_* 进入 Execution 步 2 configSnapshot

验收（所内 CI · P0 eval 须绿）：
- eval.memory.stm_governance_regression
- eval.memory.idle_default_stale
- eval.memory.resume_classifier_gate
- eval.memory.resume_classifier_multi_episode
- eval.clarify.abandon_on_cancel / read_interrupts_write / no_internal_jargon
- eval.session.inbound_serial_no_double_parse / second_write_while_confirm / new_write_blocked_on_unknown
- eval.runtime.telegram_update_idempotent

用户旅程：
- product/journey-validation-checklist.md JV-13 + JV-14 逐步全 Pass

依赖：
- 可与 MR-RT-B4 并行；Telegram BFF 同窗 MR 更佳

证据：
- executionId ______ · agent.memory.resume_classified 样例 ______
```

---

## W1-SK-B1 · 表 + import

**标题**：`[W1][BFF] SK-B01 — skill_operation_spec 表 + runtime-bundle import`

```text
DoD：
- 表结构见 skill-specs/schema/skill_operation_spec.v1.sql
- 可从 specs/.../published/runtime-bundle.json 导入全文（非摘要）
- import 脚本或一次性 migration 附在 MR

参考：MR-B-BFF-IMPLEMENTATION.md §2 MR-B1
阻塞：无（可与 MR-RT-B4 / MR-MEM-01 并行）
```

---

## W1-SK-B2 · Admin Publish API

**标题**：`[W1][BFF] SK-B02 — admin/skill-specs Publish API + contract gate`

```text
DoD：
- OpenAPI operationId 与 specs/openapi/admin/prompt-management.yaml 一致
- Publish 前跑 check_skill_contract_complete.py（或等价 CI）
- SC-SK-01～05 可在 staging 演示（至少 01/05）

参考：MR-B-BFF-IMPLEMENTATION.md §2 MR-B2
依赖：SK-B01
```

---

## W1-BILL-B1 · 轨 B S2 宿主（可与 W1 并行）

**标题**：`[W1][BFF] MR-BILL-B1 — S2 evaluateCommerceEntitlement + staging 探针`

```text
DoD：
- runConsumeAndBillS2CommerceGate 宿主接线
- scripts/staging-mr-bill-probe.sh 在目标环境 exit=0
- 回填 closure-staging-evidence-log.md §2.4

参考：closure-internal-sprint.md §3.7
JV 关联：JV-05
```

---

## W1 完成定义（复制到冲刺看板）

- [ ] 三张 MR 已开：**MR-RT-B4** · **MR-MEM-01** · **SK-B1/B2**（BILL-B1 可选并行）
- [ ] `pipeline-walkthrough-checklist` §2 **≥80%**
- [ ] **JV-13** checklist **纸面或 staging 首跑**（允许 Fail 登记缺陷）
- [ ] `closure-staging-evidence-log` **§2 有 executionId**

---

**文档版本**：1.0.0 · **维护**：产品 + 收口 owner
