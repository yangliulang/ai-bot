# 域需求：Trading Agent Config（后台 — 交易行为默认值与限制）

| 项 | 内容 |
|----|------|
| **产品** | ChainUp AI Agent（Coobit 单所） |
| **文档** | `specs/requirements/domains/admin/trading-agent-config/overview.md` |
| **状态** | **域内需求已展开（V1）**；含 **Telegram Bot 配置（709～711）**；[`design/api.md`](../../../../design/api.md) **全局配置写入** **及** **Telegram Bot/Webhook** 登记表行填链后与 [`functions.md`](functions.md)、[`keys.md`](keys.md)、[`telegram/admin-bot-config.md`](../../agent/telegram/admin-bot-config.md) **对齐 PR**。 |
| **PRD 位置** | **[`../management-console-v1-prd.md`](../management-console-v1-prd.md) §10 · 附录 A§5.1 （`configKey`）·§9 （`agentState`）· **FR-MC701～711** |
| **互引** | [`management-console-v1-prd.md`](../management-console-v1-prd.md) **附录 A**（**§5.1 · §9**）；[`keys.md`](keys.md)；[`../../agent/telegram/overview.md`](../../agent/telegram/overview.md)、[`../../agent/telegram/admin-bot-config.md`](../../agent/telegram/admin-bot-config.md)；[`../agent-management/functions.md`](../agent-management/functions.md) **G01··T07**；[`../../agent/exchange-agent/boundaries.md`](../../agent/exchange-agent/boundaries.md)；[`../../agent/exchange-agent/overview.md`](../../agent/exchange-agent/overview.md)；[`../../agent/exchange-agent/trade-assistance.md`](../../agent/exchange-agent/trade-assistance.md)；[`../../agent/exchange-agent/boundaries.md`](../../agent/exchange-agent/boundaries.md)；[`../access-control/overview.md`](../access-control/overview.md)；[`../billing-management/overview.md`](../billing-management/overview.md)；[`../../../flows/trade-via-agent.md`](../../../flows/trade-via-agent.md)；[`../../../observability/overview.md`](../../../observability/overview.md)；[`../../../../design/api.md`](../../../../design/api.md)；[`../../../contract-closure.md`](../../../contract-closure.md)；[**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · **[§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path) |

---

## 1. 目的（摘要）

维护 **全所** **影响 Agent 下单、路由与产品线闸** **`configKey`**：总开关与运维熔断、`FEATURE_*`、`SYMBOL`/`AGENT_*` 护栏、**Telegram 渠道（编排只读 + Bot 运行参数 / 凭证 / Webhook 运维）**。写路径须 **版本化、审计**、（可选）**Dry-run Diff**，与 **[`management-console`](../management-console-v1-prd.md) §7.2 · §8.4** 对签。**`design/api` 矩阵仍为 `TBD` 或未登记** 的交易能力 **不得在本域单方面承诺已交付**。详参 [`functions.md`](functions.md)、[`keys.md`](keys.md)、[`../../agent/telegram/admin-bot-config.md`](../../agent/telegram/admin-bot-config.md)。

---

## 2. 本版包含 / 不包含

| 判定 | 内容 |
|------|------|
| **包含** | **FR-MC701～711**（[`functions.md`](functions.md)，含 **§2.7** 与 [`runtime-policy`](../../agent/exchange-agent/boundaries.md) **对签**）；[`keys.md`](keys.md)；[`config.md`](config.md)、[`flow.md`](flow.md)、[`rules.md`](rules.md)；验收 **SC-TAC-01～SC-TAC-13**（[`functions` §4](functions.md)）。 |
| **不包含** | **`GLOBAL_AGENT_SWITCH` 在模块一编辑** — [`agent-management`](../agent-management/overview.md) **G01** 仅横幅只读；**Prompt** [`prompt-management`](../prompt-management/overview.md)；**Tool 矩阵** [`tool-management`](../tool-management/overview.md)；**模型密钥** [`ai-settings`](../ai-settings/overview.md)。 |

---

## 3. FR / SC 索引（SSOT：`functions.md`）

| 类型 | 位置 |
|------|------|
| FR-MC701～711 · §2 展开 · §2.6 合并 · **§2.7 `runtime-policy`** | [`functions.md` §2～§3](functions.md) |
| **SC-TAC-01～13**（V1） | [`functions.md` §4](functions.md) |
| 错误码草案 | [`functions.md` §5](functions.md) |

---

## 4. `configKey` SSOT：`keys.md`

[`keys.md`](keys.md)：全局闸 · 特性矩阵 · **Runtime · Memory / STM（§2.1 · `FR-STM*`）** · 交易护栏 · **渠道 / Telegram（§4.1～4.4）** · **`BILLING_*` 边界 · 写元数据。

**STM / Resume 默认（v0）**：**`STM_IDLE_DEFAULT_POLICY=stale_prior_write`** · **`STM_IDLE_RESUME_PROMPT_SEC=1800`** · **`STM_CLARIFY_SESSION_TTL_SEC=900`** · **`RESUME_CLASSIFIER_MIN_CONFIDENCE=0.75`** — **详表** [`keys.md` §2.1](keys.md#21-runtime--memory--stmfr-stm--产品默认-v0)。

---

## 5. 文档索引（阅读顺序）

| 顺序 | 文档 | 说明 |
|------|------|------|
| 1 | [`functions.md`](functions.md) | FR/SC/错误码 |
| 2 | [`keys.md`](keys.md) | `configKey` 枚举 |
| 3 | [`config.md`](config.md) | IA、版本写入 |
| 4 | [`flow.md`](flow.md) | 编辑/Diff、`agentState` |
| 5 | [`rules.md`](rules.md) | RBAC、灰度 |
| 6 | [`runtime-policy.md`](../../agent/exchange-agent/boundaries.md) | **执行侧政策**（与 `functions` §2.7 对签；**非** `configKey` SSOT） |

*维护：产品 + 交易所后台 owner。*
