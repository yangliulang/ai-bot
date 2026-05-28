# Prompt Runtime 写路径拼装链

> 功能 ID：`2026-05-28--prompt-runtime-assembly-write`  
> 产品 Agent 定稿 · Phase-3 **P0** · closure **CC-P1-04 / OP-PR** · **AC-09a～f** 写路径 TRADING 扩面

## 背景

Phase-1/2 已交付 **`chat.faq`**、**公有读**、部分 **现货写** 场景的 **TRADING LLM 拼装**（`agent_prompt_assembly` · 迁移 **`0018`/`0026`**）与 **Intent NLU `prompt.snapshot`**。closure **W2～W3** 仍要求 **写路径** 在 **类型 A 确认前** 具备 **可审计、可 join 的 Prompt 绑定快照**（**SC-OBS04 · AC-09j/k**），且 **拼装语义顺序**（**AC-09a/e**）与 **Tool JSON Schema SSOT**（**AC-09b**）对 **现货写三场景** 可 **pytest 静态断言**。

本包 **不** 宣称 **CC-P1-04 全流程/MR-B 多模块会签已关**；交付 **写路径 TRADING 拼装审计模块 + 时间线 join + pytest + 证据模板**，供 backend/test-agent 回归与 closure **OP-PR** 行勾选。

## 用户故事

- 作为 **Runtime/QA**，我希望 **`assemble_trading_llm_payload`** 对 **`trade.spot.limit_order` / `flash_convert` / `amend_limit_order`** 产出 **`runtime-injection` §1** 顺序块，且 **Tool Spec** 为 **JSON Schema SSOT**。
- 作为 **运营/排障**，我希望 **写路径 Type-A 回合** 时间线含 **`prompt.snapshot`（`trading_write`）**，**`promptPackVersion` / `resolvedPromptBinding`** 与 **`GET …/internal/prompts/effective`** **同窗**。
- 作为 **后端**，我希望 **`prompt_assembly_write_path_audit`**（或等价）**集中** 写路径拼装断言，**复用** 于 pytest 与 Observability 走查。

## 验收标准

- [x] **AC-1**（§1 · 09a）：对 **`trade.spot.limit_order`**、**`trade.spot.flash_convert`**、**`trade.spot.amend_limit_order`**，**`assemble_trading_llm_payload`** **不抛错**；返回 **OpenAI messages** 首条 **system** 合并块 **按序含** **`### PLATFORM_SYSTEM`**、**`### PLATFORM_SAFETY`**、**`### SCENARIO_STRATEGY_TRADE_SPOT_*`**；**observability meta** 含 **`promptAssemblyContract=runtime-injection§1.v1`**。
- [x] **AC-2**（§1 · 09b）：同上三场景拼装结果 **Tool Spec** 段为 **JSON** 且 **含** registry **只读工具** Schema 键（如 **`read_market_ticker`** / **`$schema`/`type`** 等价结构）；**禁止** 以纯 prose 参数表 **替代** Schema 作为 Tool 真源。
- [x] **AC-3**（§1 · 09e）：若 TRADING 包 **Few-shot** 存在，则 **user/assistant 示例对** 在 **Runtime Context / Tool / User** **之前**（pytest 断言 message 下标序）。
- [x] **AC-4**（§2 · 09c/f）：**`GET /api/v1/internal/prompts/effective?scenarioId=`** 对上述三 **`scenarioId`** 在 **已种子/已发布 TRADING 包** 下返回 **200**；体含 **`scenarioId`**、**`promptPackVersion`**、**`resolvedPromptBinding.scenarioId`** 与 **`messages[]`**（**camelCase**）。
- [x] **AC-5**（观测 · 09j/k）：Telegram **写路径 Type-A 展示回合**（限价/闪兑/改单任一）时间线 **含** **`prompt.snapshot`**，**`stepKind=trading_write`**，payload **`scenarioId`** 为 **trade 场景**、**`promptPackVersion`** 与 **`resolvedPromptBinding`** **非空** 且与 AC-4 **effective** 同源。
- [x] **AC-6**（观测 · 09j/k）：同一 **`executionId`** 的 **`GET /api/v1/admin/observability/executions/{executionId}/timeline`** 返回 **200**；**`items[]`** 可 join AC-5 快照；**`GET /api/v1/agent/execution/{executionId}`**（或 Admin executions 列表项）**`promptPackVersion`/`resolvedPromptBinding`** 与 effective **一致**（accept 自动快照）。
- [x] **AC-7**：**`server/tests/test_prompt_assembly_write_path.py`**（新）覆盖 AC-1～AC-4 **P0 全绿**；含 **`prompt_assembly_write_path_audit`**（或等价）模块导入。
- [x] **AC-8**：**`eval/evidence/prompt-runtime-assembly-write.md`** **§1** 已填：**运行命令**、**日期**、**pytest 摘要**；**§2** 链 **三场景** 与 **OP-PR**；**§3** 声明依赖 **`skill-publish-effective`**、**`runtime-write-path-pipeline`** **done**。

## 范围

### 本期包含

- **审计模块 + pytest**（AC-1～AC-4、AC-7）。
- **Runtime 接线**：写路径 Type-A 前 **`prompt.snapshot`（`trading_write`）**（AC-5）；**不** 改变 Type-A 确定性确认文案默认行为。
- **功能包 `eval/evidence/prompt-runtime-assembly-write.md`**（AC-8）。
- **OpenAPI**：验收用 **`GET …/internal/prompts/effective`**、**`GET …/observability/executions/{executionId}/timeline`**、**`GET …/agent/execution/{executionId}`**（只读 · 与存量契约一致）。
- **文档**：`backend/notes.md` 引用 **`runtime-injection` §1～§2**、**`closure-remaining` §7.2 OP-PR**。

### 本期不包含

- **CC-P1-04 / MR-B 全流程关单**（billing/telegram Hosted 会签 · **deferred**）。
- **Git `ASSEMBLY.md` 全文镜像**、**Orchestration 动态裁剪**（AC-09a/e **部分** 仍 **gap**）。
- **合约/杠杆/条件单** 写场景 TRADING 扩面（仅 **现货写三场景** + 可扩展 helper）。
- **改 Prompt 规范正文**；**新 Admin 页面**。
- **强制开启** Type-A 前 LLM narrate（**env 可选** 行为 **不变**）。

## 界面与交互（无页面）

**含页面：否**。验收 = **pytest + internal/effective API + 写路径时间线 join**；存量 Admin Observability **只读**。**E2E 表 N/A**。

## 非功能要求

- 审计模块 **优先纯函数/静态断言**；时间线 **不得** 写入 Secret / 规范全文。
- **`prompt.snapshot`** **追加** 须 **幂等友好**（同回合 **至多一条** `trading_write` 快照）。
- 与 **`BACKEND_SPEC` §2.1** 一致：时间字段 UTC。

## 实现备注

| 项 | 路径（计划） |
|----|----------------|
| 拼装链 | `application/agent_prompt_assembly.py` · `assemble_trading_llm_payload` |
| 写路径审计 | `application/prompt_assembly_write_path_audit.py`（新） |
| TG 写路径 | `application/telegram_bound_reply.py` · Type-A 前 **`_append_trading_write_prompt_snapshot`** |
| Effective | `application/agent_prompt_effective.py` |
| 测试 | `tests/test_prompt_assembly_write_path.py` |
| 规格 SSOT | `product-doc/.../runtime-injection.md` **§1～§2** |
| 依赖包 | `2026-05-27--skill-publish-effective` · `2026-05-27--runtime-write-path-pipeline` **done** |

## 待确认问题

- [x] Q1：与 **Phase-1 `chat.faq` 拼装** 分工 — 本包 **写路径 join + 三场景审计**；闲聊/读路径 **不重复**。
- [x] Q2：**含页面：否** → `skips: [frontend.integrate, test.e2e, designer.review]`。
- [ ] Q3：所内 **可选** 在 evidence **§4** 登记样例 **`executionId`**（P1 · 非 AC 阻塞）。
