# 测试用例（API + Registry audit pytest）

> test-agent 在 `backend_done` 后：跑 **TC-01～TC-08** pytest + 审查 **TC-09** evidence 模板。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| TC-01 | AC-1 | 版本与镜像 | 导入 `registry_idempotency`；读 `REGISTRY_AUDIT_VERSION`、`load_registry_mirror()` | **version=0.1.0**；返回 **skillIds/toolIds/scenarioIds** 非空 | P0 |
| TC-02 | AC-2 | skill 幂等 | 对 mirror + bundle SSOT 调 `assert_skill_registry_idempotent` | **不抛错**；A 类 **stableId** 与 bundle **1:1** | P0 |
| TC-03 | AC-3 | tool 幂等 | 对 mirror + manifest SSOT 调 `assert_tool_registry_idempotent` | **不抛错**；B 类 **read.*** 三工具 **1:1** | P0 |
| TC-04 | AC-4 | matrix 门禁 | `assert_enable_allowed("frozen")` vs `("TBD")` | **frozen→True**；**TBD→False** + **`REGISTRY_MATRIX_TBD`** | P0 |
| TC-05 | AC-5 | OBS join | synthetic timeline 含 tool call + scenario 调 `assert_obs_tool_call_scenario_join` | 正例 **不抛错**；缺 scenario **AssertionError** | P0 |
| TC-06 | AC-6 | Registry API | `GET /api/v1/admin/tools/registry`（Bearer） | **200**；**items[]** 含 **A/B** 行 · **stableId** 覆盖 bundle | P0 |
| TC-07 | AC-7 | Audit API | `GET /api/v1/admin/tools/registry/idempotency-audit` | **200**；**ok=true** · **mismatches 空** · **auditVersion=0.1.0** | P0 |
| TC-08 | AC-8 | pytest 套件 | `cd server && uv run pytest tests/test_registry_tool_idempotency.py -q` | **全通过**（含 P1） | P0 |
| TC-09 | AC-9 | 证据模板 | 打开 `eval/evidence/registry-idempotency-audit.md` §1～§3 | 命令、日期、pytest 摘要、MR-E 说明已填 | P0 |
| TC-10 | AC-4 | 边界 P1 | `assert_enable_allowed("draft")` | **False** | P1 |

## 契约测试

- [x] TC-08 pytest green
- [x] TC-06 + TC-07 Registry/Audit 200
- [x] TC-02 + TC-03 差集为空

## 自动化映射

| 用例 | pytest / 文件 |
|------|----------------|
| TC-01～TC-08, TC-10 | `tests/test_registry_tool_idempotency.py` |
| TC-09 | `eval/evidence/registry-idempotency-audit.md`（审查） |
