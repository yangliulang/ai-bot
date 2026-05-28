---
name: ngrok-chainup-stack
disable-model-invocation: true
description: >-
  Exposes ChainUp local dev ports via ngrok for Telegram/webhook/bind-page
  end-to-end tests. Prefer a single HTTPS tunnel to deeplink port 5174;
  aligns server/.env CHAINUP_AGENT_PUBLIC_BASE_URL and
  CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL same-origin. Use when the user asks for
  ngrok public tunnel, telegram webhook HTTPS, exposes 5174/5173/8080, or
  "三条隧道/公网联调".
---

# Ngrok · Admin / Deeplink / Server（本仓）

## 先说清「三个端口」与 Telegram

本仓本地常为：

| 端口 | 典型进程 | 经由公网给谁用 |
|------|-----------|----------------|
| **5174** | `deeplink/` Vite | **Telegram `setWebhook`、`BIND` 落地页**（经由 Vite 反代到 **8080**） |
| **8080** | `server/` FastAPI | 本地直连或通过 **5174 上**的同路径 `/api`、`/webhook`、`/docs` 等到公网 |
| **5173** | `admin/` Vite | 运营控制台；**与 Telegram webhook 同源无强制关系** |

`server/` 的 `.env` 里与 **Telegram 公网联调**强相关的是这两行（名称勿改；值需与**同一条** ngrok HTTPS 起源一致）：

- **`CHAINUP_AGENT_PUBLIC_BASE_URL`**：一般为 `https://<你的 ngrok 主机>`，**末尾通常不要**再拼 `/`（工具会规整；与 `README`/`ngrok` 辅助命令一致）。
- **`CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL`**：与上**同一主机名**；常写成根路径带尾 `/`，例如 `https://<同一主机>/`。

两者必须 **同源**（同一 scheme + host），且该 HTTPS 地址应来自 **指向本机 `127.0.0.1:5174` 的那条隧道**——由 `deeplink` 的 Vite 把 `/webhook`、`/api`、`/health`、`/docs` 等转到 **8080**。**不要**让「直通 8080 的 tunnel」与用户点的 **BIND SPA（5174）** 在 ngrok 「同源池」里混同一条对外 `public_url`，否则经常出现点开链接进到 FastAPI 根而不是 Deeplink SPA（详见 `server/README.md`、`server/ngrok.chainupEndpoints.example.yml`）。

## 前置条件

1. 本机已安装 **ngrok** 并完成 `ngrok config add-authtoken …`。  
2. 已本地拉起 **`server`（8080）** 与 **`deeplink`（5174）**（见 `.cursor/skills/start-chainup-stack/SKILL.md`）。`admin`（5173）是否启动视你是否要验收控制台而定。  
3. `deeplink/vite.config.ts` 已对 `.ngrok-free.dev` 等 tunnel Host 放行，否则会遇到 **403**。

## 推荐做法（Telegram：只公网一条路 → 5174）

**只做一条 HTTPS 隧道，上游为 `5174`。**

任选其一：

```bash
ngrok http 5174
```

或使用仓库附带命名 endpoint（与工作区中含 `authtoken` 的全局 ngrok 配置**合并**；在**仓库根**执行时路径按实际调整）：

```bash
ngrok start chainup-through-vite-5174 \
  --config "$HOME/Library/Application Support/ngrok/ngrok.yml" \
  --config ./server/ngrok.chainupEndpoints.example.yml
```

配置定义见 `server/ngrok.chainupEndpoints.example.yml`（`upstream.url: http://127.0.0.1:5174`）。

## 写入 `server/.env`（与用户片段一致的含义）

隧道起来后：

1. 将 **`CHAINUP_AGENT_PUBLIC_BASE_URL`** 设为 **`https://<本条 5174 隧道的 hostname>`**（与仓库注释一致：与 `BIND_PAGE` **同源**；仅 ngrok **到 deeplink 的 5174**）。  
2. 将 **`CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL`** 设为 **同一 hostname**，通常 **`PUBLIC_BASE_URL` + `/`** 或等价根 URL（你本地 `.env` 里两行同 host、`BIND` 带尾 `/` 的写法即符合）。  
3. **勿提交** `.env`/token/`SECRET`；聊天记录里也别贴真实密钥。

可选：用服务端辅助命令根据本机 `http://127.0.0.1:4040/api/tunnels` 推导并写回（**不负责替你启动 ngrok**）——在 **`server/`** 下：

```bash
eval "$(uv run chainup-agent-ngrok-public-url --export)"
uv run chainup-agent-ngrok-public-url --dotenv-bind
```

（若你只开了一条 HTTPS 且无 `--tunnel-upstream-port`，会选用该 HTTPS 地址。）

换隧道域名后：**必须重新**按 `README` **`POST …/telegram/webhook`**，否则 Telegram 仍打旧 URL。

## 若「还要」单独暴露另外两个端口（非 Telegram 常规）

这是**附加**场景，与上面 **`.env` 两变量无关**时才能独立使用：

- **`admin`（5173）**：另起一条 **独立 subdomain** 的隧道，例如 `ngrok http 5173`。注意控制台面与鉴权暴露面。  
- **直连 `server`（8080）**：另起 **独立 subdomain** 的 `ngrok http 8080` 仅用于你个人直连 `/docs` 等；**不要把这条 URL 填进** `CHAINUP_AGENT_PUBLIC_BASE_URL` / `CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL` 去替代 5174，否则与「BIND 走 SPA、webhook 走同 host」的推荐模型冲突，并易触发 README 所述 **8080+5174 同源池化**问题。

**规则**：凡填进 **`CHAINUP_AGENT_PUBLIC_BASE_URL`** 和 **`CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL`** 的，必须是 **5174 隧道**给出的那条 `https://…`；其它隧道仅供其它用途、且 hostname 应不同。

## 验证（简短）

- 浏览器打开 `https://<5174-tunnel>/` 应进入 Deeplink SPA（非意外落到 API 根）。  
- `https://<5174-tunnel>/docs` 等应经 Vite 代理到 8080（见 `deeplink/vite.config.ts`）。  
- 服务端日志出现 **`telegram_webhook_ingested`** 表示 Telegram 已打到本链路。

## 关联技能

- 本地三进程启动：`.cursor/skills/start-chainup-stack/SKILL.md`  
- 收口停服务：`.cursor/skills/stop-chainup-stack/SKILL.md`  
- 权威说明与排错：`server/README.md`（Telegram / ngrok 小节）
