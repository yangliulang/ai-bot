# Eval 证据 · Registry SSOT 幂等审计

> 对齐 **CC-P1-03 · MR-E** · ADR-002 · **`trade-assistance` §8** · **auditVersion `0.1.0`**

## §1 本地运行登记

| 项 | 值 |
|----|-----|
| 运行日期 | 2026-05-28 |
| Git SHA | _（部署时填写）_ |
| 执行人 | backend-agent · test-agent（API 测复核） |
| 命令 | `cd server && uv run pytest tests/test_registry_tool_idempotency.py -q` |
| 结果摘要 | **10 passed** |

## §2 审计登记

| 项 | 值 |
|----|-----|
| auditVersion | `0.1.0` |
| skill 幂等 | `assert_skill_registry_idempotent` · bundle **11** skillId |
| tool 幂等 | `assert_tool_registry_idempotent` · B 类 **read.*** 切片 |
| matrix 门禁 | `assert_enable_allowed` · **SC-MCV1-05** |
| OBS join | `assert_obs_tool_call_scenario_join` · **SC-OBS01** |
| API 审计 | `GET …/idempotency-audit` → **ok=true** |

## §3 依赖与 MR-E

| 项 | 值 |
|----|-----|
| 依赖功能包 | `2026-05-27--skill-publish-effective` → **done** |
| SSOT | ADR-002 · `trade-assistance.md` §6/§8 |
| OpenAPI 同窗 | `product-doc/specs/openapi/admin/tool-management.yaml` **Registry** |
| CC-P1-03 / MR-E | **done**（product.accept · closure §3.2 MR-E 可勾选） |

## §4 Staging 扩展（P1 · 可选）

| 备注 | 环境 |
|------|------|
| 未来 **DB registry 表** 落地后复跑同一 audit 命令 | staging |
