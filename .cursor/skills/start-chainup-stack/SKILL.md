---
name: start-chainup-stack
disable-model-invocation: true
description: >-
  Starts the ChainUp monorepo local dev processes for admin (Vite),
  deeplink (Vite on 5174), and server (FastAPI via uv). Use when the user
  invokes this skill, asks to spin up admin + deeplink + server together,
  local full-stack dev, or "启动三个项目/全套联调".
---

# 启动 Admin + Deeplink + Server（本仓联调）

## 你要做的事

在用户**显式使用本技能**时，在 Cursor 终端里把这 **三个** dev 进程拉起来：**先 `server`（8080），再两个前端**，因为 `admin/`、`deeplink/` 的 Vite 会把 `/api`、`/webhook`、`/health` 等代理到本机 **8080**。

## 仓库根目录

以**当前 Cursor 工作区根**为准（应同时包含 `admin/`、`deeplink/`、`server/` 三个顶层目录）。

## 启动命令（三个独立长期进程）

在各自目录执行；**均需后台运行**（`block_until_ms: 0` 或等价「后台任务」），不要阻塞在同一条前台命令里串联三个服务。

1. **`server`**（Python / uvicorn，默认 **8080**）

   ```bash
   cd server && uv run chainup-agent-api
   ```

   等价：`cd server && uv run python -m chainup_agent`（与 `README` 一致）。

   若报错缺依赖或未装环境：提示用户先在 `server/` 执行 `uv sync --all-groups`，并按需 `cp .env.example .env`（见仓库内 `server/README.md`）。

2. **`admin`**（Vite，默认多为 **5173**）

   ```bash
   cd admin && npm run dev
   ```

3. **`deeplink`**（Vite，配置为 **5174**，见 `deeplink/vite.config.ts`）

   ```bash
   cd deeplink && npm run dev
   ```

前端若缺包：分别在 `admin/`、`deeplink/` 执行 `npm ci`（有 `package-lock.json`）。

## 启动后自检（可选）

简短等待（约 2–5s）后可提醒用户或直接探测：

- 浏览器或可访问：`http://127.0.0.1:8080/docs`（仅 API）
- `admin`：多为 `http://127.0.0.1:5173`
- `deeplink`：`http://127.0.0.1:5174`

`/health`、`/openapi.json` 等与代理说明见 `admin/vite.config.ts`、`deeplink/vite.config.ts`。

## 避免重复启动

可先查看 Cursor **terminals** 元数据：若已有对应目录下的 `vite` / `chainup-agent-api` / `uvicorn` 在长跑，告知用户端口可能已被占用或已在运行，不要盲目再启一份（除非用户要求重启）。

## 端口冲突

若 8080 / 5173 / 5174 被占用，**不要擅自杀进程**：说明占用情况，让用户处理或改用其本地约定端口。

## 联调语义（简报）

Webhook / 同源隧道等高级联调仍以 `server/README.md` 的 Telegram 小节为准（常见：**单隧道指向 deeplink 5174**）。

## 对应：全部停掉

见 `.cursor/skills/stop-chainup-stack/SKILL.md`。

## 对应：ngrok 公网（Telegram / 联调）

见 `.cursor/skills/ngrok-chainup-stack/SKILL.md`。
