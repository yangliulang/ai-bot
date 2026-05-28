# Skill 操作规范 · 模板

**路径**：`specs/requirements/skill-specs/TEMPLATE.md`。

**用途**：复制为本目录下 `**/<skillId>.md`（文件名 **=** 登记 `skillId`）。**须在** [`trade-assistance` §4/§8.2](../domains/agent/exchange-agent/trade-assistance.md) **同序同窗 MR**。**所属体系**：[**PRS L0**](../prompt-runtime/README.md) · **派工** → **[PRS §4](../prompt-runtime/README.md#prs-where-to-edit)**。

**FR-T11 硬性要求**：Publish / `read_skill_operation_spec` **须能只读单文件完成编排** — **§1～§6 自包含**；**禁止**「同 `skill.xxx` §2」「增量见基线 skill」作为正文主体（可 **文首** 链流程专节，**不可** 替代五段式表）。

---

## 元数据

| 键 | 值 |
|----|-----|
| **`skillId`** | （与文件名一致） |
| **`skillSpecVersion`** | `0.1.0-mvp`（Publish 后由 `prompt-management` 单调版本覆盖） |
| **`scenarioId`（主）** | （[`routing-engine` §2](../domains/agent/agent-orchestration/routing-engine.md)） |
| **`confirmation-flow` 步骤** | 1→2→3→4→5（[`confirmation-flow` §1](../domains/agent/agent-orchestration/confirmation-flow.md)） |
| **流程专节** | （[`trade-via-agent`](../flows/trade-via-agent.md) 锚点） |
| **PRS 延展条文** | （[`prompts/trading/`](../prompts/trading/README.md) 或域专节 — **见** **[PRS §4](../prompt-runtime/README.md#prs-where-to-edit)**） |
| **状态** | `draft` \| `contract-complete` \| `frozen`（**勿** 用 `mvp-ready` 标记「仅增量引用」稿） |

---

## 1. Required / Optional Params

| 参数 | 必填 | 类型 | 说明 |
|------|:----:|------|------|
| | | | |

**互斥 / 二选一**：…

---

## 2. Validation Rules

| 规则 ID | 条件 | 失败处置 |
|---------|------|----------|
| | | |

**交易所精度**：`tickSize`、`stepSize`、`minNotional` — **以工具/矩阵回填为准**，**禁止** Prompt 臆造。

**产品闸**：`FR-T07`、`FR-T12`（若适用）、`FEATURE_*` — 链 [`trade-assistance` §2](../domains/agent/exchange-agent/trade-assistance.md)。

---

## 3. Confirmation Schema（类型 A）

**卡片 MUST 可见字段**：

- …

**禁止**：无 Secret；手续费等 **无事实不填** — [`order-confirmation`](../prompts/confirmation/order-confirmation.md)。

**Telegram**：[`telegram/overview` §2.5](../domains/agent/telegram/overview.md)。

---

## 4. UNKNOWN / 缺槽策略

| 缺省项 | Agent MUST | 禁止 |
|--------|------------|------|
| | 追问 / 澄清 | 进入类型 A / 声称已下单 |

**工具失败 / 504**：[`shared/common-phrases` §2](../prompts/shared/common-phrases.md)、[`Runtime/unknown-state`](../Runtime/unknown-state.md)。

---

## 5. Refusal Conditions

| 条件 | 对用户 | 稳定码 / FR |
|------|--------|-------------|
| | | `FR-T05` 族 |

---

## 6. API / 写路径（设计索引）

| 动作 | PATH（矩阵为准） |
|------|------------------|
| 下单 | |
| 撤单 | |

---

**文档版本**：template-1.0.0 · **维护**：产品 + Agent Runtime owner。
