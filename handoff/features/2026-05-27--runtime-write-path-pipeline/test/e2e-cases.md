# E2E 用例

> **含页面：否** — 无新增 Admin 路由；可选在存量 **Observability 执行详情** 肉眼核对时间线。

## 说明

- P0 以 **`test/cases.md`** API + timeline 断言为准（pytest）。
- 若 test-agent 无浏览器环境，可在 `test/e2e-report.md` 标 **N/A（API 已覆盖 AC-2/3/5）**。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| E2E-01 | AC-2, AC-3, AC-5 | Observability 时间线肉眼走查（可选） | 1. 完成 TC-02<br>2. Admin 登录 → 执行详情 → 打开对应 `executionId` 时间线 | 可见 **技能规范已读** 卡/行；**早于** 确认与交易所写事件 | P1 |
