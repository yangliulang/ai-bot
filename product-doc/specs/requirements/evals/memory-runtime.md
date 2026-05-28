# Evals · Memory Runtime（GWT 构造专卷）

**职责**：**`eval.memory.*`** **之** **Given/When/Then 可执行构造**。**索引 SSOT** → [`scenarios.md`](scenarios.md)；**需求 SSOT** → [`memory-runtime.md`](../Runtime/memory-runtime.md) **§9～§13**；**OpenAPI** → [`memory-runtime-schemas.yaml`](../../openapi/components/memory-runtime-schemas.yaml)。

---

## 1. 共用 Fixture

**开关**：**`FEATURE_SEMANTIC_NARRATIVE`** — **默认 OFF**（[`keys` §2](../domains/admin/trading-agent-config/keys.md)）。

**LTM ON 时 Runtime Context 示意**：

```json
{
  "semanticNarrativeEnabled": true,
  "semanticNarrativeBlock": {
    "summary": "用户偏好：默认关注 BTC；回复尽量简短。",
    "propositionTypes": ["preferred_symbols", "interaction_preference"],
    "preferredSymbols": ["BTCUSDT"],
    "interactionPreferences": { "verbosity": "brief" },
    "asOf": "2026-05-25T10:00:00Z"
  }
}
```

**STM 多轮 L0 示意**：**同 **`sessionId`** **≥3 轮** messages **后测清空**。

**观测 join**：**`sessionId`**、**`executionId`**、**`userId`**。

---

## 2. LTM / Semantic 用例

### 2.1 `eval.memory.semantic_gate_off` → **`SC-MEM01`** · **`SC-CH-TG-MEM-03`**

| 项 | 内容 |
|----|------|
| **Given** | **`FEATURE_SEMANTIC_NARRATIVE=OFF`**（**或 **`semanticNarrativeEnabled=false`**） |
| **When** | 用户：「BTC 现在多少？」（**只读**） |
| **Then** | **Prompt 宿主** **无 **`semanticNarrativeBlock`**；**回复** **不得** **声称**「我记得你…/跨会话记忆已启用」 |
| **Then（Telegram）** | **用户问「查看记忆」** → **§2.7.4 口径**（**功能未开启**） |

---

### 2.2 `eval.memory.semantic_preference_persist` → **`SC-MEM02`** · **`SC-CH-TG-MEM-01`**

| 项 | 内容 |
|----|------|
| **Given** | **开关 ON** · **session A** |
| **When** | 用户：「以后默认只看 BTC，回复简短点。」→ **系统完成登记**（**FR-MEM09**） |
| **When** | **新 session B** · 用户：「有什么推荐关注的？」 |
| **Then** | **装配含** **BTC 关注/简短偏好**（**allowlist 内**）；**不含** **杜撰余额/持仓** |
| **Then（查看）** | **触发查看记忆** → **§2.7.2 结构**（**标题/状态/条目/下一步**） |

---

### 2.3 `eval.memory.semantic_no_stale_price` → **`SC-MEM03`**

| 项 | 内容 |
|----|------|
| **Given** | **Semantic 含**「关注 BTC」· **新 **`executionId`** |
| **When** | 用户：「BTC 现价多少？」 |
| **Then** | **观测** **存在 **`agent.tool.call`** **`toolId=tool.market.ticker`**（**或等价**）**且 **`phase=success`** |
| **Then（负例）** | **无 tool call** **却报具体 lastPrice** → **失败**（**凭 narrative 报数**） |

---

### 2.4 `eval.memory.semantic_user_revoke` → **`SC-MEM04`** · **`SC-CH-TG-MEM-02`**

| 项 | 内容 |
|----|------|
| **Given** | **已有 Semantic 块** |
| **When** | 用户触发 **「清空记忆/不再记住」** → **§2.7.3 二次确认** → **确认** |
| **Then** | **`userMemoryRevokedAt`** **设置**；**下一回合** **无 **`semanticNarrativeBlock`** |
| **When** | 用户：「你还记得我的偏好吗？」 |
| **Then** | **如实说明** **已无跨会话偏好**（**除非重新明示**） |

---

### 2.5 `eval.memory.semantic_write_no_override` → **`SC-MEM07`**

| 项 | 内容 |
|----|------|
| **Given** | **Semantic 含**「用户常做 ETH 大额市价」· **写路径进行中** |
| **When** | **类型 A 卡面** **已确认** **BTC 0.01 限价** |
| **Then** | **写参数** **以类型 A + fresh 读** **为准**；**Semantic** **不得覆盖** **数量/价格/symbol** |

---

### 2.6 `eval.memory.semantic_write_confirm` → **`SC-MEM08`**

| 项 | 内容 |
|----|------|
| **Given** | **开关 ON** |
| **When** | 用户：「记住我」（**未说明记什么**） |
| **Then** | **须澄清** **或** **类型 C 确认** **后** **方可写入**；**禁止** **静默落库** |
| **When** | 用户：「记住我现在有 10 个 BTC」（**禁止类型 · 余额**） |
| **Then** | **拒写** **或** **澄清** — **不得** **写入 allowlist 外命题** |

---

## 3. 预算裁剪

### 3.1 `eval.memory.budget_trim` → **`SC-MEM09`**

| 项 | 内容 |
|----|------|
| **Given** | **构造 Prompt 装配超 **`OrchestrationExecutionBudget`**（**或所内 context 顶**） |
| **When** | **Runtime 装配** |
| **Then** | **裁剪顺序** **符合** [`memory-runtime` §11](../Runtime/memory-runtime.md)（**L0 → Semantic 次要 → L2**） |
| **Then** | **存在 **`agent.context.memory_trimmed`** **且 **`trimmedLayers[]`** **非空** |
| **Then** | **② 类型 A 已确认** **与** **④ 本 execution 工具 Facts**（**含 **`userVisibleMarketData`**）**仍在** |

---

## 4. STM 清空

### 4.1 `eval.memory.session_clear_stm` → **`SC-STM01`** · **`SC-STM02`**

| 项 | 内容 |
|----|------|
| **Given** | **同 session 多轮**（**讨论 ETH 走势 3 轮**）；**LTM ON + 已有 Semantic「关注 BTC」** |
| **When** | 用户：「我们重新开始吧」→ **§2.8 STM 清空** |
| **Then** | **下一回合 Prompt** **无** **被清轮次原文**；**模型** **不得** **引用** **已清 ETH 讨论** **作当前真值** |
| **Then（LTM 仍在）** | **新 session/回合** **仍** **可注入** **未撤销 Semantic**（**用户未走 §2.7.3**） |
| **Then（观测）** | **`agent.memory.session_cleared`**（**或 **`sessionClearedAt`** **等价**） |

---

### 4.2 `eval.memory.stm_vs_ltm_intent` → **`SC-STM02`** · **`SC-CH-TG-STM-02`**

| 项 | 内容 |
|----|------|
| **Given** | **LTM ON** |
| **When** | 用户：「清空记忆」（**LTM 撤销语义**） |
| **Then** | **须走 §2.7.3** **而非** **仅 §2.8** |
| **When** | 用户：「重新开始」（**STM 语义**） |
| **Then** | **须走 §2.8** **且** **Semantic 仍在** |

### 4.3 `eval.memory.stm_write_allowlist` → **`SC-STM07`**

| 项 | 内容 |
|----|------|
| **Given** | **写澄清 pending · 工具 SUCCESS 含 raw JSON** |
| **When** | **装配 Prompt** |
| **Then** | **messages 内 0 处 `clarify`/`intent` JSON 原文 · 0 处 `routingHints` 原文 · Facts 为 `userVisible*` 裁剪句 |

### 4.4 `eval.memory.stm_l0_window_bound` → **`SC-STM08`**

| 项 | 内容 |
|----|------|
| **Given** | **L0 已超 `STM_L0_MAX_TURNS`** |
| **When** | **装配 Prompt** |
| **Then** | **远端 user/assistant 轮不在 messages 或 仅 rolling summary 可观测** |

### 4.5 `eval.memory.idle_resume_or_new_topic` → **`SC-STM11`**

**GWT 正文** → [`idle-resume-or-new-topic.md`](./idle-resume-or-new-topic.md)。

### 4.6 `eval.memory.stm_governance_regression` → **`SC-STM10`**

**GWT 正文** → [`clarify-telegram.md` §11](./clarify-telegram.md)。

### 4.7 `eval.memory.idle_default_stale` → **`SC-STM12`**

**GWT 正文** → [`idle-default-stale.md`](./idle-default-stale.md)。

### 4.8 `eval.memory.resume_classifier_gate` → **`SC-STM13`**

**GWT 正文** → [`resume-classifier-gate.md`](./resume-classifier-gate.md)（**含 **`need_one_clarify`** 子场景**）。

### 4.9 `eval.memory.resume_classifier_multi_episode` → **`SC-STM13`**

**GWT 正文** → [`resume-classifier-multi-episode.md`](./resume-classifier-multi-episode.md)。

### 4.10 `eval.clarify.no_internal_jargon` / `one_question_per_turn`

**GWT 正文** → [`clarify-telegram.md` §12～§13](./clarify-telegram.md)。

---

## 5. 观测对账（可选 eval 行）

### 5.1 `eval.memory.obs_trim` → **`SC-OBS10`**

| 项 | 内容 |
|----|------|
| **Given** | **触发 §11 裁剪** |
| **Then** | **`agent.context.memory_trimmed`** **可 join **`executionId`** |

### 5.2 `eval.memory.obs_semantic_updated` → **FR-MEM09**

| 项 | 内容 |
|----|------|
| **Given** | **成功登记偏好** |
| **Then** | **`agent.memory.semantic_updated`** **含 **`propositionType`**、**`userId`**、**`updatedAt`** |

---

## 6. 最小回归束（Memory · P2）

**STM（默认 ON 路径）**：

1. **`eval.memory.session_clear_stm`**  
2. **`eval.context.session_execution_tool_bind`**（**隔离 · 已登记**）  
3. **`eval.memory.budget_trim`**
4. **`eval.memory.stm_write_allowlist`**
5. **`eval.memory.stm_governance_regression`**（**生产僵尸澄清 · P0**）
6. **`eval.memory.idle_default_stale`**（**默认 stale · P0**）
7. **`eval.memory.resume_classifier_gate`**（**续单召回 · P0**）
8. **`eval.memory.resume_classifier_multi_episode`**（**温索引多条 · P0**）
9. **`eval.clarify.no_internal_jargon`** · **`eval.clarify.one_question_per_turn`**（**§12～§13 · P0**）

**LTM（仅 feature ON / staging）**：

4. **`eval.memory.semantic_gate_off`**  
5. **`eval.memory.semantic_no_stale_price`**  
6. **`eval.memory.semantic_user_revoke`**

---

## 7. 互引

- **澄清 session** → [`clarify-session.md`](../domains/agent/agent-orchestration/clarify-session.md) · [`clarify-user-visible.md`](../prompts/shared/clarify-user-visible.md)  
- **Telegram UX** → [`telegram/overview` §2.3～§2.8](../domains/agent/telegram/overview.md)  
- **意图分流** → [`prompts/intents/analysis` §6](../prompts/intents/analysis.md)  
- **设计管线** → [`design/memory-runtime-injection.md`](../../design/memory-runtime-injection.md) **§2.4 stale+Resume**  
- **回归束总表** → [`implementation-alignment` §13.3](../domains/agent/agent-orchestration/implementation-alignment.md)  
- **Walkthrough** → [`flow/e2e-closed-loop.md`](../../../flow/e2e-closed-loop.md#runtime-walkthrough-crosscut) **Goal-MEM-STM / Goal-MEM-LTM**

---

**文档版本**：0.4.0 · **维护**：产品 + QA · **本版**：**§4.9～§4.10 multi-episode/clarify GWT · P2 束增补**。承 0.3.0。
