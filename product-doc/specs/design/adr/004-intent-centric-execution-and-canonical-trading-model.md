# ADR-004：意图中心化执行与统一交易语义层（Canonical Trading Model）


| 字段           | 内容                                    |
| ------------ | ------------------------------------- |
| **状态**       | 已接受（**文档草案 · 实现渐进落地**）                         |
| **日期**       | 2026-05-14                            |
| **决策 owner** | 产品 + 架构接口 owner + Agent Runtime owner |


## 上下文

1. **首版** 出站 **仅 Coobit**（子账户 scope、`openapi-ai` 宿主、[`agent-coobit-api-allowlist`](../../requirements/integrations/exchange/agent-coobit-api-allowlist.md)），但 **产品方向** 含 **未来多所、用户侧 API 绑定与平台独立计费**。
2. 若 **Skill / 工具实现** 长期保持 **`Skill → 交易所 HTTP 字段`** 的扁平结构，将出现 **「每所 × 每能力」** 的组合爆炸，**无法规模化**。
3. 官方或社区 **「某所 Skill」**（如所名前缀之分包）应视为 **适配器实现参考或宿主**，**不得**作为 **本产品 Agent 认知层的一等 SSOT**（与 **多模型路由** 无关的另一维度）。
4. [`ADR-002`](002-tool-skill-registry-ssot.md) 已冻结 **`skillId`/`toolId`** 与人类评审 SSOT — **本条不废止 ADR-002**：**登记表名** **仍** **面向用户与编排**；**本条追加** **执行链路上** **须** **经过** **Canonical 投影**。

## 决策

1. **统一交易语义层（Unified Trading Semantic Layer）**  
   - **产品对外的能力名**（`skillId` / `toolId` / `scenarioId`）**描述「意图与能力面」**，**不** **描述「某交易所 REST 形态」**。  
   - **结构化交易意图与领域对象**（**Canonical Trading Model**）为 **执行链路上的语义真源**，见 **[`canonical-trading-model.md`](../canonical-trading-model.md)**。

2. **执行链（强制方向）**  
   ```
   Skill / Planner 输出（意图或槽位）
     → Trading Intent（可选显式 JSON，随实现冻结）
     → Unified Domain 命令（Canonical · 如 PlaceOrder）
     → Execution Gateway（路由 venue + 选择 Adapter）
     → Exchange Adapter（当前：Coobit；未来：多所）
     → 具体 HTTP / WS（仍须同窗 [`api.md`](../api.md) 矩阵 **或** **未来各所登记表**）
   ```
   - **禁止**：在 **Prompt/Skill 正文** 中 **固化** **「仅 Binance symbol / 仅 OKX instId」** 作为 **唯一真理**；**允许**：在 **Adapter 映射表** 内固化。

3. **`venue`（执行后端）**  
   - **V1**：**仅 `coobit`**（与现网一致）。  
   - **未来**：**用户绑定** 携带 **`venue` + 凭据引用**；**Gateway** **按绑定** **选用 Adapter**，**禁止** **模型在无绑定上下文时静默换所**。

4. **与矩阵/PATH 的关系（双轨过渡期）**  
   - **[`api.md`](../api.md)** **子账户矩阵** **在 V1** **仍为 Coobit HTTP 契约真源**。  
   - **Canonical 模型** **为** **语义与跨所演进真源**；**Coobit Adapter** **须** **可证明** **将 Canonical 命令** **映射至** **已登记 PATH**（**白名单** **不破** **[`agent-coobit-api-allowlist`](../../requirements/integrations/exchange/agent-coobit-api-allowlist.md)**）。  
   - **矩阵行** **逐步** **标注** **对应的 Canonical 操作名**（**由后续 MR** **填链**）。

5. **观测**  
   - **`agent.tool.call`（或等价）** **建议** **携带** **`venue`**（默认 `coobit`）、**`canonicalOp`**（如 `place_order`），**与** **[`observability` §2](../../requirements/observability/overview.md)** **同窗演进**。

6. **类型 A 与计费**  
   - **ADR-001**、**`executionId`、计费终局** **不变**；**确认卡** **展示** **Canonical 摘要**（**用户可读**），**底层执行** **经 Gateway**。

## 后果

- **工程仓库** **须** **引入** **Execution Gateway + Coobit Adapter**（名目可替换）**之端口**；**openapi-ai** **可为 Adapter 实现子模块** — **非** **推翻** **现网**，**乃** **包一层语义边界**。**本 Agent 规格仓**（`product/`、**`specs/`**）**不** **承载** **上述可执行实现**；**Runtime 接线** **与** **对拍证据** **在所内实现 MR** **登记**。  
- **文档**：**新增** **[`canonical-trading-model.md`](../canonical-trading-model.md)**；**更新** **[`architecture.md`](../architecture.md)** **容器与数据流**。  
- **CC**：**闭环索引** **见** **[`contract-closure` CC-P1-07](../../requirements/contract-closure.md)**。  
- **风险**：**短期** **双轨**（矩阵 + Canonical）**须** **单测/对拍** **防漂移**；**PR** **须** **标明** **「仅文档」或「含实现」**。

## 引用

- **[`canonical-trading-model.md`](../canonical-trading-model.md)**  
- **[`architecture.md`](../architecture.md)** · **「与通用 Agent 栈之对照」**（Runtime / Gateway / 意图中心 vs Prompt+Tool-only）  
- [`trade-assistance.md`](../../requirements/domains/agent/exchange-agent/trade-assistance.md) · [`intents.md`](../../requirements/domains/agent/exchange-agent/intents.md)  
- [`integrations/exchange/overview.md`](../../requirements/integrations/exchange/overview.md)  
- [`contract-closure.md`](../../requirements/contract-closure.md) **CC-P1-07**
- [`closure-remaining` §0](../../requirements/closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../requirements/closure-remaining.md#cc-exec-solve-path)（**关单余量 / MR 首节**）
