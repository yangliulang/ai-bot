# UI 走查 — 2026-05-26--telegram-welcome

> `designer.review` · 2026-05-26

## 走查范围

| 项 | 值 |
|----|-----|
| 路由 | `/system/channels/telegram` |
| 区块 | **§4 用户体验**（`TelegramChannelDetailPage.vue`） |
| 环境 | Admin http://127.0.0.1:5173 · API 8080 |
| 对照 | `brief.md` §界面与交互 · `test/e2e-report.md` |

## 检查项

| # | 项 | 级别 | 结果 | 备注 |
|---|-----|------|------|------|
| 1 | 三语字段信息架构与 brief 一致（简/繁/英独立多行） | P0 | ✅ | 三个 textarea + 中文标签；与 AC-8 / SC-TG-ADMIN-05 一致 |
| 2 | 触发时机与 `{displayName}` 说明可读 | P0 | ✅ | §4 内说明段：首次绑定、每用户一次、占位符规则、4096 上限 |
| 3 | 保存 loading / 409 / 400 错误反馈 | P0 | ✅ | `保存体验配置` 有 `configSaveLoading`；409 提示刷新并 `refreshAll`；超长由服务端 **400** + toast（API/E2E 已验） |
| 4 | 与存量 §4 布局一致（`max-w-xl`、panel、focus ring） | P1 | ✅ | 与同页 H5 模板、默认语言 Select 风格统一 |
| 5 | 字段 placeholder 面向运营可读性 | P1 | ⚠️ 建议 | placeholder 仍为 `TELEGRAM_*` 配置键名；**不阻塞**（label 已为「开通欢迎语 · 简/繁/英」） |
| 6 | §4 区块副标题技术键名密度 | P2 | 建议 | 页头说明含 `keys.md` / `runtimeParams` 键名——存量控制台风格，本包未加重 |

## 问题清单

| ID | 严重度 | 摘要 | 建议负责人 | 状态 |
|----|--------|------|------------|------|
| UI-01 | P1 | textarea placeholder 为环境键名，运营侧略生硬 | frontend-agent（可选迭代） | 待迭代 |
| UI-02 | P2 | 保存前无客户端 4096 字数提示（依赖服务端 400） | frontend-agent（可选） | 待迭代 |
| — | — | 浏览器 PATCH 超时（`getMe` 慢）属工程/环境，非本功能 UI 缺陷 | backend/infra | 见 `test/e2e-report.md` |

**无 P0 未决项。**

## 走查结论

**通过** — Admin 三语欢迎语配置面满足 brief 与 AC-8；主流程信息架构、说明文案、保存态与错误反馈达标。P1/P2 为体验抛光，不阻塞产品验收。

## 截图 / 备注

- 浏览器走查：§4 可见三语输入与说明段（与 E2E-01 一致）。
- Deeplink / onboarding **无**欢迎语 UI（符合 brief「本期不包含」）。
