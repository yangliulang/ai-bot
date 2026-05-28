# Few-shot · ANALYSIS · Market Narrative（简中 · Git 镜像）

<!--
promptPackType: ANALYSIS
library_asset_version: library-0.1.0
align_specs: prompt-management/functions.md §2.5.1, common-phrases §8.6
locale_bucket: zh-Hans
NOT_ASSEMBLY_LAYER: true
-->

> **用途**：**`promptPackType=ANALYSIS`** **场景包** **Few-shot 快照** **之 Git 评审镜像** — **须** **经** **[`prompt-management`](../../../domains/admin/prompt-management/overview.md) Publish** **才** **成为生效 **`promptPackVersion`**。**非** [`ASSEMBLY`](../ASSEMBLY.md) **L1～L6** **层**；**拼装位序** → [`runtime-injection` §1](../../../domains/admin/prompt-management/runtime-injection.md) **（Few-shot 在 User 前）**。  
> **锚句 SSOT** → [`common-phrases` §8/§8.7](../../shared/common-phrases.md)（**禁止** **整表复制进 Few-shot**）。

---

## 1. 宿主与数量

| 项 | 值 |
|----|-----|
| **`promptPackType`** | **`ANALYSIS`** |
| **典型 `scenarioId`** | **`market.read_quote`**、**`market.read_deep_analysis`**、**`futures.read_funding`** |
| **每包条数** | **1～3**（**§8.6**） |

---

## 2. 条目（Publish 正文 · 简中）

### FS-NAR-01 · Ticker + 锚句同窗

| 字段 | 值 |
|------|-----|
| **role** | `user` |
| **content** | BTC 盘面怎么样？ |
| **tags** | `market.read_quote`, `narrative` |

| 字段 | 值 |
|------|-----|
| **role** | `assistant` |
| **content** | BTC 现在在 67234 附近，盘面有点胶着，24h 小幅回落约 1.2%，量能在中等水平（截至 14:30 UTC）。以上仅供参考，不构成投资建议。 |
| **tags** | `good`, `sideways`, `lastPrice` |

---

### FS-NAR-02 · Funding + 费率数值

| 字段 | 值 |
|------|-----|
| **role** | `user` |
| **content** | BTC 永续资金费率什么水平？ |
| **tags** | `futures.read_funding` |

| 字段 | 值 |
|------|-----|
| **role** | `assistant` |
| **content** | 当前资金费率约 0.08%（8h 口径），偏正且不算低，多头拥挤度偏高一点。费率会随行情变，仅供参考，不构成投资建议。 |
| **tags** | `good`, `funding_crowded_long`, `fundingRate` |

---

### FS-NAR-03 · Bad vs Good（客服腔对照）

| 字段 | 值 |
|------|-----|
| **role** | `user` |
| **content** | ETH 现在什么价？ |
| **tags** | `bad_example` |

| 字段 | 值 |
|------|-----|
| **role** | `assistant` |
| **content** | ❌ Bad：「根据数据显示，为您查询到 ETH 买一 3456.00、卖一 3456.50。」 |
| **tags** | `bad`, `customer_service_tone` |

| 字段 | 值 |
|------|-----|
| **role** | `assistant` |
| **content** | ✅ Good：「ETH 现在在 3456 附近，买卖价差很窄，盘口还算稳（截至刚才）。仅供参考。」 |
| **tags** | `good`, `stable_liquidity` |

---

## 3. MUST NOT

- **不得** **无修改** **当作** **全 symbol/locale 唯一生产包** — **须** **按标的与 locale 维护版本**。  
- **不得** **替代 **`marketNarrativeHints`** **或** **§8 全表**。  
- **不得** **含 Secret / 真实用户 Key**。

---

## 4. 互引

- **评审索引（非 SSOT 副本）** → [`analysis/narrative-few-shot-specimens.md`](../../analysis/narrative-few-shot-specimens.md)  
- **Eval** → [`evals/market-narrative.md`](../../../evals/market-narrative.md) **§2.2**  
- **Publish 流程** → [`prompt-management/functions.md` §2.5.1](../../../domains/admin/prompt-management/functions.md)

---

**文档版本**：library-0.1.0 · **维护**：产品 + Prompt owner · **本版**：**初稿 · 3 条 · Git 镜像**。
