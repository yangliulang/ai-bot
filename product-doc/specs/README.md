# Specs — 需求与设计

本目录只承载 **需求** 与 **设计**（不含实现细节与可执行代码；**Runtime / Gateway 等工程实现** **归属** **所内工程仓库**，**不在** **本 Git 仓维护**），面向 **契约、自动化与对齐实现**。**给人读的产品叙事**见仓库 **[`product/`](../product/README.md)**；二者冲突时以 `requirements/` 与 `design/` 正文为准并应回写 `product/`。

## 布局

| 路径 | 阶段 | 说明 |
|------|------|------|
| [`requirements/`](requirements/) | 需求 | **PRS**（[`prompt-runtime/README.md`](requirements/prompt-runtime/README.md) · **[§4 改什么去哪](requirements/prompt-runtime/README.md#prs-where-to-edit)**）· `Runtime/` · `evals/` 等 — [requirements/README.md](requirements/README.md#本目录布局速览) |
| [`design/`](design/) | 设计 | 架构（[**逻辑视图 · 含「与通用 Agent 栈之对照」**](design/architecture.md)、[部署与拓扑](design/deployment.md)）、[**统一交易语义 / Canonical Model**](design/canonical-trading-model.md)、接口契约、ADR；**鸟瞰** [**`flow/e2e-closed-loop.md`**](../flow/e2e-closed-loop.md) **（文首架构语言→[`architecture`](design/architecture.md) §对照）** |

**事实源**：业务「必须 / 禁止 / 验收」以 `requirements/` 为准；系统如何满足需求以 `design/` 为准；冲突时先改文档并注明日期。

Speckit 默认 **FEATURE_DIR** 指向 [`requirements/`](requirements/)（见仓库根 `.specify/feature.json`）。

**契约闭环索引**（矩阵 `TBD` → 可对签）：[`requirements/contract-closure.md`](requirements/contract-closure.md)。**关单路径 / MR 可复制勾选**：[`requirements/closure-remaining.md`](requirements/closure-remaining.md) **[§7.5](requirements/closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](requirements/closure-remaining.md#cc-closure-exec-checklist)**（**与** **`contract-closure` §2～§3** **同窗，不替代 DoD**）。**小团队日常** **可** **优先** [`requirements/LITE-MODE.md`](requirements/LITE-MODE.md)。
