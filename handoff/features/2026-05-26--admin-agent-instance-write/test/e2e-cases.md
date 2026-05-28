# E2E / 页面验证用例

> 本功能 **含页面: 是**。Admin dev + 后端 API 联调。

## 前置条件

- `cd server && uv run chainup-agent-api`（**8080**）
- `cd admin && npm run dev`（Vite proxy `/api` → 8080）
- Admin 已登录（Bearer）；测试用 **未占用** 的 `telegramUserId`

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| E2E-01 | AC-1, AC-6, AC-7 | 创建实例 | 打开 `/agents/instances` → 创建 → 填写新 `telegramUserId` → 提交 | 成功提示；列表出现新 `inst_*`；失败展示 `message`/`code` | P0 |
| E2E-02 | AC-3, AC-8 | I05 编辑 | 进入详情 → 修改 `preferredLanguage` → 保存 | 保存成功；展示区显示 `zh-Hans`（或所选值） | P0 |
| E2E-03 | AC-4, AC-5, AC-9 | I04 解绑/登记 | 详情 → 解绑 API 托管（确认）→ 状态 **NONE** → 可选登记 `subAccountId` | 解绑后绑定列为 NONE；登记后 `exchangeSubAccountUserId` 更新 | P0 |
| E2E-04 | AC-2 | 重复创建 | 对已存在 `telegramUserId` 再次打开创建并提交 | 展示 **422** 文案（含配额/已存在语义）；列表无重复行 | P0 |

## 验收对照（brief.md）

- [x] 主流程：创建 → 编辑参数 → 登记/解绑
- [x] 错误态：重复创建（E2E-04）；非法 overrides 键（API TC-04 或 UI 校验）
