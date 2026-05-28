# UI 走查 — 2026-05-27--admin-ai-settings-gateway-ui

> designer.review · 2026-05-27

## 走查范围

- Admin **`/ai-settings?tab=runtime`**（使用策略 Tab · **`GatewayPolicyPanel`** 增量分区）
- 对照 `brief.md`（AC-1～AC-8）、`test/e2e-report.md`（E2E-01～03/05）
- 参考 IA：`product-doc` **`/ai-settings`** 双 Tab；本包不改动「厂商与模型」与底部存量 **保存** 条

## 环境

- Admin http://127.0.0.1:5173 · API http://127.0.0.1:8080
- 走查页：使用策略 Tab 已加载；网关 defaults 含 NLU / narrate 样本开关状态

## 检查项

| # | 项 | 级别 | 结果 | 备注 |
|---|-----|------|------|------|
| 1 | 网关策略分区与存量「推理与路由 / Token / 预算」视觉层级清晰 | P0 | 通过 | 独立 `admin-panel` + `h2`「网关策略」置于 Runtime 表单 **顶部**；`border-t` 子区划分 NLU / narrate；与下方 **推理与路由** 间距足够 |
| 2 | 9 场景分组（只读 5 / Type-A 4）与运营中文标签可读 | P0 | 通过 | `只读行情（5）` / `交易确认 Type-A（4）`；每行 **中文标签 + `readMarketTicker` 等字段名**；E2E-01 已验 |
| 3 | env 覆盖说明可见且不遮挡操作 | P0 | 通过 | 灰底说明卡列出 NLU + ticker narrate 代表性 env；不覆盖开关列表；满足 AC-6 |
| 4 | 开关 loading / 保存 submitting 状态 | P0 | 通过 | 首屏与 `loadAll` 共用 loading；单项保存时「保存中…」/「保存 readMarketTicker…」+ 全分区禁用；存量 **保存** 按钮 `busy`（E2E-05） |
| 5 | PATCH 错误 Toast / 行内提示 | P0 | 通过 | 成功/失败走 `adminToastSuccess` / `adminToastError`（`AppError.message`）；无行内错误条为 **设计选择**（与存量 Runtime 表单一致）；422 行为 API 已覆盖 |
| 6 | 与存量 Admin 深色体系一致（`admin-panel`、emerald 开关、slate 边框） | P0 | 通过 | 对齐同页其它 section；Tab「使用策略」seg 与侧栏 **模型配置** 高亮一致 |
| 7 | 信息架构：路由 `?tab=runtime`、region `aria-labelledby` | P0 | 通过 | `#gateway-policy-heading` · `role="region"`；意图 NLU 行含可访问名称 |
| 8 | narrate 行 checkbox 无障碍名称 | P1 | 待迭代 | 自动化树中部分 narrate 复选框名为 `on`；建议 `aria-labelledby` 指向行内标签或 `aria-label` 含运营名 + 字段名 |
| 9 | 保存失败时开关回滚 / 行内错误 | P1 | 待迭代 | 依赖 Toast；E2E-04（P1）未跑；产品验收可抽测 422 catalog 场景 |
| 10 | 单项保存时锁全分区（非仅当前行） | P2 | 建议 | 防并发合理；后续可改为仅 `rowDisabled(key)` 不锁 NLU 区 |

## 问题清单

| ID | 级别 | 摘要 | 负责人 |
|----|------|------|--------|
| — | — | 无 P0 | — |
| UI-P1-01 | P1 | narrate / 部分开关补充 `aria-label` 或 `aria-labelledby` | frontend-agent（可选） |
| UI-P1-02 | P1 | 产品验收抽测 PATCH 失败 Toast 文案（409/422） | product-agent / test-agent |

## 结论

- [x] **通过**（无 P0）
- [ ] 不通过

与 **含页面** brief 及 E2E P0 一致；网关策略分区信息架构、分组与 env 说明满足运营可读性。P1 为无障碍与错误态抽测，不阻塞 `ui_reviewed`。

## 下一棒

- ~~product.accept~~ · 已 **done**（见 `product/accept.md`）
