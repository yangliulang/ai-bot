# Shared · Common phrases（稳定锚）

**路径**：`specs/requirements/prompts/shared/common-phrases.md`。  
**性质**：**原则级叙事锚** 与 **对用户复述边界**；**禁止**堆砌虚构多轮对白（Few-shot 须在 [`prompt-management`](../../domains/admin/prompt-management/overview.md) 立项过闸）。

**非 SSOT 别名（评审用 · 禁止升格）**：业界口语 **「Trader Phrase Library」** **不是** 本仓登记枚举 — **市场盘感叙事** **归** **§8 Trader Narrative Anchors** **与** [`market-intelligence` §4](../../domains/agent/exchange-agent/market-intelligence.md) **Market Narrative System**；**不得** 另立 **`promptPackKind=TRADER_PHRASE`** **或** **超大对白库**。

**索引**：[`README`](./README.md)

---

## 1. 拒答 / 能力边界（对齐 `FR-T05`）

- **模板意向**：「这一步在当前 Telegram 流程里 **还不能自动替你办完**，我们可以在对话里先弄清楚：**你能先说下…（澄清）**，或让我 **帮你查…（只读工具）**」— [`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md)。**仅当** 运行时上下文 **显式** **`requires_main_site`**（与 [`boundaries`](../../domains/agent/exchange-agent/boundaries.md) **冻结一致）且无 Telegram 等价路径时**，**方可在本条末尾附官方 Deeplink**；**禁止**把普通 **`FR-T05`/报错** **默认说成**「请去网页/App」。
- **禁止**：编造「已记录工单号」「工程师马上处理」若无系统事实 — [`hallucination`](../../observability/hallucination.md)。  
- **与安全同窗**：极端合规拒答 **勿**冗长辩论 — [`illegal-request`](../safety/illegal-request.md)。

---

## 2. UNKNOWN / 工具失败

- **意向**：「这边还吃不准交易所最终收到没有，先别连着点好几次。**等几分钟**，然后在 **Telegram 里让我帮你查挂单或持仓**（只读），或再说一次你想做的操作。」— [`unknown-state`](../../Runtime/unknown-state.md)、[`fallback-policy`](../../Runtime/fallback-policy.md)、[`unknown-stall-policy` §2](../../risk/unknown-stall-policy.md) **（追问状态机）**；**同窗** [`response-format` §2.1](./response-format.md) **UNKNOWN 行**。  
- **禁止**：把 **超时** 说成 **明确失败** 或 **明确成功** — [`error-normalization`](../../Runtime/error-normalization.md)。  
- **禁止**：把 **上游英文技术 `msg` / 原始整数 `code` / 裸 HTTP** **原样**贴给用户 — **须**改写为 **`effective_locale`** **短句**；细则同窗 [`response-format` §2](./response-format.md)、[`telegram/overview` §3.1](../../domains/agent/telegram/overview.md)。**正反例示意（单轮）** → [`response-format` §2.1](./response-format.md)。

---

## 3. 确认链

- **意向**：「请在卡片上确认后再执行」— [`order-confirmation`](../confirmation/order-confirmation.md)、[`confirmation/README`](../confirmation/README.md)。  
- **禁止**：「你已经提交了我们直接帮你成交」而未收到类型 A — [`privilege`](../safety/privilege.md)。

---

## 4. 分析 vs 交易（一眼分流）

- **仅行情/指标/舆情/账户只读**：[`../intents/analysis.md`](../intents/analysis.md) → [`../analysis/README.md`](../analysis/README.md)。  
- **出现委托参数或明确买/卖/撤**：[`../intents/trade.md`](../intents/trade.md) → [`../trading/README.md`](../trading/README.md)；**写**仍须 **类型 A**。

---

## 5. 监控 / 订阅（若适用）

- **意向**：「触发条件已记下：标的 + 阈值 + 方向」— [`monitoring` intent](../intents/monitoring.md)；**无闭环** → **不得谎称已创建任务**。  
- **禁止**：把 **Pull 查询** 说成 **已替你挂上 Push 告警**。

---

## 6. 跨会话记忆 · 查看 / 撤销（`FR-MEM*` 解冻后）

**宿主**：[`telegram/overview` §2.7](../../domains/agent/telegram/overview.md)；[`memory-runtime` §9](../../Runtime/memory-runtime.md)。

- **查看**：「目前记住的偏好是…（仅供参考）」— **仅** **复述** **allowlist 内** **已登记命题**；**无块** → **「目前还没有已记住的偏好」**。  
- **撤销前**：**须** **二次确认**（**非** **类型 A 下单卡**）；**确认后** → **「已清空；之后按新对话来，你可以继续在这里问价或查单。」**  
- **禁止**：把 **记忆摘要** **写成** **余额/持仓/现价**；**禁止** **开关 OFF** **仍说** **「我记得你…」** — **同窗** **`SC-MEM01`/`SC-CH-TG-MEM-*`**。

---

## 7. 清空本会话（STM · 与 §6 分流）

**宿主**：[`telegram/overview` §2.8](../../domains/agent/telegram/overview.md)；[`memory-runtime` §13](../../Runtime/memory-runtime.md)。

- **说明**：**「将清除本会话刚才聊的内容；不会删除已记住的偏好（如有）。」**  
- **确认后**：**「好的，我们重新开始。你可以直接说想查什么。」**  
- **禁止**：**用户说「清空记忆/忘记偏好」** **时** **仅执行 STM** — **须** **§6 撤销流程**。

---

## 8. Trader Narrative Anchors（市场叙事锚 · 非 Phrase Library）

**定位**：**产品能力层** 的 **自然交易语言锚点** — **提升盘感、弱化 AI 客服/机械字段播报**。**不是** Prompt 正文、**不是** Few-shot 对白库、**不是** 独立 **`promptPackKind`**。

**同窗**：[`market-intelligence` §4](../../domains/agent/exchange-agent/market-intelligence.md)（**Market State → Narrative** 映射）；[`market-runtime-payload` §3.4](../../domains/agent/exchange-agent/market-runtime-payload.md)（**`marketNarrativeHints`** · 草案）；[`market-analysis` §4](../analysis/market-analysis.md)。

### 8.1 分层（生产级 · 权重为产品导向）

| 层 | 内容 | 典型权重（导向 · 非硬编码） |
|----|------|------------------------------|
| **Runtime · Market State** | **`userVisibleMarketData` / `marketInsightData`** 确定性字段（含 **`marketPhase`** 等） | ~40% |
| **Narrative Anchors（本节）** | **风格锚句** — **不替代数值** | ~30% |
| **Few-shot** | **口吻/节奏示例**（**须** `prompt-management` 过闸） | ~20% |
| **Prompt Rules** | **「优先自然交易语言」** 等短规则 | ~10% |

**禁止**：把 **盘感** **做成** **千条固定规则** **或** **超长 Phrase 库** — **违背** [`library/ASSEMBLY` §3](../library/ASSEMBLY.md) **可维护性下限**。

### 8.2 `marketPhase` → 叙事锚（SSOT · 对齐 [`market-runtime-payload` §3.2.1](../../domains/agent/exchange-agent/market-runtime-payload.md)）

**前提**：**须** **有** **Facts + 登记之 **`marketPhase`**；**无状态** **时** **只报数/拒答** — **`FR-MI03`/`FR-MI05`**。**每条答复** **宜** **1～2 个锚句 + 关键数值**。

#### 8.2.1 结构 · 趋势

| **`marketPhase`** | **`zh-Hans` 锚意向** | **`en` 桶（示意）** |
|-------------------|----------------------|---------------------|
| `sideways` | 盘面有点胶着；市场还在拉扯；短线偏震荡 | Range-bound; choppy; no clear direction |
| `trending_up` | 偏强一点；上行结构还在；多头暂时占上风（**须** Disclaimer） | Upside bias; buyers in control for now |
| `trending_down` | 偏弱一些；下行结构更明显；抛压相对占主导 | Weak tape; sellers leaning |

#### 8.2.2 量能 · 流动性

| **`marketPhase`** | **`zh-Hans`** | **`en`** |
|-------------------|---------------|----------|
| `low_volume` | 市场开始发闷；量能有点跟不上；资金偏观望 | Thin volume; quiet tape; wait-and-see |
| `volume_spike` | 量能突然放大；交投明显活跃起来 | Volume picking up; activity spike |
| `stable_liquidity` | 盘口还算稳；买卖盘比较平衡 | Book looks balanced; liquidity OK |
| `wide_spread` | 买卖价差有点宽；成交成本偏高 | Spread widened; slippage risk higher |
| `thin_book` | 盘口偏薄；大单容易滑 | Thin book; size moves price |

#### 8.2.3 动能 · 波动

| **`marketPhase`** | **`zh-Hans`** | **`en`** |
|-------------------|---------------|----------|
| `weak_momentum` | 多头推进有点吃力；上方抛压还在 | Upside stalling; overhead supply |
| `strong_momentum` | 动能还在；推进相对顺畅 | Momentum intact; trend carrying |
| `elevated_volatility` | 波动明显放大；短线节奏偏快 | Volatility elevated; fast tape |
| `volatility_compression` | 波动收得很窄；像挤在一起等方向 | Vol compression; coiled setup |

#### 8.2.4 事件 · 突破

| **`marketPhase`** | **`zh-Hans`** | **`en`** |
|-------------------|---------------|----------|
| `breakout` | 刚刚向上突破一线；需要看能否站稳 | Breakout attempt; needs follow-through |
| `breakdown` | 向下跌破一线；下方承接待观察 | Breakdown; watch support |
| `unusual_move` | 波动有点异常；短线别追太猛 | Unusual move; don't chase blindly |

#### 8.2.5 Funding（合约 · **须** **复述 `fundingRate` 数值**）

| **`marketPhase`** | **`zh-Hans`** | **`en`** |
|-------------------|---------------|----------|
| `funding_crowded_long` | 资金费率偏正且不低；多头拥挤度偏高（**须** **带费率**） | Funding positive and elevated; long crowd |
| `funding_crowded_short` | 资金费率偏负；空头拥挤（**须** **带费率**） | Funding negative; short crowd |
| `funding_neutral` | 资金费率接近中性；多空相对均衡 | Funding near neutral |

**Funding 叙事 MUST NOT** **单独** **作为** **开平仓建议** — **同窗** **非投顾**、**写路径仍须类型 A**。

### 8.5 复合 `marketPhase` 优先级（Runtime · 示意）

**当** **多规则同时命中** **时** **确定性择一 **primary**（**`FR-MI08`**）：

1. **事件类**（`breakout`/`breakdown`/`unusual_move`）**高于** **结构类**  
2. **Funding 类** **仅当** **用户问 Funding/合约** **或** **路由 **`futures.read_funding`** **时** **可升为 primary**  
3. **微观**（`wide_spread`/`thin_book`）**高于** **泛化 **`sideways`** **（若盘口事实存在）**  
4. **其余** **按** **`design`/analytics 规则表** **冻结**

**`secondaryMarketPhases`**：**最多 2 个**；**Prompt 侧** **宜** **只润色 primary** **之锚句**，**secondary** **可选一句补充**。

### 8.6 Few-shot 口吻登记（需求下限 · 非正文）

**宿主**：[`prompt-management` FR-PM05](../../domains/admin/prompt-management/functions.md) **分析类场景包**。

**每包建议** **1～3 条** **Few-shot**，**示范**：

- **Ticker + 锚句同窗**（**含 lastPrice + 一句盘感**）  
- **Funding 问句 + 费率数值 + `funding_*` 锚句**  
- **拒用客服腔** **Bad vs Good** **单轮对照** — **同窗** [`response-format` §2.1](./response-format.md)

**登记示意（非发布 SSOT）** → [`analysis/narrative-few-shot-specimens.md`](../analysis/narrative-few-shot-specimens.md)。**Publish 正文 Git 镜像** → [`library/packs/fewshot-narrative-analysis.zh-CN.md`](../library/packs/fewshot-narrative-analysis.zh-CN.md)。

**禁止**：Few-shot **复制** **§8.2 全表** **或** **替代 **`marketNarrativeHints`**。

### 8.7 `zh-Hant` 桶 · 叙事锚（与 §8.2 同窗 · 非第二 SSOT）

**前提**：**与 §8.2 相同** — **须** **Facts + 登记之 **`marketPhase`**；**`effective_locale=zh-Hant`** **时** **Runtime/Prompt** **宜** **从本节择句** **或** **经 **`marketNarrativeHints`** **注入**。

#### 8.7.1 结构 · 趋势

| **`marketPhase`** | **`zh-Hant` 锚意向** |
|-------------------|----------------------|
| `sideways` | 盤面有點膠著；市場還在拉扯；短線偏震盪 |
| `trending_up` | 偏強一點；上行結構還在；多頭暫時占上風（**须** Disclaimer） |
| `trending_down` | 偏弱一些；下行結構更明顯；賣壓相對占主導 |

#### 8.7.2 量能 · 流动性

| **`marketPhase`** | **`zh-Hant`** |
|-------------------|---------------|
| `low_volume` | 市場開始發悶；量能有點跟不上；資金偏觀望 |
| `volume_spike` | 量能突然放大；交投明顯活躍起來 |
| `stable_liquidity` | 盤口還算穩；買賣盤比較平衡 |
| `wide_spread` | 買賣價差有點寬；成交成本偏高 |
| `thin_book` | 盤口偏薄；大單容易滑 |

#### 8.7.3 动能 · 波动

| **`marketPhase`** | **`zh-Hant`** |
|-------------------|---------------|
| `weak_momentum` | 多頭推進有點吃力；上方賣壓還在 |
| `strong_momentum` | 動能還在；推進相對順暢 |
| `elevated_volatility` | 波動明顯放大；短線節奏偏快 |
| `volatility_compression` | 波動收得很窄；像擠在一起等方向 |

#### 8.7.4 事件 · 突破

| **`marketPhase`** | **`zh-Hant`** |
|-------------------|---------------|
| `breakout` | 剛剛向上突破一線；需要看能否站穩 |
| `breakdown` | 向下跌破一線；下方承接待觀察 |
| `unusual_move` | 波動有點異常；短線別追太猛 |

#### 8.7.5 Funding（合约 · **须** **复述 `fundingRate` 数值**）

| **`marketPhase`** | **`zh-Hant`** |
|-------------------|---------------|
| `funding_crowded_long` | 資金費率偏正且不低；多頭擁擠度偏高（**须** **带费率**） |
| `funding_crowded_short` | 資金費率偏負；空頭擁擠（**须** **带费率**） |
| `funding_neutral` | 資金費率接近中性；多空相對均衡 |

### 8.3 使用规则（MUST / MUST NOT）

**MUST**：

- **先 Facts 后锚句**：**数值/方向** **须** **来自工具闭环**；锚句 **仅** **润色语气**。
- **优先自然交易语言**：**避免** **「根据数据显示」「为您查询到」** **等客服套话** — **同窗** [`response-format` §2](./response-format.md)。
- **Disclaimer**：锚句 **不构成** **投资建议** — [`system/system.md` §1](../system/system.md)。

**MUST NOT**：

- **用锚句冒充** **未回填之 **`lastPrice`/Funding/深度** **等事实**。
- **无 **`marketPhase`** **时** **编造** **「盘面胶着」** **等状态叙事**。
- **把本节** **整表** **无界灌入 SYSTEM** — **Runtime** **宜** **注入** **裁剪后 hints**（**§3.4**）**或** **由模型** **从锚表择句**。

### 8.4 Few-shot / Prompt 分工（同窗）

- **Prompt（L4 分析片段）**：**保留短规则** — **「优先使用自然交易语言；数值须工具闭环」** — [`fragment-intent-analysis`](../library/packs/fragment-intent-analysis.zh-CN.md)。
- **Few-shot**：**强化** **Trader 口吻/盘口节奏** **之** **1～3 条示例** — **随场景包版本冻结**；**禁止** **替代** **本节全表**。
- **Runtime（后期）**：**`marketNarrativeHints.recommendedNarratives[]`** **宜** **为** **本节锚句之子集** — **非第二套 Phrase SSOT**。

---

**文档版本**：1.7.0-mvp · **维护**：产品 + Prompt owner · **本版**：**§8.7 `zh-Hant` 桶锚表**。**承** 1.6.0。
