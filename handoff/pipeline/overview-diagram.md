# 唤起 Agent — 总览图

> 你从指挥官视角唤起某 Agent 做 XXX 时，**Rules / Skills / roles / 流转** 如何叠加。  
> 详细时序与返工分支见 [invoke-flow.md](invoke-flow.md)。  
> Mermaid 源文件（便于导出/编辑）：[diagrams/invoke-overview.mmd](diagrams/invoke-overview.mmd)

---

## 总览

```mermaid
flowchart TB
  subgraph YOU["👤 指挥官"]
    A["新开 Chat\n/pipeline-* 2026-05-25--xxx\n或 @*-agent.mdc 2026-05-25--xxx"]
  end

  subgraph CURSOR["Cursor 加载层（自动叠加）"]
    P["project.mdc  alwaysApply\n全项目约定 + 简写协议"]
    SK["Skill  可选\n→ 指定 tasks.yaml 任务键"]
    AG["*-agent.mdc\nphase/next 门禁"]
    DEV["api-dev / web-dev / test-dev\n改代码时 globs 附加"]
  end

  subgraph DOCS["handoff 分工"]
    R["roles.md  岗位与擅长区"]
    T["tasks.yaml  本步怎么做"]
    W["WORKFLOW.md  状态机说明"]
    C["conventions  代码/测试规范"]
  end

  subgraph FeaturePkg["功能包 handoff/features/2026-05-25--xxx/"]
    ST["status.yaml  门禁开关"]
    BR["brief + api.openapi.yaml"]
    OUT["各角色交接产出"]
  end

  subgraph CODE["apps/"]
    API["apps/api/"]
    WEB["apps/web/"]
  end

  A --> SK
  A --> AG
  SK --> T
  AG --> T
  AG --> R
  AG --> W
  P --> T
  P --> ST

  T --> ST
  T --> BR
  T --> OUT
  T --> C
  C --> DEV
  DEV --> API
  DEV --> WEB

  ST -->|"phase/next 不符"| STOP["❌ 停止\n说明该找谁"]
  ST -->|"符合"| OK["✅ 写产出\n更新 status.yaml"]
```

---

## 图例（读图用）

| 区域 | 含义 |
|------|------|
| 指挥官 | 你只给 功能 ID + Skill 或 @规则 |
| Cursor 加载层 | 自动叠加上下文；Skill 只有用 `/` 唤起时才有 |
| handoff 分工 | 谁 / 何时 / 做什么 / 怎么写 —— 各管一块 |
| 功能包 | **真相源**：门禁与交接文件都在这里 |
| apps | 实际代码；规范由 conventions + *-dev 约束 |

| 箭头含义 | |
|----------|--|
| Skill / agent → tasks | 展开「做 XXX」的具体步骤 |
| agent → roles | 岗位边界与擅长区（不替代门禁） |
| tasks → status | 执行前/后都要对上门禁 |
| status 不符 → 停止 | 不擅自改 phase，报告该找哪个 Agent |

---

## 相关文档

- [COMMANDER.md](COMMANDER.md) — 你怎么下命令
- [roles.md](roles.md) — 各 Agent 岗位对照
- [tasks.yaml](tasks.yaml) — 任务步骤正文
- [WORKFLOW.md](../WORKFLOW.md) — phase 定义
