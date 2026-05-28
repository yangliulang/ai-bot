# 测试报告（API）

> test-agent · `backend_done` → `tested` · 2026-05-28

## 概要

- 执行时间：2026-05-28T18:00:00+0800
- 执行人：test-agent
- 环境：本地 `http://127.0.0.1:8080`（API 已运行）；pytest 隔离 SQLite + helper seed
- 结论：✅ **通过**

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 8 (P0) | 8 | 0 | 0 | 0 |

| ID | AC | 场景 | 结果 | 备注 |
|----|-----|------|------|------|
| TC-01 | AC-1 | §1 拼装顺序 | ✅ | 三写场景 `assemble_trading_llm_payload` · PLATFORM_SYSTEM → SAFETY → SCENARIO_STRATEGY_* · `promptAssemblyContract` |
| TC-02 | AC-2 | Tool Schema SSOT | ✅ | Tool 段含 JSON Schema / `read.market.ticker` registry 键 |
| TC-03 | AC-3 | Few-shot 位置 | ✅ | user/assistant 示例早于 Context/Tool/User |
| TC-04 | AC-4 | effective API | ✅ | 三 `scenarioId` live **200** + pytest；`promptPackVersion=1` · binding 匹配 |
| TC-05 | AC-5 | trading_write 快照 | ✅ | TG 限价 Type-A · `prompt.snapshot` · `stepKind=trading_write` · 早于 `confirm_prompt` |
| TC-06 | AC-6 | execution join | ✅ | `GET …/agent/execution/{id}` 与 effective / timeline binding 一致 |
| TC-07 | AC-7 | pytest 套件 | ✅ | **7 passed** · `test_prompt_assembly_write_path.py` |
| TC-08 | AC-8 | 证据模板 | ✅ | `eval/evidence/prompt-runtime-assembly-write.md` §1～§3 已填；test-agent 复核 |

### P1（可选）

| ID | 结果 | 备注 |
|----|------|------|
| TC-09 | ✅ | `test_prompt_assembly.py` + `test_agent_llm_chat.py` **19 passed**（合计 **26 passed**） |

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | 无 | — | — |

## 备注

- TC-04 live curl 依赖本地 DB 迁移种子 **0018/0026**；pytest 用 `prompt_write_path_helpers` 显式 seed。
- 本包 `skips` 含 `frontend.integrate` / `test.e2e` / `designer.review`；推进 **`tested`** 后请指挥官 **`/pipeline-skip 2026-05-28--prompt-runtime-assembly-write`**。
