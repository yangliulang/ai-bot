# Staging 走读操作指引

> contract 阶段占位；**backend/notes.md** 可补充所内 Bot、账号与 Base URL。

## 前置

1. 确认 **`2026-05-27--runtime-write-path-pipeline`** 已 **done** 且部署含 MR-RT-B4 能力。
2. 使用 **staging** 或所内沙箱；填写 `staging/evidence-log.md` **§1**。
3. 测试账号须 **已绑定** 托管 API（与 `trade.spot.limit_order` 一致）。

## 主轴步骤（`trade.spot.limit_order`）

1. Telegram 发送限价下单意图（含交易对、方向、价、量）。
2. 确认收到 **类型 A** Inline 确认（**在** 交易所写之前）。
3. 点击确认；记录 Bot 回执与 **`executionId`**（运营台或日志）。
4. Admin **`/observability/executions/{executionId}`** 导出时间线，勾选 [`pipeline-walkthrough-checklist.md`](../../../product-doc/specs/requirements/Runtime/pipeline-walkthrough-checklist.md) **§2.1～2.10**。
5. 运行 **`eval.runtime.pipeline_write_order`** 正例（所内 Eval _runner_；输出链入 evidence **§2.2**）。
6. 可选：执行 **§3 负例** 之一并记录证据。

## 验收 API（对拍时间线）

```bash
# 替换 executionId / staging Base URL / Admin token
cd server && uv run python \
  ../handoff/features/2026-05-27--telegram-write-path-staging/scripts/verify_timeline_order.py \
  --execution-id exec-XXXXXXXXXXXXXX \
  --base-url https://YOUR-STAGING-HOST \
  --token "$ADMIN_BEARER" \
  --pretty
```

或 curl：

```bash
curl -s -H "Authorization: Bearer $ADMIN_BEARER" \
  "$STAGING_BASE/api/v1/admin/observability/executions/$EXECUTION_ID/timeline"
```

## 本地回归（不替代 staging）

```bash
cd server && uv run pytest tests/test_write_path_pipeline.py -q
```
