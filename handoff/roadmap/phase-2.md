# Phase 2 — 主链闭环、Publish 生效与契约收口（ChainUp）

> 产品 Agent 维护。backlog 对齐 `product-doc/product/roadmap.md` **P0-3 / 阶段 A3** 与 [`closure-completion-matrix`](../../product-doc/specs/requirements/closure-completion-matrix.md) **P‑04～P‑08**、**W1**。  
> **存量已实现**见 [`inventory.md`](../product/inventory.md) §2（本表 **不** 重复标 `planned`）。Phase-1 六项功能包均已 **done**（见 [`phase-1.md`](phase-1.md)）。

## 阶段目标

1. 推进 **端到端写路径主链**（**read_skill** 先于类型 A、管线事件序可验收），对齐 closure **P‑04**、**P‑05** 与 W1 **MR-RT-B4**。
2. 落地 **Skill Publish 生效链**（bundle 发布 → 运行时仅读 **PUBLISHED** effective），对齐 **P‑07** 与 W1 **SK-B1～B3**。
3. 收口 **已实现能力的契约/验收追溯**（对账 HTTP、条件单查撤、合约撤单）与 **Admin AI 网关开关**（Phase-1 FE 债）；为 **P‑08** staging 走读预留 **P2** 包。

## 对齐说明

**对照真源**：[`product-doc/product/roadmap.md`](../../product-doc/product/roadmap.md)（2026-05-27 批次 · L1～L7 快照 · W1 硬排序见 closure 矩阵 §0）、[`inventory.md`](../product/inventory.md) §2/§5/§6、[`closure-completion-matrix`](../../product-doc/specs/requirements/closure-completion-matrix.md) §1～§3/§5。

**文档变更摘要（本轮回对齐）**：

- PRD 篇首 **计费轨 B / Admin·Web IA 清扫（2026-05-26～27）** 与 **OP-BILL** 归属 **Phase-4**（`backlog.yaml` 四项 `queued`），**不**纳入 Phase-2 范围（本阶段原规划已排除计费真实入账）。
- PRD **Prompt 治理 IA + 16 包正文（2026-05-27）**、**运营台 reconciliation §0**（工具登记 / 执行协查 / 实例）为 **Admin 原型对账** 横切 — Phase-2 已交付 **Publish 生效链** 与 **九场景网关 UI**；**深化 Prompt Inspector / 16 包正文** 非本阶段原 backlog，**推迟** Phase-4+ 或所内 MR。
- **矩阵 §1 P‑06/P‑07/P‑08 仍为黄** = **所内 Gateway / SK-B DB·BFF / MR-RT-B4 联调余量**；本仓七项 **done** 与 PRD **无条文冲突**，升格须 **所内 MR + staging**，**不**默认 reopen 原 ID。
- **W2～W3 所内收口**（Eval 管线 · Prompt 写路径 · Skill eval · Registry 幂等 · Memory STM）已由 **[`phase-3.md`](phase-3.md)** 承接 — 属 Phase-2 主链 **自然延伸**，**非** Phase-2 返工。

| 原项（功能 ID） | 处置 | 新功能 ID | 理由 |
|-----------------|------|-----------|------|
| 2026-05-27--runtime-write-path-pipeline | **保留** · done | — | 对齐 **P‑04/P‑05** · W1 **MR-RT-B4**；矩阵 **绿**；Phase-3 `pipeline-eval-orchestration-align` 补 Eval staging |
| 2026-05-27--skill-publish-effective | **保留** · done | — | 对齐 **P‑07** · SK-B1～B3/B5；矩阵 **黄** = 所内 DB/BFF 余量；Phase-3 `skill-contract-eval-staging` 补 eval |
| 2026-05-27--admin-ai-settings-gateway-ui | **保留** · done | — | Phase-1 FE 债已清 · `/ai-settings?tab=runtime`；**≠** Prompt 16 包 Inspector（PRD 2026-05-27 横切） |
| 2026-05-26--trading-reconcile | **保留** · done | — | 对齐 **P‑03** / Recovery · Step §6 契约追溯 |
| 2026-05-26--condition-order-list-cancel | **保留** · done | — | Step 2.5 已实现 API 契约收口 |
| 2026-05-26--futures-cancel | **保留** · done | — | Step 2.3 已实现 cancel 契约收口 |
| 2026-05-27--telegram-write-path-staging | **保留** · done | — | 对齐 **P‑08** · `exec-3d132b3ad3ad44` evidence；矩阵 **黄** = Gateway 联调所内 |
| OP-BILL · Commerce S2/S5 · `me/commerce` | **推迟** | Phase-4 四项（`backlog.yaml` queued） | PRD 横切计费 **2026-05-26～27** · inventory §5 非 Phase-2 范围 |
| Prompt 16 包 · Canonical Inspector · Admin Billing 页 | **推迟** | Phase-4+ / 所内 | PRD 2026-05-27 IA 对账 · 非 Phase-2 原七项 |
| P-06 Gateway · CC-P0 红项 | **移除**（本阶段范围外） | — | 所内工程仓 / 运维 · inventory §5 |

**返工项**：无。七项交付与当前 PRD **无条文冲突**；矩阵 **黄** 项与 Prompt/Billing IA 深化须 **后续 phase 或所内 MR** 承接，**不**在 Phase-2 新建 `-v2` ID。

## 功能 backlog

| 优先级 | 功能 ID | 功能名 | 状态 | 功能包路径 | 备注 |
|--------|---------|--------|------|------------|------|
| P0 | 2026-05-27--runtime-write-path-pipeline | 写路径管线（read_skill + 事件序） | done | handoff/features/2026-05-27--runtime-write-path-pipeline/ | **P‑04** · **P‑05** · W1 **MR-RT-B4**；含 TG/时间线；**含页面：否** · 2026-05-27 收口 |
| P0 | 2026-05-27--skill-publish-effective | Skill Publish 生效链 | done | handoff/features/2026-05-27--skill-publish-effective/ | **P‑07** · W1 **SK-B1～B3/B5**；**含页面：是** · 2026-05-26 收口 |
| P1 | 2026-05-27--admin-ai-settings-gateway-ui | Admin AI 网关开关 UI | done | handoff/features/2026-05-27--admin-ai-settings-gateway-ui/ | Phase-1 FE 债 · `/ai-settings?tab=runtime` 网关策略 · 2026-05-27 收口 |
| P1 | 2026-05-26--trading-reconcile | 504 对账契约收口 | done | handoff/features/2026-05-26--trading-reconcile/ | **P‑03** / Recovery；**含页面：否** · 2026-05-26 收口 |
| P1 | 2026-05-26--condition-order-list-cancel | 条件单查撤契约收口 | done | handoff/features/2026-05-26--condition-order-list-cancel/ | Step 2.5 · **含页面：否** · 2026-05-28 收口 |
| P1 | 2026-05-26--futures-cancel | 合约撤单契约收口 | done | handoff/features/2026-05-26--futures-cancel/ | Step 2.3 · **含页面：否** · 2026-05-28 收口 |
| P2 | 2026-05-27--telegram-write-path-staging | 主链 TG 写路径 staging 证据 | done | handoff/features/2026-05-27--telegram-write-path-staging/ | **P‑08** · `exec-3d132b3ad3ad44` · evidence 已填 · 2026-05-26 收口 |

功能 ID 格式：`YYYY-MM-DD--kebab-slug`（双横线 `--`）。

### 状态说明

| 状态 | 含义 |
|------|------|
| `planned` | 未建包或未 contract_ready |
| `contract_ready` | 可交后端 |
| `in_dev` | 开发中 |
| `done` | 功能包 phase 为 done |

### 指挥官下一步

**Phase-2 已全部 done**（对齐后无新增 planned）。当前迭代在 **Phase-4**（OP-BILL · `backlog.yaml` 四项 `queued`）：

```text
/pipeline-product-plan
```

（附 `@product-doc/product/roadmap.md`；或 `/pipeline-product-phase-realign phase-4` 对齐 OP-BILL）

Phase-2 后续延伸见 **[`phase-3.md`](phase-3.md)**（W2～W3 五项 **done**）。

## 依赖与顺序

```text
首包（二选一，勿并行 contract）：
  2026-05-26--trading-reconcile              ← 快收口（P1 · 无依赖）
  2026-05-27--runtime-write-path-pipeline    ← 主链 P0（依赖 Phase-1 504 扩面 done）

P0 可并行开发（定稿仍建议一次一个）：
  2026-05-27--runtime-write-path-pipeline
  2026-05-27--skill-publish-effective        ← 依赖 Prompt/编排存量，与管线勿混单包

P1（契约三件套可并行；与 P0 定稿错开）：
  2026-05-26--trading-reconcile
  2026-05-26--condition-order-list-cancel
  2026-05-26--futures-cancel
  2026-05-27--admin-ai-settings-gateway-ui   ← 依赖 nlu-llm-strategy · telegram-llm-narrate done

P2（须在 runtime 管线至少 contract_ready 之后）：
  2026-05-27--telegram-write-path-staging → 2026-05-27--runtime-write-path-pipeline
```

**并行纪律**（`closure-internal-sprint`）：单 MR/功能包 **勿**堆 P0 管线 + Publish + Gateway；**P‑06 Gateway 核心**不在本阶段 backlog。

绑定/登录、504 扩面、Observability 列表等前置已在 inventory §2，brief 中写清即可，**不重复建包**。

## 本阶段不做

见 [`inventory.md`](../product/inventory.md) §5，并补充：

- **OP-BILL** · **Commerce S2/S5** · **`me/commerce`** — **Phase-4**（`backlog.yaml` 四项 `queued`）
- **roadmap P0-1 / P0-2** — 纯 specs / 文档冻结项
- **P-06 Gateway 主实现**（`call_exchange_write` · 所内工程仓 · **CC-P1-07**）— **deferred**
- **CC 红项**（Hosted rollout、矩阵延期终裁、账务三线、财务专户、D-5/D-7 等）— 须所内/运维
- **Prompt 16 包 Inspector / Admin Billing 运营页** — PRD 2026-05-27 横切 · **非** Phase-2 原七项
- **OCO/bracket 写**、**计费真实入账**、**Memory LTM 全闭环** — 见 closure 矩阵灰/黄项
- **单 MR 堆叠**：P0 管线 + Publish + Gateway

## 非功能

见 [`inventory.md`](../product/inventory.md) §7：

| 项 | 值 |
|----|-----|
| API | http://127.0.0.1:8080 |
| Admin | http://127.0.0.1:5173 |
| Deeplink | http://127.0.0.1:5174 |
| 时间 | API JSON 默认 UTC（`BACKEND_SPEC` §2.1） |

## 变更记录

| 日期 | 变更 | 操作人 |
|------|------|--------|
| 2026-05-26 | 创建 phase-2：inventory §4 七项 → backlog | product-agent |
| 2026-05-26 | **Phase-2 收束** · 七项全 done · mode → continuing | product-agent |
| 2026-05-27 | **phase-realign** · 对照 PRD roadmap + inventory · 七项 **保留 done** · 无返工 ID · OP-BILL/Prompt IA 确认推迟 Phase-4+ | product-agent |
