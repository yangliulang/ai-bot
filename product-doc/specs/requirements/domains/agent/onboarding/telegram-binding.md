# Telegram · 会话绑定与 Deeplink

**职责**：本版唯一会话渠道上，**Coobit `userId`（及允许的 Agent 实例上下文）** 与 **Telegram 会话** 的建立、维持、换绑与吊销；以及 **FR-T02/F05** 不满足时如何在频道侧给出 **可追溯归因**摘要与 **Deeplink**（**狭义 onboarding**与 **API/权限/运行时态**须有可区分话术，同窗 **`initialization-flow` §3**）。

**HTTP / 契约真源**：[`design/api.md`](../../../../design/api.md) **与** **`me/agent/*`、Bot** **登记表** **及所内 OpenAPI**。

---

## 1. 绑定生命周期（产品态）

| 状态名 | 含义 | 与用户能力的关系 |
|--------|------|------------------|
| **未绑定** | **会话尚无**经审计的 **实例上下文**：即 **该 Telegram 锚点** **未**在任一 **可用 Agent 实例**绑定登记 **或** 尚无经审计的 **`userId` 映射**（二者以实现与 **`design`** 冻结字段为准；用户体感常为「未完成 §1.2」） | 禁止输出 **个性化私有持仓/成交**；可提供 **Agent 产品线 Deeplink**（**绑定页**链） |
| **已绑定** | 映射生效且未被吊销 | 在满足 **FR-T02** / Feature 前提下进入正常 Agent 能力 |
| **已吊销 / 待重绑** | 用户注销、风控或超时吊销 | **禁止**继续使用旧 **`userId` 上下文**答复私域问题；须可读原因 |

状态迁移须 **可审计**；审计内容 **不包含** Agent API Secret。

---

## 2. 首次绑定链路（叙事下限）

**Telegram 首触（实例门禁）**：用户 **在 Telegram 向 Bot 发出消息**时，系统须判定 **当前会话锚点**是否已在 **实例绑定**中登记为 **可用**（与 **`activate-trading-agent` S5** 前置 **同窗**）；**若否** → 返回可读摘要并下发 **产品线 Deeplink**（指向 **[`initialization-flow` §1.2](initialization-flow.md)** **Agent 绑定页**，**非**交易所主站），**不得**假设用户已完成绑定页步骤。

1. 用户在 Telegram 点击入口或 **上述 Deeplink** 回程。  
2. 校验 **`CHANNEL_TELEGRAM`**、全局熔断等渠道因子（同窗 [`activation-policy.md`](activation-policy.md)）。  
3. 用户 **打开** **Agent 产品线绑定页（§1.2）**（**不须访问交易所主站**，同窗 [**`FR-WEB01`**](../../web/agent-onboarding.md)）；提交 **`agentSubAccountUid`**、**API Key** 与 **Secret** 并保存 **`POST /api/v1/me/agent/bindings/trading-api`** **须**在 **`FR-WEB01`** **可归因上下文** **下** — **须通过** **§1.2 下限校验**（[**`initialization-flow` §1.2 项 2**](initialization-flow.md)、[**`FR-WEB06`**](../../web/agent-onboarding.md)，含 **`AGENT_BIND_SUBACCOUNT_UID_MISMATCH`**）；失败 **`409`** **`TradingApiBindRejectCode`** — **通过后**方建立 **chat 锚点 ↔ `userId`（± 实例上下文）** 可审计映射（签章、TTL、撤销策略由实现与 **`design`** 冻结）。**映射建立前** **不得**将 **未校验**Secret 写入 **默认持久化观测面**。  
4. （若产品与 **`design`** 仍要求 OAuth/凭证补强）用户经由 **`design/api` 所定**链路完成对 **`userId` 控制权**的附加证明 — **不得**单独替代 §1.2 **API 校验**。  
5. 会话内返回与子账户/API、VIP、计费一致的 **可读「可执行 / 尚需…」摘要**。  
6. 若 **[`keys` §4.2](../../admin/trading-agent-config/keys.md) **按** [`telegram/overview` §2.1.1](../telegram/overview.md) **语言解析与回退链** **可得** **非空** **开通欢迎语正文** **且** **`CHANNEL_TELEGRAM=ON`**：在用户 **首次**达成「**Agent 开通已完成**」∧「**本条绑定生效**」，Bot **投递一条** **对该用户语言（经回退）** **的** 欢迎语（**幂等**）。

**换绑 / 多端**：须提供 **可比首次绑定更清晰**的反滥用路径；**禁止**仅凭自然语言断言完成换绑（FR-ON02）。

---

## 3. onboarding 阻断与 FR-T05

当运行时因 **FR-T02/F05** 不满足而 **拒绝私域调用**，且须在 Telegram 给出 **可读摘要 + 可走通的恢复链**时（宿主 **`initialization-flow` §2、§3**，同窗 [`consume-and-bill`](../../../flows/consume-and-bill.md) **S2**）：

| 元素 | 产品下限 |
|------|----------|
| **会话摘要** | **按稳定码归因**，**禁止**笼统「稍后重试」：**子账户未就绪**、**API 吊销/待轮换**、**运营收窄模板致只读不可用**、**VIP/计费/合规**、**实例 Pause / `GLOBAL_OFF` / Warm-up** **不得互相冒充**（[`initialization-flow` §3](initialization-flow.md)；权限收窄误判见 [`permission-authorization` §6.3 **`ON-PERM-03`**](permission-authorization.md)；Pause/Warm-up 话术见 [`runtime-provisioning` §3](runtime-provisioning.md)） |
| **Deeplink** | **须与该条摘要归因同窗**：**§1.2 Agent 绑定页**（**保存** **`POST .../bindings/trading-api`** · **§1.2 下限** [**`FR-WEB06`**](../../web/agent-onboarding.md) · **`TradingApiBindRejectCode`**）未完成 → [`initialization-flow` §1.2](initialization-flow.md)；**API 吊销/轮换后再绑定**同窗 [`permission-authorization` §5、§6.2 **`ON-PERM-02`**](permission-authorization.md)（**重新绑定** **同窗** **Agent 产品线绑定页**；与「子账户未开立」话术 **须有可区分 copy**）；**VIP/计费** 等沿用 **billing / access-control** 既定 Deeplink |
| **回程体验** | 用户在 **绑定页保存**成功后，回到 Telegram **不必**重装客户端即可触发 **状态复查**（显式指令或系统自动） |

与 [`initialization-flow.md §3`](initialization-flow.md) **失败表**、[`boundaries.md`](../exchange-agent/boundaries.md) **稳定码**，及 **上表所链 `permission-authorization` / `runtime-provisioning`** 同窗会签。

---

## 4. 多会话（若产品启用）

若允许同一 **`userId` 多端并行**：

- 须有 **会话数上限**，或「新会话顶替旧会话」的 **显性提示**。  
- 执行归因仍以 **observability** 宿主字段 **唯一绑定快照**可追溯（不在本文展开）。

---

## 5. 非目标

- 不写 Telegram 卡面皮囊级控件全集（若有渠道 overview 则以渠道文为准）。  
- 不写 **类型 A/B 写**确认语义（[**`confirmation-flow`**](../agent-orchestration/confirmation-flow.md)、**`trade-assistance`**）。

---

## 6. 补充验收 · Given / When / Then（与 **`ON-GWT-*`、`ON-PERM-*`** 同窗）

### 6.1 `TG-GWT-01` · 回程须可复查状态

- **Given**：用户会话已收到含 **onboarding Deeplink** 的阻断说明（对应 **`initialization-flow` ON-GWT-02** 前置）。  
- **When**：用户在 **未卸载 Bot**前提下，使用产品定义的「刷新/重试」指令或再次点击同一入口。  
- **Then**：系统须 **重新评估**该 `userId` 的门禁快照；**默认不得**要求重装客户端（除非渠道 SSOT 明示安全例外）。

### 6.2 `TG-GWT-02` · 未绑定不得输出私域持仓/成交

- **Given**：会话处于 **§1** 表之 **未绑定**。  
- **When**：用户发问须 **私有订单/持仓**语义。  
- **Then**：应答 **不得**含真实个性化成交/挂单；须引导 **§2** 绑定链路。验收同窗 [**`portfolio-insight` SC-PI01**](../exchange-agent/portfolio-insight.md) 之「未通过 FR-T02 则无成功私域工具结果」精神。

### 6.3 `TG-GWT-03` · 权限收窄不得在频道侧冒充「子账户未开」

- **Given**：测试数据下 **摘要**表明 **子账户与 Agent API 宿主链在技术态上已就绪**（与 **I02/摘要同窗**，[`initialization-flow` **ON-GWT-03**](initialization-flow.md) 精神一致），但因 **运营收窄默认模板**致使某 **`FR-T01` 矩阵只读** **不可用**。  
- **When**：用户在 **Telegram** 发起须该只读的私域语义请求。  
- **Then**：频道应答之 **`lastProductBlockReason` / copy** **不得将主因写成**「须先完成 **§1.2** **绑定页**」之类 **狭义 onboarding** 归因 — **当**阻断实为 **运营收窄默认模板**所致 **只读不可用**；**不得以** **`AGENT_SUBACCOUNT_BLOCKED`** **单独**冒充 **权限收窄**场景；须有 **可被测试断言的**能力与权限类稳定码或频道文案。**同窗**：[`permission-authorization` **`ON-PERM-03`**](permission-authorization.md)、[`initialization-flow` §3](initialization-flow.md) **API** 行。

### 6.4 `TG-GWT-04` · 开通完成后欢迎语（可配置 · 简/繁/英）

- **Given**：运营已配置 **使得** [`telegram/overview` §2.1.1 **回退链**](../telegram/overview.md) **可得** **非空** **欢迎正文**（**`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_*`** **或** **遗留键**）；**`CHANNEL_TELEGRAM=ON`**；该 **`userId`** **尚未**按 [`telegram/overview` §2.1.1 **幂等规则**](../telegram/overview.md) 接收过 **开通欢迎语**。  
- **When**：用户 **首次**同时满足 **Agent 开通已完成**（[`activate-trading-agent`](../../../flows/activate-trading-agent.md) **`S2～S5`** 叙事、[initialization-flow 成功终态](initialization-flow.md) **同窗**）且 **Telegram 绑定**对该 **`userId`** **生效**。  
- **Then**：Bot **须**向该会话发送 **一条** **按该用户语言（经解析与回退）选定模板** **渲染后的** 欢迎消息；**整条链无正文** → **不发送**。**同窗**：[`admin-bot-config` **SC-TG-ADMIN-05**](../telegram/admin-bot-config.md)。

---

**文档版本**：1.3.1 · **维护**：产品 + Channels owner · **本版**：§3 **Deeplink** **同窗** **Agent 绑定页**（承 **1.3.0**）。
