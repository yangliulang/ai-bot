# E2E 用例

> **含页面：是** — Admin **`/ai-settings?tab=runtime`** + Vite proxy → API **8080**。

## 前置条件

- `cd server && uv run chainup-agent-api`（**8080**）
- `cd admin && npm run dev`（**5173**）
- Admin 已登录（Bearer）
- 至少 1 个 **enabled** 模型在 catalog（AC-7 保存 scenario 模型时需要）

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| E2E-01 | AC-1, AC-2, AC-6, AC-8 | 网关策略分区加载 | 打开 **`/ai-settings?tab=runtime`** | 可见 **网关策略**、**意图 NLU**、**Telegram LLM 叙述**；9 行开关；env 说明文案；加载完成后开关可操作 | P0 |
| E2E-02 | AC-3 | NLU 开关保存 | 切换 **意图 NLU 优先 LLM** → 保存 | Toast 成功；刷新后状态保持 | P0 |
| E2E-03 | AC-4 | 单场景 narrate 保存 | 仅开启 **行情 · 最新价** → 保存 → 刷新 | **readMarketTicker** 为开；其它 narrate 行与保存前一致（抽样 1～2 行） | P0 |
| E2E-04 | AC-5 | 错误展示（可选） | 制造 422：在另一会话 PATCH defaults 使 catalog 引用失效，或 mock | 界面展示失败原因，非静默成功 | P1 |
| E2E-05 | AC-7 | 存量使用策略保存 | 在使用策略 Tab 修改 **普通问答** 模型 → **保存**（存量按钮） | **200** / Toast 成功；网关分区仍可见 | P0 |

## 验收对照（brief.md · 页面）

- [ ] 主流程：加载 → 改 NLU / narrate → 保存 → 回显
- [ ] 错误态：PATCH 失败可见 `message`
- [ ] 加载态：首屏 loading；保存 submitting
