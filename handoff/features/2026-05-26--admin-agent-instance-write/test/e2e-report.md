# E2E / 页面验证报告

> 功能包 `2026-05-26--admin-agent-instance-write` · **e2e_verified**

## 概要

- **执行时间**：2026-05-26T16:00:00+0800
- **执行人**：test-agent
- **环境**：
  - 前端：`http://127.0.0.1:5173`（`admin` · Vite proxy `/api` → 8080）
  - 后端 API：`http://127.0.0.1:8080`（`uv run chainup-agent-api`）
- **结论**：✅ **通过**（P0 全绿；首跑前已执行 `alembic upgrade head`）

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| 4 (P0) | 4 | 0 | 0 | 0 |

## P0 用例明细

| 用例 ID | 关联 AC | 场景 | 结果 | 实际 |
|---------|---------|------|------|------|
| E2E-01 | AC-1、AC-7 | 创建实例 | ✅ | `telegramUserId=88100901` → toast「已创建实例 **inst_90576c015fe5cda698bd3543**」；列表出现 `inst_*` 行 |
| E2E-02 | AC-3、AC-8 | I05 编辑 | ✅ | 详情 `inst_90576c…`：`preferredLanguage=zh-Hans` →「已保存实例参数」；表单回显 **zh-Hans** |
| E2E-03 | AC-4、AC-5、AC-9 | I04 登记/解绑 | ✅ | `inst_90576c…` 登记 **sub_e2e_88100901** 成功；`inst_4760d6d…`（存量 BOUND）二次确认解绑 →「已解绑 API 托管」、解绑按钮 **disabled**（NONE）；`instanceId` 未变 |
| E2E-04 | AC-2 | 重复创建 | ✅ | 同 tg **88100901** 再提交 → toast/alert **AGENT_QUOTA_EXCEEDED · 该 Telegram 用户已有 Agent 实例。**；列表仍为 2 行 |

## 验收对照（brief.md）

- [x] 主流程：创建 → 编辑参数 → 登记/解绑
- [x] 错误态：重复创建（E2E-04）；非法 overrides 由 API 层 TC-04 覆盖

## 失败与阻塞项

无（本轮无 blockers）。

## 备注

- **环境前置**：未迁移 DB 时首次创建会 **DATABASE_ERROR**（缺 `instance_overrides_json`）；执行 `cd server && uv run alembic upgrade head` 后重试通过。建议在 `frontend/integration.md` / 本地 README 强调联调前迁移。
- **E2E-03 解绑**：使用存量实例 `inst_4760d6d9244d1b6f9f4e09a2`（已有托管行）；新建实例 `inst_90576c…` 完成 **登记子账户** 路径；**BOUND** 态 Deeplink 绑定未在本轮浏览器复现（API TC-07 已覆盖）。
- **测试数据**：`telegramUserId` **88100901**；勿与生产 tg 冲突。
