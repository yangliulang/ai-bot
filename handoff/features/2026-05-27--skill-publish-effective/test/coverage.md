# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-27--skill-publish-effective` |
| 含页面（需 E2E） | 是（Admin `/ai/tool-registry`） |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | DB + bundle import | TC-01 | E2E-01 | 迁移/命令 + 表存在；列表可见种子 |
| AC-2 | Admin 列表 | TC-02 | E2E-01 | `GET …/admin/skill-specs` |
| AC-3 | 详情/履历/正文 | TC-03 | E2E-02 | `GET …/skill-specs/{id}*` |
| AC-4 | Publish | TC-04 | E2E-03 | `POST …/publish` |
| AC-5 | internal effective | TC-05 | E2E-01 | `GET …/internal/skills/effective` |
| AC-6 | runtime effective 读 DB | TC-06 | E2E-01 | `GET …/runtime/skill-operation-spec/effective` |
| AC-7 | Prompt skillSpecRef 门禁 | TC-07 | E2E-04 | `POST …/prompt-packs/{id}/publish` |
| AC-8 | Admin 发布 UI | TC-02, TC-04 | E2E-03 | `/ai/tool-registry` 列表 + Publish |
| AC-9 | 版本单调 | TC-08 | E2E-03 | Publish 低版本 **400**；UI 错误文案 |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/admin/skill-specs | TC-02, E2E-01 |
| GET | /api/v1/admin/skill-specs/{skillId} | TC-03, E2E-02 |
| GET | /api/v1/admin/skill-specs/{skillId}/versions | TC-03 |
| GET | /api/v1/admin/skill-specs/{skillId}/versions/{skillSpecVersion} | TC-03, E2E-02 |
| POST | /api/v1/admin/skill-specs/{skillId}/publish | TC-04, TC-08, E2E-03 |
| GET | /api/v1/internal/skills/effective | TC-05 |
| GET | /api/v1/runtime/skill-operation-spec/effective | TC-06 |
| POST | /api/v1/admin/prompt-packs/{promptPackId}/publish | TC-07 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 或 E2E 用例（`test/cases.md` / `test/e2e-cases.md`）
- [x] 含页面：是；AC-8 有 E2E 列
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-27--skill-publish-effective` 退出码 0
