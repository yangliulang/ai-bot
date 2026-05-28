# Phase 3 — W2/W3 所内收口：编排对拍、Prompt Runtime 与 Eval 证据（ChainUp）

> 产品 Agent 维护。backlog 对齐 `product-doc/product/roadmap.md` **规格体系快照 L2/L4/L6/L7**、[`closure-completion-matrix`](../../product-doc/specs/requirements/closure-completion-matrix.md) **W2～W3** 与 **OP-AO3 / OP-PR / OP-SKILL / OP-MEM**。  
> **存量已实现**见 [`inventory.md`](../product/inventory.md) §2（本表 **不** 重复标 `planned`）。Phase-2 七项均已 **done**（见 [`phase-2.md`](phase-2.md)）。

## 阶段目标

1. 完成 **编排 §3 对拍** 与 **`eval.runtime.pipeline_write_order`** staging 证据（**OP-AO3** · W2 **Eval**），补齐 Phase-2 管线走读的可验收闭环。
2. 推进 **Prompt Runtime 写路径拼装链**（**CC-P1-04 / OP-PR** · AC-09a～f），使 TRADING 拼装从 Phase1 子集扩至写路径场景可观测 join。
3. 落地 **Skill 契约 Eval staging**（**OP-SKILL B** · W3 **SK-B03**）与 **Registry 幂等**（**CC-P1-03**）；交付 **Memory STM** 基线（**OP-MEM** · LTM 默认 OFF）。

## 对齐说明

**对照真源**：[`product-doc/product/roadmap.md`](../../product-doc/product/roadmap.md)（2026-05-27 批次 · L1～L7 快照 · W1 硬排序见 closure 矩阵 §0）、[`inventory.md`](../product/inventory.md) §2/§5/§6、[`closure-completion-matrix`](../../product-doc/specs/requirements/closure-completion-matrix.md) §1～§3/§5。

**文档变更摘要（本轮回对齐）**：

- PRD 篇首 **计费轨 B / Admin·Web IA 清扫（2026-05-27）** 与 **OP-BILL** 归属 **Phase-4**（`backlog.yaml` 四项 `queued`），**不**纳入本阶段 backlog。
- **W2～W3** 所内收口主轴（Eval 管线 · Prompt 写路径 · Skill eval · Registry 幂等 · Memory STM）与 Phase-3 原规划 **一致**；矩阵 §3 部分横切仍为 **黄** = **所内 MR / staging 会签余量**，非本仓单包返工依据。
- **W4 可选**（MR-B Prompt 会签深化 · Memory LTM · **OP-NAR** MNRA 注入）与 **P-06 Gateway** 主实现 — 见下文「本阶段不做」，**推迟**至 Phase-4 或所内工单。

| 原项（功能 ID） | 处置 | 新功能 ID | 理由 |
|-----------------|------|-----------|------|
| 2026-05-28--pipeline-eval-orchestration-align | **保留** · done | — | 对齐 **OP-AO3** · W2 · `eval.runtime.pipeline_write_order`；inventory §2 已 rollover |
| 2026-05-28--prompt-runtime-assembly-write | **保留** · done | — | 对齐 **CC-P1-04 / OP-PR** · AC-09a～f 写路径 TRADING join |
| 2026-05-28--skill-contract-eval-staging | **保留** · done | — | 对齐 **OP-SKILL B** · W3 **SK-B03** · `eval.skill.*` P0 |
| 2026-05-28--registry-tool-idempotency | **保留** · done | — | 对齐 **CC-P1-03** · MR-E · `SC-MCV1-05` / `SC-OBS01` |
| 2026-05-28--memory-stm-session | **保留** · done | — | 对齐 **OP-MEM** STM 基线 · `eval.memory.session_clear_stm` · LTM 默认 OFF（与 PRD L4 及 matrix §6 话术边界一致） |
| OP-BILL · `me/commerce` · S2/S5 宿主 HTTP | **推迟** | Phase-4 四项（`backlog.yaml` queued） | PRD 横切计费 **2026-05-26～27** 明确 **Phase 2 商业轨** 为下一阶段 |
| Memory LTM 全闭环 · MNRA phase 注入 | **移除**（本阶段范围外） | — | closure §5 W4 可选 · inventory §5 非目标 |
| P-06 Gateway · CC-P0 红项 | **移除**（本阶段范围外） | — | 所内工程仓 / 运维 · inventory §5 |

**返工项**：无。五项交付与当前 PRD **无条文冲突**；矩阵 **黄** 项须 **所内 MR + staging 证据** 升格，**不**默认 reopen 原 ID。

## 功能 backlog

| 优先级 | 功能 ID | 功能名 | 状态 | 功能包路径 | 备注 |
|--------|---------|--------|------|------------|------|
| P0 | 2026-05-28--pipeline-eval-orchestration-align | 管线 Eval + 编排 freeze 对拍 | done | handoff/features/2026-05-28--pipeline-eval-orchestration-align/ | **OP-AO3** · `eval.runtime.pipeline_write_order` · `runtime-freeze` §3 · W2 Eval；**含页面：否** |
| P0 | 2026-05-28--prompt-runtime-assembly-write | Prompt Runtime 写路径拼装链 | done | handoff/features/2026-05-28--prompt-runtime-assembly-write/ | **CC-P1-04** · **OP-PR** · AC-09a～f · 写路径 TRADING 扩面；**含页面：否** |
| P1 | 2026-05-28--skill-contract-eval-staging | Skill 契约 Eval staging | done | handoff/features/2026-05-28--skill-contract-eval-staging/ | **OP-SKILL B** · W3 **SK-B03** · `eval.skill.*` P0 真跑；**含页面：否** |
| P1 | 2026-05-28--registry-tool-idempotency | Registry toolId/skillId 幂等 | done | handoff/features/2026-05-28--registry-tool-idempotency/ | **CC-P1-03** · MR-E · `SC-MCV1-05` / `SC-OBS01`；**含页面：否** |
| P2 | 2026-05-28--memory-stm-session | Memory STM 会话基线 | done | handoff/features/2026-05-28--memory-stm-session/ | **OP-MEM** · `eval.memory.session_clear_stm` · LTM 默认 OFF；**含页面：否** |

功能 ID 格式：`YYYY-MM-DD--kebab-slug`（双横线 `--`）。

### 状态说明

| 状态 | 含义 |
|------|------|
| `planned` | 未建包或未 contract_ready |
| `contract_ready` | 可交后端 |
| `in_dev` | 开发中 |
| `done` | 功能包 phase 为 done |

### 指挥官下一步

**Phase-3 已全部 done**（对齐后无新增 planned）。继续 **Phase-4** 规划：

```text
/pipeline-product-plan
```

（附 `@product-doc/product/roadmap.md`；plan 后 `./scripts/sync-backlog-from-phase.sh`）

若需对 Phase-4 已 reset 的四项 **OP-BILL** 重新对齐，可用 `/pipeline-product-phase-realign phase-4`。

## 依赖与顺序

```text
首包（二选一，勿并行 contract）：
  2026-05-28--pipeline-eval-orchestration-align   ← OP-AO3 · 依赖 Phase-2 runtime-write-path-pipeline done
  2026-05-28--prompt-runtime-assembly-write       ← CC-P1-04 · 可与上表错开定稿

P0 可并行开发（定稿仍建议一次一个）：
  2026-05-28--pipeline-eval-orchestration-align
  2026-05-28--prompt-runtime-assembly-write

P1（可并行；与 P0 定稿错开）：
  2026-05-28--skill-contract-eval-staging         ← 依赖 skill-publish-effective done
  2026-05-28--registry-tool-idempotency           ← 无硬依赖

P2（须在 Prompt/Skill 基线 contract_ready 之后）：
  2026-05-28--memory-stm-session
```

**并行纪律**（`closure-internal-sprint`）：单 MR/功能包 **勿**堆 P0 Eval + Prompt + Gateway；**P-06 Gateway 主实现**（所内工程仓）**不在**本阶段 backlog。

Phase-2 主链（read_skill、Publish、TG staging）、契约三件套、Admin 网关 UI 等前置已在 inventory §2，brief 中写清即可，**不重复建包**。

## 本阶段不做

见 [`inventory.md`](../product/inventory.md) §5，并补充：

- **OP-BILL** · **Commerce S2/S5** · **`me/commerce`** — **Phase-4**（`backlog.yaml` 四项 `queued`）
- **P-06 Gateway 主实现**（`call_exchange_write` · 所内工程仓 · **CC-P1-07**）— **deferred**
- **CC 红项**（Hosted rollout、矩阵延期终裁、账务三线、财务专户、D-5/D-7 等）— 须所内/运维
- **OCO/bracket 写**、**计费真实入账**、**Memory LTM 全闭环（B）**、**OP-NAR MNRA 生产注入** — 见 closure 矩阵灰/黄项 · W4 可选
- **单 MR 堆叠**：P0 Eval + Publish + Gateway

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
| 2026-05-28 | 创建 phase-3：closure W2/W3 五项 → backlog | product-agent |
| 2026-05-27 | **Phase-3 收束** · 五项全 done · inventory §2 rollover | product-agent |
| 2026-05-27 | **phase-realign** · 对照 PRD roadmap + inventory · 五项 **保留 done** · 无返工 ID · OP-BILL 确认推迟 Phase-4 | product-agent |
