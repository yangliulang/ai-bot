# Phase 1 — 504 扩面、体验/运营对齐与 Pipeline 验证（ChainUp）

> 产品 Agent 维护。backlog 来自 `handoff/product/inventory.md` §4，不全文复制路线图。  
> **存量已实现**见 inventory §2（本表 **不** 重复标 `planned`）。

## 阶段目标

1. 推进 **写路径 504/UNKNOWN 全局扩面**，在存量对账 HTTP 基础上覆盖更多写操作终态语义。
2. 对齐 **P1 体验与运营**（NLU 策略、欢迎语、narrate、Observability Admin、实例扩展等，以 inventory §4 为准）。
3. 用 Agent Pipeline 跑通至少 **1 个功能包** 全链路（contract → done），验证 monorepo 协作。

## 功能 backlog

| 优先级 | 功能 ID | 功能名 | 状态 | 功能包路径 | 备注 |
|--------|---------|--------|------|------------|------|
| P0 | 2026-05-26--trading-write-unknown-global | 写路径 504 UNKNOWN 全局扩面 | done | handoff/features/2026-05-26--trading-write-unknown-global/ | 全链路 done（2026-05-26）；TG callback 文案见 brief Q2 P1 |
| P1 | 2026-05-26--admin-observability | Observability Admin 对齐 | done | handoff/features/2026-05-26--admin-observability/ | 全链路 done（2026-05-26）；UI P1 待迭代见 design/ui-review.md |
| P1 | 2026-05-26--nlu-llm-strategy | NLU LLM 默认策略 | done | handoff/features/2026-05-26--nlu-llm-strategy/ | 全链路 done（2026-05-26）；`/ai-settings` UI 留后续 FE |
| P1 | 2026-05-26--telegram-welcome | 开通欢迎语 | done | handoff/features/2026-05-26--telegram-welcome/ | 全链路 done（2026-05-26）；UI P1 placeholder 见 design/ui-review.md |
| P1 | 2026-05-26--telegram-llm-narrate | 场景 LLM narrate 扩面 | done | handoff/features/2026-05-26--telegram-llm-narrate/ | 全链路 done（2026-05-26）；`/ai-settings` UI 留后续 FE |
| P1 | 2026-05-26--admin-agent-instance-write | Agent 实例能力扩展 | done | handoff/features/2026-05-26--admin-agent-instance-write/ | 全链路 done（2026-05-26）；UI P1 见 design/ui-review.md |

功能 ID 格式：`YYYY-MM-DD--kebab-slug`（双横线 `--`）。

### 状态说明

| 状态 | 含义 |
|------|------|
| `planned` | 未建包或未 contract_ready |
| `contract_ready` | 可交后端 |
| `in_dev` | 开发中 |
| `done` | 功能包 phase 为 done |

### 存量已实现（inventory §2 · 不建包 · 勿标 planned）

以下能力 **服务端已交付**；仅当需要契约/验收追溯时可 **可选收口** 建包，**不占用** 上表 backlog 优先级：

| 能力 | 可选功能 ID | 说明 |
|------|-------------|------|
| 条件单查/撤 | `2026-05-26--condition-order-list-cancel` | Step 2.5 已含 |
| 合约撤单 | `2026-05-26--futures-cancel` | Step 2.3 cancel 已含 |
| 504/UNKNOWN 对账 HTTP | `2026-05-26--trading-reconcile` | Step §6 已含；与上表 P0 扩面不同 |

### 指挥官下一步

Phase-1 表内 backlog **均已 done**（2026-05-26）。后续见 **[`phase-2.md`](phase-2.md)** · `handoff/product/inventory.md` §4。

## 依赖与顺序

```text
2026-05-26--admin-observability          ← 首包（后端已有，Admin + 契约收口）
2026-05-26--trading-write-unknown-global ← 可并行；依赖 §2 对账存量

P1 体验（可并行，互不阻塞）：
  2026-05-26--nlu-llm-strategy
  2026-05-26--telegram-welcome
  2026-05-26--telegram-llm-narrate

2026-05-26--admin-agent-instance-write   ← 视 Admin 产品 scope，可后置
```

绑定/登录等前置能力已在 inventory §2，brief 中写清即可，**不重复建包**。

## 本阶段不做

见 `handoff/product/inventory.md` §5。

## 非功能

见 `handoff/conventions/chainup-monorepo.md` 联调表。

## 变更记录

| 日期 | 变更 | 操作人 |
|------|------|--------|
| 2026-05-26 | 创建 phase-1（接入流水线） | product-agent |
| 2026-05-26 | 对齐 inventory §4：P0 交易已收口至 §2；backlog 改为 504 扩面 + P1；首包 Observability Admin | product-agent |
| 2026-05-26 | 2026-05-26--admin-observability 建包定稿 → contract_ready | product-agent |
| 2026-05-26 | 2026-05-26--admin-observability product.accept → **done**（Phase-1 首包全链路） | product-agent |
| 2026-05-26 | 2026-05-26--trading-write-unknown-global 建包定稿 → contract_ready | product-agent |
| 2026-05-26 | 2026-05-26--trading-write-unknown-global product.accept → **done**（Phase-1 P0 504 扩面全链路） | product-agent |
| 2026-05-26 | 2026-05-26--nlu-llm-strategy 建包定稿 → contract_ready | product-agent |
| 2026-05-26 | 2026-05-26--nlu-llm-strategy product.accept → **done**（Phase-1 P1 NLU 策略全链路） | product-agent |
| 2026-05-26 | 2026-05-26--telegram-welcome 建包定稿 → contract_ready | product-agent |
| 2026-05-26 | 2026-05-26--telegram-welcome product.accept → **done**（Phase-1 P1 欢迎语全链路） | product-agent |
| 2026-05-26 | 2026-05-26--telegram-llm-narrate 建包定稿 → contract_ready | product-agent |
| 2026-05-26 | 2026-05-26--telegram-llm-narrate product.accept → **done**（Phase-1 P1 narrate 全链路） | product-agent |
| 2026-05-26 | 2026-05-26--admin-agent-instance-write 建包定稿 → contract_ready | product-agent |
| 2026-05-26 | 2026-05-26--admin-agent-instance-write backend.implement → **backend_done** | backend-agent |
| 2026-05-26 | 2026-05-26--admin-agent-instance-write test.api → **tested** | test-agent |
| 2026-05-26 | 2026-05-26--admin-agent-instance-write frontend.integrate → **frontend_done** | frontend-agent |
| 2026-05-26 | 2026-05-26--admin-agent-instance-write test.e2e → **e2e_verified** | test-agent |
| 2026-05-26 | 2026-05-26--admin-agent-instance-write designer.review → **ui_reviewed** | designer-agent |
| 2026-05-26 | 2026-05-26--admin-agent-instance-write product.accept → **done**（Phase-1 实例写路径全链路） | product-agent |
