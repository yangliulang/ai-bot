# 后端开发规范

> 对应 `apps/api/`。硬约束摘要见 `.cursor/rules/api-dev.mdc`。

## 技术栈

- Node.js + Express（ESM，`"type": "module"`）
- 入口：`apps/api/src/index.js`（或按功能拆路由后从 index 挂载）

## 路由与契约

- 路径、方法、query/body、状态码与 `api.openapi.yaml` 一致
- 前缀：`/api`（与 OpenAPI `servers.url` 一致）
- 实现与契约不一致时：先改实现或先更新 OpenAPI，并在 `backend/notes.md` 说明

## 响应

- 成功：`res.json({ code: 0, message, data })`
- 业务错误：4xx + `{ code, message }`（`code` 为非 0 整数，与 OpenAPI 示例对齐）
- 避免裸字符串或裸数组作为根响应

## 跨域

```javascript
cors({ origin: 'http://localhost:5173' })
```

## 配置

- 端口：`process.env.PORT || 3000`
- 不在代码中写死环境密钥

## backend/notes.md（交付必填）

- Base URL、启动命令（`npm run dev`）
- 每个对外路径至少一条 **可复制 curl**
- 错误码表（code → 含义）
- 与 OpenAPI 的差异说明（无则写「无」）

## 自测

标记 `backend_done` 前本地跑通 OpenAPI 中所有路径。
