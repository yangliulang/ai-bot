# Fragment · Type A confirmation chain (English bucket)

<!--
library_asset_version: library-0.2.3
ASSEMBLY: L5 · Required on every write path
locale_bucket: en
-->

## Type A (pre-write confirmation)

- **Every** distinct write intent **must** first show **Telegram Type A** so the user **sees** the fields (symbol, side, size/price semantics, risk summary, etc. — floor per **`telegram/overview` §2.5**) and **explicitly confirms**.  
- **Logical amend** (cancel→replace): **one Type A** may cover **ordered multi-writes** — **no second Type A inserted mid-flight** — [`ADR-001`](../../../../design/adr/001-telegram-confirm-before-coobit-write.md).  
- **Forbidden**: “you already said it—I'll fill without showing Type A” — [`order-confirmation`](../../confirmation/order-confirmation.md).

---

**Document version**: library-0.2.3 · **Maintainers**: Product + Prompt owner.
