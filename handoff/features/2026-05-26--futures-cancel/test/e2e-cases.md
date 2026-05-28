# E2E 用例

> **含页面：否** — 本功能无 Admin/Deeplink 路由，E2E 不适用。

## 说明

- 验收以 **`test/cases.md`** API P0 为准。
- Telegram 绑定会话内直接撤单为 **P1** 手工/staging，**不** 阻塞本包 contract。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| — | — | 无页面 | — | — | — |

## 验收对照（brief.md）

- [x] 主流程：HTTP POST + 意图 `EXECUTE_FUTURES_CANCEL`（API 覆盖）
- [x] TG 直接撤单：可选 P1，不在本包 P0 门禁（e2e N/A）
