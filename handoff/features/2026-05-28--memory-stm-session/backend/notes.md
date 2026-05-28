# 后端实现备注

> **2026-05-28--memory-stm-session** · OP-MEM · `eval.memory.session_clear_stm` / `eval.memory.stm_vs_ltm_intent`

## 规格引用

| SSOT | 路径 |
|------|------|
| Memory Runtime §13 | `product-doc/specs/requirements/Runtime/memory-runtime.md` |
| Eval GWT §4 | `product-doc/specs/requirements/evals/memory-runtime.md` |
| OpenAPI fragment | `product-doc/specs/openapi/components/memory-runtime-schemas.yaml` |
| Design 管线 | `product-doc/specs/design/memory-runtime-injection.md` |
| Telegram §2.8 | `product-doc/specs/requirements/domains/agent/telegram/overview.md` |

## 实现模块

| 模块 | 路径 |
|------|------|
| Eval + 意图 | `server/chainup_agent/application/eval_memory_stm.py` |
| STM store | `server/chainup_agent/application/memory_session_store.py` |
| Router | `server/chainup_agent/api/routers/v1/runtime_memory.py` |
| Schemas | `server/chainup_agent/api/schemas/runtime_memory.py` |
| Tests | `server/tests/test_eval_memory_stm.py` |

## 启动

```bash
cd server && uv run chainup-agent-api
```

## Base URL

`http://127.0.0.1:8080`

## 鉴权

本包 Runtime memory 路由 **无 Bearer**（与 `runtime/skill-operation-spec` 同窗 · 所内/Eval 用）。

## curl 示例

```bash
# 1) 预览（LTM 默认 OFF · semanticNarrativeBlock 为 null）
curl -s "http://127.0.0.1:8080/api/v1/runtime/memory/sessions/tg:123/context?userId=u-demo"

# 2) 清空 STM（须先有 L0 — pytest/宿主写入 store 或后续接线）
curl -s -X POST "http://127.0.0.1:8080/api/v1/runtime/memory/sessions/tg:123/clear-stm" \
  -H "Content-Type: application/json" \
  -d '{"userId":"u-demo"}'

# 3) 清空后再读 context（l0MessageCount=0 · sessionClearedAt 非空）
curl -s "http://127.0.0.1:8080/api/v1/runtime/memory/sessions/tg:123/context?userId=u-demo"

# 4) Eval/fixture — 模拟 FEATURE_SEMANTIC_NARRATIVE ON（SC-STM02 对拍）
curl -s "http://127.0.0.1:8080/api/v1/runtime/memory/sessions/tg:123/context?userId=u-demo&semanticNarrativeEnabled=true"
```

## 错误码

| HTTP | code | 说明 |
|------|------|------|
| — | — | 本包 **不** 严格 404 未知 session；`clear-stm` **幂等** 返回 `clearedAt`（TC-12 P1） |

## 实现备注

- **Store**：进程内 dict（`memory_session_store`）；`reset_memory_session_store_for_tests()` 供 pytest 隔离。
- **LTM 默认 OFF**：`GET …/context` 无 `semanticNarrativeEnabled=true` 时 **`semanticNarrativeBlock=null`**。
- **Semantic fixture**：`set_semantic_fixture(userId, …)` 或 query ON 时使用 `DEFAULT_SEMANTIC_FIXTURE`（Eval SC-STM02）。
- **观测**：`POST clear-stm` 响应含 `eventName=agent.memory.session_cleared`；`build_session_cleared_event()` 供 timeline 接线。
- **意图分流**：`resolve_memory_user_intent()` — 「重新开始/新话题」→ `stm_clear`；「清空记忆/不再记住」→ `ltm_revoke`。

## 自测

```bash
cd server && uv run pytest tests/test_eval_memory_stm.py -q
# 2026-05-27 · 10 passed
```

## 依赖功能包

- `2026-05-28--prompt-runtime-assembly-write` → **done**
- `2026-05-28--skill-contract-eval-staging` → **done**
