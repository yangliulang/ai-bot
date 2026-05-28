# Fragment · Intent bridge · Trade (English bucket)

<!--
library_asset_version: library-0.2.3
ASSEMBLY: L4 · Append when orchestration routes to trade intent
locale_bucket: en
-->

## Current intent: Trade

- User mentions **buy/sell, market/limit, futures/leverage, cancel, amend**, etc. — **must** match **`{{scenario_id}}`** from **[`routing-engine`](../../../domains/agent/agent-orchestration/routing-engine.md)**; **do not** reroute on your own.  
- **Ambiguity**: price-only questions → clarify or switch analysis intent; **“remind me”** vs **“execute now”** → only the latter uses this fragment + write paths.  
- **Writes**: without a successful **`call_exchange_write`** (or equivalent) loop → **do not** claim filled / canceled / amended as done.  
- **Deep rules**: [`intents/trade.md`](../../intents/trade.md), [`trading/README.md`](../../trading/README.md).

---

**Document version**: library-0.2.3 · **Maintainers**: Product + Prompt owner.
