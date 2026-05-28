# ChainUp Agent 单体仓 — 三端部署注意事项（运维 / QA）

> **范围**：与本仓三个可部署单元对齐 — **`server/`**（FastAPI Agent API）、**`admin/`**（运营控制台 SPA）、**`deeplink/`**（用户绑定 / H5 SPA）。  
> **契约真源**：`server/docs/API_INTEGRATION_GUIDE.md`、`server/docs/BACKEND_SPEC.md`；产品设计见 `product-doc/`。  
> **机密**：密钥、Bot Token、`CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY`、控制台密码等 **只放部署环境密钥管理**，**勿提交仓库**。

---

## 1. 推荐拓扑（一目了然）

典型联调 / 小规模部署：**用户浏览器与同域网关**可同时访问控制台、绑定页；**Telegram** 仅能访问 **公网 HTTPS**。

```
[Telegram Servers] ──HTTPS──► [网关 /  ingress]
                                  │
                     ┌────────────┼────────────┐
                     ▼            ▼            ▼
              Deeplink SPA   Admin SPA    Agent API
              (静态资源)     (静态资源)    (反向代理到 /api,/webhook,… → 后端 :8080)
```

- **`server`**：进程监听 **`CHAINUP_AGENT_API_HOST`** / **`CHAINUP_AGENT_API_PORT`**（默认 **`0.0.0.0:8080`**）。  
- **`deeplink`**：Vite dev 默认 **5174**；生产为静态资源 + 由网关决定是否仍代理 `/api`、`/webhook`。  
- **`admin`**：Vite dev 默认 **5173**（未在配置里写死 port 则用 Vite 默认）；生产同上。

---

## 2. 开发与仓库内默认：API / Webhook 代理（必须与生产对齐语义）

两处前端在 **开发模式** 下通过 **同源路径**把请求转发到本机 Agent（`127.0.0.1:8080`）。**运维在预发 / 生产**应用 **网关/nginx** 做 **等价映射**，而不要假设浏览器能直连后端内网端口。

### 2.1 `deeplink/vite.config.ts`（dev · 端口 5174）

| 浏览器路径前缀 | 代理目标（dev） |
|----------------|-----------------|
| `/api` | `http://127.0.0.1:8080` |
| `/webhook` | `http://127.0.0.1:8080` |
| `/health` | `http://127.0.0.1:8080` |
| `/docs`、`/openapi.json`、`/redoc` | `http://127.0.0.1:8080` |

- **deeplink**：`deeplink/.env` / `VITE_API_BASE_URL` 未配置时，HTTP 客户端默认前缀为 **`/api`**（即走同源代理）。  
- 若生产 **SPA 与 API 不同源**，须在构建注入 **`VITE_API_BASE_URL=https://…`**（末尾不要多余 `/`，或按 `http-client.ts` 规则统一）。

### 2.2 `admin/vite.config.ts`（dev · 默认 5173）

| 浏览器路径前缀 | 代理目标（dev） |
|----------------|-----------------|
| `/api` | `http://127.0.0.1:8080` |
| `/webhook` | `http://127.0.0.1:8080` |
| `/health` | `http://127.0.0.1:8080` |
| `/openapi.json` | `http://127.0.0.1:8080` |

- **admin**：未设置 **`VITE_API_BASE_URL`** 时，默认 **`prefixUrl`** 为 **`/api`**（`admin/src/shared/api/http-client.ts`）。  
- 生产若 Admin 域名与 API 分离：构建参数 **`VITE_API_BASE_URL=https://你的-agent-网关前缀`**（需带路径前缀则说明书与代码一致：`/api` 或直接根路径）。

### 2.3 生产网关建议（与 dev 等价）

任选一种策略即可，团队需 **统一文档**：

1. **同源入口（推荐小规模）**：用户访问 `https://app.example.com`（deeplink）、`https://admin.example.com`（admin）；网关将 **`/api`、`/webhook`、…** 反向代理到 **`server:8080`**，与两份 `vite.config` 一致。  
2. **跨域**：前端 `VITE_API_BASE_URL` 指向独立 API 域名；网关仅对 API 域名开放 **`/api/*`、`POST /webhook/telegram/*`** 等。**CORS** 需在 **`server`** 侧或网关按环境放开（若有浏览器直连 API）。

**必须可达的路径（Telegram / 控制台）**

- **`POST …/webhook/telegram/{botToken}`** — Telegram 投递更新（见下文）。  
- **`POST …/api/v1/agent/*`**、`**/api/auth/login**`、**/api/v1/admin/**`* — Deeplink / Admin 业务能力依赖（具体以 OpenAPI / 路由为准）。

---

## 3. Telegram Webhook（非 GitHub Webhook）

本仓 **不涉及 GitHub Webhook**。运维配置的是 **Telegram Bot Webhook**。

### 3.1 服务端路由

- **接收更新**：`POST /webhook/telegram/{bot_token}`  
  - `{bot_token}` 为 BotFather Token 原样（URL 中会 **百分比编码**，见实现 `telegram_webhook_admin.webhook_callback_public_url`）。

### 3.2 写入 Telegram 的目标 URL从何而来

- 控制台或通过 **`POST /api/v1/admin/channels/telegram/webhook`** 登记（见 `admin/telegram-channels.yaml` / `BACKEND_SPEC`）。
- **`url`** 若不传 Body，则用 **`CHAINUP_AGENT_PUBLIC_BASE_URL`** 拼出：  
  **`{PUBLIC_BASE_URL}/webhook/telegram/{url_encoded_token}`**

### 3.3 硬性要求

| 项 | 说明 |
|----|------|
| **HTTPS** | `setWebhook` **仅接受 HTTPS**（实现会拒绝 `http://`）；测试隧道可用 ngrok/cloudflared。**localhost 不可直接被 Telegram 访问。** |
| **`CHAINUP_AGENT_TELEGRAM_BOT_TOKEN`** | 未配置则 Webhook 相关接口 **503**，且服务端可能拒绝处理更新（见 `webhook.py` 提示）。 |
| **`PUBLIC_BASE_URL` 与绑定页同源** | 用户点击 Deeplink **`CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL`** 与 **`PUBLIC_BASE_URL`** **须同一公网主机**（或与产品冻结的「单入口」一致），避免出现「控制台填的隧道与用户点的链接是两台入口」导致的 **404 / 进错服务**。参见 `server/README.md` ngrok **单隧道 → 5174** 的最佳实践语义；生产则用 **正式域名单入口**。 |
| **勿混用两条隧道同源** | 「8080 一条 + 5174 一条」但浏览器与 Telegram **看起来同一域名**，易导致 **打开的永远是 API 而非 H5**。 |
| **`secret_token`** | 若在 `POST …/telegram/webhook` Body 传入，须与网关/Telegram 配置一致（可选安全加固）。 |

### 3.4 运维自检命令（示例）

- 健康：**`curl -sSf https://<你的入口>/health`**  
- Swagger（若网关放开）：`/docs`、`/openapi.json`  
- Telegram：`getWebhookInfo` 或通过 Admin 页的 Webhook 状态接口核对 **`url`** 是否仍为当前环境域名（换域名后 **必须重新 setWebhook**）。

---

## 4. `server/.env` 依赖项说明（对齐 `server/.env.example`）

以下为 **运维必须理解**的核心变量类别；完整列表与默认值以 **`server/chainup_agent/core/config.py`** 与 **`server/.env.example`** 为准。**勿将真实密钥贴进工单**。

### 4.1 运行时与监听

| 变量 | 作用 |
|------|------|
| `CHAINUP_AGENT_ENV`、`CHAINUP_AGENT_DEBUG` | 环境名、调试日志详细程度 |
| `CHAINUP_AGENT_API_HOST`、`CHAINUP_AGENT_API_PORT` | 绑定地址 / 端口（默认 `0.0.0.0:8080`） |
| `CHAINUP_AGENT_LOG_JSON` | 日志形态 |

### 4.2 数据库与迁移

| 变量 | 作用 |
|------|------|
| `CHAINUP_AGENT_DATABASE_URL` | 异步 SQLAlchemy URL。**开发默认**：`sqlite+aiosqlite:///./db/chainup_agent.sqlite3`（**工作目录为 `server/`**；持久化时对 **`server/db`** 挂载卷或使用绝对路径。**生产建议使用 PostgreSQL** `postgresql+asyncpg://…`）。 |

部署后必须：**`cd server && uv run alembic upgrade head`**（或使用镜像内等价命令），再启动 API。

### 4.3 公网语义与 Telegram

| 变量 | 作用 |
|------|------|
| `CHAINUP_AGENT_PUBLIC_BASE_URL` | Webhook URL 推导、对外可见的 HTTPS **根**（**不要尾随 `/`**）。 |
| `CHAINUP_AGENT_TELEGRAM_BOT_TOKEN` | Telegram Bot API；Webhook 与用户消息链路依赖。**泄漏须 BotFather 轮换。** |
| `CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL` | 用户在 Bot 内看到的 **绑定页** 起源；常与 `PUBLIC_BASE_URL` **同源**（可带尾 `/`）。 |
| `CHAINUP_AGENT_TELEGRAM_PHASE1_BOUND_CHAT_IDS` | 可选；联调绕过绑定（逗号分隔 `chat_id`）。**生产慎用。** |
| `CHAINUP_AGENT_TELEGRAM_WEBHOOK_INLINE_PROCESSING` | **`false`（默认）**：先 `200` 再在后台任务处理；若在「返回后进程冻结」的无服务器模型，改为 **`true`**。 |

### 4.4 托管绑定与安全（Confirm / Deeplink）

| 变量 | 作用 |
|------|------|
| `CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY` | **Fernet 密钥**：密封落库的 `api_key` / `secret_key`。**为空则禁止 Confirm 写入（503）。** |

生成示例见 `.env.example` 注释：`python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'`。

### 4.5 控制台登录（Admin 调 `POST /api/auth/login`）

| 变量 | 作用 |
|------|------|
| `CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE` | `env`：**单账号**来自下面一对环境变量；`database`：走表 **`admin_console_user`**。 |
| `CHAINUP_AGENT_ADMIN_PANEL_USERNAME` / `PASSWORD` | 仅 **env** 模式；任一欠配可能导致 **503**（`ADMIN_CONSOLE_AUTH_DISABLED`）。 |
| `CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET` | **≥16** 字符时：登录签发 **JWT**，**`/api/v1/admin/*` 强制 Bearer**。生产强烈推荐开启。 |

### 4.6 产品与功能开关（摘）

| 变量 | 作用 |
|------|------|
| `CHAINUP_AGENT_FEATURE_TRADING` / `CHAINUP_AGENT_FEATURE_AGENT_SPOT` | 意图与现货能力闸 |
| `CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED` / `_OPS_SUSPENDED` | 全站/运维暂停闸 |
| `CHAINUP_AGENT_INTENT_NLU_USE_LLM`、`CHAINUP_AGENT_LLM_FALLBACK_API_KEY` 等 | NLU / LLM 行为（详见 `.env.example`） |

部署前：**按 QA/产品清单**核对是否放行 LLM、是否需 Admin AI Provider 已从 DB **配置**。

---

## 5. QA / 运维部署顺序建议（简版）

1. **PostgreSQL/SQLite 卷就绪** → **`alembic upgrade head`** → 按需 **`chainup-agent-seed-admin`**（若 `database` 登录模式）。  
2. 配置 **`BINDING`** Fernet、`DATABASE_URL`、 **`TELEGRAM_BOT_TOKEN`**、`PUBLIC_BASE_URL`、`BIND_PAGE_URL`。  
3. 拉起 **`server`** → **`curl`/网关**检查 **`/health`**。  
4. 构建并发布 **`deeplink`**、**`admin`**，确认 **`/api`** 与 **`/webhook`**（或等价跨域域名）路由 **与 dev 语义一致**。  
5. **`POST`** Admin **Telegram Webhook** → 用 Telegram 实测一条消息或对 **`getWebhookInfo`**。  
6. Deeplink：**绑定 / validate / confirm** 走通（参见 `deeplink/.env.example` 与产品 `design/api`）。

---

## 6. 参考路径（不写实现细节）

- `server/README.md` — ngrok **单隧道**、环境说明  
- `server/docs/API_INTEGRATION_GUIDE.md` — 路径清单 §4.x  
- `server/docs/BACKEND_SPEC.md` — §5 配置 §6 迁移  
- `deeplink/vite.config.ts`、`admin/vite.config.ts` — 开发代理一览  
- `server/chainup_agent/application/telegram_webhook_admin.py` — Webhook URL 推导

---

**文档版本**：与本仓主干一致；域名与端口以实际发布为准。**若条目与产品 OpenAPI / PM 冻结冲突，以产品 SSOT 为准。**
