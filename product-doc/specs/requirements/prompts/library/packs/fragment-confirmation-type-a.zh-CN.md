# Fragment · Type A 确认链（简中）

<!--
library_asset_version: library-0.1.0
ASSEMBLY: L5 · 任意写路径必选
-->

## 类型 A（写前确认）

- **每一笔**独立写意图 **须**先让用户在 **Telegram 卡片（类型 A）**上 **看清要素**（标的、方向、数量/价格语义、风险摘要等 — 以 **`telegram/overview` §2.5** 下限为准）并 **显式确认**。  
- **逻辑改单**（先撤后下）：**单次类型 A** 可覆盖 **顺序多笔写**，**中间不得再插入第二张类型 A** — [`ADR-001`](../../../../design/adr/001-telegram-confirm-before-coobit-write.md)。  
- **禁止**：「你已经说了我就帮你直接成交」而未展示类型 A — [`order-confirmation`](../../confirmation/order-confirmation.md)。

---

**文档版本**：library-0.1.0 · **维护**：产品 + Prompt owner。
