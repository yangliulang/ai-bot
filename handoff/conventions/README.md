# 开发规范（Conventions）

本目录是 **各角色在开发项目时的约定正文**（可写长、可带示例）。  
与 **Agent 流转** 分离：流转见 [WORKFLOW.md](../WORKFLOW.md)，规则见 `.cursor/rules/`。  
**指挥官操作**（怎么 `/` 或 `@` 各 Agent）：见 [pipeline/COMMANDER.md](../pipeline/COMMANDER.md)。

## 规则如何生效

| 层级 | 位置 | 作用 |
|------|------|------|
| 全项目 | `.cursor/rules/project.mdc` | `alwaysApply: true`，所有对话 |
| 按路径 | `.cursor/rules/api-dev.mdc`、`web-dev.mdc`、`test-dev.mdc` | 编辑匹配文件时自动附加（api/web 由 `sync-project-rules.sh` 生成） |
| 项目绑定 | `pipeline.project.yaml` | 代码路径、URL、PRD；见 [pipeline-project.md](pipeline-project.md) |
| 按角色流转 | `.cursor/rules/*-agent.mdc` | 手动 `@` 或匹配 `handoff/features` 等 |
| 本目录正文 | `handoff/conventions/*.md` | 人读 + Agent 规则内引用 |
| 单功能例外 | `handoff/features/2026-05-25--xxx/brief.md` 等 | 覆盖本目录的共性约定 |

**扩展方式**：优先改本目录对应 `*.md`，再同步精简 `.cursor/rules/*-dev.mdc` 中的硬约束（保持 rule 短小）。

## 各角色读哪份

| Agent | 流转规则 | 开发规范正文 | 自动附加的 dev rule |
|-------|----------|--------------|---------------------|
| product-agent | `product-agent.mdc` | [product.md](product.md) | `project.mdc` |
| backend-agent | `backend-agent.mdc` | [backend.md](backend.md) | `api-dev.mdc`（编辑 `apps/api/`） |
| test-agent | `test-agent.mdc` | [testing.md](testing.md) | `test-dev.mdc` |
| frontend-agent | `frontend-agent.mdc` | [frontend.md](frontend.md) | `web-dev.mdc` |
| designer-agent | `designer-agent.mdc` | [design.md](design.md) | `web-dev.mdc`（只读页面时可选） |

## 目录

- [project.md](project.md) — 仓库结构、契约优先、禁止事项
- [pipeline-project.md](pipeline-project.md) — `pipeline.project.yaml` 字段与迁移
- [product.md](product.md) — brief / OpenAPI / backlog 写法
- [onboarding-modes.md](onboarding-modes.md) — greenfield / brownfield / continuing
- [../product/inventory.md](../product/inventory.md) — 存量项目切口清单（接入流水线前填写）
- [../product/brownfield-product-plan-prompt.md](../product/brownfield-product-plan-prompt.md) — 存量 `product.plan` 可复制 Prompt
- [backend.md](backend.md) — `apps/api/` 实现约定
- [frontend.md](frontend.md) — `apps/web/` 实现约定
- [testing.md](testing.md) — 用例、追溯矩阵、报告、自动化
- [../pipeline/checklists/README.md](../pipeline/checklists/README.md) — 规划与定稿检查清单
- [design.md](design.md) — UI 走查与严重度

## 与功能包的关系

```text
handoff/conventions/*     → 全项目默认
handoff/features/2026-05-25--*/  → 本功能需求与契约（优先级高于 conventions 冲突处）
```

示例：全局约定「错误响应含 code + message」；某功能包的 `api.openapi.yaml` 定义了具体 `code` 取值，以契约为准。
