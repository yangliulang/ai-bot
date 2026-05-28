# 权限与授权（子账户交易 API）

本卷约定 **子账户交易 API（Agent 绑定）**如何从 **Agent 产品线绑定页（§1.2）**明示提交产生、默认权限模板的能力边界，以及吊销与轮换的用户侧下限。**HTTP 与 PATH** 以 [**`design/api.md`**](../../../../design/api.md) 为终裁。**对上 Coobit 私网出站**：服务端 **校验与运行时私域读写**默认 **`openapi-ai`/Skill**，**制品须 pin**；能力与 PATH **详见** [`integrations/exchange/overview`](../../../../integrations/exchange/overview.md)、[`agent-coobit-api-allowlist`](../../../../integrations/exchange/agent-coobit-api-allowlist.md) **及本条**。**不改变托管与权限叙事**。

---

## 1. 授权来源与托管

| 项 | 要求 |
|----|------|
| 触发条件 | 仅在用户完成 **[`initialization-flow` §1.2](initialization-flow.md)** 所述 **服务端校验成功**并完成 **托管挂载**后，系统可将该 Key **视为**与本产品 **Active** 绑定（明示提交须同窗 **FR-WEB01**、**FR-ON02**）。 |
| Secret | Secret 仅存在于密钥托管与 Agent Runtime；控制台、工单、会话侧默认日志不出现明文。 |
| 子账户 scope | 凭据必须挂在 Agent 专用子账户；禁止以主账户 API Key 作为默认介质调用须本子账户 scope 的私域写接口（与 FR-T01、`api.md` 叙事同窗）。 |

---

## 2. 默认权限模板（能力族）

**默认应覆盖**（仅在 `design/api` 矩阵冻结后与 FR-T01、`trade-assistance` §8 对签）：

- 策略必需的私有只读（订单、持仓、余额、风险快照等矩阵已列能力）。  
- 用户确认后可执行的 `call_exchange_write` 能力族（逐条以 **FR-TS07** 登记表为准，见 [**`trade-assistance`**](../exchange-agent/trade-assistance.md)）。

**默认禁止或须转主站**（同窗 [**`boundaries`**](../exchange-agent/boundaries.md)）：

- 提币/出金；未矩阵化的理财写。  
- 母账户与 Agent 子账户划转（`TRANSFER_REQUIRES_WEB` 等）。

收窄权限须可配置、可审计，不得在未登记 MR 情况下静默删除 FR-T01 已依赖只读。

---

## 3. 凭据生命周期（概念）

| 阶段 | 含义 |
|------|------|
| **已创建** | 交易所侧重密钥已生成，可能尚未挂载至本产品运行时 |
| **Active** | Runtime 已通过密钥服务取钥，可被 **FR-T02** 判定为可用 |
| **Rotating**（可选显式态） | 新旧 Key 切换窗：仅允许一方对 **新执行**生效；旧 Key 废止须有审计时间戳 |
| **Suspended / Revoked** | 风控、用户主动或交易所吊销；须停止 **新** `trading.exchange_private` **成功**路径直至恢复 |

**吊销 / 冻结**：须给出与用户摘要 **`agentTradingApiBindingStatus`/`lastProductBlockReason`** 同窗的枚举；并按 **FR-T05** 提供可读恢复 Deeplink（**重新绑定** → **Agent 产品线绑定页**；**须交易所站内**之动作 **同窗** **`exchange-agent`** 稳定码；细节 **同窗** [`telegram-binding` §3](telegram-binding.md)、[`initialization-flow` §3](initialization-flow.md)）。

**轮换**：重叠策略由 **`design`/ADR** 冻结；**产品下限**：禁止 **>T**（如 24h，实现定义）内 **两套互斥绑定均判 Active** 且无 **运营可观测**告警；禁止 **静默**轮换导致用户 **不知**旧 Key 已失效。

---

## 4. 与 FR-T02

在未满足子账户就绪与 API **Active** 前，不得进入 **`trading.exchange_private`** **成功**语义路径。门禁顺序宿主：[**`consume-and-bill` S2**](../../../flows/consume-and-bill.md) 与各 **exchange-agent** 分卷对 **FR-T02** 的引用。

---

## 5. 轮换与吊销 · 用户可达路径（叙事）

以下 **不**替代主站页面线框；**只锁**「须有」与 **Deeplink** 下限。

| 事件 | 用户侧下限 | 运营/审计下限 |
|------|------------|----------------|
| **计划轮换** | 会话或摘要 **可**提示「安全升级中」；**不得**伪称「子账户未开立」 | **公开 `agentTradingApiKeyId`** 迁移记录（旧→新 **id**） |
| **紧急吊销** | **FR-T05** + **Agent 绑定页 / 交易所 API 管理**链（重获有效 Key） | 原因码、操作者、时间；**无 Secret** |
| **权限收窄（运营）** | **不得**在 **无版本登记**下删除 **FR-T01** 已依赖只读；若导致阻断须 **显式 `code`** | 与 [**`tool-management`**](../../../domains/admin/tool-management/overview.md) 审计同窗 |

---

## 6. 验收草案 · Given / When / Then

与 [`initialization-flow` §7](initialization-flow.md) **ON-GWT** 系列、[`telegram-binding` **`TG-GWT-03`** §6.3](telegram-binding.md) **同窗评审**：本节约束 **API 生命周期与权限收窄**，**不**替换 **子账户/会话**主路径用例。

### 6.1 `ON-PERM-01` · 轮换后新执行只认新钥

- **Given**：测试注入 **Rotating** 完成，旧 **`agentTradingApiKeyId`=A** 已标记废止，**B** 为 **Active**。  
- **When**：触发一条须 **子账户 scope** 的新 **`trading.exchange_private`** 读/写。  
- **Then**：交易所侧请求 **不得**再带 **A** 的 Secret；若误带须 **失败可观测**（不得随机成功）。审计可证明 **B** 为唯一 Active。

### 6.2 `ON-PERM-02` · 吊销后会话须可恢复

- **Given**：**API** 被 **Revoked**（测试或沙箱）。  
- **When**：用户在 Telegram 重试 **同意图**私域请求。  
- **Then**：应答满足 **ON-GWT-02**（摘要 + **产品线 Deeplink**）；用户在 **Agent 产品线绑定页**完成 **重新绑定 / §1.2 保存校验** 后，**同一意图**在 **API 恢复 Active** 后 **可通过**（同窗 [`initialization-flow` §7.2](initialization-flow.md)）。

### 6.3 `ON-PERM-03` · 收窄权限不致「假 onboarding」

- **Given**：运营收窄 **模板权限**致使某 **只读**矩阵能力不可用（**合法**变更且已审计）。  
- **When**：用户请求触发该 **只读**。  
- **Then**：阻断 **`lastProductBlockReason`/会话稳定码**须 **归因于权限/能力**，**不得以** **`AGENT_SUBACCOUNT_BLOCKED`** **冒充** 「未开通子账户」（同窗 [`activation-policy` §1](activation-policy.md) **归因诚实性**）。

---

## 7. 非目标

- 不重写 FR-TS07 单行登记全表。  
- 不写 HMAC / 时钟偏移 / IP 白名单 **字段级**契约。

---

**文档版本**：1.3.2 · **维护**：产品 + Security + Accounts owner · **本版**：篇首 **Coobit HTTP **`openapi-ai`**/`integrations`** 同窗。**承** **1.3.1**。
