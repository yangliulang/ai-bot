# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-25--slug` |
| 含页面（需 E2E） | 是 / 否 |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 页面行为 |
|----|------|----------|----------|-------------------|
| AC-1 | | TC-01 | E2E-01 | `GET /...` 或 `页面 /` |

<!-- 每个 brief.md 中的 AC-N 必须占一行；API 列填 TC-xx；有页面时 E2E 列必填 E2E-xx -->

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /example | TC-01 |

## 自检

- [ ] AC 数量与 `brief.md` 验收标准一致
- [ ] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [ ] 含页面时每个 AC 至少 1 条 P0 E2E（`test/e2e-cases.md`）
- [ ] `./scripts/check-test-coverage.sh handoff/features/<功能ID>` 退出码 0
