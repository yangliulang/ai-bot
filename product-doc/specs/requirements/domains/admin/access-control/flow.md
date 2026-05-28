# Access Control · 流程

**叙事**：[`overview.md`](overview.md)；**FR**：[`functions.md`](functions.md) **§2**。

| 流程 | 步骤 |
|------|------|
| **放白** | 申请 → （合规）审批 → 写入名单 → **在读侧 SLA 内**生效（[`functions` §6](functions.md)） |
| **封禁** | 选用户 → 原因 → **可选**联动 **Pause 实例** · [`agent-management` flow](../agent-management/flow.md) |
| **VIP 阈值变更** | 编辑 `AGENT_MIN_VIP_TIER` → **审批** → **`keys`/附录 A §5.1 MR** |
| **VIP 降级（检测）** | 发现 **母账号** **`vipTier`** **低于** **`AGENT_MIN_VIP_TIER`** → **拒答** **`AGENT_MEMBERSHIP_BLOCKED`** · **I02** **与** **FR-T02** **一致**（[`exchange-agent` flow](../../agent/exchange-agent/trade-assistance.md)） |

## 邻域索引

[**`risk/`**](../../../risk/README.md)（合规/风险叙事索引）；[**`exchange-agent` overview**](../../agent/exchange-agent/overview.md)。

---

**文档版本**：0.1.0 · **维护**：产品 + 后台 owner。
