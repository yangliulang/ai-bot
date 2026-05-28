# Global Risk · Compliance（合规横切）

**职责**：**非投顾**、**Disclaimer**、**违法/滥用话术**、**主站回退** 等与 **自然语言输出** 相关的 **全局下限** — **条文与稳定码** 仍以 [`../domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md) **为 SSOT**。

---

## 1. 原则（摘录）

| 原则 | 说明 |
|------|------|
| **非投顾** | **不得** **保证**收益 **或** **代替**用户风险承受判断；收益/风险结论 **须** **Disclaimer** — **`boundaries` §1** |
| **矩阵终裁** | **`design/api` 未列 / TBD** → **不实现、不承诺**；**`FR-T05` 族** 拒答 — **`boundaries` §1、§2** |
| **主站回退** | **`WEALTH_ACTION_REQUIRES_WEB`**、**`TRANSFER_REQUIRES_WEB`** 等 — **`boundaries` §8**、[`../flows/wealth-via-agent.md`](../flows/wealth-via-agent.md) |

---

## 2. Prompt 与 Safety

| 资产 | 用途 |
|------|------|
| [`../prompts/safety/illegal-request.md`](../prompts/safety/illegal-request.md) | 合规拒绝、绕过闸门、禁入地域等 **话术侧下限** |
| [`../prompts/safety/jailbreak.md`](../prompts/safety/jailbreak.md) | 越狱与套取密钥 **处置** |
| [`../prompts/system/system.md`](../prompts/system/system.md) | **个性化配资** 等 **系统层否认**（与 **`boundaries`** 对读） |
| [`../domains/admin/prompt-management/rules.md`](../domains/admin/prompt-management/rules.md) | 后台 **RBAC · 合规边界**（发布物） |

---

## 3. 互引

| 文档 | 关系 |
|------|------|
| [`../domains/agent/exchange-agent/risk-alerts.md`](../domains/agent/exchange-agent/risk-alerts.md) | **提醒** **不**作 **隐含投顾** |
| [`../integrations/exchange/overview.md`](../integrations/exchange/overview.md) | **所**侧政策 **上游索引**（**非** Runtime） |

---

## 4. 准入与闸（运行时可观测）

- **地域 / VIP / 开通矩阵**：编排拒绝须有 **可对账原因** — [`access-control/overview`](../domains/admin/access-control/overview.md)、[`eligibility-runtime`](../domains/admin/access-control/eligibility-runtime.md)；与 **`FR-T05`** 话术同窗 [`common-phrases` §1](../prompts/shared/common-phrases.md)。

---

**文档版本**：0.2.0 · **维护**：产品 + 合规 owner · **本版**：**access-control**、**FR-T05 话术锚**。
