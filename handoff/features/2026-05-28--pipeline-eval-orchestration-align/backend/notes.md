# Backend 交付说明 · 2026-05-28--pipeline-eval-orchestration-align

## 启动

```bash
cd server && uv run chainup-agent-api
```

Base URL：`http://127.0.0.1:8080`

## 实现摘要

| AC | 交付 |
|----|------|
| AC-1 / AC-6 | `orchestration_freeze_align.py` + catalog **`trade.spot.flash_convert`** 补 **`read.skill`** 步 |
| AC-2～AC-4 | `eval_pipeline_write_order.py`（`EVAL_SET_ID` / `EVAL_VERSION` + 正/负例断言） |
| AC-5 | `tests/test_eval_pipeline_write_order.py` |
| AC-6 | `tests/test_orchestration_freeze_align.py` |
| AC-8 | `admin_orchestration_policy.py` · `engineeringSpecRefs` 首行 **`runtime-freeze.md §3`** |

`write_path_pipeline.assert_write_path_pipeline_order` **委托** `assert_eval_pipeline_write_order_positive`（行为不变）。

## 规格 SSOT

- `product-doc/specs/requirements/evals/pipeline-write-order.md`
- `product-doc/specs/requirements/domains/agent/agent-orchestration/runtime-freeze.md` **§3.1～3.2**
- `product-doc/specs/requirements/Runtime/pipeline-walkthrough-checklist.md` **§2.10**

## 自测

```bash
cd server && uv run pytest \
  tests/test_eval_pipeline_write_order.py \
  tests/test_orchestration_freeze_align.py \
  tests/test_write_path_pipeline.py \
  -q
```

**2026-05-28**：**20 passed**（eval 7 + freeze 10 + write_path 回归子集；全量 write_path 7 亦 green）。

## curl 示例

### 场景编排（AC-1）

```bash
curl -s http://127.0.0.1:8080/api/v1/agent/scenarios/trade.spot.limit_order | jq '.executionSteps[] | {stepKey, order}'
```

### 编排策略 refs（AC-8 · 需 Admin JWT）

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8080/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | jq -r .accessToken)
curl -s http://127.0.0.1:8080/api/v1/admin/orchestration/policy \
  -H "Authorization: Bearer $TOKEN" | jq '.engineeringSpecRefs'
```

### 时间线（Eval 集成 · 可选）

```bash
curl -s "http://127.0.0.1:8080/api/v1/admin/observability/executions/{executionId}/timeline" \
  -H "Authorization: Bearer $TOKEN" | jq '.items[].eventName'
```

## 错误码

本包 **无新路由**；沿用存量 **401** / **404**（`AppError`）。

## 依赖

- **`2026-05-27--runtime-write-path-pipeline`** **done**（五段序 Runtime 接线）
