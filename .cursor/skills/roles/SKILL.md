---
name: 链上角色技能路由
description: >-
  链上单体仓角色入口：/fe /be /pm /qa 与话术别名；选角色后 Read 对应技能。English: ChainUp
  monorepo role router — maps slash aliases to fe/be/pm/qa skills.
disable-model-invocation: true
---

# 链上 · 角色技能路由

## 为什么输入栏里会看到 `/fe`、而不是一串英文？

在 Cursor Agent 技能里：**输入 `/` 后列表里显示的指令名 = 含有 `SKILL.md` 的那层文件夹名**（本仓为英文 `fe` / `be` / `pm` / `qa` / `roles`，以满足路径与索引约定）。`SKILL.md` 前置 **`name:`** 可用 **中文** 作为技能在别处展示或检索时的可读标题；与文件夹名可以不同。需要中文导读时仍以各文件内标题为准。

## 别名 → `/` 技能 → 职责

| 常用话术（搜索/口述即可） | 在 Agent 中选此技能（文件夹 → `/` 指令） | `Read` 路径 | 职责与代码根 |
|---------------------------|------------------------------------------|-------------|--------------|
| `/fe`、`/frontend`、`/admin`、`/web` | 文件夹 **`fe`** → `/fe` | `.cursor/skills/fe/SKILL.md` | `admin/`：管理端 Vue、路由与 deeplink / 外链相关前端 |
| `/be`、`/backend`、`/server`、`/db` | 文件夹 **`be`** → `/be` | `.cursor/skills/be/SKILL.md` | `server/`、数据库与 API |
| `/pm`、`/product`、`/prd`、`/doc` | 文件夹 **`pm`** → `/pm` | `.cursor/skills/pm/SKILL.md` | `product-doc/`：需求与规格文档 |
| `/qa`、`/test`、`/验收`、`/qe` | 文件夹 **`qa`** → `/qa` | `.cursor/skills/qa/SKILL.md` | `admin/` 页面验收 + 对照 `server/docs` 的 **HTTP/API 契约验收**、用例与回归；收口后交 **`feishu-report`** 上报测试报告 |
| **`/feishu-report`**、飞书汇报、测试报告上报 | 文件夹 **`feishu-report`** → `/feishu-report` | `.cursor/skills/feishu-report/SKILL.md` | 飞书发送：当日 FE/验收汇总，或承接 **`/qa`** 的测试报告 |
| **`/design-md`**、`/designmd`、`/设计系统`、`/design-tokens` | 文件夹 **`design-md`** → `/design-md` | `.cursor/skills/design-md/SKILL.md` | 仓库根目录 **`DESIGN.md`**（Google design.md）；Token、CLI lint/export、与 UI 对齐 |

聚合本路由说明：**`/roles`**（文件夹 `roles/`）。

## Agent 执行顺序

1. 按上表或用户话术选技能；用户若已 `@fe` `@be` `@pm` `@qa` `@roles`，以用户为准。
2. **`Read`** 上表所列路径下的 `SKILL.md`。
3. 若需完整 PM 条文：**`Read`** `product-doc/.cursor/skills/product-manager/SKILL.md`。

## 边界

- 本文件不重复各角色细则；只做路由与 Cursor 显示规则说明。
- 跨角色改动时可按用户指令串行加载多个技能。
- **各栈默认只改本仓对应目录**（避免「一个 Agent 改全栈」）：见 **[`monorepo-role-scopes.mdc`](../../rules/monorepo-role-scopes.mdc)**。
