# 只读澄清 · Read Clarify Session（轻量 SSOT）

**路径**：`specs/requirements/domains/agent/agent-orchestration/read-clarify-session.md`。

**职责**：**只读 / 分析 / 外网检索 / 监控订阅草案** 路径上 **跨轮补槽、消歧、二选一** 的 **轻量会话状态** — **非** 写路径 [`clarify-session.md`](clarify-session.md) **之** **`ClarifySessionSnapshot`** **替代品**。**用户可见话术** → [`prompts/shared/clarify-user-visible.md`](../../../prompts/shared/clarify-user-visible.md) **§2 只读行**；**流程宿主** → [`read-analyze-and-search-via-agent.md`](../../../flows/read-analyze-and-search-via-agent.md) **S2**。

**互引**：[`session-concurrency-policy.md`](session-concurrency-policy.md) **§4**（只读 vs 写并存）；[`clarify-session.md`](clarify-session.md) **§2.3 步 2**（写澄清遇只读 **abandon 写** — **本篇** **对称** **只读澄清遇写 **abandon 读**）；[`memory-runtime.md`](../../../Runtime/memory-runtime.md) **§10**（**只读 Facts 注入** · **不含** **写澄清槽位）；[`routing-engine.md`](routing-engine.md) **§1、§4**；[`intents.md`](../exchange-agent/intents.md) **§3**。

---

## 1. 与写路径澄清的边界（MUST）

| 维度 | **只读澄清（本篇）** | **写澄清** [`clarify-session.md`](clarify-session.md) |
|------|----------------------|------------------------------------------------------|
| **目的** | 补齐 **symbol/范围/监控条件/读侧路由** | 补齐 **写槽位** → **类型 A** |
| **`callback_data` 前缀** | **`rc:`**（read clarify） | **`cl:`** |
| **持久化** | **`ReadClarifySessionSnapshot`**（本篇 §3） | **`ClarifySessionSnapshot`** |
| **类型 A** | **禁止** | **写路径 MUST** |
| **交易所写** | **禁止** **`call_exchange_write`** | **澄清钮不得写**；**类型 A 才可写** |
| **idle stale 温索引** | **v0 默认** **无** **`WarmExecutionEpisode`**（**仅** **可选** **挂起草案** **≤ TTL**） | **§14.6 写路径 stale+Resume** |
| **计费 `executionId`** | **可** **起** **只读 **`executionId`**（**同窗** [`consume-and-bill`](../../../flows/consume-and-bill.md)）**；**与** **写 execution** **可并存** **（** [`session-concurrency-policy` §4](session-concurrency-policy.md) **）** |

**验收**：**`SC-READ-CLARIFY-01`**（**`rc:*` 不触发写**）。

---

## 2. 何时进入 / 退出只读澄清（MUST）

### 2.1 进入条件（任一）

| **触发** | **示例 inbound** | **`pendingReadClarifyKind`（示意）** |
|----------|------------------|--------------------------------------|
| **多标的未指明** | 「BTC 和 ETH 哪个涨得多」 | `multi_symbol_compare` |
| **标的歧义** | 「苹果币多少钱」 | `symbol_disambiguation` |
| **行情 vs 账户** | 「盈亏怎么样」**未说明** **本人持仓** | `scope_portfolio_vs_market` |
| **监控草案缺参** | 「涨到 10 万提醒我」**缺** **合约/现货** | `monitoring_price_threshold` |
| **读路由冲突** | 「分析 + 顺便帮我买一点」 | **先** **只读澄清** **或** **拆句** — **写意图** **见** **§2.3** |

**禁止**：**单 symbol 轻量询价** **且** **路由已收敛** **`market.read_quote`** → **不得** **为了凑轮次** **假澄清**。

### 2.2 退出条件（MUST）

| **事件** | **Then** |
|----------|----------|
| **槽位齐 · Resolver 可跑只读工具链** | **`abandoned=false` → 执行 S4/S5** → **终局后** **清除** **或** **保留 0 轮** |
| **用户放弃**（「不用了」「算了」） | **`abandoned=true`** · **短句确认** |
| **用户转写意图**（买/卖/确认下单） | **`abandoned=true`** · **转** **写路径** **新 **`executionId`** **或** **写澄清** — **§2.3** |
| **TTL 到达** | **`abandoned=true`** · **可选** **一句** **「上次问题已过期，请再说一次」** |
| **只读已答毕 · 用户新话题** | **新 inbound 重意图** → **可** **覆盖** **旧 snapshot** |

**TTL 默认**：**`READ_CLARIFY_SESSION_TTL_SEC`**（**600s · 10min**）— **短于** **写澄清** **`STM_CLARIFY_SESSION_TTL_SEC`** — [`keys` §2.3](../../admin/trading-agent-config/keys.md)。

### 2.3 澄清态 inbound 全序（MUST）

**每条** **`Update.message`** **（** **非** **幂等重投** **）** **须**：

| **步** | **MUST** |
|--------|----------|
| **1 重读** | **L→R**：**本条** **参与** **意图**；**禁止** **仅** **凭** **`pendingReadClarifyKind`** **复读 outbound** |
| **2 写意图分流** | **若** **`invokes_exchange_write=true`** **或** **写槽位草案** → **`ReadClarifySession.abandoned=true`** · **转** [`clarify-session`](clarify-session.md) **/ **`trade-via-agent`** — **`SC-READ-CLARIFY-02`** |
| **3 只读 follow-up** | **合并** **`resolvedReadSlotsSoFar`** → **重跑 Resolver** → **工具或 S6 回复** |
| **4 出站** | **禁止** **内部 routing/scenarioId 字面** — **同窗** **`SC-CLARIFY-09`** |

**对称**：写澄清中只读打断 → **`SC-CLARIFY-07`**；只读澄清中写打断 → **`SC-READ-CLARIFY-02`**。

**轮次预算**：**`READ_CLARIFY_MAX_TURNS`**（**默认 2**）— **超限** **须** **给** **范围缩窄建议** **或** **主站/分步** **（** **非** **写** **）**。

---

## 3. `ReadClarifySessionSnapshot` · 字段下限（产品）

**性质**：**BFF/Runtime 缓存**；**B 阶段** **OpenAPI** **同窗** **`orchestration-runtime-schemas.yaml`** **专项 MR**（**逻辑名** **以下表为准**）。

| 字段 | **必填** | **说明** |
|------|----------|----------|
| **`sessionId`** | MUST | 聊天锚点 |
| **`executionId`** | 推荐 | **本条只读轨** **归因**（**可与** **写 execution** **不同**） |
| **`readClarifyTurn`** | MUST | **从 1 递增** |
| **`intentFamily`** | 推荐 | **`market_read` / `portfolio_read` / `research` / `monitoring_draft` / `mixed`** |
| **`resolvedReadSlotsSoFar`** | MUST | **如** `symbols[]`、`scope`（`market|portfolio`）、`threshold`、`monitoringKind` |
| **`pendingReadClarifyKind`** | 推荐 | **§2.1 枚举** **或** **`missing[]` 首项** |
| **`targetScenarioId`** | 推荐 | **收敛后** **`market.read_quote`** **等** — **仍** **经** **寄存器校验** |
| **`effectiveLocale`** | 推荐 | **同窗** **Telegram §2.4** |
| **`expiresAt`** | 推荐 | **默认** **`READ_CLARIFY_SESSION_TTL_SEC`** |
| **`abandoned`** | 可选 | **放弃/转写/TTL** |

**STM 注入（轻量）**：**须** **含** **`resolvedReadSlotsSoFar` 人话摘要** + **仍缺一项** — **禁止** **注入** **写路径 **`resolvedSlotsSoFar`** **或** **`pendingClarifyKind`** **（** **防串轨** **）**。

**验收**：**`SC-READ-CLARIFY-03`**。

---

## 4. `callback_data` · `rc:*` 注册表（首版 · MUST）

**约束**：**≤64B**；**禁止** **「确认下单」** **类** **动词**。

### 4.1 键 → 槽位（v0 冻结集）

| **`callback_data`** | **用户动作** | **写入 `resolvedReadSlotsSoFar`** |
|---------------------|--------------|-------------------------------------|
| **`rc:sym:BTC`** | 选 **BTC**（**示例**） | `primarySymbol=BTCUSDT`（**或** **所内归一**） |
| **`rc:sym:ETH`** | 选 ETH | 同上模式 |
| **`rc:scope:market`** | **问行情** | `scope=market` |
| **`rc:scope:portfolio`** | **问我的持仓/盈亏** | `scope=portfolio` **→** **须** **FR-T02** |
| **`rc:mon:spot`** | **现货到价提醒**（**草案**） | `monitoringAssetClass=spot` |
| **`rc:mon:fut`** | **合约到价** | `monitoringAssetClass=futures` |
| **`rc:cancel`** | **不问了** | **→** **`abandoned=true`** |

**扩展**：**理财/杠杆监控** **须** **另 MR** **增键** — **禁止** **未登记 **`rc:*`**。

### 4.2 点按序（MUST）

1. **`answerCallbackQuery`**  
2. **校验** **未 abandoned、未 TTL**  
3. **合并槽位** · **`readClarifyTurn++`**  
4. **重跑 Resolver（R）** → **只读工具链或下一 **`rc:*` 键盘**  
5. **L 润色 outbound** — **禁止** **跳过 Resolver 直接假答数字**

**与 session 并发**：**`rc:*` 与 `message` 同窗队列** — [`session-concurrency-policy` §2](session-concurrency-policy.md)。

---

## 5. 场景叙事表（评审用）

| **用户话束** | **Then（产品）** |
|--------------|------------------|
| 「BTC 和 ETH 哪个涨得多」 | **二选一或** **先比再答** · **Facts 齐后** **一次 S6** |
| 「盈亏怎么样」 | **先问** **「看全市场还是你的持仓？」** **`rc:scope:*`** |
| 「涨到 10 万提醒我」 | **补** **现货/合约 · 标的** · **仍只读** **直到** **用户确认创建监控任务** **（** **写路径** **另 **`executionId`** **+ 类型 A** **）** |
| 只读澄清中「那帮我买 100U」 | **abandon 读** · **转** **写澄清** — **`SC-READ-CLARIFY-02`** |
| 只读澄清中「你好」 | **寒暄** · **可** **abandon 读** · **0** **复读 scope 盘问** |

---

## 6. 与监控任务创建交界（MUST）

**只读澄清** **可** **收集** **监控草案槽位**；**创建 `taskId` / 所内写** **须**：

1. **结束** **只读澄清**（**槽位齐**）  
2. **新起** **写路径 **`executionId`**（**或** **监控族** **既定起票规则**）  
3. **类型 A** — [`automation-alerts.md`](../../../flows/automation-alerts.md)、[`monitoring-tasks.md`](../exchange-agent/monitoring-tasks.md)

**禁止**：**一张 **`rc:*` 键盘** **直接** **创建** **监控写**。

---

## 7. 验收（`SC-READ-CLARIFY-*`）

| ID | Then |
|----|------|
| **`SC-READ-CLARIFY-01`** | **`rc:*`** **不触发** **`call_exchange_write`**；**键盘无** **写确认动词** |
| **`SC-READ-CLARIFY-02`** | **只读澄清 active + 写意图 inbound** → **读 session `abandoned`** · **转写路径** |
| **`SC-READ-CLARIFY-03`** | **第 2 轮 STM/Prompt** **含** **只读槽位摘要** · **0** **写澄清槽位混入** |
| **`SC-READ-CLARIFY-04`** | **多标的比较** **须** **先收敛 symbol 集或 scope** **再** **调工具** |
| **`SC-READ-CLARIFY-05`** | **每条 inbound 重意图** · **禁止** **同字 outbound 复读**（**同窗** **`SC-CLARIFY-08`**） |
| **`SC-READ-CLARIFY-06`** | **portfolio scope** **须** **FR-T02** **通过后再答私有数据** |
| **`SC-READ-CLARIFY-07`** | **监控草案** **仅** **澄清槽位** · **创建任务** **须** **独立类型 A** |

**Eval**：[`evals/read-clarify-telegram.md`](../../../evals/read-clarify-telegram.md)。

---

**文档版本**：1.0.0-mvp · **维护**：产品 + Agent Runtime owner · **本版**：**P1 首卷** — **轻量只读澄清 · `rc:*` · 与写澄清对称分流**。
