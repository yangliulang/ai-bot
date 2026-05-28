# 测试报告（API）

> test.api · `2026-05-26--telegram-welcome`

## 概要

- 执行时间：2026-05-26（本地）
- 执行人：test-agent
- 环境：`server/` · `uv run pytest` · SQLite 测试库 · `http://127.0.0.1:8080/health` → 200
- 结论：✅ **通过**（P0 全通过；P1 回归通过）

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 10 | 10 | 0 | 0 | 0 |

（P0：9；P1：1）

## 用例执行明细

| ID | 优先级 | 结论 | 自动化 / 说明 |
|----|--------|------|----------------|
| TC-01 | P0 | ✅ | `test_admin_welcome_trilingual_patch_get_echo`；`test_admin_welcome_text_too_long` |
| TC-02 | P0 | ✅ | `test_resolve_activation_welcome_text_fallback_chain` |
| TC-03 | P0 | ✅ | `test_confirm_sends_activation_welcome_first_time` |
| TC-04 | P0 | ✅ | `test_me_binding_sends_activation_welcome` |
| TC-05 | P0 | ✅ | `test_confirm_welcome_idempotent_second_confirm` |
| TC-06 | P0 | ✅ | `test_confirm_welcome_no_template_skips_send` |
| TC-07 | P0 | ✅ | `test_confirm_welcome_send_failed_still_200` |
| TC-08 | P0 | ✅ | `test_render_activation_welcome_display_name`；confirm mock 含 `Lee` |
| TC-09 | P0 | ✅ | `test_admin_welcome_trilingual_patch_get_echo`（API 面三语键） |
| TC-10 | P1 | ✅ | `test_api.py::test_admin_telegram_bot_patch_409_if_match_conflict` |

## 契约测试

- [x] `activationWelcomeSent` / `activationWelcomeSkipReason` 与 OpenAPI 一致（confirm + me 响应断言）
- [x] `bindingRowCreated` 在 agent confirm / me 路径均暴露

## 命令

```bash
cd server && uv run pytest \
  tests/test_telegram_activation_welcome.py \
  tests/test_api.py::test_admin_telegram_bot_patch_409_if_match_conflict -q
```

结果：**10 passed**

```bash
./scripts/check-test-coverage.sh handoff/features/2026-05-26--telegram-welcome
```

结果：**退出码 0**

## 失败与阻塞项

无。

## 备注

- **AC-8 Admin 三语 UI** 仍待 `frontend.integrate`；API 面 TC-09 已通过。
- E2E（`test/e2e-cases.md`）在 `frontend_done` 后由 `test.e2e` 执行。
