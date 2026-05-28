# Skill Publish 生效链

> 功能 ID：`2026-05-27--skill-publish-effective`  
> 产品 Agent 定稿 · 对齐 closure **P‑07** · W1 **SK-B1～B3**（+ **SK-B5** Prompt 门禁）

## 背景

**`read_skill_operation_spec`** 的生产链路要求：Git **`skill-specs`** 正文经 **Publish** 落库为 **全文快照**，Runtime **仅读 `PUBLISHED` effective**；未发布引用 **`PROMPT_SKILL_REF_INVALID`**（**FR-T11 / PUBLISH.md**）。

**`2026-05-27--runtime-write-path-pipeline`**（**done**）已交付 **编排接线 + 时间线五段序**，Runtime 首版从仓内 **`runtime-bundle.json`** 读规范。本包补齐 **DB 存储 + Admin Publish API + 控制台发布面 + Runtime 改读 DB**，并与 **Trading Prompt `skillSpecRef` Publish 门禁**（**SC-PM-21**）对齐。

规格 SSOT：`product-doc/specs/requirements/skill-specs/` · OpenAPI 同窗 **`prompt-management.yaml`** · **`skill-operation-spec-schemas.yaml`**。

## 用户故事

- 作为 **运营**，我在 Admin **「技能与工具」** 查看已登记 `skillId`、版本履历，并将 **contract-complete** 规范 **Publish** 到 Runtime，使交易员写路径读到最新版。
- 作为 **Prompt 编辑**，我发布 **TRADING** 包时，若 **`skillSpecRef`** 指向未发布 skill 版本，系统 **阻断 Publish** 并提示修正。
- 作为 **Runtime/测试**，**`GET …/skills/effective`**（及存量 **`GET …/runtime/skill-operation-spec/effective`）在 Publish 后返回 **200 + 全文/节摘要**；未发布返回 **`PROMPT_SKILL_REF_INVALID`**。

## 验收标准

- [x] **AC-1**：存在 **`skill_operation_spec_version`** / **`skill_operation_spec_pointer`** 表（同窗 [`skill_operation_spec.v1.sql`](../../../product-doc/specs/requirements/skill-specs/schema/skill_operation_spec.v1.sql)）；提供 **一次性 import**（Alembic data 或管理命令）可从 **`product-doc/.../published/runtime-bundle.json`**（或同步后的 `server/.../runtime-bundle.json`）导入 **11** 篇 **publishRequired** 技能 **全文 `bodyMarkdown`** + **`specDigest`**，并设置各 `skillId` **生效指针**。
- [x] **AC-2**：**`GET /api/v1/admin/skill-specs`** 返回 **200**，**`items[]`** 含 **`skillId`、`skillSpecVersion`、`lifecycle`、`contractComplete`、`specDigest`、`publishedAt`**（camelCase）；支持 Query **`lifecycle`** 筛选。
- [x] **AC-3**：**`GET /api/v1/admin/skill-specs/{skillId}`**、**`GET …/versions`**、**`GET …/versions/{skillSpecVersion}`** 分别返回摘要、履历、指定版 **全文**；未知 `skillId` / 版本 → **404**。
- [x] **AC-4**：**`POST /api/v1/admin/skill-specs/{skillId}/publish`** Body 含 **`skillSpecVersion`**（及可选 **`bodyMarkdown`、`specDigest、sourceGitRef`**）→ **200**，**`lifecycle=PUBLISHED`**；**禁止**版本回退；**`contractComplete=false`** 或契约校验失败 → **400/422** + 明确 **`code`**；**禁止**仅存摘要无全文。
- [x] **AC-5**：**`GET /api/v1/internal/skills/effective?skillId=&skillSpecVersion=`** 对已发布组合返回 **200** + **`bodyMarkdown`**（及 **`specDigest`、`etag`**）；未发布/未知 → **404** 或 **403**，**`code=PROMPT_SKILL_REF_INVALID`**。支持 **`If-None-Match` → 304**（策略见 `backend/notes.md`）。
- [x] **AC-6**：**`GET /api/v1/runtime/skill-operation-spec/effective?skillId=`**（存量 Runtime 路由，见 **`runtime-write-path-pipeline`**）在 AC-1 import / AC-4 Publish 后 **改读 DB 生效指针**（**不再仅依赖** 静态 bundle 文件）；行为与 AC-5 一致（未发布 → **`PROMPT_SKILL_REF_INVALID`**）。
- [x] **AC-7**：**`POST /api/v1/admin/prompt-packs/{promptPackId}/publish`** 当包为 **TRADING**（或配置要求 **`skillSpecRef`** 的 **ANALYSIS**）且 **`skillSpecRef`** 指向 **未 PUBLISHED** 的 skill 版本时 → **422**，**`code=PROMPT_SKILL_REF_INVALID`**（**SC-PM-21**）；已发布引用可成功发布。
- [x] **AC-8**：Admin 路由 **`/ai/tool-registry`**（菜单 **技能与工具**）：列表展示 AC-2 数据；可查看版本履历与正文预览；**Publish** 操作调用 AC-4 成功后列表/详情显示新版 **`skillSpecVersion`**；失败展示 API **`message`/`code`**。
- [x] **AC-9**：Publish **单调性**：对已存在 **`0.2.0-contract`** 的 skill 再 Publish **`0.1.0-mvp`** → **400**（或文档约定码）；成功 Publish 后旧版可标 **`DEPRECATED`** 或保留履历但 **指针仅向前**（实现细节见 `backend/notes.md`，须与 OpenAPI 一致）。

## 范围

### 本期包含

- **SK-B01**：表结构 + **runtime-bundle import**（种子）。
- **SK-B02**：Admin **`/api/v1/admin/skill-specs/*`**（list / get / versions / version body / publish）。
- **SK-B03**：**`GET /api/v1/internal/skills/effective`** + Runtime **改读 DB**（AC-6）。
- **SK-B05**：Prompt Publish **`skillSpecRef`** 门禁（AC-7）。
- **Admin FE**：**`/ai/tool-registry`**（对齐 `product-doc/src/admin` 原型交互，接真实 API）。
- **测试**：pytest Admin + internal + runtime 读路径；**E2E** Admin 发布主流程（见 `test/e2e-cases.md`）。
- 功能包 **`api.openapi.yaml`**、**`test/*`** 追溯。

### 本期不包含

- **写路径编排 / 时间线五段序**（**`2026-05-27--runtime-write-path-pipeline`** · **done**）。
- **Git CI** `check_skill_contract_complete.py` 入仓门禁实现（可 **调用** 或等价校验；CI 脚本本身属规格仓）。
- **Eval staging 真跑**（**SK-B03 eval** · P2 / 独立 staging 包）。
- **Rollback API**（指针回指；可后续迭代，本包 **仅** Publish 单调 + import 初始指针）。
- **Deeplink** 页面。

## 界面与交互（含页面）

**含页面：是**。

| 入口 | 路由 | 说明 |
|------|------|------|
| 技能与工具 | **`/ai/tool-registry`** | 列表 · 详情/履历 · Publish（对齐 product-doc 原型 **A 类 Tab**） |
| Prompt 策略（门禁提示） | **`/prompts/strategy`** · 编辑器 | Publish 前 **`skillSpecRef`** 校验失败提示（**不** 重做整页，仅接 AC-7 错误体） |

**Observability** 存量页继续消费 **`agent.skill.spec_read`**（**runtime-write-path-pipeline** 已交付）；本包 **不** 强制新增时间线 UI。

## 非功能要求

- **不得** 在 API 响应 / 日志写入 Secret；**`bodyMarkdown`** 可进 DB，**时间线仍仅** `specDigest` + 版本元数据。
- Publish 与 effective 读须 **事务一致**（Publish 提交后下一读可见）。
- Admin 鉴权：Bearer（与存量 Admin API 一致）。
- 时间字段 UTC（`BACKEND_SPEC` §2.1）。

## 实现备注

| 层 | 路径（计划） |
|----|----------------|
| DDL / import | Alembic · `skill_operation_spec_*` · import 命令 |
| Admin API | `api/routers/v1/admin_skill_specs.py`（新） |
| Internal / Runtime 读 | `application/skill_operation_spec_store.py` · 改造 `runtime_skill_operation_spec.py` |
| Prompt 门禁 | `application/admin_prompt_packs.py`（或 publish 服务） |
| Admin FE | `admin/src/pages/ai/ToolRegistryPage.vue` · `admin/src/shared/api/admin-skill-specs.ts` |
| 参考原型 | `product-doc/src/admin` · `/ai/tool-registry` |

## 待确认问题

- [x] Q1：Runtime 对外保留 **`/api/v1/runtime/skill-operation-spec/effective?skillId=`**（无必填 `skillSpecVersion`），内部按 **指针** 解析最新 **PUBLISHED** — 与 **`internal/skills/effective`**（显式版本）并存。
- [x] Q2：首版 **Rollback** 不做；运营通过 **再 Publish 更高版本** 前进。
