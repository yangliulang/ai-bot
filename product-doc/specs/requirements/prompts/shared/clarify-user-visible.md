# Shared · Clarify · 用户可见澄清（条文）

**路径**：`specs/requirements/prompts/shared/clarify-user-visible.md`。  
**性质**：**澄清/追问** 的 **Telegram 用户可见下限** — **非** 编排 `routingHints`、**非** 结构化 `clarify` JSON SSOT（后者见 [`governance-map` §2](../governance-map.md) · `pp-runtime-output-contract`）。

**索引**：[`README`](./README.md) · 同窗 [`response-format.md` §2～§2.1](./response-format.md) · [`common-phrases.md` §4](./common-phrases.md)

**域宿主**：[`confirmation-flow` §1 步骤 2](../../domains/agent/agent-orchestration/confirmation-flow.md)；[`Runtime/runtime-invariants` INV-008～010](../../Runtime/runtime-invariants.md)；[`trade-via-agent` 专节 · INV-010](../../flows/trade-via-agent.md#trade-inv-010-semantic-full-book)。

**执行体分工 SSOT（本篇 §0）**：澄清链路 **LLM / 规则 / 组合** **须** **以 §0 表为准** — **禁止** **因** **某段未写「LLM」** **即默认** **全流程** **为** **规则澄清**。**意图识别总表** **同窗** [`implementation-alignment` §8](../../domains/agent/agent-orchestration/implementation-alignment.md)。

---

<a id="clarify-execution-split"></a>

## 0. 执行体分工（LLM / 规则 / 组合）

**性质**：写路径 **澄清与补槽** 的 **执行体归属 SSOT**（**非** OpenAPI 字段名 SSOT）。**MR / 实现评审** **须** **逐行对签** **下表** **「执行体」列**；**Eval** **宜** **按** **组合列** **分断言**（**LLM 文案** vs **Resolver 输出** vs **Gateway 闸**）。

### 0.1 读文档约定（防乌龙）

| 误区 | 正确理解 |
|------|----------|
| 条文只写 Resolver / INV / `missing`，没写 LLM | **不等于** **澄清话术由规则引擎生成** — **用户可见句** **默认** **LLM + Prompt**（§0.2 **R5**），**规则** **只产出** **结构化缺口** |
| 写了 `pp-runtime-clarify` / §7 标准话术 | **LLM 须贴近**，**不是** **规则模板替换引擎** |
| 写了 `orchestrationNextSteps` | **编排规则** **插入只读步**；**对用户那句「我在查余额」** **仍** **LLM/Prompt** |
| 写了「禁止猜测」 | **Runtime/Gateway 硬闸**（INV-008～010），**不是** **把澄清改成 if-else 文案树** |

### 0.2 分层速查

| 代号 | 执行体 | 典型落点 | 产出物 |
|------|--------|----------|--------|
| **L** | **LLM** | Parser / 结构化 `clarify`·`intent` 草案；`pp-runtime-clarify` + 场景 Prompt；STM 注入后的自然语言润色 | 槽位**草稿**、**用户可见**澄清/镜像句、`semanticIntent` **候选** |
| **R** | **规则** | `tradeWriteResolverGate` · `missing[]`；`routing-engine` 寄存器；FEATURE 闸；INV-008～010 · Gateway；`allInOrchestration` | **`missing`**、**可否类型 A**、**`orchestrationNextSteps`**、**路由键终裁** |
| **B** | **BFF/编排** | 会话状态机、只读工具调度、Telegram 出站拼装 | **`executionId`**、只读读余额/持仓、**`inline_keyboard` 载荷**（字面仍同窗 LLM locale） |
| **L→R** | **组合（先 LLM 后规则）** | 模型填 `slots` → Resolver 算缺参 → **规则为准** | 草案被 **接受/剔除**；**禁止** **LLM 单独** **填满** **经济敏感槽**（INV-009/010） |
| **R→L** | **组合（先规则后 LLM）** | Resolver 给出 `missing` / `routingHints` / `orchestrationNextSteps` → Prompt **只负责** **人话** | **事实走向** **由 R 定**；LLM **不得** **增删** **待确认项**（§1） |
| **L↔R** | **组合（对签）** | 意图族 / `scenarioId` 候选（L）+ 寄存器校验（R）；话束启发式（R）+ 用户纠正重读（L） | **冲突** → **澄清或 FR-T05**，**禁止** **静默写** |

### 0.3 澄清情境 · 执行体对照表

| 情境（同窗 §2） | 执行体 | LLM 做什么 | 规则/编排 做什么 |
|-----------------|--------|------------|------------------|
| **听懂 inbound、镜像承接** | **L** | 复述「买入 BNB」等；语气 P1/P6 | — |
| **槽位草稿**（symbol/side/数量/方式） | **L→R** | 从自然语言 **提取草案** | Resolver **`missing[]`** **终裁**；**缺则禁类型 A**（INV-008） |
| **是否仍须用户澄清** | **R→L** | 按 **`missing`** **生成一条追问**（§7） | **不算** **LLM 自觉** — **以 `missing` 为准** |
| **闪兑 vs 限价未选** | **L→R→L** | 听懂「闪兑/限价/市价」 | 路由 **族** **须** 收敛；已选 **则 R 禁止再问** |
| **普通缺数量/价格** | **L→R→L** | 听懂数字或「一半」等 **须解析** 的表述 | **无数字** → **`missing`**；**有用户字面数字** → `provenance=user_input` |
| **ALL_IN / 全部买入/清仓** | **L→R→B→L** | 识别 **语义**、打 **`semanticIntent`**（或话束供 R 启发式） | **`orchestrationNextSteps`** **只读补槽**；**禁** LLM 填 `quoteQty`/`quantity`（INV-010） |
| **交易对歧义** | **L↔R** | 听懂标的 | **默认 `SYMBOL_POLICY_*`**；**一句**确认 **L 润色** |
| **用户纠正理解** | **L**（主）+ **R** | 重读 inbound；§7.5 话术 | **可** **清空错误草案**；**不** **编造** **历史原话** |
| **结构化 `clarify` JSON** | **L** 产出 · **R/B** 消费 | Parser 输出 | **禁止** **原样或改写** **为 Telegram 正文**（§1） |
| **类型 A 前校验失败**（S13/S15） | **R→L** | 解释 **建议价/最小名义** 等 | **校验规则** **拦截**；**新澄清轮** **事实由 R** |
| **Telegram `inline_keyboard`** | **R→B**（载荷）+ **L**（字面） | **同窗语** 按钮文案 | **callback 短 id**、**选项集合** **由编排冻结** · **§2.3.2** |
| **澄清 `cl:*` 点按** | **B→R→L** | **合并 `resolvedSlotsSoFar`** → **Resolver** → **下一键盘/类型 A** | [`clarify-session` §4.2](../../domains/agent/agent-orchestration/clarify-session.md) |
| **澄清态 · 每条 inbound** | **L→R→L/B** | **重读本条**；**镜像承接**；**寒暄/只读/放弃** **分流** | **禁止** **盲复读 **`pendingClarifyKind`** — [`clarify-session` §2.3](../../domains/agent/agent-orchestration/clarify-session.md) · **`SC-CLARIFY-05～07`** |
| **BFF 出站** | **R→B**（载荷）+ **L**（正文） | **键盘/typing** | **禁止** **`routingHints`/`orchestrationNextSteps`** **作正文** — **`SC-CLARIFY-09`** |

### 0.4 多轮澄清 · 谁记上下文

| 能力 | 执行体 | 说明 |
|------|--------|------|
| **已确认槽位累积** | **B + L** | **L1/STM** **注入** **`resolved_slots_so_far`**（**B 持久化**）；LLM **每轮** **读取** **不得** **丢 BNB/闪兑/ALL_IN**（§3） |
| **每 inbound 重跑 Resolver** | **R** | **无状态** **缺参计算**；**不** **假设** **「上轮 LLM 已补齐」** **即可写** |
| **轮次预算 ≤2** | **产品（L 约束）** | Prompt **宜** **收束**；**硬闸** **仍** **是** **INV-008** **非空 `missing`** |

### 0.5 评审 / MR 勾选（摘录）

- [ ] 新增澄清分支 **已在 §0.3 增行** **或** **明示归入** **既有行** **之** **执行体**  
- [ ] **经济敏感数量/价格** **未** **标注为** **纯 L**  
- [ ] **用户可见话术** **未** **标注为** **纯 R**（**除非** **类型 A/B/C/D 冻结模板** — **同窗** [`telegram/overview` §2.5](../../domains/agent/telegram/overview.md)）  
- [ ] **组合链** **写清** **先后**（**L→R** vs **R→L**）  
- [ ] **Demo/BFF** **`postInternalAgentOrchestrationTradeResolver`** **仅** **覆盖** **R 段** — **不** **替代** **L 段** **须在** **Parser/Prompt MR** **单列**

---

## 1. 硬原则

- **澄清句须像聊天**：先 **承接用户已说**（镜像 1 句），再 **只问仍缺且须用户说** 的那一项；**禁止** 把 Prompt/编排/不变式 **原文** 贴给用户。  
- **禁止对用户出现**（含近义改写）：`路由`、`scenarioId`、`写路径`、`FR-T*`、`INV-*`、`禁止猜测`、`仅澄清`、`routingHints`、`call_exchange_write`、`Parser`、`Gateway`、`provenance`、**`多主场景`**、**`须澄清后再路由`**、**`混用两种说法`**（**审计/编排口吻**）。  
- **BFF MUST NOT** 将 **`routingHints`**、**`orchestrationNextSteps`**、**Prompt/Clarify Rules 条文** **原文或近义** **作为 Telegram 正文** — **`SC-CLARIFY-09`**。
- **结构化 `clarify` / `intent` JSON** **仅** 供编排消费 — **不得** 原样或改写为 Telegram 正文（同窗 `pp-runtime-output-contract`）。  
- **若上下文已有 `user_visible_message` 或编排给定澄清要点列表**：**优先润色**，**不得** 改事实走向或 **编造** 用户未说的主题。

---

## 2. 澄清 vs 系统补槽（分工）

| 情形 | 对用户 | 编排/规则 |
|------|--------|-----------|
| **普通缺数量/价格**（无「全部/买满/清仓」语义） | 问「买多少 / 用多少 U / 限价多少」 | Resolver `missing` · INV-008 |
| **「全部买入 / 用全部 U 买 / 全部卖出 / 清仓」**（**INV-010**） | 「我先查一下你子账户可用余额，再给你确认卡」— **不问**「买多少 U」 | **`slot_fill` + 只读余额/持仓** → 落 `quoteQty`/`quantity` |
| **交易对仍歧义**（多种 quote） | 一句确认：「是用 USDT 买 BNB 吗？」 | 默认 **`SYMBOL_POLICY_*`** 所内冻结 |
| **闪兑 vs 限价未选** | 「市价闪兑还是挂限价？」— **用户已说「闪兑」则不再问** | 路由 `flash_convert` / `limit_order` |
| **用户纠正理解**（「你没澄清」「不是这个意思」） | 「可能理解偏了，你刚才想做的是…？」— **禁止** 编造用户历史原话 | 重读 inbound · 见 §3 |
| **寒暄/能力问询**（「你好」「在吗」） | 简短问候 + **能做什么**（查价、余额、下单等）；**不得** 进入写澄清 | **不得** 因残留 session **触发** 闪兑/限价盘问 — **`SC-CLARIFY-07`** |
| **澄清中切只读**（「有哪些币可买」「现价多少」） | **先答只读** 或 **说明可查范围**；**须** **放弃/挂起** 写澄清 session | **读优先** — [`system/system` §2](../system/system.md) · **`SC-CLARIFY-07`** |
| **只读澄清中切写**（「买 100U BNB」「确认下单」） | **abandon 读澄清** · **转写路径/写澄清** | [`read-clarify-session` §2.3](../../domains/agent/agent-orchestration/read-clarify-session.md) · **`SC-READ-CLARIFY-02`** |
| **多标的/scope 只读澄清**（「BTC 和 ETH」「盈亏怎么样」） | **先收敛 symbol 或 scope** · **`rc:*` 可选** | [`read-clarify-session` §2.1](../../domains/agent/agent-orchestration/read-clarify-session.md) · **`SC-READ-CLARIFY-04/06`** |
| **监控草案只读澄清**（「涨到 X 提醒我」） | **补标的/现货合约** · **创建任务仍须类型 A** | **`SC-READ-CLARIFY-07`** |
| **用户放弃写路径**（「不要了」「算了」） | 「好的，已取消。」**或** 等价 — **不得** 再追问闪兑/限价 | **`abandoned=true`** — [`clarify-session` §2.1.1](../../domains/agent/agent-orchestration/clarify-session.md) · **`SC-CLARIFY-06`** |

---

## 3. 会话镜像（STM）

- **同 session 已确认**：标的、方向、闪兑/限价、**全部/买满** 语义 — **后续轮次 MUST 承接**，**禁止** 举例与已确认标的 **无关** 的币对（如用户已说 BNB **却** 只举 BCH/BTC）。  
- **澄清轮次上限（产品导向）**：写路径在 **用户已补齐路由必要信息** 后，**宜** **≤2 轮** 进入 **只读补槽或类型 A**；**禁止** 无限 checklist。  
- **澄清态 inbound（MUST）**：**每条** **新 **`message`** **须** **重跑意图** — **禁止** **连续两轮** ** outbound ** **逐字相同**（**除非** 用户重复同义且仍缺同一槽）— [`clarify-session` §2.3](../../domains/agent/agent-orchestration/clarify-session.md) · **`SC-CLARIFY-05/08`**。

### 3.1 澄清会话 · STM 注入（`resolvedSlotsSoFar`）

**SSOT 字段与 callback 语义**：[`clarify-session.md`](../../domains/agent/agent-orchestration/clarify-session.md) **§3～§4**；OpenAPI **`ClarifySessionSnapshot`**。

**Prompt / STM MUST**：

- **每轮** **写路径澄清** **须** **注入** **`resolvedSlotsSoFar` 人话摘要**（**如**「已确认：买入 BNB、闪兑」）+ **仍缺一项**（**与** **`missing[]` 或 `pendingClarifyKind` **一致**）。  
- **按钮点按（`cl:*`）** **与** **自然语言 follow-up** **同等** **更新** snapshot — **禁止** **仅** **信 LLM 历史** **而不写** snapshot。  
- **验收**：**`SC-CLARIFY-02`**、**`SC-CLARIFY-03`**。

---

## 4. 示意（单轮 · 非 Few-shot）

| 情境 | Bad（禁止） | Good（方向 · 简体） |
|------|-------------|---------------------|
| 全部买入 BNB | 「写路径禁止猜测缺失字段，请指定交易对。」 | 「好的，用你账户里的 USDT **全部**市价买入 BNB。我先查可用余额，再给你确认。」 |
| 已说闪兑仍问市价限价 | 「路由前须澄清：仅 spot market 或 limit？」 | （**不应再问**）直接走闪兑轨 + 余额只读 |
| 用户说 BNB | 举例「BCH-USDT、BTC-USDT」 | 「继续：**BNB/USDT** 闪兑买入，对吗？」 |
| 用户「你好」却盘问方式 | 「请用一句说明：只做现货市价还是限价…须澄清后再路由」 | 「你好，我可以帮你看行情、查余额或下单。你想做什么？」 |
| 用户「都不要了」仍复读 | **同一条** 闪兑/限价澄清 **第 3 次** | 「好的，已取消。需要时再叫我。」 |
| 用户「有哪些币可买」 | **仍问** 闪兑/限价 | **只读 listing/说明** + **写 session abandoned** |

---

## 5. 拼装

- **Publish**：[`governance-map` §2](../governance-map.md) · `pp-runtime-clarify` **须** 吸收本节 **§0～§4、§6～§7** 行为子集（**勿**抄 FR/INV 编号进运营正文）。  
- **Library**：可粘贴 [`../library/packs/fragment-clarify-user-visible.zh-CN.md`](../library/packs/fragment-clarify-user-visible.zh-CN.md)（**L2**）。

---

## 6. 用户体验原则（澄清专节 · 2026-05 增补）

**定位**：在 **合规/不缺参**（INV-008～010）之上，澄清 **须** **以用户任务完成为中心**，**禁止** 「审计式盘问」或「工程师 checklist」。

| 原则 | 用户侧含义 | 实现侧约束 |
|------|------------|------------|
| **P1 · 先懂再办** | 第一句 **复述我理解你要做什么** | 镜像 1 句后再问；见 §3 |
| **P2 · 一次只问一件事** | 每条消息 **最多 1 个** 待补信息（或 **二选一** 按钮） | **禁止** 首条澄清同时列 4 项必填（交易对+数量+价格+方式） |
| **P3 · 能系统做的不问用户** | 「全部买入」**不问**买多少 — **先说**去查余额 | INV-010 · `orchestrationNextSteps` |
| **P4 · 能默认的不反复问** | 已说 BNB → **默认 USDT 交易对**，仅 **一句**确认 | `SYMBOL_POLICY_*` · 见 §7 |
| **P5 · 进度可见** | 查余额 / 校验中 **有一句**「稍等，我在查…」；**首条回复前** **宜** **见** **「正在输入…」** | **入站 `message`**：**须** **`sendChatAction(typing)`** — [`telegram/overview` §2.3.1](../../domains/agent/telegram/overview.md) · **`SC-CH-TG-09`**；长只读 **>5s** **续发 typing 或短进度句** |
| **P6 · 语气一致** | 全程 **同一助手人格**（产品客服，非规则引擎） | **禁止** 轮次间从「我可以帮你…」突变为「须澄清/禁止」体 |
| **P7 · 可退出** | 每轮澄清 **可** 附带「先不买了 / 只查价」；**用户说放弃须停** | 不强制写路径；切 analysis **须** **显式** · **`SC-CLARIFY-06`** |

**写路径澄清轮次预算**（产品导向 · **非** 硬法条）：**从用户表达写意图到类型 A**，**宜 ≤2 轮** 用户可见澄清；第 3 轮仍缺参 → **宜** 收束为 **一句总结 + 一个最关键问题**，**禁止** 加长 checklist。

**与 Telegram 交互**：写路径 **二选一**（闪兑/限价、买/卖、数量口径等）**须** **`inline_keyboard`** — **同窗** [`telegram/overview` §2.3.2～§2.3.3](../../domains/agent/telegram/overview.md) · **`SC-CH-TG-10`**；**禁止** **仅** **开放题让用户打长句。

---

## 7. 标准话术 · 首版（买入 / 闪兑 · `zh-Hans`）

**性质**：**Approved copy 方向** — LLM **须** **贴近** 下列句式 **润色**，**允许** 替换同义口语，**禁止** 偏离事实或 **增删** 待确认项。**动态值** 用 `<…>` 占位。

### 7.1 首次表达买某币（信息不全）

**触发**：如「我想买入 BNB」— **缺** 数量/方式。

**Bad**：一次性列出交易对、数量、价格方式、确认流程四段 checklist。

**Good（单轮 · 优先二选一）**：

> 好的，**买入 BNB**。  
> 你想 **市价闪兑**（按当前价立刻成交），还是 **挂限价单**？  
> **须附** **`inline_keyboard`**：**闪兑** · **限价** — [`telegram/overview` §2.3.2](../../domains/agent/telegram/overview.md) · **`SC-CH-TG-10`**

### 7.2 已选闪兑 · 缺数量（非 ALL_IN）

**Good**：

> 明白，**BNB/USDT 闪兑买入**。  
> 你想 **买多少 BNB**，还是用 **多少 USDT** 买？

**宜附键盘**（**同窗** [`telegram/overview` §2.3.2](../../domains/agent/telegram/overview.md) **数量口径行** · **`cl:qty:base` / `cl:qty:quote`**）：**按 BNB 数量** · **按 USDT 金额** — **用户点选后** **仍可以** **下条消息给数字**；**禁止** **同条** **再问** **闪兑/限价**。

### 7.3 全部买入 / 买满（ALL_IN · 已选或隐含闪兑）

**Good**：

> 好的，用你子账户里的 **USDT 全部** 市价买入 **BNB**。  
> 我先查一下可用余额，马上给你确认卡。

**禁止**：同条再问「买多少 U」或「市价还是限价」（用户已说闪兑/全部时）。

### 7.4 仅需确认交易对

**Good**：

> 继续帮你 **买入 BNB** — 默认 **BNB/USDT**，对吗？

### 7.5 用户纠正（「你没澄清呀」）

**Good**：

> 抱歉，可能理解偏了。  
> 你刚才想 **<用一句话复述 inbound 或请用户重述>** — 我按你的意思重新来。

### 7.6 只读进行中

**Good**：

> 稍等，我在查你子账户的 **USDT 可用余额**…

---

### 7.7 寒暄（无写意图）

**Good**：

> 你好，我是你的交易助手。  
> 我可以帮你看 **行情**、查 **余额/持仓**，或在确认后 **下单**。你想先做哪一件？

**禁止**：**无写意图** **却** **问** 闪兑/限价或列出写路径 checklist。

---

**Eval 抽检**：[`eval.clarify.no_internal_jargon`](../evals/scenarios.md) **+** **首条写澄清** **不得** **>1** **个** **主问句**（**P2**）· [`evals/clarify-telegram.md`](../evals/clarify-telegram.md)（**typing / 键盘 / callback / STM / abandon / read-interrupt / no-repeat**）。

---

**文档版本**：0.5.0-mvp · **维护**：产品 + Prompt owner · **本版**：**§2 寒暄/只读/放弃 · §3 inbound 重意图 · §4 负例扩面 · §7.7 · SC-CLARIFY-05～09 链**。**承** 0.4.0-mvp。
