# Tool Management · 规则与约束

与 [`functions.md`](functions.md) **FR-TM-G01**、**§2.4** **一致**。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. 矩阵与「假开」

1. **禁止**：**PATH `TBD`** 或 **`DEFERRED` 且无书面备注**时，控制台 **启用**工具 **或对终端展示「已可用」**。  
2. **SC-MCV1-05**（[`management-console-v1-prd` §13](../management-console-v1-prd.md)）：与本域 **SC-TM-01～02～08** **同一事实**。  
3. **矩阵解冻 MR** **必须** **`design/api` 脚注**递增（[`contract-closure` §4](../../../contract-closure.md)）。

---

## 2. 登记一致

- **`toolId`** **∈** [`trade-assistance.md`](../../agent/exchange-agent/trade-assistance.md) **§8** **登记** **或** **`design/api` 登记表** **显式行**。  
- **禁止**：后台 **捏造** **`toolId`** **调用** **`runtime`** **未注册的**后端路由。

---

## 3. Secret 与日志

- **Schema / 抽样日志**：**默认** **无** **用户 API Secret / 明文私钥**；**必要时** **`LOG_SENSITIVE_VIEW`** 类审计（与 **observability-management** 对签）。

---

## 4. RBAC（最小集合 · V1）

**角色占位**——**IAM** **1:1** 映射。

| 资源 / 动作 | Viewer | ToolOperator | RiskAdmin | Admin |
|-------------|--------|--------------|-----------|-------|
| Registry / Schema **只读** | ✓ | ✓ | ✓ | ✓ |
| **Enable / Disable** | ✗ | ✓（受 **矩阵**） | ✓（**C 类终裁**） | ✓ |
| **FR-TM03 策略**编辑 | ✗ | ✓ | ✓ | ✓ |
| **日志全文 / 导出** | ✗ | ✓（可限） | ✓ | ✓ |
| **Tool 策略 / Registry 配置导出**（若有） | ✗ | ✗ | ✗ | ✓（**须** **`TOOL_EXPORT` + 审计**，见 [`functions.md`](functions.md) **§7**） |

---

## 5. C 类外网工具

须 **同时**满足 [`contract-closure` CC-P1-02](../../../contract-closure.md)（**ADR、速率、脱敏、`agent-context` 预算**）。**RiskAdmin**或**合规角色**未批准 → **Enable** **拒绝**。

---

**Governance**：**FR-TM-G01** · [`functions.md`](functions.md) **§2.1**。
