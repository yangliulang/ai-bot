# Backend 交付说明 · 2026-05-28--registry-tool-idempotency

## 启动

```bash
cd server && uv run chainup-agent-api
```

Base URL：`http://127.0.0.1:8080`

## 实现摘要

| AC | 交付 |
|----|------|
| AC-1 | `registry_idempotency.py` · `REGISTRY_AUDIT_VERSION` · `load_registry_mirror()` |
| AC-2 | `assert_skill_registry_idempotent` · bundle **11** PUBLISHED skillId |
| AC-3 | `assert_tool_registry_idempotent` · B 类 **read.*** 三工具 |
| AC-4 | `assert_enable_allowed` · **SC-MCV1-05** · `REGISTRY_MATRIX_TBD` |
| AC-5 | `assert_obs_tool_call_scenario_join` · **SC-OBS01** |
| AC-6 | `GET /api/v1/admin/tools/registry` |
| AC-7 | `GET /api/v1/admin/tools/registry/idempotency-audit` |
| AC-8 | `tests/test_registry_tool_idempotency.py` |

**数据**：`data/registry/ssot_manifest.json` · `data/skill_specs/runtime-bundle.json` · `exchange_tool_schema_registry.py` · `orchestration_flow_catalog.py`

## 规格 SSOT

- ADR-002 · `trade-assistance.md` §6/§8
- `contract-closure.md` **MR-E · CC-P1-03**
- `product-doc/specs/openapi/admin/tool-management.yaml` **Registry** 子集

## 自测

```bash
cd server && uv run pytest tests/test_registry_tool_idempotency.py -q
```

**2026-05-28**：**10 passed**。

## curl 示例

### Registry 列表（AC-6）

```bash
curl -s http://127.0.0.1:8080/api/v1/admin/tools/registry | jq '{registryVersion, count: (.items|length)}'
```

### 幂等审计（AC-7）

```bash
curl -s http://127.0.0.1:8080/api/v1/admin/tools/registry/idempotency-audit | jq .
```

（本地 JWT secret 为空时可匿名；生产须 Admin Bearer。）

## 错误码

| code | 场景 |
|------|------|
| `REGISTRY_MATRIX_TBD` | Enable 门禁 · matrix **TBD/draft**（模块返回，非 HTTP 默认） |
| `ADMIN_CONSOLE_AUTH_REQUIRED` | 未授权 Admin（JWT 启用时） |

## 依赖

- **`2026-05-27--skill-publish-effective`** **done**（bundle 真源）

## test-agent 提示

本包 `skips` 含 API-only 三步。API P0 通过后：

```text
/pipeline-skip 2026-05-28--registry-tool-idempotency
```
