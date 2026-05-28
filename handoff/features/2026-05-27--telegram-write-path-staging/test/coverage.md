# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-27--telegram-write-path-staging` |
| 含页面（需 E2E） | 否（staging 走读；浏览器 E2E 表 N/A） |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 行为 |
|----|------|----------|----------|----------------|
| AC-1 | 环境 §1 填全 | TC-01 | — | `staging/evidence-log.md` §1 |
| AC-2 | 主轴走读 ≥80% | TC-02 | STG-01 | Telegram + checklist §2 |
| AC-3 | 时间线五段序 | TC-03 | STG-01 | `GET …/timeline` + 导出 |
| AC-4 | Eval 正例 | TC-04 | — | `eval.runtime.pipeline_write_order` |
| AC-5 | 依赖 runtime 包 done | TC-05 | — | evidence §2.3 |
| AC-6 | 负例快检 ≥1 | TC-06 | — | checklist §3 N1～N4 |
| AC-7 | 扩展走读 P1 | TC-07 | — | evidence §3 |
| AC-8 | 关单回填 | TC-08 | — | evidence §5 |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /health | TC-01（可选探活） |
| GET | /api/v1/admin/observability/executions/{executionId}/timeline | TC-03 |
| — | Telegram webhook（无 OpenAPI path） | TC-02 · STG-01 |

## 本地回归（代理，非 staging 替代）

| 文件 | 说明 |
|------|------|
| `server/tests/test_write_path_pipeline.py` | 与 AC-3 同构序断言；**backend/test-agent** 须 green |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API/STG 用例（`test/cases.md`）
- [x] 无页面；E2E 列对 AC-2/3 填 **STG-01**（staging 走读）
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-27--telegram-write-path-staging` 退出码 0
