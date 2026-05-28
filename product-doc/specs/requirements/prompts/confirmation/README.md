# `confirmation/` · 索引（MVP）

**路径**：`specs/requirements/prompts/confirmation/README.md`。

本目录三篇为 **类型 A / 风险披露 / 高危二次确认** 的 **Git 条文下限**，与 **线上 Prompt Pack**（[`prompt-management`](../../domains/admin/prompt-management/overview.md)）**对签演进**。

**Publish 映射**：**不**单独占 `promptPackId`；Runtime 拼装注入 [`library/packs/fragment-confirmation-type-a.*`](../library/packs/fragment-confirmation-type-a.zh-CN.md) · 对照 [`governance-map.md` §2](../governance-map.md)。

---

## 阅读顺序（建议）

1. [`order-confirmation.md`](./order-confirmation.md) — **步骤序**、摘要字段、超时 / 拒绝  
2. [`risk-disclosure.md`](./risk-disclosure.md) — **触发**、披露≠授权、数字防捏造  
3. [`high-risk-confirmation.md`](./high-risk-confirmation.md) — **显著 UX**、二次数字、冻结同窗  

---

## 域宿主（终裁链）

| 主题 | 文档 |
|------|------|
| **步骤序 · SC-TA** | [`confirmation-flow`](../../domains/agent/agent-orchestration/confirmation-flow.md)、[`trade-assistance` §2](../../domains/agent/exchange-agent/trade-assistance.md) |
| **Telegram 类型 A** | [`telegram/overview` §2.5 · 类型 A、§2～§2.6](../../domains/agent/telegram/overview.md)、[`ADR-001`](../../../design/adr/001-telegram-confirm-before-coobit-write.md) |
| **拼装 / 冻结** | [`runtime-injection`](../../domains/admin/prompt-management/runtime-injection.md) |
| **幻觉观测** | [`hallucination`](../../observability/hallucination.md) |

---

## 上级

[`../README.md`](../README.md)

---

**文档版本**：1.0.2 · **维护**：产品 + Prompt owner · **本版**：**governance-map** Publish 说明；**承** 1.0.1。
