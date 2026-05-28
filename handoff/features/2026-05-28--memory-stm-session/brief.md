# Memory STM 会话基线

> 功能 ID：`2026-05-28--memory-stm-session`  
> 产品 Agent 定稿 · Phase-3 **P2** · closure **OP-MEM** · **`eval.memory.session_clear_stm`** · LTM 默认 OFF

## 背景

Phase-3 已交付 **Prompt Runtime 写路径拼装**、**Skill Eval staging**、**Registry 幂等** 等包（均 **done**）。closure **OP-MEM**（**黄**）仍要求 **STM 实现 MR**：**会话内 L0/L1 召回**、**「重新开始」清空**、**与 LTM 撤销分流**、**`eval.memory.session_clear_stm`** 可重复真跑。

规格 SSOT 已齐：

- [`memory-runtime.md`](../../../product-doc/specs/requirements/Runtime/memory-runtime.md) **§10～§13**（**`FR-STM*` / `SC-STM*`**）
- [`memory-runtime-schemas.yaml`](../../../product-doc/specs/openapi/components/memory-runtime-schemas.yaml)
- [`evals/memory-runtime.md`](../../../product-doc/specs/requirements/evals/memory-runtime.md) **§4**
- [`design/memory-runtime-injection.md`](../../../product-doc/specs/design/memory-runtime-injection.md)

本包把 **STM 会话存储 + 清空 + Prompt 装配预览 + Eval 断言 + 观测事件形状** 固化为 **Python 模块 + Runtime 只读/清空 API + pytest + 证据模板**。**LTM/Semantic 默认 OFF**（**`FEATURE_SEMANTIC_NARRATIVE`** fixture 仅用于 **SC-STM02** 负例对拍）；**不** 交付 LTM 全闭环（B）。

## 用户故事

- 作为 **Runtime/QA**，我希望 **`eval.memory.session_clear_stm`** **0.1.0** 在 pytest 中 **Given/When/Then** 可登记，**多轮后清空** → **下一回合 Prompt 无旧轮**，**Semantic fixture 仍在**。
- 作为 **编排/产品**，我希望 **「重新开始」** 与 **「清空记忆」** **路由到不同管线**（**`eval.memory.stm_vs_ltm_intent`** 方向），**禁止混意图**。
- 作为 **排障**，我希望 **`POST …/memory/sessions/{sessionId}/clear-stm`** 后 **`GET …/context`** 返回 **`sessionClearedAt`** 与 **空 L0**，且 timeline/事件 **可观测** **`agent.memory.session_cleared`**。

## 验收标准

- [x] **AC-1**：新增 **`eval_memory_stm`**（路径见 `backend/notes.md`）暴露 **`EVAL_MEMORY_STM_P0_SET_IDS`**（含 **`eval.memory.session_clear_stm`**、**`eval.memory.stm_vs_ltm_intent`**）及 **`EVAL_VERSION = "0.1.0"`**。
- [x] **AC-2**：新增 **`memory_session_store`**（或等价）：**同一 `sessionId`** 可 **追加 L0 messages**、**登记 session 级 L1 草稿/工具快照**；**`get_l0_for_prompt(session_id)`** 返回 **装配用近轮列表**。
- [x] **AC-3**：**`clear_session_stm(session_id, user_id)`**（**FR-STM01**）：**清除** 该 session **L0 窗口** 与 **活跃 L1 注入源**；**MUST NOT** 修改 **L2/Semantic**（**FR-STM02**）；返回 **`clearedAt`**（UTC）。
- [x] **AC-4**：**`assert_eval_memory_session_clear_stm(state_before, state_after, semantic_fixture)`**：**Given** 同 session **≥3 轮 L0** + **LTM ON fixture**（**`semanticNarrativeBlock` 非空**）· **When** 已执行 clear · **Then** **`l0Messages` 为空或不含被清轮次**；**`semanticNarrativeBlock` 仍 present**（**SC-STM01/02**）。
- [x] **AC-5**：**`invalidate_pending_type_a_on_stm_clear(session_id)`**（**FR-STM03**）：**存在 `waiting_confirmation` 卡** 时 clear 后 **`pendingTypeAValid=False`**；**旧 callback 不得再允许写**（模块断言或 store 标志）。
- [x] **AC-6**：**`build_session_cleared_event(user_id, session_id, cleared_at)`** 返回 **`eventName=agent.memory.session_cleared`** 载荷，**含** **`userId`、`sessionId`、`clearedAt`**（**FR-STM04**）；**`AgentRuntimeMemoryContext.sessionClearedAt`** **同窗** OpenAPI schema。
- [x] **AC-7**：**`resolve_memory_user_intent(utterance)`**（或等价）：**「重新开始/新话题」** → **`intent=stm_clear`**；**「清空记忆/不再记住」** → **`intent=ltm_revoke`**；**二者不得同路由**（**`eval.memory.stm_vs_ltm_intent`**）。
- [x] **AC-8**：**`server/tests/test_eval_memory_stm.py`**（新）覆盖 AC-2～AC-7：**P0 全绿**；含 **至少 1 条 P1**（如 **未绑定 session 负例** 或 **LTM OFF 时 semantic 为空**）。
- [x] **AC-9**：**`POST /api/v1/runtime/memory/sessions/{sessionId}/clear-stm`**（body **`userId`**）→ **200**，**`clearedAt`** 非空，**`sessionClearedAt`** 对账字段；**`GET …/context?userId=`** → **200**，**`l0MessageCount=0`**（清空后），**`semanticNarrativeEnabled`** 默认 **false**（**LTM OFF**）。
- [x] **AC-10**：**`eval/evidence/eval-memory-session-clear-stm.md`** **§1～§3** 已填：**命令**、**日期**、**pytest 摘要**、**两条 `evalSetId` / version**、依赖 **Phase-3 Prompt/Skill 基线 done**。

## 范围

### 本期包含

- **STM 会话存储 + 清空模块**（AC-2～AC-6）。
- **Eval 断言 + 意图分流**（AC-1、AC-4、AC-7）。
- **Runtime API**：**`POST …/clear-stm`**、**`GET …/context`**（AC-9）。
- **pytest + 证据模板**（AC-8、AC-10）。
- **文档**：`backend/notes.md` 引用 **`memory-runtime` §13**、**`evals/memory-runtime.md` §4**、Telegram **§2.8**（**实现备注**，本包 **不** 改 TG 宿主）。

### 本期不包含

- **LTM 全闭环（B）**：**Semantic 写入/撤销 UX**、**`FR-MEM09`** 生产落库、**`contract-closure` §1.2** 对客宣称（**仅 fixture 对拍 SC-STM02**）。
- **`eval.memory.budget_trim`**、**`eval.context.session_execution_tool_bind`**（**另包或后续扩面**；本包 **可** 在 evidence **§4** 链最小回归束 **序号**）。
- **Telegram §2.8 真机按钮/确认卡文案**（宿主 MR；本包 **提供** Runtime API + 模块 **供接线**）。
- **新 Admin 页面**、**Hosted/CC 红项**、**Gateway CC-P1-07**。
- **改 `memory-runtime` / `eval.memory.*` 规范正文**（仅实现对拍）。

## 界面与交互（无页面）

**含页面：否**。验收 = **pytest + Runtime memory API + eval 证据**；**不** 新增 Admin 路由。E2E **N/A**。

## 非功能要求

- Store/Eval **纯内存或 DB 投影** 须 **可单测**；**不得** 在 evidence 写入 Secret / 用户原文全量。
- **LTM 默认 OFF**：**无开关** 时 **`semanticNarrativeBlock` MUST 为 null**（**`SC-MEM01`**）。
- 时间 UTC（**`BACKEND_SPEC` §2.1**）。

## 实现备注

| 项 | 路径（计划） |
|----|----------------|
| Eval / 意图 | `application/eval_memory_stm.py`（新） |
| STM 存储 | `application/memory_session_store.py`（新） |
| Runtime 路由 | `api/routers/v1/runtime_memory.py`（新） |
| Schema | `api/schemas/runtime_memory.py`（新 · 引用 `memory-runtime-schemas` 形状） |
| 测试 | `tests/test_eval_memory_stm.py` |
| 规格 SSOT | `product-doc/specs/requirements/Runtime/memory-runtime.md` **§13** |
| Eval GWT | `product-doc/specs/requirements/evals/memory-runtime.md` **§4** |
| 依赖 | **`prompt-runtime-assembly-write`** · **`skill-contract-eval-staging`** **done**（写路径/Skill 基线） |

## 待确认问题

- [x] Q1：**含页面：否** → `skips: [frontend.integrate, test.e2e, designer.review]`。
- [x] Q2：本包 **实现 (a) 原地清空 L0/L1**；**不** 强制 **(b) 新 `sessionId`**（**`design` MR 可后续冻结**）。
- [ ] Q3：所内 staging **可选** 在 evidence **§4** 追加 **TG `sessionId= tg:{chatId}`** 走查（P1 · 非 AC 阻塞）。
