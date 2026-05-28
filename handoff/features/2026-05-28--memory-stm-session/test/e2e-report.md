# E2E / 页面验证报告

> 测试 Agent 在 `frontend_done` 后执行并填写，通过后推进 status 至 `e2e_verified`（next: designer-agent）。

## 概要

- 执行时间：
- 执行人：test-agent
- 环境：
  - 前端：
  - 后端 API：
- 结论：⬜ 通过 / ⬜ 不通过 / ⬜ 有条件通过

## 结果汇总

| 总数 | 通过 | 失败 | 跳过 | 阻塞 |
|------|------|------|------|------|
| | | | | |

## P0 用例明细

| 用例 ID | 关联 AC | 场景 | 结果 | 实际 |
|---------|---------|------|------|------|
| | | | | |

## 失败与阻塞项

| 用例 ID | 现象 | 严重程度 | 负责人 |
|---------|------|----------|--------|
| | | | frontend-agent / backend-agent |

## 备注

- 不通过时：`phase` 保持 `frontend_done`，`next` 改为 `frontend-agent`（或 `backend-agent`），勿推进 `e2e_verified`。
