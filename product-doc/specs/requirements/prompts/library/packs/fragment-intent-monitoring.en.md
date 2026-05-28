# Fragment · Intent bridge · Monitoring (English bucket)

<!--
library_asset_version: library-0.2.3
ASSEMBLY: L4 · Conditional alerts / scheduled pull / event-trigger clarification
locale_bucket: en
-->

## Current intent: Monitoring · subscriptions

- **Separate**: “notify me at price” ≠ “place the trade now”; the former follows monitoring/task paths — **no** silent writes.  
- **No closed loop**: **do not** claim Push created / conditional exchange order placed unless tools + **`scenarioId`** explicitly support it **and** the tool succeeded.  
- **Deep rules**: [`intents/monitoring.md`](../../intents/monitoring.md), [`automation-alerts`](../../../flows/automation-alerts.md).

---

**Document version**: library-0.2.3 · **Maintainers**: Product + Prompt owner.
