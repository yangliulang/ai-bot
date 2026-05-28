# 后端实现说明

> **2026-05-28--prompt-runtime-assembly-write** · OP-PR · AC-09a～f 写路径子集

## 环境

- Base URL：`http://127.0.0.1:8080`
- 启动方式：`cd server && uv run chainup-agent-api`

## 鉴权

- `GET /api/v1/internal/prompts/effective`：内部只读，测试/运维走查
- Admin observability / agent execution：与存量 BACKEND_SPEC 一致

## 已实现

| 模块 | 路径 | 说明 |
|------|------|------|
| 写路径拼装审计 | `application/prompt_assembly_write_path_audit.py` | AC-1～3 静态断言；`append_trading_write_prompt_snapshot_if_missing` |
| TRADING 拼装 | `application/agent_prompt_assembly.py` | 复用 `assemble_trading_llm_payload`（三写场景已在 allow-list） |
| TG Type-A 前快照 | `application/telegram_bound_reply.py` | 限价 / 闪兑 / 改单 Type-A 前 `prompt.snapshot` · `stepKind=trading_write` |
| Effective | `application/agent_prompt_effective.py` | 与 timeline / execution accept 同源 binding |
| 测试 | `tests/test_prompt_assembly_write_path.py` | AC-1～7；种子 helper `tests/prompt_write_path_helpers.py` |

## 规格 SSOT

- `product-doc/specs/requirements/domains/admin/prompt-management/runtime-injection.md` **§1～§2**
- closure **OP-PR** · `closure-remaining` §7.2

## 依赖

- `2026-05-27--skill-publish-effective` · `2026-05-27--runtime-write-path-pipeline` **done**
- 迁移种子：`0013`（平台包）· `0018`（flash/limit）· `0026`（amend）；pytest 用 helper 显式 seed

## 示例

```bash
cd server && uv run pytest tests/test_prompt_assembly_write_path.py tests/test_prompt_assembly.py -q

curl -s "http://127.0.0.1:8080/api/v1/internal/prompts/effective?scenarioId=trade.spot.limit_order" | jq '.scenarioId,.promptPackVersion'
```

## 与 OpenAPI 的差异

无。

## 已知问题 / 技术债

- 未强制 Type-A 前 LLM narrate（env 可选，行为不变）
- Git `ASSEMBLY.md` 全文镜像 / Orchestration 动态裁剪仍为 closure gap
