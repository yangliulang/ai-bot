# ChainUp 单体仓与 Agent Pipeline 对照

> 与 `.cursor/rules/monorepo-role-scopes.mdc`（`/be` `/fe` `/pm` `/qa`）**并存**：流水线 Agent 管「单功能交付」；角色规则管「默认只改本栈目录」。

## 目录职责

| 目录 | 维护方 | 流水线中的角色 |
|------|--------|----------------|
| `product-doc/` | 产品 | PRD / 路线图 SSOT；`product.plan` 读 inventory + 指定 PRD 章节 |
| `server/` | 后端 | `apps.backend.path`；契约另见 `server/docs/`、`product-doc/specs/openapi/` |
| `admin/` | 前端 | **默认** `apps.frontend.path`（运营控制台） |
| `deeplink/` | 前端 | 开通 H5；有页面功能在 `brief.md` + `frontend/integration.md` 标明 |
| `official-website/` | 前端 | 官网；非默认 frontend 路径，按功能包范围 |
| `handoff/features/` | 全员（按 phase） | 单功能 brief、OpenAPI、status.yaml |

## API 契约真源（优先级）

1. 功能包内 `api.openapi.yaml`（本功能增量/冻结）
2. `product-doc/specs/openapi/`、`product-doc/specs/design/api.md`
3. `server/` 运行中 `/openapi.json`（联调参考，以产品冻结 YAML 为准）

**响应格式**：FastAPI **HTTP 状态码** + JSON body（`AppError` 等），**不是** demo 流水线里的 `{ "code": 0, "message", "data" }`。功能包 OpenAPI 须写真实 schema。

## 本地联调默认端口

| 服务 | 命令 | URL |
|------|------|-----|
| API | `cd server && uv run chainup-agent-api` | http://127.0.0.1:8080 |
| Admin | `cd admin && npm run dev` | http://127.0.0.1:5173（proxy `/api` → 8080） |
| Deeplink | `cd deeplink && npm run dev` | http://127.0.0.1:5174 |

## 与 `/be` `/fe` `/pm` 协作

- 开 **product-agent** Chat 做规划/定稿时，等价产品侧；仍遵守不改 `server/` 代码。
- **backend-agent** 只改 `server/`；**frontend-agent** 改 `admin/` / `deeplink/`（按 brief）。
- 用户显式 `/be` 或 `/fe` 时，以 `monorepo-role-scopes.mdc` 为准；流水线 `status.yaml` 的 `next` 决定当前负责 Agent。

## 存量 backlog 参考

- **`product-doc/product/roadmap.md`** — 流水线 **PRD 主真源**（`project.prd.primary`）：**P0**、阶段 **A～D**、**优先级与编号对照**；`product.plan` 据此列 `handoff/roadmap/phase-*.md` backlog
- **`product-doc/specs/requirements/closure-completion-matrix.md`** · **`closure-internal-sprint.md`** — **当周硬排序**（**P‑01～P‑08**、**W1** 五步）；与 roadmap 同窗，优先于口头排期
- `product-doc/development-roadmap.md` — **遗留**分阶段 HTTP 路线图（新规划勿再以之为 SSOT）
- `handoff/product/inventory.md` — 接入流水线时的切口（指挥官维护）

## Hook 提醒（需用户确认再下一步）

配置在 **`pipeline.project.yaml` → `pipeline.hooks`**（`.cursor/hooks.json` 路径不变）。详见 [hooks.md](../pipeline/hooks.md)。

| 字段 | 本仓默认 | 含义 |
|------|----------|------|
| `enabled` | `true` | 总开关 |
| `remind_on_write` | `true` | 写入 `status.yaml` 后提示下一条 `/pipeline-*` |
| `stop_followup` | **`false`** | **不在 Agent 结束时自动续聊** → 需指挥官新开 Chat |
| `require_new_chat` | `true` | 文案强调「确认后新开 Chat，勿自动推进门禁」 |

**更半自动**：`stop_followup: true`。**完全关闭**：`enabled: false`。
