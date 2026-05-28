# 测试用例（API + pytest）

> test-agent 在 `backend_done` 后：跑 **TC-01～TC-08** pytest/API + 审查 **TC-08** evidence 模板。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | §1 拼装顺序 | 对三写场景调用 `assemble_trading_llm_payload`（见 `test_prompt_assembly_write_path.py`） | **不抛错**；system 块含 **PLATFORM_SYSTEM → PLATFORM_SAFETY → SCENARIO_STRATEGY_***；meta **`promptAssemblyContract`** | P0 |
| TC-02 | AC-2 | Tool Schema SSOT | 同上 · 断言 Tool 段 JSON | 含 registry 工具 Schema 结构；**非** 纯 prose 参数表 | P0 |
| TC-03 | AC-3 | Few-shot 位置 | 种子包含 few-shot 时断言 message 序 | user/assistant 示例 **早于** Context/Tool/User | P0 |
| TC-04 | AC-4 | effective API | 对三 `scenarioId` 调 `GET /api/v1/internal/prompts/effective?scenarioId=` | **200**；**`resolvedPromptBinding.scenarioId`** 匹配；**`promptPackVersion`** 非空 | P0 |
| TC-05 | AC-5 | trading_write 快照 | Telegram 写路径 Type-A 回合（限价/闪兑/改单 pytest）→ timeline | **含** **`prompt.snapshot`** · **`stepKind=trading_write`** · binding 非空 | P0 |
| TC-06 | AC-6 | execution join | 同 **`executionId`**：`GET …/agent/execution/{id}` + Admin timeline | **`promptPackVersion`/`resolvedPromptBinding`** 与 effective **一致** | P0 |
| TC-07 | AC-7 | pytest 套件 | `cd server && uv run pytest tests/test_prompt_assembly_write_path.py -q` | **全通过** | P0 |
| TC-08 | AC-8 | 证据模板 | 打开 `eval/evidence/prompt-runtime-assembly-write.md` §1～§3 | 命令、日期、pytest 摘要、依赖 **done** 已填 | P0 |
| TC-09 | AC-1 | 回归 | `uv run pytest tests/test_prompt_assembly.py tests/test_agent_llm_chat.py -q` | **仍通过**（读路径拼装无回归） | P1 |

## 契约测试

- [ ] TC-04 effective 200 schema 与 OpenAPI 一致
- [ ] TC-05/TC-06 timeline + execution camelCase
- [ ] TC-07 pytest green

## 自动化映射

| 用例 | pytest / 文件 |
|------|----------------|
| TC-01～TC-03, TC-07 | `tests/test_prompt_assembly_write_path.py` |
| TC-04 | `tests/test_prompt_assembly_write_path.py` 或 `test_api.py` effective |
| TC-05～TC-06 | `tests/test_prompt_assembly_write_path.py`（TG 集成） |
| TC-08 | `eval/evidence/prompt-runtime-assembly-write.md`（审查） |
