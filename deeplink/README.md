# C 端 · Deeplink / H5 (`deeplink/`)

面向 **Telegram 内浏览器 / H5 落地页** 的 Vue 3 壳工程，与同仓 `admin/` 技术基线对齐（Vite · TS strict · Pinia · Vue Router · ky · zod · Tailwind v4）。

## 与本仓文档关系

| 文档 | 用途 |
|------|------|
| `product-doc/specs/requirements/integrations/telegram/deeplink.md` | Deeplink **协议与非目标**（签名校验、ticket 等以 design / risk 为准） |
| `admin/docs/前端开发规范.md` | **目录分层、文件头留痕、架构原则**（本工程 `docs/前端开发规范.md` 为摘要 + 补丁） |
| 仓库根目录 `DESIGN.md` | 设计 Token 与叙事（C 端为浅色壳，可与 Admin 深色并存） |

## 命令

```bash
cd deeplink
npm install
npm run dev
```

默认开发端口 **5174**（见 `vite.config.ts`）。`/api` 等同仓策略：开发期代理到 `server` `8080`。

## 环境变量

复制 `.env.example` 为 `.env`（本地可选）。

## 目录（规范 §5）

- `src/app/` — 入口、路由注册、根布局
- `src/pages/` — 路由级薄页面
- `src/features/` — 业务切片（后续页面逻辑主战场）
- `src/shared/` — `api/`、`config/`、`ui/`
- `src/entities/` — 无 UI 实体与纯函数

导入边界与 `admin` 规范一致：`shared` 不引用 `features` / `pages`。
