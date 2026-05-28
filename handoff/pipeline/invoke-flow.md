# 唤起 Agent 时发生了什么

> 你从指挥官视角喊一句：`/pipeline-backend 2026-05-25--greeting` 或 `@backend-agent.mdc 2026-05-25--greeting`。  
> **总览图（单独保存）**：[overview-diagram.md](overview-diagram.md) · 源文件：[diagrams/invoke-overview.mmd](diagrams/invoke-overview.mmd)

---

## 总览（一张图）

与 [overview-diagram.md](overview-diagram.md) 同源；下文为详细展开（时序、返工、主路径）。

---

## 按时间顺序（推荐理解路径）

```mermaid
sequenceDiagram
  participant U as 指挥官
  participant S as Skill pipeline-*
  participant P as project.mdc
  participant A as *-agent.mdc
  participant T as tasks.yaml
  participant R as roles.md
  participant ST as status.yaml
  participant F as 功能包其它文件
  participant C as conventions

  U->>S: /pipeline-backend 2026-05-25--greeting
  Note over S: 解析功能 ID，选定 task 键<br/>backend.implement
  S->>T: 读取 tasks.backend.implement.steps
  S->>A: 遵守 backend-agent 门禁

  P-->>A: 始终生效：契约优先、简写协议
  A->>ST: 检查 phase / next
  alt next ≠ backend-agent
    A-->>U: 停止：当前应由 test-agent 等
  else 门禁通过
    A->>R: 查阅岗位边界与借鉴能力（可选深读）
    A->>F: 读 brief + api.openapi.yaml
    A->>T: 按 steps 实现
    A->>C: 写 apps/api 时遵循 api-dev + backend.md
    A->>F: 写 backend/notes.md
    A->>ST: phase→backend_done, next→test-agent
    A-->>U: 完成，下一步 /pipeline-test-api
  end
```

---

## 四类「说明文档」分工（别混）

```mermaid
flowchart LR
  subgraph WHO["Who 我是谁"]
    roles["roles.md"]
  end
  subgraph WHEN["When 何时交接"]
    wf["WORKFLOW.md"]
    st["status.yaml"]
  end
  subgraph WHAT["What 这一步做什么"]
    tasks["tasks.yaml"]
    skill["Skill 点名 task"]
  end
  subgraph HOW["How 怎么写代码/用例"]
    conv["conventions/"]
    dev["*-dev.mdc"]
  end

  roles -.->|"不决定 phase"| st
  wf --> st
  skill --> tasks
  tasks --> st
  tasks --> conv
  conv --> dev
```

| 你唤起时… | 实际在用什么 |
|-----------|----------------|
| `/pipeline-backend 2026-05-25--xxx` | **Skill** 选任务 → **tasks.yaml** 展开步骤 → **backend-agent.mdc** 守门 |
| `@backend-agent.mdc 2026-05-25--xxx` | 无 Skill，**project.mdc** 简写协议 + **agent 规则** 猜/读 **tasks** |
| `/pipeline-next 2026-05-25--xxx` | **Skill** 读 **status.yaml** → **next_task_map** → 自动选 **tasks** |
| Agent 想「像 PM/QA 那样思考」 | 读 **roles.md**（不替代 **status** 门禁） |
| Agent 改 `apps/api/` | 附加 **api-dev.mdc** + **conventions/backend.md** |

---

## 标准主路径（7 步 ↔ 7 次唤起）

```mermaid
flowchart LR
  P1["product\ncontract"] --> P2["backend\nimplement"]
  P2 --> P3["test\napi"]
  P3 --> P4["frontend\nintegrate"]
  P4 --> P5["test\ne2e"]
  P5 --> P6["designer\nreview"]
  P6 --> P7["product\naccept"]

  P1 -.->|status| S1["contract_ready"]
  P2 -.-> S2["backend_done"]
  P3 -.-> S3["tested"]
  P4 -.-> S4["frontend_done"]
  P5 -.-> S5["e2e_verified"]
  P6 -.-> S6["ui_reviewed"]
  P7 -.-> S7["done"]
```

每一步都是：**新 Chat → 对应 Skill + 功能 ID → 读 status 门禁 → 执行 tasks 里该步 → 更新 status**。

---

## 返工时的分支（同一套机制）

```mermaid
flowchart TD
  E2E["test.e2e 失败"] --> FE["frontend.fix-e2e"]
  FE --> RT["test.e2e-retest"]
  RT --> DR["designer.review"]

  UI["designer.review P0"] --> FU["frontend.fix-ui"]
  FU --> RR["designer.rereview"]
  RR --> ACC["product.accept"]

  API["test.api 失败"] --> BE["backend 修 + 再 test.api"]
```

---

## 指挥官最小记忆

1. **你只给**：功能 ID +（推荐）一个 **Skill** 名。  
2. **门禁看**：`status.yaml` 的 `phase` / `next`。  
3. **步骤在**：`tasks.yaml`（Skill 帮你点名）。  
4. **岗位感在**：`roles.md`（Agent 按边界做事，不越权）。  
5. **代码规范在**：`conventions/` + `*-dev.mdc`（改代码时自动带上）。

操作手册：[COMMANDER.md](COMMANDER.md)
