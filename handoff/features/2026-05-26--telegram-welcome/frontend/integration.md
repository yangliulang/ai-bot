# 前端对接说明

> `frontend.integrate` · Admin 三语欢迎语已联调真实 API。

## 页面与路由

| 页面 | 路由 | 说明 |
|------|------|------|
| Telegram 渠道详情 | `/system/channels/telegram` | **§4 用户体验**：简中 / 繁中 / 英文三语欢迎语 + 触发说明 + `{displayName}` |

## 接口映射

| 页面/操作 | API | 方法 | 备注 |
|-----------|-----|------|------|
| 加载 Bot 配置 | `/api/v1/admin/channels/telegram/bot` | GET | `runtimeParams` → `welcomeZhCn` / `welcomeZhTw` / `welcomeEn` |
| 保存欢迎语/体验 | `/api/v1/admin/channels/telegram/bot` | PATCH | 三键 `TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_*` + 默认语言/H5/能力键；**If-Match** = `configVersion` |
| 绑定（无 FE 变更） | `/api/v1/me/agent/bindings/trading-api` | POST | Deeplink 已有；响应含 `activationWelcomeSent` |

## 实现文件

| 文件 | 变更 |
|------|------|
| `admin/src/entities/telegram/telegram-runtime-params.ts` | `TelegramChannelUxForm` 三语字段；`runtimeParamsFromUxForm` 同时写入三键 |
| `admin/src/pages/system/TelegramChannelDetailPage.vue` | §4 三个 textarea；409 时刷新并提示 |
| `admin/src/entities/telegram/__tests__/telegram-runtime-params.spec.ts` | 映射单测 |

## 自测

```bash
cd admin && npm run test:unit -- --run src/entities/telegram/__tests__/telegram-runtime-params.spec.ts
cd admin && npm run dev   # http://127.0.0.1:5173
```

手动：打开 `/system/channels/telegram` → **4. 用户体验** → 填入三语 → **保存体验配置** → 刷新后回显。

## 联调环境

- Admin：`http://127.0.0.1:5173`
- API：`http://127.0.0.1:8080`（Vite 代理 `/api`）

## Deeplink

无 UI 变更；欢迎语仅在 Telegram 私聊送达。
