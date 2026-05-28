# Pipeline 任务索引

**指挥官请用**：[handoff/pipeline/COMMANDER.md](pipeline/COMMANDER.md)（一步一步怎么开 Chat、怎么 `/` 或 `@`）。

Prompt 正文唯一来源：[handoff/pipeline/tasks.yaml](pipeline/tasks.yaml)。  
不要复制本页大段文字；用 Skill 或 `@*-agent.mdc 2026-05-25--xxx` 即可。

---

## 调用方式（摘要）

```text
/pipeline-backend 2026-05-25--greeting
/pipeline-next 2026-05-25--greeting
@backend-agent.mdc 2026-05-25--greeting
```

---

## 任务键 ↔ Skill

| 任务键 | Skill | 典型完成后 phase |
|--------|-------|------------------|
| `product.plan` | `pipeline-product-plan` | —（只改 roadmap） |
| `product.plan-reset` | `pipeline-product-plan-reset` | —（清除未交付规划） |
| `product.phase-realign` | `pipeline-product-phase-realign` | —（指定 phase 对齐 + 返工） |
| `product.contract` | `pipeline-product-contract` | `contract_ready` |
| `backend.implement` | `pipeline-backend` | `backend_done` |
| `test.prepare` | `pipeline-test-prepare` | （不改 status） |
| `test.api` | `pipeline-test-api` | `tested` |
| `frontend.mock` | `pipeline-frontend-mock` | （不改 status） |
| `frontend.integrate` | `pipeline-frontend-integrate` | `frontend_done` |
| `test.e2e` | `pipeline-test-e2e` | `e2e_verified` |
| `test.e2e-retest` | `pipeline-test-e2e-retest` | `e2e_verified` |
| `frontend.fix-e2e` | `pipeline-frontend-fix-e2e` | `frontend_done` → 再测 |
| `designer.review` | `pipeline-designer-review` | `ui_reviewed` |
| `frontend.fix-ui` | `pipeline-frontend-fix-ui` | `e2e_verified` → 再走查 |
| `designer.rereview` | `pipeline-designer-rereview` | `ui_reviewed` |
| `product.accept` | `pipeline-product-accept` | `done` |
| （自动） | `pipeline-next` | 按 `status.yaml` |

---

## 开发规范

见 [handoff/conventions/README.md](conventions/README.md)。

---

## 流转说明

见 [handoff/WORKFLOW.md](WORKFLOW.md)。
