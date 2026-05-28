# 建包定稿检查清单（product.contract）

> 推进 `status.yaml` → `contract_ready` 前，product-agent 须逐项满足。  
> 自动化：`./scripts/check-test-coverage.sh {{feature_dir}}` 须退出码 0。

## 1. brief.md

- [ ] 含编号验收标准 **AC-1、AC-2…**（禁止只有模糊描述）
- [ ] 每条 AC 为「操作 / 输入 → **可观测**结果」，无「尽量」「可能」「大概」
- [ ] **本期包含 / 本期不包含** 已填写
- [ ] 有页面时 **界面与交互** 已写：路由、主流程、加载态、错误态（若适用）
- [ ] 用户故事与 AC 一致，无 AC 无法追溯的需求

## 2. api.openapi.yaml

- [ ] 每个需后端验证的 AC 至少对应一个 path + method
- [ ] `servers`、统一响应 `{ code, message, data? }` 与 [project.md](../../conventions/project.md) 一致
- [ ] 200 与主要 4xx 有示例或 schema
- [ ] 路径、方法、字段名与 brief 一致（无口头约定未写入契约）

## 3. 测试追溯（必做）

- [ ] 已创建并填写 [test/coverage.md](../../templates/feature/test/coverage.md)（AC ↔ 用例矩阵）
- [ ] 矩阵中**每个 AC** 一行，且 **API 用例** 列含 `TC-xx`
- [ ] 有页面时，每个 AC 的 **E2E 用例** 列含 `E2E-xx`
- [ ] `test/cases.md`：每个 P0 的 `TC-xx` 已写**步骤、预期、关联 AC**
- [ ] `test/e2e-cases.md`：有页面时每个 P0 的 `E2E-xx` 已写**步骤、预期、关联 AC**
- [ ] 至少一条 **P1** 或边界用例（异常/空参/服务不可用等，按 brief 需要）
- [ ] 已运行 `./scripts/check-test-coverage.sh` 且通过

## 4. 可选但推荐

- [ ] `design/ui-review.md` 检查项占位（有页面时）
- [ ] `test.prepare` 由 test-agent 复审矩阵（`contract_ready` 后、后端开发前）

## 5. status 与 roadmap

- [ ] `status.yaml`：`phase: contract_ready`，`next: backend-agent`，`history` 已追加
- [ ] `handoff/roadmap/phase-*.md` 对应行状态为 `contract_ready`
- [ ] **一次只定稿一个功能**（避免多个功能同时 `contract_ready`）

## 不通过时

- **禁止** `contract_ready`
- 补全 `test/coverage.md` 或用例后重新跑脚本
- 若 AC 不合理，改 `brief.md` 而非在测试里降低标准
