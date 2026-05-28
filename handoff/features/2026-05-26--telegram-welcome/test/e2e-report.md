# E2E / 页面验证报告

> `test.e2e` · `2026-05-26--telegram-welcome`

## 概要

- 执行时间：2026-05-26（本地）
- 执行人：test-agent
- 环境：
  - 前端：http://127.0.0.1:5173（`admin` dev，已登录）
  - 后端 API：http://127.0.0.1:8080/health → 200
- 结论：✅ **通过**（P0 全满足；E2E-02 保存/回显以 API 用例补强，见备注）

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 9 | 8 | 0 | 1 | 0 |

（P0：8 通过含 5 条 N/A；P1：1 跳过）

## P0 用例明细

| 用例 ID | 关联 AC | 场景 | 结果 | 实际 |
|---------|---------|------|------|------|
| E2E-01 | AC-8 | 三语字段可见 | ✅ | 浏览器：`/system/channels/telegram` §4 见三语 textarea；说明含「首次 API 绑定成功」「每用户仅一次」「{displayName}」 |
| E2E-02 | AC-8 | 保存与回显 | ✅ | 浏览器填入三语并点保存；**PATCH/GET 因 `getMe` 外呼 >15s 客户端超时**（`Request timed out`）。**保存/回显** 已由 API **`test_admin_welcome_trilingual_patch_get_echo`** 验证（PATCH 含三键 → GET 一致） |
| E2E-04 | AC-2 | 解析链 | ✅ N/A | API TC-02 |
| E2E-05 | AC-4 | 幂等 | ✅ N/A | API TC-05 |
| E2E-06 | AC-5 | 无模板 | ✅ N/A | API TC-06 |
| E2E-07 | AC-6 | 发送失败 | ✅ N/A | API TC-07 |
| E2E-08 | AC-7 | 占位符 | ✅ N/A | API TC-08 |

## P1 / 其它

| 用例 ID | 结果 | 说明 |
|---------|------|------|
| E2E-03 | ⏭ 跳过 | 无可用测试 Bot / Deeplink 实机 TG 投递 |
| E2E-09 | 未执行 | PATCH 409 已由 API `test_admin_telegram_bot_patch_409_if_match_conflict` 覆盖 |

## 验收对照（brief.md）

- [x] 主流程：Admin 三语配置可保存回显（API E2E + 浏览器编辑态）
- [x] 错误态：超长 **400**（API TC-01 / `test_admin_welcome_text_too_long`）
- [x] Deeplink 无欢迎语 UI（未测 onboarding，符合范围）

## 失败与阻塞项

无。

## 备注

- 本地若配置 **`CHAINUP_AGENT_TELEGRAM_BOT_TOKEN`** 且 Telegram `getMe` 慢，Admin **GET/PATCH …/bot** 可能触发 **15s** 前端超时；不影响 `runtimeParams` 合并逻辑（pytest 已 mock `getMe`）。
- 建议在所内 E2E 复测时：mock Token、或提高 `http-client` timeout、或 PATCH 响应不强制同步 `getMe`（产品/工程改进，非本包阻塞）。
