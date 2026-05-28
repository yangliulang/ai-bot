# 后端说明 — 2026-05-27--skill-publish-effective

> P‑07 · SK-B1～B3 · SK-B5 · `backend_done`

## 启动与环境

| 项 | 值 |
|----|-----|
| 启动 | `cd server && uv run chainup-agent-api` |
| Base URL | http://127.0.0.1:8080 |
| 迁移 | `cd server && uv run alembic upgrade head`（`0029_skill_operation_spec_publish` 含 bundle 种子） |
| 功能包 OpenAPI | `handoff/features/2026-05-27--skill-publish-effective/api.openapi.yaml` |

## 实现位置

| 层 | 模块 |
|----|------|
| ORM | `infrastructure/persistence/models/skill_operation_spec.py` |
| Store / Publish / effective | `application/skill_operation_spec_store.py` |
| skillSpecRef 解析 | `application/skill_operation_spec_ref.py` |
| Prompt Publish 门禁 | `application/skill_operation_spec_publish_gate.py`（`admin_prompt_packs.py` 调用） |
| Admin 路由 | `api/routers/admin_skill_specs.py` |
| Internal effective | `api/routers/internal_skills.py` |
| Runtime effective（DB） | `api/routers/v1/runtime_skill.py` |
| 写路径读规范 | `application/write_path_pipeline.py` → `get_effective_from_db` |
| 种子数据 | `data/skill_specs/runtime-bundle.json`（11 skills） |

## 路由（本包新增/变更）

| Method | Path | 说明 |
|--------|------|------|
| GET | `/api/v1/admin/skill-specs` | 列表；可选 `lifecycle` |
| GET | `/api/v1/admin/skill-specs/{skillId}` | 摘要 + 生效指针 |
| GET | `/api/v1/admin/skill-specs/{skillId}/versions` | 版本履历 |
| GET | `/api/v1/admin/skill-specs/{skillId}/versions/{skillSpecVersion}` | 指定版本 Markdown |
| POST | `/api/v1/admin/skill-specs/{skillId}/publish` | Publish；单调版本 |
| GET | `/api/v1/internal/skills/effective` | Runtime/编排侧读；`If-None-Match` → 304 |
| GET | `/api/v1/runtime/skill-operation-spec/effective` | 行为不变，**数据源改为 DB 指针** |
| POST | `/api/v1/admin/prompt-packs/{id}/publish` | 增量：`variableSchema.skillSpecRef` 门禁（SC-PM-21） |

## 错误码（本包相关）

| code | HTTP | 场景 |
|------|------|------|
| `PROMPT_SKILL_REF_INVALID` | 404/403 | 无指针、版本不存在、scenario 与 skillId 不匹配 |
| `PROMPT_SKILL_VERSION_ROLLBACK` | 400 | Publish 版本 ≤ 已发布最大版本 |
| `VALIDATION_ERROR` | 422 | skillId 空、body 不合规 |

## curl 示例

```bash
# 列表（迁移后应有 11 条 PUBLISHED）
curl -s 'http://127.0.0.1:8080/api/v1/admin/skill-specs'

# 生效指针 + 摘要
curl -s 'http://127.0.0.1:8080/api/v1/admin/skill-specs/skill.spot.limit_order'

# Internal effective（ETag）
curl -sI 'http://127.0.0.1:8080/api/v1/internal/skills/effective?skillId=skill.spot.limit_order'

# Runtime（写路径同源）
curl -s 'http://127.0.0.1:8080/api/v1/runtime/skill-operation-spec/effective?skillId=skill.spot.limit_order'

# Publish（需 Admin Bearer，若已配置 JWT）
curl -s -X POST -H 'Content-Type: application/json' -H 'Authorization: Bearer YOUR_TOKEN' \
  'http://127.0.0.1:8080/api/v1/admin/skill-specs/skill.spot.limit_order/publish' \
  -d '{"skillSpecVersion":"1.0.1","bodyMarkdown":"## 1. ...（≥200 字）"}'
```

## 自测（pytest）

```bash
cd server && uv run pytest tests/test_skill_publish_effective.py tests/test_write_path_pipeline.py -q
```

2026-05-26 本地：**13 passed**。

## 与功能包 OpenAPI 差异

| 项 | 说明 |
|----|------|
| Rollback API | brief 标明 Out of scope，未实现 |
| `scenarioIds` 列表项 | 列表接口暂返回 `[]`；场景映射见 `skill_operation_spec_ref.SCENARIO_PRIMARY_SKILL` |

## 关联

- `product-doc/specs/openapi/admin/prompt-management.yaml`
- `handoff/features/2026-05-27--runtime-write-path-pipeline/`（写路径时间线，已接 DB effective）
