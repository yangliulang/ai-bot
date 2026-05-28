# 设计 / UI 走查规范

> 对应 `designer-agent`。流转见 `.cursor/rules/designer-agent.mdc`。

## 产出

- `design/ui-review.md`：走查结论、检查项、问题清单

## 输入

- `brief.md`（界面与交互）
- `frontend/integration.md`（路由、组件、联调说明）
- `test/e2e-report.md`（E2E 已通过）

## 走查环境

- 使用真实前后端（与 E2E 相同），在浏览器打开目标路由
- 默认 **不改** `apps/web/` 代码；问题写入 `blockers` 交给 frontend-agent

## 严重度

| 级别 | 说明 | 阻塞 `ui_reviewed` |
|------|------|-------------------|
| P0 | 主流程不可用或与 brief 明显不符 | 是 |
| P1 | 体验瑕疵 | 否（记入待迭代） |
| P2 | 建议 | 否 |

## 通过标准

- `design/ui-review.md` 结论为通过
- 无未解决的 P0
- 更新 `status.yaml`：`phase: ui_reviewed`，`next: product-agent`

## 返工

- P0 未过：保持 `e2e_verified`，`next: frontend-agent`，填写 `blockers`
- 前端修完：`next: designer-agent` 复走查
- 若涉及 AC/接口变更：在报告中要求 test-agent 复测 E2E
