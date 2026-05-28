# AC ↔ 测试追溯矩阵

> product.contract 定稿时必填；`./scripts/check-test-coverage.sh` 据此校验完备性。

## 功能信息

| 项 | 值 |
|----|-----|
| 功能 ID | `2026-05-26--telegram-welcome` |
| 含页面（需 E2E） | 是 |

## 追溯表

| AC | 简述 | API 用例 | E2E 用例 | OpenAPI / 页面行为 |
|----|------|----------|----------|-------------------|
| AC-1 | Admin 欢迎语键读写/超长 | TC-01 | E2E-02 | `GET|PATCH …/channels/telegram/bot` |
| AC-2 | 语言桶与回退链解析 | TC-02 | E2E-04 | `resolve_activation_welcome_text`（E2E N/A） |
| AC-3 | 首次绑定发送欢迎语 | TC-03, TC-04 | E2E-03 | `POST …/api-binding/confirm` · `…/me/…/trading-api` |
| AC-4 | 幂等不再发送 | TC-05 | E2E-05 | `activationWelcomeSkipReason=already_sent`（E2E N/A） |
| AC-5 | 无模板不发送 | TC-06 | E2E-06 | `no_template`（E2E N/A） |
| AC-6 | 发送失败仍 200 | TC-07 | E2E-07 | `send_failed`（E2E N/A） |
| AC-7 | `{displayName}` 渲染 | TC-08 | E2E-08 | 单元 + confirm mock（E2E N/A） |
| AC-8 | Admin 三语独立编辑 | TC-09 | E2E-01, E2E-02 | `/system/channels/telegram` |

## OpenAPI 路径覆盖

| Method | Path | 对应用例 |
|--------|------|----------|
| GET | /api/v1/admin/channels/telegram/bot | TC-01 |
| PATCH | /api/v1/admin/channels/telegram/bot | TC-01, TC-09 |
| POST | /api/v1/agent/api-binding/confirm | TC-03～TC-08 |
| POST | /api/v1/me/agent/bindings/trading-api | TC-04 |

## 自检

- [x] AC 数量与 `brief.md` 验收标准一致
- [x] 每个 AC 至少 1 条 P0 API 用例（`test/cases.md`）
- [x] 含页面时每个 AC 至少 1 条 P0 E2E（`test/e2e-cases.md`）
- [x] `./scripts/check-test-coverage.sh handoff/features/2026-05-26--telegram-welcome` 退出码 0
