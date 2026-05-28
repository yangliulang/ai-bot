# 前端对接

> **含页面：是** · `frontend.integrate` 完成 · 2026-05-26

## 联调结论

| 项 | 值 |
|----|-----|
| 路由 | **`/ai/tool-registry`**（侧栏 **技能与工具** · `ai.tool-registry`） |
| 重定向 | `/ai/skill-specs`、`/tools/registry`、`/tools`、`/ai/tool-policies` → `/ai/tool-registry` |
| API 客户端 | `admin/src/shared/api/admin-skill-specs.ts` |
| 页面 | `admin/src/pages/ai/ToolRegistryPage.vue` |
| 导航 | `admin/src/shared/config/admin-nav.ts`（`tool-registry` 图标复用 orchestration） |
| 后端 Base URL | http://127.0.0.1:8080（Vite proxy `/api`） |
| 联调日期 | 2026-05-26 |

## 接口映射

| 页面/操作 | Method | Path |
|-----------|--------|------|
| 列表 | GET | `/api/v1/admin/skill-specs` · Query `lifecycle` |
| 摘要（抽屉头） | GET | `/api/v1/admin/skill-specs/{skillId}`（列表行已含指针，履历用 versions） |
| 履历 | GET | `/api/v1/admin/skill-specs/{skillId}/versions` |
| 正文预览 | GET | `/api/v1/admin/skill-specs/{skillId}/versions/{skillSpecVersion}` |
| Publish | POST | `/api/v1/admin/skill-specs/{skillId}/publish` |

## Prompt 门禁（AC-7）

| 项 | 说明 |
|----|------|
| 页面 | `/prompts/strategy` · `/prompts/editor/:id`（存量） |
| 错误展示 | `explainPromptPackApiError` 增加 `PROMPT_SKILL_REF_INVALID` / `PROMPT_SKILL_VERSION_ROLLBACK` 文案 |
| 实现 | `admin/src/pages/prompts/usePromptPackEditor.ts` |

## 联调自检

- [x] **主流程**：列表加载 → 详情抽屉 → 版本切换 → 正文预览 → Publish 新版本
- [x] **错误态**：列表/履历/正文/Publish 失败展示 API `message`（含 `code` 说明）
- [x] **加载态**：列表 loading、`UiTableEmptyRow`；Publish 按钮 submitting
- [x] **筛选**：生命周期 Query + 本地 keyword

## 联调环境

```bash
cd server && uv run alembic upgrade head && uv run chainup-agent-api   # :8080
cd admin && npm run dev   # :5173
```

Admin 登录后 Bearer 由 `httpClient` 自动附加（`ADMIN_CONSOLE_JWT_SECRET` 配置时）。

## 代码变更摘要

| 文件 | 变更 |
|------|------|
| `admin/src/shared/api/admin-skill-specs.ts` | list/get/versions/body/publish |
| `admin/src/pages/ai/ToolRegistryPage.vue` | **对齐 product-doc 原型**：5 统计卡 · Tab（可下单/查询/外部/审计）· 三列技能表 · 行点抽屉 |
| `admin/src/pages/ai/SkillOperationDrawer.vue` | 概览 + 正文 Tab · Publish · 版本履历 |
| `admin/src/entities/tool-registry/*` | 登记元数据（userFlow/exchange）与 API merge |
| `admin/src/app/router/index.ts` | 路由 + 旧路径重定向 |
| `admin/src/shared/config/admin-nav.ts` | 侧栏「技能与工具」 |
| `admin/src/assets/main.css` | tool-registry 行高亮 / tbd 行样式 |
| `admin/src/pages/prompts/usePromptPackEditor.ts` | skillSpecRef 发布错误文案 |

**原型对照**：`product-doc/src/admin` · `http://localhost:5176/ai/tool-registry`（统计区 + Tabs + `SkillRegistryTable` 列布局）；B/C/审计 Tab 本期占位，数据仅 **A 类 + 真实 API**。

## 遗留 / 非本期

- product-doc 原型中的 **B/C 类工具矩阵 Tab**、本地 demo 开关未移植（brief 仅要求 skill Publish 主流程）
- E2E 由 test-agent 执行 `test/e2e-cases.md`

## 备注

- 与 `backend/notes.md`、功能包 `api.openapi.yaml` 一致；camelCase 直出。
- 下一步：**新开 Chat** → `/pipeline-test-e2e 2026-05-27--skill-publish-effective`
