# 测试规范

> 对应 `test-agent`。流转见 `.cursor/rules/test-agent.mdc`。

## 用例文件

| 文件 | 阶段 | 内容 |
|------|------|------|
| `test/coverage.md` | `contract_ready` 前（定稿） | AC ↔ API/E2E 追溯矩阵 |
| `test/cases.md` | `backend_done` 后执行 | API P0/P1，关联 AC |
| `test/e2e-cases.md` | `frontend_done` 后执行 | 页面 E2E P0，关联 AC |

每条用例建议包含：**步骤、预期、优先级、关联 AC**。

## 追溯矩阵（test/coverage.md）

- 定稿时由 **product-agent** 填写（与 `cases.md` / `e2e-cases.md` 同步）
- 每个 `brief.md` 中的 **AC-N** 占矩阵一行
- **API 用例** 列：`TC-xx`（须存在于 `test/cases.md`）
- **含页面** 时 **E2E 用例** 列：`E2E-xx`（须存在于 `test/e2e-cases.md`）
- 校验命令：`./scripts/check-test-coverage.sh handoff/features/<功能ID>`

`contract_ready` 前脚本须 **退出码 0**，否则禁止定稿。

## 报告文件

| 文件 | 通过后 phase |
|------|----------------|
| `test/report.md` | `tested` |
| `test/e2e-report.md` | `e2e_verified` |

报告须含：时间、环境、**结论**、P0 明细表、失败/阻塞项。

## 执行顺序

1. **定稿**：`test/coverage.md` + 用例骨架，跑覆盖脚本
2. **可选** `test.prepare`：test-agent 在 `contract_ready` 后复审矩阵与 P0 用例（不改 status）
3. API：`backend_done` 后跑 `test/cases.md` P0
4. E2E：`frontend_done` 后跑 `test/e2e-cases.md` P0（前后端都启动）

## 契约校验

- 响应 JSON 字段与 `api.openapi.yaml` schema 一致
- 错误响应含 `code` + `message`

## 失败处理

- P0 未全通过 **不得** 推进 phase
- 在 `status.yaml` 的 `blockers` 记录，并设正确 `next`（返工负责人）
- API 失败 → `next: backend-agent`；E2E 失败 → `next: frontend-agent`（保持 `frontend_done`）

## 自动化

- **定稿门禁**：`scripts/check-test-coverage.sh`
- 功能测试脚本可放在 `apps/api/tests/` 或功能包内注明命令
- 优先自动化；手工执行须在报告中写清「实际结果」

## 不改动的文件

- 不修改 `brief.md`、业务实现（仅测试代码与 `test/*`、必要时 `status.yaml`）
