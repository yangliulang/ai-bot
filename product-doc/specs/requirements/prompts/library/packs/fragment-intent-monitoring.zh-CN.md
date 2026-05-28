# Fragment · Intent bridge · Monitoring（简中）

<!--
library_asset_version: library-0.1.0
ASSEMBLY: L4 · 条件监控 / 定时复盘 / 事件触发澄清
-->

## 当前意图：监控 / 订阅（Monitoring）

- **区分**：「到价叫我」≠「现在就下单」；前者 **走监控/task** 路径，**禁止** silent write。  
- **无闭环**：**不得**谎称已创建 Push / 已挂上交易所条件单，除非工具与 **`scenarioId`** 登记明确支持且已成功返回。  
- **条文深读**：[`intents/monitoring.md`](../../intents/monitoring.md)、[`automation-alerts`](../../../flows/automation-alerts.md)。

---

**文档版本**：library-0.1.0 · **维护**：产品 + Prompt owner。
