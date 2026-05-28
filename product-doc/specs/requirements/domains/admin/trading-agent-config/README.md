# Trading Agent Config（`admin/trading-agent-config/`）

**聚合 PRD**：[`management-console-v1-prd · §10 · 附录 A`](../management-console-v1-prd.md)

| 文件 | 说明 |
|------|------|
| [`overview.md`](overview.md) | 域定位、阅读顺序、索引 |
| [`keys.md`](keys.md) | `configKey` 枚举 SSOT |
| [`functions.md`](functions.md) | FR-MC701～711、SC-TAC、错误码 |
| [`config.md`](config.md) | IA、`If-Match` / `configVersion` |
| [`flow.md`](flow.md) | Diff、回滚、`agentState` |
| [`rules.md`](rules.md) | SSOT、RBAC、灰度 |

**建议阅读**：overview → functions → keys → config / flow → rules；**执行侧政策**兼读 [`runtime-policy.md`](../../agent/exchange-agent/boundaries.md)（**与 `functions` §2.7 对签**）。
