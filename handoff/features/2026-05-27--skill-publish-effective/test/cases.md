# 测试用例（API）

> 测试 Agent 在 backend_done 后执行 P0。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | Import 种子 | 1. `alembic upgrade head`<br>2. 运行 import（见 `backend/notes.md`）<br>3. 查 DB `skill_operation_spec_pointer` | ≥1 行；`skill.spot.limit_order` 指针非空；`body_markdown` 长度 > 1k | P0 |
| TC-02 | AC-2 | 列表 | `GET /api/v1/admin/skill-specs` Bearer | **200**；`items[]` 含 `skillId`、`lifecycle`；`?lifecycle=PUBLISHED` 过滤有效 | P0 |
| TC-03 | AC-3 | 详情三件套 | 对 `skill.spot.limit_order` 依次 GET 摘要 / versions / version body | **200**；body 含 `bodyMarkdown` 全文；未知 skill **404** | P0 |
| TC-04 | AC-4 | Publish 成功 | `POST …/skill-specs/skill.spot.limit_order/publish` Body 更高 `skillSpecVersion` + `bodyMarkdown` | **200**；`lifecycle=PUBLISHED`；指针更新 | P0 |
| TC-05 | AC-5 | internal effective | `GET …/internal/skills/effective?skillId=&skillSpecVersion=` 已发布组合 | **200** + `bodyMarkdown`；未发布 **403/404** + `PROMPT_SKILL_REF_INVALID` | P0 |
| TC-06 | AC-6 | runtime effective DB | import 后 `GET …/runtime/skill-operation-spec/effective?skillId=skill.spot.limit_order` | **200**；`skillSpecVersion` 与指针一致；删除/未发布 skill **404** | P0 |
| TC-07 | AC-7 | Prompt 门禁 | 创建 TRADING 草稿带 `skillSpecRef` 未发布版 → `POST …/publish` | **422** `PROMPT_SKILL_REF_INVALID`；发布后 **200** | P0 |
| TC-08 | AC-9 | 版本回退 | 对已发布 skill `POST publish` 更低 `skillSpecVersion` | **400**（`PROMPT_SKILL_VERSION_ROLLBACK` 或文档码） | P0 |
| TC-09 | AC-4 | 契约门禁 | Publish `contractComplete=false` 的 skill（或缺 body） | **400/422**；无新 PUBLISHED 行 | P1 |

## 契约测试

- [ ] Admin skill-specs 响应字段 camelCase 与 `api.openapi.yaml` 一致
- [ ] `PROMPT_SKILL_REF_INVALID` 与 Runtime/Prompt 路径一致
- [ ] Publish 后 internal 与 runtime 读到的 `specDigest` 一致

## 边界与异常

| ID | 场景 | 预期 |
|----|------|------|
| TC-09 | 契约未 complete | 不写库、指针不变 |
