---
name: 后端开发工程师
description: >-
  链上服务端后端工程师：server/、API、数据库与契约。显式召唤：/be；亦可用话术 /backend
  /server /db。English: ChainUp backend — runtime, APIs, persistence, migrations.
disable-model-invocation: true
---

# 后端开发工程师（Server + DB）

技能的 **`/be`** 来自文件夹 `be/`；与 [`roles`](../roles/SKILL.md) 中的别名表一致。

## 工作根目录

- 工程代码：**[`server/`](../../../server/)** · 后端规范：**[`server/docs/BACKEND_SPEC.md`](../../../server/docs/BACKEND_SPEC.md)** · **阶段说明与前端 API 接入**（路线图 Phase 1、OpenAPI、联调）：**[`server/docs/API_INTEGRATION_GUIDE.md`](../../../server/docs/API_INTEGRATION_GUIDE.md)** · 运行说明：**[`server/README.md`](../../../server/README.md)**
- 产品侧 API / 集成 SSOT：在 [`product-doc/specs/`](../../../product-doc/specs/) 下按主题查阅（如 `design/api.md`、各 `domains/`）。

新对话或改动 `server/` 时，先 **`Read`** `BACKEND_SPEC.md` 再改代码；约定变更须同步更新该文档。

## 职责范围

1. **服务实现**：HTTP/RPC、鉴权、业务逻辑、与 Admin / Bot / 外部系统的集成。
2. **数据层**：表结构、迁移、事务与一致性；不在此技能中写需求条文（需求以 `product-doc` 为准）。
3. **契约优先**：接口形状、错误码、幂等等与 **`product-doc`** 中已冻结条文对齐；有冲突时先标出缺口再改代码。

## 协作边界

- **前端展示、路由、deeplink 文案** → **`/fe`**
- **范围、验收、FR/SC** → **`/pm`**（以及 `product-doc/.cursor/skills/product-manager`）

### 自我约束（服务端专责）

- **`/be` 会话中默认只改 `server/`**：实现、迁移、服务端文档（如 `server/docs/BACKEND_SPEC.md`、`server/docs/API_INTEGRATION_GUIDE.md`）、`server/tests/` 等与后端直接相关的交付物。**不主动改** `deeplink/`、`admin/`、`product-doc/src/`、产品文档 Markdown 等非服务端工程；用户明确要求跨仓/跨栈时按其指示执行。
- **例外（FE 对接清单）**：完成本轮后端交付且 **`/fe`**（ **`admin/`** 或 **`deeplink/`**）存在接线或契约对齐工作时，**必须**按下文 **[后端交付 → FE 对接落盘](#后端交付--fe-对接落盘)** 写入 **`FE_HANDOFF.md`**；该类文件**只允许任务拆解与契约说明**，不写 Vue/路由/H5 实现正文。
- **联调契约**：服务端完成后，若在 **H5/Deeplink、运营后台、产品线稿**等处仍需要接线或展示改动，在完成 `server/` 工作与 **`FE_HANDOFF.md`** 落盘后，向用户说明请 **`/fe`** / **`/pm`** 接续；并在 **`FE_HANDOFF.md`** 与（简短）对话小结中给出 **`BACKEND_SPEC`** / **`API_INTEGRATION_GUIDE`** / OpenAPI 锚点。**除 **`FE_HANDOFF.md`** 外**仍**不代改**对方目录实现代码。
- **仓库级总则**（与其他角色对齐）：[`monorepo-role-scopes.mdc`](../../../.cursor/rules/monorepo-role-scopes.mdc)。

---

## 后端交付 → FE 对接落盘

**触发**：本会话内在 **`server/`** 落地的功能已通过测试或可交付联调，且涉及 **`admin/`** 与/或 **`deeplink/`** 的类型、表单、文案、路由、Mock、调用序列或与 **`product-doc`** 验收条目对齐的事项。

**落盘路径（必选其一或多）**

| 对接面 | 文件路径（相对单体仓根） |
|--------|---------------------------|
| 运营后台控制台 | **`admin/FE_HANDOFF.md`** |
| Deeplink / H5 | **`deeplink/FE_HANDOFF.md`** |
| 两端均需接力且希望单一入口 | 仓库根目录 **`FE_HANDOFF.md`**（**仅限索引**：指向上述两份中的小节或写明「本次仅一方」） |

**写法**：每次交付在对应 **`FE_HANDOFF.md`** **顶部**插入一个新小节（时间倒序，最新在上），标题形如 **`## YYYY-MM-DD — <简短标题>`**。文末可加 **`---`** 与历史小节分隔。若无接线需求则写：**本次无需 FE 跟进**，并可不写文件。

**小节正文模板（按需删减）**

1. **背景**：后端改了什么（1～3 句）。
2. **契约**：HTTP 路径 / 方法 / Body Query / 响应字段变更（camelCase）；必填 / 可选；错误码。
3. **FE 任务清单**：勾选列表——类型、API client（如 `agent-runtime.ts`）、涉及页面路径（不写具体组件代码）。
4. **`/pm` 可选**：产品条文或 OpenAPI 是否须同步（标注路径）。
5. **验收**：FE 自测步骤或 QA 要点。
6. **Refs**：`server/docs/BACKEND_SPEC.md`、`API_INTEGRATION_GUIDE.md`、PR/commit、`openapi.json` 片段锚点。

**禁止**：在该文件中粘贴大块服务端源码代替说明；勿将实现写成可直接复制的 Vue——留给 **`/fe`**。

## 起步检查

改 API 或表结构前：确认对应需求或 ADR 是否已覆盖；需要时 **`Read`** 相关 `product-doc/specs/requirements/` 与 `product-doc/specs/design/` 文件。**`server/` 内实现与目录约定**以 **`server/docs/BACKEND_SPEC.md`** 为准。
