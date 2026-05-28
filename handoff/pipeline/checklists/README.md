# 流水线检查清单

指挥官与各 Agent 在关键节点对照本目录清单，**全部满足**后再推进 `status.yaml` 或开下一步 Chat。

| 清单 | 何时用 | 谁负责 |
|------|--------|--------|
| [product-plan.md](product-plan.md) | `product.plan` 完成后、开第一个 `contract` 前 | product-agent + 指挥官 |
| [phase-realign.md](phase-realign.md) | `product.phase-realign` 重写 phase-N 后、开 contract 前 | product-agent + 指挥官 |
| [contract-test-coverage.md](contract-test-coverage.md) | `product.contract` 推进 `contract_ready` 前 | product-agent |

自动化（定稿门禁）：

```bash
./scripts/check-test-coverage.sh handoff/features/2026-05-25--xxx
```

退出码 `0` 表示 AC ↔ 用例追溯通过。

定稿或每步更新 `status.yaml` 后，Cursor Hook 会提示下一条 `/pipeline-*` 命令（[hooks.md](../hooks.md)）。
