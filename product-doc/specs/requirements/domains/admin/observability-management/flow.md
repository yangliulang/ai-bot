# Observability Management · 流程

| 流程 | 步骤 | 互引 |
|------|------|------|
| **工单协查（通用）** | 输入 **`executionId`** → **时间线**（`agent.*` / `trading.exchange_private`）→ **按需脱敏** · **不降**结构化键 | **`FR-MC801`**、[§2.1](../../../observability/overview.md) |
| **计费 / 账务协查** | **`userId` 或 **`executionId` 或 **`billingTraceId`**（**FR-MC503 三联任一入口**）→ 拉 **`billing.entitlement_debit_attempt|success|fail|skipped`**（**主链**）→ **并排** **`trading.exchange_private`**（504→`unknown`）→ **跳到** **`billing-management`/`commerce` 单笔协查** **或同窗 API** | **FR-MC503**、[`billing-management/flow.md`](../billing-management/flow.md) |
| **事故定界** | 对比 **工具错误率** vs **LLM 429** vs **交易所 5xx** vs **`billing.entitlement_debit_fail`（gateway/quota）** | **§2、`FR-MC506` 归因可接** |
| **审计下载** | 选时间窗 → **异步**打包 → **签名限时 URL** · **水印**（[`rules.md`](rules.md)） | **`FR-MC806～807`** |
| **保留策略** | 热/温/冷 **由** infra 执行；控制台 **仅**展示 **当前策略版本号**（只读） | [`overview`](overview.md) **§5 M3** |

## 互引

[`../../observability/overview.md`](../../../observability/overview.md)；[`../../agent/agent-orchestration/overview.md`](../../agent/agent-orchestration/overview.md)；[`../billing-management/overview.md`](../billing-management/overview.md)

---

**文档版本**：0.1.3 · **维护**：产品 + SRE · **本版**：**计费协查** **轨 B 事件名**。**承** **0.1.2**。
