# Access Control · 配置与 IA

**叙事**：[`overview.md`](overview.md)；**FR/SC**：[`functions.md`](functions.md)。

## 1. 与附录 A、`keys` 对齐

| Key / 概念 | 说明 |
|------------|------|
| `AGENT_MIN_VIP_TIER` | **数值真源**：[**`keys` §3**](../trading-agent-config/keys.md)；本域提供 **编辑 + 审批 UX**；**须**与 **keys** **同一 MR** 更新（见 [`functions` §2.7](functions.md)）。 |
| **白名单 / 灰度 bucket** | `channel`、`uidSegment`、导入模板；**命中失败** → **`AGENT_ROLLOUT_BLOCKED`**（[`functions` §4](functions.md)、[`agent-management` §7.1](../agent-management/functions.md)）。 |

## 2. IA

- **门禁总览**：当前活跃规则数、误杀率（若接入）  
- **名单与灰度**：筛选、导入、导出、双人复核入口（[`rules`](rules.md)）  
- **VIP**：`AGENT_MIN_VIP_TIER` 展示与变更历史（若产品拆分 Tab，**仍** **单值真源**）

## 3. KYC

**只读**展示；写回 **须**走 **合规/风控**既有系统 API（本域 **不**发明第二套 KYC 状态机）。

---

## 4. 与 Agent Management · **I02**（门禁次序与本域触点）

管理台 **创建 Agent 实例（I02）** 的前置链以 **[`../agent-management/functions.md`](../agent-management/functions.md) · §2.1 I02** 为 **行为 SSOT**，顺序为：

1. **`GLOBAL_AGENT_SWITCH`**（非本域）  
2. **`access-control`**：**封禁** / **VIP（`AGENT_MIN_VIP_TIER`）** / **灰度与白名单**（**本域 + 附录 A**）  
3. **计费**（`billing`）  
4. **模板启用与依赖**（`agent-management`）  
5. **每用户实例配额**（若有）

**本域须保证**：

| 触点 | 要求 |
|------|------|
| **封禁 / 灰度 / 白名单** | 决策须能映射到 **附录 A** **`agentState` / `lastProductBlockReason`**（或 BFF 合成字段），与 **用户摘要 API**、**实例详情** **同源**；**禁止**与 `exchange-agent` **FR-T02** 口径分裂。 |
| **VIP / `AGENT_MIN_VIP_TIER`** | 与 **附录 A §5.1**、[`keys` §3](../trading-agent-config/keys.md)、**FR-MC607** **单源**；**比对须取母账号 `vipTier`**（[`eligibility-runtime` §1](eligibility-runtime.md)）；未达标 → **`AGENT_MEMBERSHIP_BLOCKED`**（[`agent-management` §7.1](../agent-management/functions.md)）。 |
| **用户封禁类** | **`AGENT_USER_BLOCKED`**（[`agent-management` §7.1](../agent-management/functions.md)）。 |
| **灰度未命中** | **`AGENT_ROLLOUT_BLOCKED`**（[`functions` §4](functions.md) **`agent-management` §7.1** **同窗冻结**）。 |

**BFF / 权限服务**：**不得**对 I02 自创 **未在 [`agent-management` §7.1](../agent-management/functions.md)** 与 **OpenAPI** 登记的 **业务 `code`**；新增原因须 **先**扩 **§7.1** 表 **再**改实现。

---

**文档版本**：0.1.1 · **维护**：产品 + 后台 owner · **本版**：**VIP** **母账号 `vipTier`**（承 **0.1.0**）。
