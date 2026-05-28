# Phase N — {阶段名称}

> 产品 Agent 维护。本文件定义 **一个开发阶段** 的功能清单与优先级，不替代单个功能包的 `brief.md`。

## 阶段目标

<!-- 本阶段要达成的业务/产品目标，1～3 句 -->

## 时间范围（可选）

- 开始：
- 结束：

## 功能 backlog

| 优先级 | 功能 ID | 功能名 | 状态 | 功能包路径 | 备注 |
|--------|---------|--------|------|------------|------|
| P0 | 2026-05-25--slug | 功能名 | planned / contract_ready / in_dev / done | handoff/features/2026-05-25--slug/ | |

功能 ID 格式：`YYYY-MM-DD--kebab-slug`（日期与 slug 之间为 **双横线** `--`）。

### 状态说明（roadmap 视角）

| 状态 | 含义 |
|------|------|
| `planned` | 已列入本阶段，功能包未创建或需求未写完 |
| `contract_ready` | brief + API 契约已定稿，可交给后端 |
| `in_dev` | 后端/测试/前端开发中（对应功能包 phase 非 done） |
| `done` | 功能包 status.yaml phase 为 done |

## 依赖与顺序

<!-- 哪些功能必须先做，哪些可并行 -->

```text
2026-05-25--feature-a → 2026-05-25--feature-b → 2026-05-25--feature-c
              ↘ 2026-05-25--parallel-feature（可并行）
```

## 本阶段不做

-

## 变更记录

| 日期 | 变更 | 操作人 |
|------|------|--------|
| | 创建 phase-N | product-agent |
