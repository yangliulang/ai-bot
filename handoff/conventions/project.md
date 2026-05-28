# 全项目约定

## 项目绑定（Layer B）

路径、本地 URL、PRD 与 roadmap 默认文件由根目录 **`pipeline.project.yaml`** 定义。

- 模板：`pipeline.project.yaml.example`
- 读取：`source scripts/lib/read-pipeline-project.sh && pp_print_context`
- 修改后端/前端目录后：运行 `./scripts/sync-project-rules.sh` 更新 Cursor `globs`

## 仓库结构（本仓库示例）

```text
apps/api/          # apps.backend.path
apps/web/          # apps.frontend.path
handoff/features/     # features.root — 功能包（交接真相源）
handoff/roadmap/      # 阶段 backlog
handoff/conventions/  # 本目录
pipeline.project.yaml
```

## 契约优先

1. 实现以功能包内 `api.openapi.yaml` 为准；变更须同步 `backend/notes.md` 并注明。
2. 前端对接以 `frontend/integration.md` + OpenAPI 响应结构为准。
3. 不得在未更新契约的情况下改变对外 API 行为。

## 统一 API 响应（HTTP JSON）

```json
{ "code": 0, "message": "ok", "data": { } }
```

错误：

```json
{ "code": 40001, "message": "可读说明" }
```

## 环境默认值

以 `pipeline.project.yaml` 中 `apps.*.dev.base_url` 为准。本仓库当前为：

| 服务 | URL |
|------|-----|
| API | `http://localhost:3000/api` |
| Web dev | `http://localhost:5173` |

## 禁止（所有 Agent）

- 不要改无关功能包或无关应用目录
- 不要跳过 `status.yaml` 门禁推进 phase（除非指挥官在 Prompt 中显式豁免）
- 不要把密钥、token 写入仓库
- 不要依赖聊天历史作为需求来源（以功能包目录内文件为准）

## 修改范围原则

| 角色 | 可改代码 | 可改文档 |
|------|----------|----------|
| backend-agent | `apps.backend.path` | 本功能包的 `api.openapi.yaml`、`backend/notes.md`、`status.yaml` |
| frontend-agent | `apps.frontend.path` | 本功能包的 `frontend/integration.md`、`status.yaml` |
| test-agent | 测试脚本 | 本功能包的 `test/*`、`status.yaml` |
| designer-agent | 默认不改代码 | 本功能包的 `design/ui-review.md`、`status.yaml` |
| product-agent | 不改应用代码 | `handoff/roadmap/`、本功能包需求与契约、`status.yaml` |
