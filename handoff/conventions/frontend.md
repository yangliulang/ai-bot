# 前端开发规范

> 对应 `apps/web/`。硬约束摘要见 `.cursor/rules/web-dev.mdc`。

## 技术栈

- Vite + React（函数组件 + Hooks）
- 路由：`react-router-dom`
- 页面放在 `apps/web/src/pages/`
- API 封装放在 `apps/web/src/api/`

## 对接 API

- baseURL：`http://localhost:3000/api`（与 OpenAPI servers 一致）
- 解析统一响应：`code === 0` 取 `data`；否则展示 `message`
- Mock 阶段结构须与 OpenAPI 一致；`tested` 后切真实地址（见 `backend/notes.md`）

## 页面与 brief

- 路由、文案、主流程以 `brief.md` + `frontend/integration.md` 为准
- 须覆盖：**主流程** + brief 要求的 **错误态**
- 提交中：按钮禁用或 loading，避免重复请求

## 状态与存储

- Token 等存储方式 **只** 按 `brief.md`（无约定则不要擅自引入 localStorage）

## 样式

- 当前项目可用简单 CSS（如 `src/index.css` + 页面 className）
- 不引入与现有栈冲突的 UI 框架，除非指挥官要求

## frontend/integration.md（联调后必填）

- 路由、关键文件、接口映射表
- 联调结果勾选（主流程 / 错误态 / 加载态）

## 自测

标记 `frontend_done` 前本地前后端联调通过主流程与至少一种错误态。
