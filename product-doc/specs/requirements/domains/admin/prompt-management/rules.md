# Prompt Management · 规则与约束

本文档为 **`functions.md`** **MUST** 类约束 **展开版**；与 **合规**冲突时以 **书面 OVERRIDE / `contract-closure`** 为准。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. 审计（不可降级 · 最低集）

实现侧须注册 **白名单**动作（**非穷举**占位可增）：

| 动作类型（示例） | 须含字段 |
|------------------|----------|
| **`PROMPT_DRAFT_SAVED`** | `promptPackId`、diff 或 body hash ref |
| **`PROMPT_PUBLISHED`** | `promptPackVersion`、`scenarioId`（若有） |
| **`PROMPT_ROLLBACK`** | 源/目标 `promptPackVersion` |
| **`PROMPT_SYSTEM_VERSION_CREATED`** | 母 `LOCKED` 版 id |
| **`FEWSHOT_MUTATED`** | 关联 `promptPackId` / 草稿 id |
| **`PROMPT_PUBLISH_BLOCKED`** | `promptPackId`（草稿/目标）、**`gate`**（`PLACEHOLDER_DENYLIST` / `SAFETY_PHRASE` / **`design`**扩展）、**`matchedRuleId`**、`actor` |与 **`observability` / 合规** 对签；本域 **不定**月数。

---

## 2. RBAC（最小集合 · V1）

**角色名为占位**；**IAM** 须 **`1:1`** 映射到下表能力行（建议使用 permission 名如 `prompt.pack.publish`）。

| 资源 / 动作 | Viewer | PromptEditor | PromptApprover | PromptAdmin |
|-------------|--------|----------------|----------------|-------------|
| 系统/场景包 **只读列表 + 履历** | ✓ | ✓ | ✓ | ✓ |
| **草稿** 编辑 / Few-shot | ✗ | ✓ | ✗ | ✓ |
| **`LOCKED`** 包 **正文 PATCH** | ✗ | ✗ | ✗ | ✗ |
| **Publish** | ✗ | ✗（除非 [`functions.md`](functions.md) **§7** P0 免检且 IAM 授 `prompt.pack.publish` 给 Editor） | ✓ | ✓ |
| **Rollback** | ✗ | ✗ | ✓ | ✓ |
| **沙箱 Run** | ✗ | ✓ | ✗ | ✓ |
| **枚举/策略配置**（若存在） | ✗ | ✗ | ✗ | ✓ |

**原则**：与 **模块一模板**、**全局配置** 的 **资源 id** **分离**——满足 **`functions` FR-PM01**。**对象属主 / 默认无写权限 / 修改与删除分项 IAM**：[`runtime-injection.md` §9](runtime-injection.md)。

---

## 3. 内容与双 SSOT

1. **不得**在本文或 **Prompt 正文**中 **内嵌** **`trade-assistance`** **操作规范全文**；**允许**引用 **`skillSpecVersion` / `skillId`**。  
2. **场景话术** **不得**诱导 **第二条主交易路径**——与 [`trade-via-agent`](../../../flows/trade-via-agent.md)、[`agent-orchestration`](../../agent/agent-orchestration/overview.md) **冲突**时 **以编排/flow SSOT 为准**。  
3. **Telegram 卡片**：模板 **以** [`telegram/overview` §2.5 · 类型 A；总则 §2～§2.6](../../agent/telegram/overview.md) **为准**。  
4. **PII / Secret**：Few-shot、沙箱 fixture、审计 **默认不落**可逆明文；**详见** **`observability`** 脱敏策略。**`{{…}}` 占位符**：**下限 denylist** [`runtime-injection.md` §2.3](runtime-injection.md)（**可增不可减**）。

---

## 4. 话术与评审

**SAFETY/`POLICY` 类包** **Publish** **建议强制 Approver**。**灰度**：新 `promptPackVersion` **可先** **canary 用户段**（与本域 **可选**能力，**非** V1 必列 —— 若做须 **MR + `access-control`**）。

---

**Governance 条目编号**：**FR-PM01** — 见 [`functions.md`](functions.md) **§2.1**。
