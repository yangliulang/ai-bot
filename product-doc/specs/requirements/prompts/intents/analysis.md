# Intent · Analysis（条文）

**路径**：`specs/requirements/prompts/intents/analysis.md`。  
**性质**：**意图识别侧下限** — **只读分析族**；**不**替代 **`scenarioId` 寄存器** — [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)、[`exchange-agent/intents`](../../domains/agent/exchange-agent/intents.md)。

**域宿主**：[`exchange-agent/intents` §1～§3](../../domains/agent/exchange-agent/intents.md)；[`market-intelligence`](../../domains/agent/exchange-agent/market-intelligence.md)；[`portfolio-insight`](../../domains/agent/exchange-agent/portfolio-insight.md)；[`read-analyze-and-search-via-agent`](../../flows/read-analyze-and-search-via-agent.md)。

---

## 1. 语义归属（示意）

**典型簇**：行情、Funding、盘口、K 线解读、要闻舆情；**账户理解**（余额/持仓/盈亏 **只读口径**）— [`exchange-agent/intents` §1](../../domains/agent/exchange-agent/intents.md)。

---

## 2. 与其它意图 / 流程的歧义

| 混淆 | 分流 |
|------|------|
| **「盈亏/敞口」** vs **「现价多少」** | 前者 → [`portfolio-read.md`](../analysis/portfolio-read.md)；后者 → [`market-analysis.md`](../analysis/market-analysis.md)。**禁止**用 ticker **冒充**已实现盈亏 — [`intents` §3](../../domains/agent/exchange-agent/intents.md) |
| **分析与下单同桌** | **先拆轮次**：先满足只读答复或追问；**写**单独走 [`../confirmation/order-confirmation.md`](../confirmation/order-confirmation.md) — [`system/system.md`](../system/system.md) §2 读优先 |
| **理财收益咨询** vs **理财申购写** | **仅咨询** → **可落在 analysis 口径或澄清**；**明确申购赎回写** → [`trade.md`](./trade.md) + [`wealth-via-agent`](../../flows/wealth-via-agent.md) — [`boundaries` §8.3](../../domains/agent/exchange-agent/boundaries.md) |

---

## 3. 落地正文（`prompts/analysis/` 四分卷）

**索引**：[`../analysis/README.md`](../analysis/README.md)。

| 文件 | 用途 |
|------|------|
| [`market-analysis.md`](../analysis/market-analysis.md) | 公开行情 / Funding / 盘口 |
| [`technical-analysis.md`](../analysis/technical-analysis.md) | 指标 / 形态 / 支撑阻力 |
| [`sentiment-summary.md`](../analysis/sentiment-summary.md) | 舆情 / 情绪摘要 |
| [`portfolio-read.md`](../analysis/portfolio-read.md) | **账户只读**（余额 / 持仓 / 盈亏聚合） |

**事实口径**：各稿 **「工具与事实」** 节 — **无闭环不编造** — [`hallucination`](../../observability/hallucination.md)、[`../safety/privilege.md`](../safety/privilege.md)。

---

## 4. 失败 / 能力边界

- **`FR-T05` / 私读未绑定** → [`exchange-agent/overview`](../../domains/agent/exchange-agent/overview.md)、[`shared/common-phrases` §1](../shared/common-phrases.md)。  
- **UNKNOWN**：[`shared/common-phrases` §2](../shared/common-phrases.md)、[`Runtime/unknown-state`](../../Runtime/unknown-state.md)。

---

## 5. 路由

- [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)。

---

## 6. 记忆管理意图簇（只读 · 非交易写）

**契约**：[`memory-runtime` §9～§13](../../Runtime/memory-runtime.md)；[`telegram/overview` §2.7～§2.8](../../domains/agent/telegram/overview.md)。

**须** **与** **trade** **分流** — **查看/撤销/清空本会话** **不得** **隐式触发** **`call_exchange_write`**。

| **用户话束（示意）** | **意图** | **宿主 UX** | **禁止** |
|----------------------|----------|-------------|----------|
| 「你记得什么」「我的偏好」「查看记忆」 | **LTM 查看** | **Telegram §2.7.2** | **把摘要写成余额/现价** |
| 「清空记忆」「忘记偏好」「不再记住」 | **LTM 撤销** | **§2.7.3** **二次确认** | **用类型 A 下单卡** |
| 「重新开始」「新话题」「清空本次对话」 | **STM 清空** | **§2.8.2** | **误清 LTM** **或** **仅清 STM 当用户要清偏好** |
| 「关闭记忆功能」 | **能力边界** | **§2.7.4** + **主站入口**（**若冻结**） | **假称已记住** |

**开关 OFF**：**LTM 查看/撤销** **仍** **可识别** — **须** **§2.7.4** **口径**（**`SC-MEM01`**）。

**Eval**：**`eval.memory.*`** — [`evals/scenarios.md`](../../evals/scenarios.md) · **GWT** [`evals/memory-runtime.md`](../../evals/memory-runtime.md)。

---

**文档版本**：1.5.0-mvp · **维护**：产品 + Prompt owner · **本版**：**§6 记忆管理意图簇**。**承** 1.4.0。
