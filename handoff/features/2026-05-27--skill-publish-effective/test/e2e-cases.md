# E2E 用例

> **含页面：是** — Admin **`/ai/tool-registry`** + Vite proxy → API **8080**。

## 前置条件

- `cd server && uv run chainup-agent-api`（**8080**）
- `cd admin && npm run dev`（**5173**）
- Admin 已登录（Bearer）
- 已完成 **TC-01** import（或测试环境预置数据）

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| E2E-01 | AC-1, AC-2, AC-5, AC-6, AC-8 | 列表加载（含种子） | 打开 **`/ai/tool-registry`** | 表格展示 `skill.spot.limit_order` 等 import 项、`lifecycle`；无白屏 | P0 |
| E2E-02 | AC-3, AC-8 | 履历与正文预览 | 点选 `skill.spot.limit_order` → 打开版本履历 → 查看某一版正文 | 可见 `skillSpecVersion` 列表；正文预览区有 Markdown 片段（非空） | P0 |
| E2E-03 | AC-4, AC-8, AC-9 | Publish 交互 | 对测试 skill 输入新版本号 → 确认 Publish；可选再试更低版本 | 成功提示；失败展示 API `message`/`code`（含回退） | P0 |
| E2E-04 | AC-7 | Prompt 门禁提示（可选） | `/prompts/strategy` 编辑 TRADING 包 → 填未发布 `skillSpecRef` → Publish | 阻断并展示 `PROMPT_SKILL_REF_INVALID` 类文案 | P1 |

## 验收对照（brief.md · 页面）

- [ ] 主流程：列表 → 履历/预览 → Publish
- [ ] 错误态：Publish 失败可见原因（E2E-03 可 mock 或测 TC-08）
- [ ] 加载态：列表 loading、Publish 按钮 submitting
