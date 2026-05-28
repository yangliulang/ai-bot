# E2E 用例

> **含页面：否** — 无新增 Admin 路由。  
> **Staging 走读** 记为 **STG-01**（见 `test/cases.md`），**不** 填入浏览器 E2E 表。

## 说明

- 浏览器 E2E：**不适用**（可用存量 Observability 页辅助导出，非本包交付）。
- P0 门禁 = **`staging/evidence-log.md`** + **`test/cases.md` STG-01** + pytest 代理。

## 用例列表

| ID | 关联 AC | 场景 | 步骤 | 预期结果 | 优先级 |
|----|---------|------|------|----------|--------|
| STG-01 | AC-2, AC-3 | Staging 主轴走读 | 见 `staging/walkthrough.md` | evidence §2 完整；时间线序满足 SC-OBS08/11 | P0 |

## 验收对照（brief.md）

- [x] 主轴 TG 写路径 staging 证据已提交 — **待所内** 填 `staging/evidence-log.md`（product.accept 门禁）
- [x] 本地 `test_write_path_pipeline.py` 回归 green（代理 · e2e 回归 7 passed）
