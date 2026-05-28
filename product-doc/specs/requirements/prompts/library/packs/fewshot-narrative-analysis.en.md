# Few-shot · ANALYSIS · Market Narrative (English bucket · Git mirror)

<!--
promptPackType: ANALYSIS
library_asset_version: library-0.1.0
align_specs: prompt-management/functions.md §2.5.1, common-phrases §8.6
locale_bucket: en
NOT_ASSEMBLY_LAYER: true
-->

> **Use**: **Git review mirror** for **`promptPackType=ANALYSIS`** **Few-shot snapshot** — **effective only after** **[`prompt-management`](../../../domains/admin/prompt-management/overview.md) Publish** **freezes **`promptPackVersion`**. **Not** an [`ASSEMBLY`](../ASSEMBLY.md) **L1–L6** layer; **insertion order** → [`runtime-injection` §1](../../../domains/admin/prompt-management/runtime-injection.md) (**Few-shot before User**).  
> **Anchor phrases SSOT** → [`common-phrases` §8/§8.7](../../shared/common-phrases.md) (**do not** paste the full §8 table into Few-shot).

---

## 1. Host & count

| Item | Value |
|------|-------|
| **`promptPackType`** | **`ANALYSIS`** |
| **Typical `scenarioId`** | **`market.read_quote`**, **`market.read_deep_analysis`**, **`futures.read_funding`** |
| **Entries per pack** | **1–3** (**§8.6**) |

---

## 2. Entries (Publish body · English bucket)

### FS-NAR-01 · Ticker + anchor in same turn

| Field | Value |
|-------|-------|
| **role** | `user` |
| **content** | How’s BTC looking right now? |
| **tags** | `market.read_quote`, `narrative` |

| Field | Value |
|-------|-------|
| **role** | `assistant` |
| **content** | BTC is around 67,234 — price action feels a bit stuck; 24h is down roughly 1.2% with medium volume (as of 14:30 UTC). For reference only — not investment advice. |
| **tags** | `good`, `sideways`, `lastPrice` |

---

### FS-NAR-02 · Funding + rate number first

| Field | Value |
|-------|-------|
| **role** | `user` |
| **content** | What’s BTC perp funding at? |
| **tags** | `futures.read_funding` |

| Field | Value |
|-------|-------|
| **role** | `assistant` |
| **content** | Funding is about 0.08% (8h basis) — positive and not exactly low; longs look a bit crowded. Rates move with the market. For reference only — not investment advice. |
| **tags** | `good`, `funding_crowded_long`, `fundingRate` |

---

### FS-NAR-03 · Bad vs Good (call-center tone)

| Field | Value |
|-------|-------|
| **role** | `user` |
| **content** | What’s ETH trading at? |
| **tags** | `bad_example` |

| Field | Value |
|-------|-------|
| **role** | `assistant` |
| **content** | ❌ Bad: “According to our data, ETH bid is 3456.00 and ask is 3456.50.” |
| **tags** | `bad`, `customer_service_tone` |

| Field | Value |
|-------|-------|
| **role** | `assistant` |
| **content** | ✅ Good: “ETH is around 3456 — spread is tight and the book looks steady (as of just now). For reference only.” |
| **tags** | `good`, `stable_liquidity` |

---

## 3. MUST NOT

- **Do not** treat this mirror **unchanged** as the **only** production pack for all symbols/locales — **maintain per-symbol/locale versions**.  
- **Do not** **replace **`marketNarrativeHints`** **or** the full §8 anchor table.  
- **Do not** include secrets or real user keys.

---

## 4. Cross-links

- **Review index (non-SSOT duplicate)** → [`analysis/narrative-few-shot-specimens.md`](../../analysis/narrative-few-shot-specimens.md)  
- **Eval** → [`evals/market-narrative.md`](../../../evals/market-narrative.md) **§2.2**  
- **Publish flow** → [`prompt-management/functions.md` §2.5.1](../../../domains/admin/prompt-management/functions.md)

---

**Document version**: library-0.1.0 · **Maintainers**: Product + Prompt owner · **This revision**: initial · 3 entries · Git mirror.
