# Eval 证据 · Prompt Runtime 写路径拼装链

> 对齐 **OP-PR** · **CC-P1-04（写路径子集）** · [`runtime-injection.md`](../../../../product-doc/specs/requirements/domains/admin/prompt-management/runtime-injection.md) **§1～§2**

## §1 本地运行登记

| 项 | 值 |
|----|-----|
| 运行日期 | 2026-05-27 |
| Git SHA | _（部署时填写）_ |
| 执行人 | backend-agent · test-agent（API 测复核） |
| 命令 | `cd server && uv run pytest tests/test_prompt_assembly_write_path.py tests/test_prompt_assembly.py tests/test_agent_llm_chat.py -q` |
| 结果摘要 | **26 passed**（test-agent · 7 write-path + 12 assembly + 7 llm_chat） |

## §2 场景登记

| 项 | 值 |
|----|-----|
| 写路径 TRADING 场景 | `trade.spot.limit_order` · `trade.spot.flash_convert` · `trade.spot.amend_limit_order` |
| 拼装契约 | `runtime-injection§1.v1` · `promptAssemblyContract` |
| trading_write 快照 | `prompt.snapshot` · `stepKind=trading_write` |
| OP-PR 勾选 | **done**（product.accept · closure §7.6 写路径子集可勾选） |

## §3 依赖

| 项 | 值 |
|----|-----|
| 依赖功能包 | `2026-05-27--skill-publish-effective` → **done** |
| | `2026-05-27--runtime-write-path-pipeline` → **done** |
| 迁移种子 | `0018_spot_trade_trading_prompt_seed` · `0026_spot_amend_trading_prompt_seed` |

## §4 Staging 扩展（P1 · 可选）

| executionId | 环境 | 备注 |
|-------------|------|------|
| _（写路径 Type-A 样例）_ | staging | 非本包 AC 阻塞 |
