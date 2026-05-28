# Analysis · Narrative Few-shot 登记示意（评审索引 · 非发布 SSOT）

**路径**：`specs/requirements/prompts/analysis/narrative-few-shot-specimens.md`。  
**性质**：**`prompt-management` FR-PM05 / §2.5.1** **之** **登记下限示范** — **须** **经** **场景包 Publish** **才** **成为生效 Few-shot**；**本条** **不是** **`promptPackVersion`** **真源**。

**Publish 正文 Git 镜像（SSOT for MR diff）** → [`library/packs/fewshot-narrative-analysis.zh-CN.md`](../library/packs/fewshot-narrative-analysis.zh-CN.md)（**`en`** → [`.en.md`](../library/packs/fewshot-narrative-analysis.en.md)）。

**锚句 SSOT** → [`common-phrases` §8/§8.7](../shared/common-phrases.md)（**禁止** **整表复制进 Few-shot**）。

---

## 1. 宿主与数量

| 项 | 值 |
|----|-----|
| **`promptPackType`** | **`ANALYSIS`** |
| **典型 `scenarioId`** | **`market.read_quote`**、**`market.read_deep_analysis`**、**`futures.read_funding`** |
| **每包条数** | **1～3**（**§8.6**） |

---

## 2. 示意条目（评审用 · 简中）

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

**要点**：**含 lastPrice + asOf 语义 + §8.2.1 锚意向**；**非客服腔**。

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

**要点**：**`FR-MI07`** — **数值先于锚句**。

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

**要点**：**同窗** [`response-format` §2.1](../shared/response-format.md)；**单轮对照** **即可**。

---

## 3. MUST NOT

- **不得** **把本节** **三例** **无修改** **当作** **生产包唯一内容** — **须** **按 symbol/ locale 维护版本**。  
- **不得** **替代 **`marketNarrativeHints`** **或** **§8 全表**。  
- **不得** **含 Secret / 真实用户 Key**。

---

## 4. 互引

- **Eval 对签** → [`evals/market-narrative.md`](../../evals/market-narrative.md) **§2.2 Bad/Good**  
- **Publish** → [`prompt-management/functions.md` §2.5.1](../../domains/admin/prompt-management/functions.md)；**Git 镜像** → [`library/packs/fewshot-narrative-analysis.zh-CN.md`](../library/packs/fewshot-narrative-analysis.zh-CN.md)

---

**文档版本**：0.1.1 · **维护**：产品 + Prompt owner · **本版**：**链向 library Git 镜像**。**承** 0.1.0。
