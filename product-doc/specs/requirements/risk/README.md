# Risk（全局风险横切）

**路径**：`specs/requirements/risk/README.md`。

**职责**：**运营可配闸、横切收口与对签指针** — **不**重复 **`exchange-agent`** 内单笔能力正文。**产品与合规边界、稳定码、主站回退** 的 **条文 SSOT**：[`../domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md)。**交易写门禁、技能登记、类型 A 与 FR-T09/T11**：[`../domains/agent/exchange-agent/trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md)。**全局 `configKey` 与附录 A 枚举**：[`../domains/admin/trading-agent-config/keys.md`](../domains/admin/trading-agent-config/keys.md)。

**分层（阅文顺序）**

| 层级 | 内容 | 主链 |
|------|------|------|
| **产品/单笔** | 矩阵终裁、写须确认、非投顾、主站回退码 | **`boundaries`**、[`../flows/trade-via-agent.md`](../flows/trade-via-agent.md) |
| **运营闸** | 总开关、特性矩阵、交易护栏键 | **`trading-agent-config/keys`**、[`flow.md`](../domains/admin/trading-agent-config/flow.md)、[`agent-management/rules.md`](../domains/admin/agent-management/rules.md) §3 |
| **执行管线** | 读快照 → Kill/Pause 拒新写 → 确认门 → 工具；**504/UNKNOWN 无进展阈值** | [`../Runtime/execution.md`](../Runtime/execution.md) **§1**、[`../Runtime/freeze-policy.md`](../Runtime/freeze-policy.md)、[`unknown-stall-policy.md`](unknown-stall-policy.md) |
| **提醒外显** | 爆仓/波动/集中度等 **话术与边界**（**非**本目录运营键） | [`../domains/agent/exchange-agent/risk-alerts.md`](../domains/agent/exchange-agent/risk-alerts.md) |
| **审计观测** | `admin.audit`、事件下限 | [`../observability/overview.md`](../observability/overview.md) |
| **契约收口** | 矩阵解冻 MR **`§4`/`§7`** **核对项** **含** **护栏键与 `boundaries` §9** | [`../contract-closure.md`](../contract-closure.md) **§4、§6、§7** · [`closure-remaining.md`](../closure-remaining.md)（**[§0](../closure-remaining.md#closure-remaining-quicklinks)** · **[§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)** · **[§7.5～§7.6](../closure-remaining.md#cc-remaining-open-close-path)**） |

**分卷索引**

| 文件 | 说明 |
|------|------|
| [`kill-switch.md`](kill-switch.md) | 全局/运维/实例级 **停止与 Pause**；与 **FR-T05** 拒答 |
| [`leverage-limit.md`](leverage-limit.md) | **杠杆/合约产品线** 与 **运营杠杆上限**；与 **确认串联** |
| [`symbol-restriction.md`](symbol-restriction.md) | **品种 allowlist/blocklist** 与 **限价偏离带** |
| [`exposure-limit.md`](exposure-limit.md) | **净敞口、集中度、会话亏损、大额、频控** 等护栏键 |
| [`user-confirmation.md`](user-confirmation.md) | **类型 A** 与 **写前确认链**（**ADR-001**） |
| [`compliance.md`](compliance.md) | **合规与非投顾** 横切条；与 **Prompt safety** 对读 |
| [`hitl-and-automation-matrix.md`](hitl-and-automation-matrix.md) | **HITL** **vs** **自动化/护栏** **对照矩阵**（**与** **`user-confirmation`/`kill-switch`** **互链**） |
| [`acceptance.md`](acceptance.md) | **横切验收 `SC-RISK-01～06`**（**Kill/护栏/审计/UNKNOWN 无进展**） |
| [`unknown-stall-policy.md`](unknown-stall-policy.md) | **`unknown_pending` 无进展**：阈值/查单有界/超时终局或人工 — **`exchange-agent` §4** **与** **`unknown-state`** **对签宿主** |

---

## 资格 / Prompt / 契约收口（横切）

| 主题 | 文档 |
|------|------|
| **准入 · eligibility · VIP** | [`access-control/overview`](../domains/admin/access-control/overview.md)、[`eligibility-runtime`](../domains/admin/access-control/eligibility-runtime.md) |
| **Prompt Safety / 确认条文** | [`prompts/safety/README`](../prompts/safety/README.md)、[`prompts/confirmation/README`](../prompts/confirmation/README.md)；拼装 [`runtime-injection` §7.1](../domains/admin/prompt-management/runtime-injection.md) |
| **契约收口** | [`contract-closure`](../contract-closure.md) · [`closure-remaining` §0～§7.6](../closure-remaining.md#closure-remaining-quicklinks) |
| **横切验收 `SC-RISK*`** | [`acceptance`](acceptance.md) |

---

## 上级

[`../README.md`](../README.md)

---

**文档版本**：0.3.6 · **维护**：产品 + 风控 owner · **本版**：**§资格** **表** **`closure-remaining`** **首节** **链（§0～§7.6）。** **承** 0.3.5。
