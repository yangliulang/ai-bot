# Prompt 书写标准（薄索引）

**正文 SSOT**：[`prd-standard.md`](prd-standard.md) **§4～§6**（条目结构、邻域与验收）、[`interaction-flow-standard.md`](interaction-flow-standard.md)（终端形态与字段下限）、[`../domains/admin/prompt-management/overview.md`](../domains/admin/prompt-management/overview.md)（分层、版本与发布）。

---

## 1. 双层：运营正文 vs Git 条文

| 层 | 位置 | 结构 / 用途 |
|----|------|-------------|
| **运营发布（Publish）** | `promptPackId`（`pp-*`） | **六段**：Identity → Scenario Context → Behavioral Rules → Capability Awareness（可选）→ Clarify Rules（可选）→ Output Contract（可选）。模板见 [`src/admin/src/data/promptBodyTemplates.ts`](../../../src/admin/src/data/promptBodyTemplates.ts) |
| **Git 条文 + 拼装库** | [`../prompts/`](../prompts/README.md) 七目录 + [`library/`](../prompts/library/README.md) | **评审下限**、FR/Skill 引用、`scenarioId` 拼装字母（C/E/S/…）；**可**含 `call_exchange_write` 等 **契约指称**，**不**等于运营粘贴体 |

**映射 SSOT**：[`../prompts/governance-map.md`](../prompts/governance-map.md) · 产品清单 [`product/prompt-governance-checklist.md`](../../../product/prompt-governance-checklist.md)。

**原则**：运营正文只写 **LLM 如何理解与表达**；Validation、Canonical、Billing、Gateway 由 **Runtime / Skill Spec** 承担。

---

## 2. 存量协作目录（导航）

- **索引**：[`../prompts/README.md`](../prompts/README.md) — §2 治理双层、§1 目录树  
- **写 / 读场景**：[`trading/README.md`](../prompts/trading/README.md)、[`analysis/README.md`](../prompts/analysis/README.md)  
- **拼装**：[`library/scenarios/registry.md`](../prompts/library/scenarios/registry.md)  
- **版本约定**：索引 `1.x.0` vs 条文 `1.x.0-mvp`（见 prompts 根 README）  
- **不设**：`fallbacks/`、`policies/` prompt 子树；条文优先，禁止无评审对白占位
