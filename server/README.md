# ChainUp AI Agent — Python 服务端

本目录为 **Agent 运行时 HTTP 服务**（与 `product-doc/`、`admin/` 同仓）。

- **契约 SSOT**：`../product-doc/specs/design/api.md`、`../product-doc/specs/openapi/`
- **阶段范围**：首版对齐 `../product-doc/product/roadmap.md`（Phase 1 HTTP 见遗留 `development-roadmap.md` **第一阶段**）
- **工程约定**：必读 [`docs/BACKEND_SPEC.md`](docs/BACKEND_SPEC.md)（**时间与 UTC**：同文档 **§2.1**）
- **阶段与前端/API 接入**（路线图 Phase 1 路径、OpenAPI、`501` 桩说明）：[`docs/API_INTEGRATION_GUIDE.md`](docs/API_INTEGRATION_GUIDE.md)
- **收口验收**（可勾选）：[`docs/PHASE1_ACCEPTANCE.md`](docs/PHASE1_ACCEPTANCE.md)

## 环境

- Python **≥ 3.11**
- [uv](https://docs.astral.sh/uv/) 推荐使用

```bash
cd server
uv sync --all-groups
cp .env.example .env   # 按需修改
uv run chainup-agent-api    # 或: uv run python -m chainup_agent
```

### 线上参考：`server/.env.online.example`

部署时把模板中的 **`CHAINUP_AGENT_*`** 写入 **`server/.env`**（或容器/编排的环境变量）；进程**只读 `.env`**，与本地开发相同。勿提交含密钥的 **`.env`**。

- **SQLite（本地默认）**：未设置 **`CHAINUP_AGENT_DATABASE_URL`** 时，库文件为 **`server/db/chainup_agent.sqlite3`**（相对 URL **`./db/…`**，须在 **`server/`** 目录启动进程）。标准部署可对 **`db/`** 挂卷或改为 **`postgresql+asyncpg://…`**。

- **Telegram（联调）**：在 `.env` 设置 `CHAINUP_AGENT_TELEGRAM_BOT_TOKEN`（勿提交；泄漏请 BotFather 轮换）。Admin 前端 **不要**放 Bot Token。闲聊走 LLM：Admin Provider **`secretRef`** 为 **环境变量名**（匹配规则见 [`BACKEND_SPEC.md`](docs/BACKEND_SPEC.md) §3.1）**或** **明文 API Key**（入库）；空时用 **`CHAINUP_AGENT_LLM_FALLBACK_API_KEY`**。**`baseUrl`** 含 **`volces.com`** 时上游为方舟 **`/api/v3/responses`**，否则 OpenAI 兼容 **`/chat/completions`**。
- **用户绑定引导（Phase1）**：`CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL` 为 Bot 按钮/明文回填的 **Deeplink HTTPS 起源**（与 `PUBLIC_BASE_URL` 在本地联调时可相同，见下文 ngrok 小节）。路径以产品 **`design/api`** 为准。可选 `CHAINUP_AGENT_TELEGRAM_BOUND_CHAT_ALLOWLIST`（逗号分隔 `chat_id`）仅用于本地联调「视为已绑定」。
- **Webhook（公网 HTTPS）**：推荐 **单条 ngrok 指向 `../deeplink` 的 Vite 5174**，由 Vite dev 代理 `/webhook`→Agent；将同一 `https://…` 填入 `CHAINUP_AGENT_PUBLIC_BASE_URL` 与（通常带尾 `/` 的）`CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL`，再 `POST /api/v1/admin/channels/telegram/webhook` 注册。勿让「8080+5174」两条隧道 **池化在同一个 public_url**——否则点链接常进 API 而非 SPA。详见 **`ngrok.chainupEndpoints.example.yml`** 与下文。
- **仅直连 API 文档（不经 Vite）**：http://127.0.0.1:8080/docs ；经公网 ngrok→5174 时由 Vite 转发至 8080：`https://<隧道>/docs`

### 控制台登录：`database` 模式（多账号）

如需 **运营账号入库（bcrypt）** 或对 **`POST /api/auth/register`**：

1. `CHAINUP_AGENT_ADMIN_CONSOLE_AUTH_MODE=database`
2. `uv run alembic upgrade head`
3. 首张：`POST /api/auth/register`（**`username`/`password`**，口令 ≥8，**空库**即可）**或**
   `uv run chainup-agent-seed-admin --username <u> --password '<pw>'`（可加 `--ensure-schema` 仅限本地）
4. 后续账号：**`CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION=true`** 后再 **`POST /api/auth/register`**，或继续使用 **seed-admin** CLI

默认 **`env`** 仍为单账号环境变量，**不访问** `admin_console_user`。注册接口在 **env** 模式下返回 **503 **`ADMIN_CONSOLE_REGISTRATION_REQUIRES_DATABASE_AUTH`**。

### Telegram Webhook 本地：`ngrok`（推荐单隧道 → Vite **5174**）

1. **安装 ngrok**（本机全局；非 `pip`/`uv` 依赖）：见上文环境说明，`ngrok config add-authtoken …`。
2. **拉起依赖进程**：
   - `cd ../deeplink && npm run dev`（监听 **5174**；`vite.config.ts` 已对 `.ngrok-free.dev` 等隧道 Host 放行，否则整站 **`403 Forbidden`**；并已反向代理 `/webhook`、`/api` 等到 **8080**）；
   - `cd server && uv run chainup-agent-api`（监听 **8080**）。
3. **只暴露 5174 到公网**（任选其一）：

```bash
# 等价：显式配置文件（仅一条 endpoint）
ngrok start chainup-through-vite-5174 \
  --config "$HOME/Library/Application Support/ngrok/ngrok.yml" \
  --config ./server/ngrok.chainupEndpoints.example.yml
```

或简写：**`ngrok http 5174`**（同样在单进程下只起一个 https 起源）。

4. 在 `server/` 取 **同一条隧道**写入 `.env`（**两者同源**，绑定页可加尾 `/`）：

```bash
eval "$(uv run chainup-agent-ngrok-public-url --export)"
uv run chainup-agent-ngrok-public-url --dotenv-bind
```

若仅一条隧道且无 `--tunnel-upstream-port`，`chainup-agent-ngrok-public-url` 会自动选用该 HTTPS 地址。

说明：辅助命令只读本机 **`http://127.0.0.1:4040/api/tunnels`**，不会替你开隧道。

- **不推荐**：同时配置 `/webhook` 直连 **8080** tunnel 与用户点击的 **BIND** 又用 **同源池化到 5174** 的第二 tunnel —— Telegram 与用户浏览器共用一个 `public_url` 时，**GET `/` 常落到 Agent**，看起来「打开的永远不是 Deeplink SPA」。
- **`--tunnel-upstream-port`**：若你仍并行开着多条 HTTPS 隧道，可用 `8080` / `5174` 区分（仅在你明确需要多套隧道时使用）。

### Telegram Bot 不回消息 · 控制台也没「报错」？

常见原因：**Telegram Webhook URL 仍为旧域名**。换隧道后须再次 **`POST /api/v1/admin/channels/telegram/webhook`**。

1. **`CHAINUP_AGENT_PUBLIC_BASE_URL`** = `https://当前隧道根`（指向 **5174** 这一条；末尾一般 **不要**再加 `/`，工具会规整）。
2. **`CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL`** = 通常为 **`PUBLIC_BASE_URL` + `/`**，与上同一主机名。
3. **重新登记 Webhook**：`GET /docs` → Admin Telegram → `POST …/telegram/webhook`（Body 可空）。
4. 服务端日志：**`telegram_webhook_ingested`** 表示 Telegram 已到本机。
6. 闲聊走 LLM 且上游很慢时：`200` 先于出站逻辑（默认 **`BackgroundTasks`**，见 **`BACKEND_SPEC` §3.1）。若部署在「响应返回后进程即冻结」的环境（部分无服务器），设 **`CHAINUP_AGENT_TELEGRAM_WEBHOOK_INLINE_PROCESSING=true`** 在同请求内处理。仍无回复请看 **`telegram_send_message_failed`**、**`telegram_webhook_build_reply_failed`** 日志。

## 测试与静态检查

本地 **`alembic upgrade head`** 后 **`demo`** Provider 由迁移 **`0004_aisettings`** 写入。若仅用 ORM `create_all` 且不跑迁移，可在 `.env` 设 **`CHAINUP_AGENT_ADMIN_AI_CATALOG_SEED_DEMO_IF_EMPTY=true`**，以便首次 **`GET /api/v1/admin/ai/providers`** 注入演示目录（默认 **false**：删除空库后刷新不会自动重现 **`demo`**）。

```bash
uv run pytest
uv run ruff check chainup_agent tests
```

## 目录速写

```
server/
├── chainup_agent/     # Python 包
│   ├── api/           # HTTP 适配层（路由器、DTO）
│   ├── application/    # 用例编排（逐步实现）
│   ├── cli/            # 命令行入口（seed、ngrok URL 助手等）
│   ├── domain/         # 领域模型与不变式
│   ├── infrastructure/# DB、Telegram、交易所客户端
│   └── core/           # 配置、日志、横切异常
├── tests/
└── docs/
    ├── BACKEND_SPEC.md
    ├── API_INTEGRATION_GUIDE.md
    ├── PHASE1_ACCEPTANCE.md                  # 收口验收清单（可勾选）
    └── API_ADMIN_OBSERVABILITY_EXECUTIONS.md   # Admin 执行记录 API 契约（agent_execution）
```

## 免责声明

占位路由现阶段返回 **501** + `StubBody`，直到与 `specs/openapi/` 逐项对签并实现领域逻辑为止。
