# 产品验收 — 2026-05-27--admin-ai-settings-gateway-ui

> product.accept · 2026-05-27 · **结论：通过**

## 验收依据

| 来源 | 结论 |
|------|------|
| `brief.md` AC-1～AC-8 | 本文件逐项勾选 |
| `test/report.md` | API P0 TC-01～05 全通过 |
| `test/e2e-report.md` | E2E P0 E2E-01～03/05 通过；E2E-04（P1）跳过 |
| `design/ui-review.md` | 无 P0；P1 无障碍/错误抽测 |
| `frontend/integration.md` | 联调完成 |
| `backend/notes.md` | 无新路由；存量 defaults 回归 |

`./scripts/check-test-coverage.sh` → **0**

## AC 对照

| AC | 验收结论 | 证据 |
|----|----------|------|
| AC-1 | 通过 | E2E-01；`GatewayPolicyPanel` @ `/ai-settings?tab=runtime` |
| AC-2 | 通过 | TC-01、E2E-01；GET 回显 9 narrate + NLU |
| AC-3 | 通过 | TC-02、E2E-02；单项 PATCH + Toast |
| AC-4 | 通过 | TC-03、E2E-03；部分 `telegramLlmNarrate` 合并 |
| AC-5 | 通过（附注） | 网关 PATCH 失败 → `adminToastError`；TC-04 验 422；存量 `saveGateway` 复用 catalog 422 文案（E2E-04 P1 未造 409/422 页复现） |
| AC-6 | 通过 | E2E-01、ui-review #3；分组 + env 说明卡 |
| AC-7 | 通过 | TC-05、E2E-05；catalog Tab + scenario 模型保存不退化 |
| AC-8 | 通过 | E2E-01/02/03/05；loading / 「保存中…」/ 底部保存 busy |

## 范围外 / P1 backlog（不阻塞 done）

| 项 | 说明 | 跟进 |
|----|------|------|
| E2E-04 | PATCH 409/422 页面手造未跑 | 可选 test-agent 补测；代码路径已接 Toast |
| UI-P1-01 | narrate checkbox `aria-label` | frontend-agent 迭代 |
| UI-P1-02 | 产品抽测 catalog 422 Toast | 验收抽检 |

## 交付物

- `admin/src/features/ai-settings/GatewayPolicyPanel.vue`
- `admin/src/features/ai-settings/gateway-policy-constants.ts`
- `admin/src/pages/ai/AiSettingsPage.vue`（挂载）
- `admin/src/shared/api/admin-ai-settings.ts`（类型）
- `server/tests/test_admin_ai_settings_gateway_ui.py`

## 收口

Phase-2 **P1**「Admin AI 网关开关 UI」（Phase-1 FE 债）**done**；运营可在控制台配置 NLU / 9 场景 Telegram narrate，无需改 env。
