# `shared/` · 索引（MVP）

**路径**：`specs/requirements/prompts/shared/README.md`。

本目录承载 **跨场景复用的 Prompt 辅助条文**：**术语表**、**输出格式**、**稳定话术锚**。**不含**场景独占正文（交易 / 分析 / 确认等 **见各子目录索引**：[`../trading/README.md`](../trading/README.md)、[`../analysis/README.md`](../analysis/README.md)）。

**书写规范**：[`standards/prompt-standard.md`](../../standards/prompt-standard.md)、[`prd-standard` §4～§6](../../standards/prd-standard.md)。

---

## 文件

| 文件 | 用途 |
|------|------|
| [`glossary.md`](./glossary.md) | **`scenarioId`**、确认、`FR-T05`、`executionId` 等与 Prompt 拼装相关的 **术语锚** |
| [`response-format.md`](./response-format.md) | Telegram 分段、Markdown 子集、错误对用户句式 |
| [`common-phrases.md`](./common-phrases.md) | **`FR-T05`/UNKNOWN/确认链/意图分流** 的 **原则级句式锚**（**非** Few-shot 对白库）；**§8 Trader Narrative Anchors**（**市场叙事 · 非 Phrase Library SSOT**） |
| [`clarify-user-visible.md`](./clarify-user-visible.md) | **澄清/追问** Telegram **用户可见下限** · **[§0 LLM/规则/组合分工 SSOT](./clarify-user-visible.md#clarify-execution-split)** · **INV-010** · **禁内部术语外泄** |
| **↑ 拼装落地** | **[`../library/README.md`](../library/README.md)** — **可粘贴 SYSTEM / 片段 / 全表 **`scenarioId`** 配方** |

---

## 阅读顺序（建议）

1. [`response-format.md`](./response-format.md) — **§1「用户问题解决面」**（**Telegram 唯一解决面** + **`requires_main_site`** 例外）；**§2～§2.1** 与 [`telegram/overview` §2.5 · 类型 A；§2～§2.6](../../domains/agent/telegram/overview.md) **同窗**  
2. [`clarify-user-visible.md`](./clarify-user-visible.md) — **写路径澄清话术** · **§0 分工** · **同窗** [`clarify-session`](../../domains/agent/agent-orchestration/clarify-session.md)  
3. [`glossary.md`](./glossary.md) — 对齐 **`routing-engine`** / **`prompt-management`**  
4. [`common-phrases.md`](./common-phrases.md) — 与 [`Runtime/fallback-policy`](../../Runtime/fallback-policy.md)、[`unknown-state`](../../Runtime/unknown-state.md) **同窗**；**行情叙事锚** → **§8**

---

## 上级

[`../README.md`](../README.md)

---

**文档版本**：1.2.2 · **维护**：产品 + Prompt owner · **本版**：**clarify-user-visible §0 执行体分工链入**。**承** 1.2.1。
