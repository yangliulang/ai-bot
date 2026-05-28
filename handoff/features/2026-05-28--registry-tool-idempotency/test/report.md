# 测试报告（API）

> test-agent · `backend_done` → `tested` · 2026-05-28

## 概要

- 执行时间：2026-05-28T21:00:00+0800
- 执行人：test-agent
- 环境：本地 pytest（ASGI client）；Base URL `http://127.0.0.1:8080`
- 结论：✅ **通过**

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 9 (P0) | 9 | 0 | 0 | 0 |

| ID | AC | 场景 | 结果 | 备注 |
|----|-----|------|------|------|
| TC-01 | AC-1 | 版本与镜像 | ✅ | `REGISTRY_AUDIT_VERSION=0.1.0` · 11 skill · 3 tool · catalog scenarios |
| TC-02 | AC-2 | skill 幂等 | ✅ | `test_skill_registry_idempotent` · A 类与 bundle **1:1** |
| TC-03 | AC-3 | tool 幂等 | ✅ | `test_tool_registry_idempotent` · manifest ≡ exchange registry |
| TC-04 | AC-4 | matrix 门禁 | ✅ | frozen/ready **True** · TBD **`REGISTRY_MATRIX_TBD`** |
| TC-05 | AC-5 | OBS join | ✅ | 正例 + 缺 scenario 负例 |
| TC-06 | AC-6 | Registry API | ✅ | **200** · A≥11 + B=3 · filter **entryClass=B** |
| TC-07 | AC-7 | Audit API | ✅ | **200** · **ok=true** · mismatches 空 |
| TC-08 | AC-8 | pytest 套件 | ✅ | **10 passed** |
| TC-09 | AC-9 | 证据模板 | ✅ | `eval/evidence/registry-idempotency-audit.md` §1～§3 复核 |

### P1（可选）

| ID | 结果 | 备注 |
|----|------|------|
| TC-10 | ✅ | `test_enable_allowed_draft_p1` |

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| — | 无 | — | — |

## 备注

- pytest 环境 JWT secret 为空时 Admin 路由匿名 **200**；live curl 若启用 JWT 须 Bearer（与 skill-specs 包一致）。
- 本包 `skips` 含 API-only 三步；推进 **`tested`** 后请 **`/pipeline-skip 2026-05-28--registry-tool-idempotency`**。
