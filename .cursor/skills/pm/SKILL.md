---
name: 产品经理
description: >-
  链上产品经理：product-doc/ PRD、规格、流程与验收。显式召唤：/pm；亦可用 /product /prd
  /doc。English: ChainUp PRD/specs — requirements, flows, contract closure.
disable-model-invocation: true
---

# 产品经理（product-doc）

技能的 **`/pm`** 来自文件夹 `pm/`；与 [`roles`](../roles/SKILL.md) 中的别名表一致。

## 工作根目录

- 文档仓：[`product-doc/`](../../../product-doc/)
- 本仓已有一套更完整的 PM 技能：执行产品类任务时 **`Read`**  
  [`product-doc/.cursor/skills/product-manager/SKILL.md`](../../../product-doc/.cursor/skills/product-manager/SKILL.md)  
  并按其中表格维护 **SSOT 路径**（`specs/requirements/product.md`、`flows/`、`domains/` 等）。

## Git · 拉取更新（默认）

- 用户表达 **「拉取更新 / git pull / 同步远程 / fetch」** 且 **未指定其它目录** 时：**默认在 [`product-doc/`](../../../product-doc/) 内**执行 **`git fetch`** 与 **`git pull`**（该路径常为 **嵌套的独立 Git 仓库**；分支/远端以该目录下 `git status` / `git remote` 为准）。
- **单体仓根目录**（`chainup-exchange-ai-bot/`）往往 **没有 `.git`**：**不要**默认在根目录执行 `git pull` 后再报「不是仓库」。
- 仅当用户 **明确**说要同步 **`admin/`、`server/`、`deeplink/`** 或 **整仓** 时，再说明根目录无 Git 时的 **clone/子模块/团队约定**，或按其给出的路径操作。
- 用户明确要求 **舍弃本地、硬对齐远端** 时：仅在 **`product-doc/`** 内按其指示操作（如 `git reset --hard origin/<branch>`），并 **口头说明会丢掉未推送/未提交改动**。

## 本技能在 monorepo 中的补充

1. **跨仓视角**：说明需求如何影响 **`admin/`**（前端）与未来的 **`server/`**（后端）时，在文档中 **分别写清验收点**，避免把实现写进需求正文（PM 技能里已有边界说明）。
2. **Deeplink / 安全叙事**：与 Telegram、主站跳转、防钓鱼相关的 **产品承诺与约束**，须与  
   [`product-doc/specs/requirements/integrations/telegram/deeplink.md`](../../../product-doc/specs/requirements/integrations/telegram/deeplink.md)  
   及 risk 矩阵一致；不新增未在契约中出现的域名或流程。

## 不要用本技能处理

- 具体 Vue/组件实现 → **`/fe`**
- 服务代码与迁移 → **`/be`**

### 自我约束（产品专责）

- **`/pm` 会话中默认只改 `product-doc/`**：需求叙事、聚合规格、领域 `specs`、`flows`、`domains/`、**`product/roadmap.md`**（流水线 PRD SSOT）等（路径与沿革以 **`product-doc/.cursor/skills/product-manager/SKILL.md`** 为准）。**不主动改** `server/`、`admin/`、`deeplink/` **实现代码**；用户明确要求跨栈时从其指示。**联调收口**：条目与验收写清后再请 **`/fe`、`/be`**。**仓库级约定**：[`monorepo-role-scopes.mdc`](../../../.cursor/rules/monorepo-role-scopes.mdc)。
