# Sub-account isolation（子账户隔离 — 设计切片）

**定位**：**聚合** **母子账 / Agent 专用子账户** 在 **信任边界与 API scope** 上的 **设计结论与真源索引**。**HTTP PATH、字段、矩阵格子** 仍以 **[`api.md`](./api.md)** 与 **`specs/openapi/`** 为 **唯一契约真源**。

**写路径（子账户 scope）与统一交易语义**：**Intent→Canonical→Gateway→Adapter** [`canonical-trading-model.md`](./canonical-trading-model.md)、[`ADR-004`](./adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`trade-assistance` §2.6](../requirements/domains/agent/exchange-agent/trade-assistance.md)；**契约** [`CC-P1-07`](../requirements/contract-closure.md#cc-p1-07)；**人类评审** [`requirements-review` §7.5](../../product/requirements-review.md#cc-adr004-review-checklist)；**管线** [`Runtime/execution` §1 步 7](../requirements/Runtime/execution.md)。**Execution Gateway 可执行实现** **在所内工程仓**，**不在本规格仓**。

**关单余量（MR 首节）**：[`closure-remaining` §0](../requirements/closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../requirements/closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../requirements/closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../requirements/contract-closure.md)。

---

## 1. 设计目标（产品可验收）

- **资金隔离**：**Token 扣减与交易** **默认** **仅** 作用于 **Agent 专用子账户** **现货 USDT 可用**；**不得** **隐式**动 **主账户母账本**（例外须 **ADR + [`contract-closure.md`](../requirements/contract-closure.md)**）。  
- **凭证边界**：**子账户 API Key** 的 **scope** **须**与 **[`api.md`](./api.md)** **矩阵 `operationId`** **可登记表对签**；平台 **不得**用 **主站用户 Web 会话** **冒充**子账户私有调用链。  
- **观测与归因**：**计费/审计 join** **须**能区分 **终端用户身份** 与 **子账户执行**，**换绑/迁移** **不得**串户（与 [`Runtime/sessions.md`](../requirements/Runtime/sessions.md)、[`onboarding/`](../requirements/domains/agent/onboarding/overview.md) 同窗）。  

---

## 2. 真源分工

| 主题 | SSOT |
|------|------|
| 矩阵、双网关、504、幂等 | [`api.md`](./api.md)、[`contract-closure.md`](../requirements/contract-closure.md) |
| 业务 FR、边界码、用户可见冻结 | [`exchange-agent/overview.md`](../requirements/domains/agent/exchange-agent/overview.md)、[`boundaries.md`](../requirements/domains/agent/exchange-agent/boundaries.md) |
| 开通、密钥、`secretRef` | [`onboarding/`](../requirements/domains/agent/onboarding/overview.md)、[`management-console-v1-prd.md`](../requirements/domains/admin/management-console-v1-prd.md) |
| 逻辑架构容器 | [`architecture.md`](./architecture.md) |
| 会话与执行锚点 | [`Runtime/sessions.md`](../requirements/Runtime/sessions.md) |

---

## 3. 工程充实项（非本篇范围）

- **密钥轮换、硬件/服务模块存密、分账户 rate limit** — **ADR + Infra**。**组件级数据流图** — [`runtime-architecture.md`](./runtime-architecture.md) **充实后对签**。  

---

**文档版本**：0.2.2 · **维护**：系统架构 + 产品 · **本版**：**篇首补** **`closure-remaining` §0·§6/§6.4。** **承** **0.2.1**。
