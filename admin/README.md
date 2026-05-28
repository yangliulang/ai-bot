# TG-BOT-Admin

Telegram Bot 管理端前端（脚手架）。协作约定见根目录 [`agent.md`](./agent.md)，工程规范见 [`docs/前端开发规范.md`](./docs/前端开发规范.md)。

## 技术栈（锁定）

- Vue 3 + `<script setup>` + TypeScript（strict）
- Vite 8、Vue Router、Pinia
- Tailwind CSS v4（`@tailwindcss/vite`）
- **Reka UI**（无样式基元，无障碍）+ `src/shared/ui` 薄封装（Button / Input / Modal 等）
- ky（HTTP）、Zod（运行时校验）
- ESLint + Prettier + Oxlint、Vitest + Vue Test Utils

## 常用命令

```bash
npm install
npm run dev
npm run build
npm run type-check
npm run lint
npm run test:unit
```

## 分层目录

详见 `docs/前端开发规范.md` §5（目录与分层）。代码入口：`src/app/main.ts`。

## 环境变量

复制 `.env.example` 为 `.env.local`（勿提交密钥）。仅允许 `VITE_` 前缀变量进入前端构建。

## UI 组件试跑

开发环境可打开 [`/system/ui-playground`](http://localhost:5173/system/ui-playground) 查看基于 Reka UI + Tailwind 的封装示例（Button / Input / Modal）。
