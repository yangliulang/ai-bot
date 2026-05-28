# ChainUp AI Agent · 仓库导航

本仓库以 **规格驱动** 组织：**`product/`** 供人读，`specs/requirements/` + `specs/design/` 承载可契约需求与设计；**`src/`** 侧为 **管理台等原型（非量产后端 SSOT）** — 编排与网关的 **正式上线代码由专门开发团队在所内仓库维护**。详见 [`src/admin/README.md`](src/admin/README.md)、[`specs/README.md`](specs/README.md)。

## 目录结构（目标）

```text
Agent/
├── README.md                    # 本文件
├── product/                     # 产品层（叙事）
│   ├── overview.md
│   ├── roadmap.md
│   ├── milestones.md
│   ├── user-scenarios.md
│   ├── positioning.md
│   └── roadmap/                 # 路线图维护说明与执行计划（历史）
├── flow/                        # 端到端鸟瞰（Mermaid）；[`flow/README`](flow/README.md) · 文首「架构语言」→ [`architecture`](specs/design/architecture.md)
├── specs/
│   ├── requirements/
│   │   ├── domains/
│   │   │   ├── agent/
│   │   │   │   ├── exchange-agent/
│   │   │   │   ├── agent-orchestration/
│   │   │   │   ├── runtime/
│   │   │   │   └── onboarding/
│   │   │   └── admin/           # 后台模块
│   │   ├── runtime/
│   │   ├── prompts/
│   │   ├── tools/
│   │   ├── risk/
│   │   ├── observability/
│   │   ├── integrations/       # 外部系统（交所 / Telegram / LLM / 通知）
│   │   ├── standards/
│   │   ├── flows/
│   │   └── …
│   └── design/
│       ├── architecture.md      # 含「与通用 Agent 栈之对照」
│       ├── canonical-trading-model.md
│       ├── api.md
│       └── adr/
├── src/                         # 实现代码（占位 + Demo；**不含** Runtime / Execution Gateway 生产实现）
│   ├── admin/                   # 管理后台 Demo（Vite + React；非生产）
│   └── Web/                     # 主站 / H5 Demo
```

**Admin Console Demo**（本地运行、路由表）：[`src/admin/README.md`](src/admin/README.md)。**规格主索引**（契约收口、派工）：[`specs/requirements/contract-closure.md`](specs/requirements/contract-closure.md)。
**关单余量 / MR 路径**（本仓 vs 所内；**不**替代上表 DoD）：[`specs/requirements/closure-remaining.md`](specs/requirements/closure-remaining.md)（[§0 速链](specs/requirements/closure-remaining.md#closure-remaining-quicklinks) · [§7 开放项总表](specs/requirements/closure-remaining.md#cc-remaining-open-items) · [§7.5 闭环路径](specs/requirements/closure-remaining.md#cc-remaining-open-close-path) · [§7.6 MR 执行清单](specs/requirements/closure-remaining.md#cc-closure-exec-checklist)）。

**必读**：[`specs/README.md`](specs/README.md) · [`.specify/memory/workspace-layout.md`](.specify/memory/workspace-layout.md) · **`specs/requirements/spec.md`** · **设计** [`specs/design/overview.md`](specs/design/overview.md)（[`architecture` · 架构语言](specs/design/architecture.md)、[`canonical-trading-model`](specs/design/canonical-trading-model.md)、[`adr/`](specs/design/adr/README.md)）。**端到端鸟瞰**：[`flow/e2e-closed-loop.md`](flow/e2e-closed-loop.md)（文首 **「架构语言」** → [`architecture` §对照](specs/design/architecture.md)）。
