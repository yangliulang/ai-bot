# 产品 / 需求规范

> 对应 `product-agent`。流转见 `.cursor/rules/product-agent.mdc`。

## brief.md

- 必须有 **可测试的验收标准（AC）**，编号 `AC-1`、`AC-2`…
- AC 表述用「输入 / 操作 → 预期结果」，避免模糊词（「尽量」「可能」）
- **本期包含 / 本期不包含** 必须写清，减少范围蔓延
- 有页面时写 **界面与交互**（路由、主流程、错误提示方式）

### AC 质量（Rubric）

| 规则 | 说明 |
|------|------|
| 可观测 | 结果可被测试断言（HTTP 状态、JSON 字段、页面文案） |
| 可编号 | 每条 AC 独立编号，便于 `test/coverage.md` 追溯 |
| 无歧义 | 不用「正常」「合理」「友好」等主观词代替具体行为 |
| 范围一致 | AC 不超出「本期包含」；「本期不包含」里的能力不得写成 AC |

## api.openapi.yaml（产品初稿）

- 每个 AC 至少能对应到一个 API 或页面行为
- 路径挂在 `servers.url` 之下（默认 `/api` 前缀由 server 表达）
- 200 / 4xx 示例与统一响应格式一致（见 [project.md](project.md)）
- 不在此阶段写实现细节（数据库、内部类名）

## backlog（roadmap）

- 功能 ID：`{YYYY-MM-DD}--{kebab-slug}`
- 一行一功能；状态与功能包 `status.yaml` 同步
- 模式 1 只排期，不写完整 brief（避免 backlog 与功能包重复维护）

### 存量项目（已开发一段时间）

PRD 往往包含已上线能力，**不要**从 PRD 第一章起把全部能力再排进 backlog。

1. 设置 `project.onboarding.mode: brownfield`（续写迭代用 `continuing`）
2. 填 [inventory.md](../product/inventory.md)，运行 `./scripts/seed-backlog-from-inventory.sh`
3. 执行 [brownfield-product-plan-prompt.md](../product/brownfield-product-plan-prompt.md) 或 `/pipeline-product-plan`（**greenfield** 且 inventory §2 非空时，plan 亦不得把 §2 已实现写成 planned）；plan 结束须 `./scripts/sync-backlog-from-phase.sh`
4. phase 全 `done` 后：`/pipeline-product-phase-close` 或 `./scripts/advance-phase.sh`（自检 `./scripts/check-phase-close-ready.sh`）

模式说明：[onboarding-modes.md](onboarding-modes.md)

## 规划门禁（product.plan）

完成 `handoff/roadmap/phase-N.md` 后，运行 `./scripts/sync-backlog-from-phase.sh` 写回 `backlog.yaml`，再对照 [product-plan 检查清单](../pipeline/checklists/product-plan.md)。  
指挥官确认后再对 backlog 项执行 `product.contract`。

## 定稿门禁（contract_ready）

同时具备：

| 交付物 | 要求 |
|--------|------|
| `brief.md` | 含 AC、范围、有页面时含界面与交互 |
| `api.openapi.yaml` | 含路径与方法，与 AC 对齐 |
| `test/coverage.md` | AC ↔ TC/E2E 追溯矩阵（见 [testing.md](testing.md)） |
| `test/cases.md` | P0 API 用例，步骤与预期非空 |
| `test/e2e-cases.md` | 有页面时 P0 E2E 用例，步骤与预期非空 |

推进 `contract_ready` 前须运行并通过：

```bash
./scripts/check-test-coverage.sh handoff/features/<功能ID>
```

清单正文：[contract-test-coverage](../pipeline/checklists/contract-test-coverage.md)。
