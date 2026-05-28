# 测试用例（API）

> 测试 Agent 在 `backend_done` 后执行。实现前由 product.contract 定稿。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | Admin defaults | `PATCH …/admin/ai/defaults` body `{ intentNluUseLlm: true }` → `GET` | GET 返回 `intentNluUseLlm: true`；row_version/If-Match 行为与存量一致 | P0 |
| TC-02 | AC-2 | LLM 启用 | defaults true（或 env true）；mock `try_llm_intent_nlu_draft` 成功；`POST …/intent/recognize` text=代表性 utterance | 200；`nlu.source=llm_structured_v1` | P0 |
| TC-03 | AC-3 | LLM 回退 | 启用策略；mock `try_llm_intent_nlu_draft` 返回 None | 200；`nlu.source=keyword_v1`；无 5xx | P0 |
| TC-04 | AC-4 | 仅关键词 | defaults false；env false；不 mock LLM | 200；`nlu.source=keyword_v1`；LLM helper 未被调用 | P0 |
| TC-05 | AC-5 | env 覆盖 | defaults `intentNluUseLlm=false`；env `INTENT_NLU_USE_LLM=true`；mock LLM 成功 | 200；`llm_structured_v1` | P0 |
| TC-06 | AC-6 | 有效标志 | TC-02/04 响应 | `effectiveIntentNluUseLlm` 与是否进入 LLM 分支一致 | P0 |
| TC-07 | AC-7 | TG timeline | 模拟已绑定回合或单测 `_append_intent_nlu_prompt_timeline`；effective 启用/关闭各一例 | payload `intentNluLlmEnabled` 等于 effective，非仅 settings 原始 env | P0 |
| TC-08 | AC-8 | 注入禁止 | mock `assemble_intent_nlu_system_prompt` 抛 `PROMPT_INJECTION_FORBIDDEN` | 200；`keyword_v1` | P0 |
| TC-09 | AC-2 | 空输入 | `POST` text=`""` | 200；`EMPTY_INPUT`；不调用 LLM | P1 |

## 契约测试

- [ ] `intentNluUseLlm` 默认 false（新库或缺字段合并后）
- [ ] `effectiveIntentNluUseLlm` 出现在 OpenAPI 示例与响应 schema

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| TC-09 | 空 utterance | CLARIFY；不尝试 LLM |
