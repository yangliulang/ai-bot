# Prompt Management（`admin/prompt-management/`）

**聚合 PRD**：[`../management-console-v1-prd.md` · §5 模块二](../management-console-v1-prd.md)

| 文件 | 说明 |
|------|------|
| [`overview.md`](overview.md) | 域定位 · 划界 · 文档索引 |
| [`functions.md`](functions.md) | **FR-PM01～08** · **`PM-C01～15`**（§1.2 **PM-C15** + §1.3 **PM-C01～14**）· **§7** · **FR-MC** · **SC-PM-01～20** · §5 错误码 · [`runtime-injection`](runtime-injection.md) |
| [`runtime-injection.md`](runtime-injection.md) | **Assembly · denylist§2.3 · Safety§7.1 · Session 冻结 · Tool SSOT · 兼容闸 · Budget · 错误 Scope · Ownership** |
| [`flow.md`](flow.md) | **状态机**、`FR-PM08` **读汇合**、审计锚点 |
| [`config.md`](config.md) | **IA · 路由 · 字段 ↔ OpenAPI** |
| [`rules.md`](rules.md) | **审计矩阵** · **RBAC** · 双 SSOT · 合规 |

**建议阅读**：`overview` → **`functions`（验收主表）** → **`runtime-injection`（拼装与风控）** → `config` / `flow` → `rules`。

**邻域**：[`agent-management`](../agent-management/overview.md) **T03/T04**；[`agent-orchestration`](../../agent/agent-orchestration/overview.md)；[`trade-assistance`](../../agent/exchange-agent/trade-assistance.md)；[`design/api`](../../../../design/api.md) **登记表**；[`observability`](../../../observability/overview.md) **§2.3 · SC-OBS04**。
