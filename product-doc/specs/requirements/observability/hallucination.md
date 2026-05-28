# Observability · 话术可信度与安全阻断（Hallucination / Grounding）

**路径**：`specs/requirements/observability/hallucination.md`。

**职责**：从 **观测与协查** 角度约定：**模型输出不可信**、**工具拒答**、**合规阻断** 时 **须留什么结构化痕迹**，以便 **客诉 / 风控回放 / Prompt 迭代** — **不**替代 **产品话术 SSOT**（[`exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md) **`FR-T05`** **族**、[`boundaries.md`](../domains/agent/exchange-agent/boundaries.md)）。

---

## 1. 原则

1. **禁止默认落全文**：**用户 utterance / 模型回复** **默认** **不落** **可检索明文全文** — **[`overview.md`](./overview.md) §2 末段** **脱敏** **同窗**。  
2. **须可回答三件事**：**是否调过工具**、**工具成败与机器码**、**本轮绑定 Prompt 包版本** — **`agent.tool.call`** + **`agent.prompt.binding_resolved`** **（[`overview.md`](./overview.md) §2.3）**。  
3. **不把「幻觉」当作可观测枚举**：**实现侧** **用 ** **`failureClass` / `reasonCode` / `stableReason`** **表达 ** **可行动语义**（[`Runtime/error-normalization.md`](../Runtime/error-normalization.md)、[`exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md)）。

---

## 2. 建议事件（可选命名 · OpenAPI 终裁）

下列 **约束**：若与 `agent.tool.call` **FAILED 终态** **共用同一 event schema**，**须** 能以布尔或子类型区分。

| 场景 | 建议事件名 | 必备字段（示意） |
|------|------------|------------------|
| **工具规划与事实不符**（例：调用不存在 **`toolId`**、参数校验失败） | **`agent.tool.call`** **`invocationState=FAILED`** **（不变更 SSOT）** | **`toolId`**、**`failureCode`**（所内枚举）、**可选** **`validatorHint`**（**无**用户原文） |
| **模型安全 / 政策拦截**（输出未下发用户） | **`agent.output.blocked`**（**或** **`agent.model.completion`** **之 **`phase=blocked`**） | **`userId`**、**`executionId`**、**`scenarioId`**（若有）、**`blockReason`**=`policy`\|`legal`\|`provider_refusal` **等** **枚举**、ts |
| **事实 grounding 不足**（内部降级为澄清 / 拒答） | 同上 **或** **`agent.tool.call`** **无调用 ** **且 ** **`billing.skipped`** **`reason=policy`** **链** | **须 ** **与 **`FR-T05`** **用户可见码 ** **同窗映射表** **冻结** |

**Prompt 运营侧拦截**：**[`overview.md`](./overview.md) §2.3 · `admin.prompt.publish_blocked`** — **不**在本条重复字段。

---

## 3. 与测试 / 抽检

- **回放**：给定 **`executionId`**，**须** **拼出** **「绑定包版本 → 工具调用序列 → 交易所 UNKNOWN」** **是否 ** **符合 ** **`overview` §2** **下限** — **与 **`SC-OBS01～06`** **同窗抽检**。  
- **不新增 SC 编号**：本条 **仅 ** **叙事 ** **收敛 ** **直至 ** **评审 ** **单列 **`SC-OBS*`** **扩展项**。

---

## 4. 互引

| 文档 | 关系 |
|------|------|
| [`overview.md`](./overview.md) | **事件 SSOT** · **脱敏** · **§2.3** |
| [`domains/admin/prompt-management/functions.md`](../domains/admin/prompt-management/functions.md) | **SC-PM-09** |
| [`Runtime/error-normalization.md`](../Runtime/error-normalization.md) | **`stableReason`** |

---

**文档版本**：0.1.0 · **维护**：产品 + 安全 + SRE · **本版**：占位 **落地** **协查原则与可选事件**。
