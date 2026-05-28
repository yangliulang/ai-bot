# 前端对接

> **frontend.integrate** 已完成 · 2026-05-27

## 联调结论

| 项 | 值 |
|----|-----|
| 路由 | **`/ai-settings`** · **`?tab=runtime`**（使用策略 Tab） |
| 页面 | `admin/src/pages/ai/AiSettingsPage.vue` — 顶部增量 **网关策略** |
| 组件 | `admin/src/features/ai-settings/GatewayPolicyPanel.vue` |
| 常量 | `admin/src/features/ai-settings/gateway-policy-constants.ts` |
| API 客户端 | `admin/src/shared/api/admin-ai-settings.ts`（`TelegramLlmNarrateFlags` · `intentNluUseLlm`） |

## 接口映射（已实现）

| 页面/操作 | Method | Path | 实现 |
|-----------|--------|------|------|
| 加载网关策略 | GET | `/api/v1/admin/ai/defaults` | `loadAll` → `applyGatewayPolicy` |
| 保存 NLU 开关 | PATCH | `{ intentNluUseLlm }` | `GatewayPolicyPanel` 切换即 PATCH + Toast |
| 保存 narrate 单场景 | PATCH | `{ telegramLlmNarrate: { key } }` | 同上，仅单键 |
| 存量模型策略 | PATCH | `scenario*` 等 | 存量 **保存** 按钮 `saveGateway`（不退化） |

## 交互说明

- 开关 **即时保存**（单项 PATCH），成功 Toast；失败 `adminToastError`（含 409/422 `message`）。
- 首屏与 `loadAll` 共用 loading；保存中禁用全分区开关（`savingIntentNlu` / `savingNarrateKey`）。
- env 覆盖说明区：NLU + ticker narrate 代表性变量名（AC-6）。

## 自测（本地）

1. `cd server && uv run chainup-agent-api`（8080）
2. `cd admin && npm run dev`（5173）
3. 打开 `/ai-settings?tab=runtime` — 可见网关策略、9 行 narrate、env 说明
4. 切换 NLU / 任一场景 → Toast → 刷新回显

## 下一 Chat

```text
/pipeline-test-e2e 2026-05-27--admin-ai-settings-gateway-ui
```
