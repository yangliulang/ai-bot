# 测试报告（API）

> 测试 Agent 在 backend_done 后执行并填写，通过后推进 status 至 `tested`。

## 概要

- 执行时间：2026-05-26T18:32:00+0800
- 执行人：test-agent
- 环境：macOS · Python 3.13.9 · `cd server && uv run pytest`（ASGITransport 隔离 SQLite，`CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET` 空 · 与 `conftest` 一致）；本机 API `http://127.0.0.1:8080/health` → **200**（Admin 路由需 Bearer，P0 以 pytest 为准）
- 结论：✅ **通过**

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 8 (P0) | 8 | 0 | 0 | 0 |

## P0 明细

| 用例 ID | 关联 AC | 执行方式 | 结果 | 备注 |
|---------|---------|----------|------|------|
| TC-01 | AC-1 | `test_skill_spec_import_list_count` + bundle seed fixture | ✅ | 列表 ≥11 条；`skill.spot.limit_order` 在列 |
| TC-02 | AC-2 | 同上 + 列表字段断言 | ✅ | `skillId`/`lifecycle` 存在；`?lifecycle=PUBLISHED` 实现见 store（种子均为 PUBLISHED） |
| TC-03 | AC-3 | `test_skill_spec_admin_detail_versions_body` | ✅ | 摘要/versions/body **200**；未知 skill **404**；`bodyMarkdown` > 200 字 |
| TC-04 | AC-4 | `test_skill_spec_publish_higher_version` | ✅ | Publish **200**，`lifecycle=PUBLISHED` |
| TC-05 | AC-5 | `test_internal_effective_and_runtime_pointer` | ✅ | internal **200** + ETag；未发布版 **403** `PROMPT_SKILL_REF_INVALID` |
| TC-06 | AC-6 | 同上 | ✅ | runtime effective 与指针 `skillSpecVersion` 一致 |
| TC-07 | AC-7 | `test_prompt_publish_skill_spec_ref_gate` | ✅ | 未发布 ref → **422**；修正后 Publish **200** |
| TC-08 | AC-9 | `test_publish_version_rollback_rejected` | ✅ | 回退 **400** `PROMPT_SKILL_VERSION_ROLLBACK` |

## 自动化命令

```bash
cd server && uv run pytest tests/test_skill_publish_effective.py tests/test_write_path_pipeline.py -q
# 2026-05-26：13 passed in 1.59s
```

## 契约测试（抽查）

| 项 | 结果 |
|----|------|
| Admin skill-specs camelCase 与 OpenAPI | ✅ pytest 响应字段与路由一致 |
| `PROMPT_SKILL_REF_INVALID` 跨 internal/runtime/prompt | ✅ |
| Publish 后 internal 与 runtime `specDigest` 一致 | ✅（effective 用例内断言 body + version） |

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | — | — | — |

## 备注

- **TC-09**（P1，契约未 complete）未在本轮执行。
- 本机 curl 未带 Bearer 时 Admin 返回 `ADMIN_CONSOLE_AUTH_REQUIRED`；与 `backend/notes.md` 一致，不影响 pytest P0 结论。
- 关联写路径：`test_write_path_pipeline.py` 同批 **13 passed**，与 `runtime-write-path-pipeline` 衔接无回归。
