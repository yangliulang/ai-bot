# Trading Agent Config · 功能清单、需求与验收

**叙事**：[`overview.md`](overview.md)；**模块七 PRD**：[`../management-console-v1-prd.md`](../management-console-v1-prd.md) §10（**701～711**）；**`configKey` SSOT**：[`keys.md`](keys.md)；**Telegram Bot**：[`telegram/admin-bot-config.md`](../../agent/telegram/admin-bot-config.md)。

---

## 1. 划界

| 主题 | 说明 |
|------|------|
| **本模块** | 全所 **`configKey`**：**总开关 / 运维闸、`FEATURE_*`、交易护栏、Telegram 渠道（**编排只读 + Bot 参数 / 凭证 / Webhook 运维**）**；**Diff / 版本写 / 审批（可选）/ 回滚 / 审计 / JSON·YAML 导出**（[`config`](config.md)、[`flow`](flow.md)、[`rules`](rules.md)）。**Telegram 功能项叙事** **[`telegram/admin-bot-config.md`](../../agent/telegram/admin-bot-config.md)**。 |
| **非本模块** | **`GLOBAL_AGENT_SWITCH` 不在模块一编辑** → [`agent-management`](../agent-management/overview.md) **G01 只读横幅**；Prompt / Tool / **`ai-settings`** → 见 [`overview` 不包含 §2](overview.md)。 |
| **真源** | OpenAPI / `design` > [`keys.md`](keys.md) > 本文件；**运行时配置叠层 / 会话冻结 / Kill 优先 / 单笔状态机** **[`runtime-policy`](../../agent/exchange-agent/boundaries.md)**（**不**重复列举 `configKey`）。 |

---

## 2. FR-MC701～711 展开

### 2.1 FR-MC701 · 全局总开关（`GLOBAL_AGENT_SWITCH`）

- **能力**：**全局闸** Tab 对 [`keys` §1](keys.md#1-全局闸tab全局闸--fr-mc701702) **读/写**；写须 **二次确认 + 审计**。  
- **`OFF`**：附录 A §9 · `agentState` = **`GLOBAL_OFF`**；与 [`agent-management` G01 §5.1](../agent-management/functions.md) **同源** → **禁止新建实例 / Start / Resume**；**允许** Pause、Stop、R06 批量 Pause/Stop。  
- **`ON`**：不自动绕过其它 **`FEATURE_*`、准入、billing**。

### 2.2 FR-MC702 · 运维熔断（`OPS_GLOBAL_AGENT_PAUSE`）

- **与总开关分块展示**；`OPS_SUSPENDED` 与 **`GLOBAL_OFF`** 的并行语义与优先级由 **`design`/OpenAPI** 冻结。  
- **独立二次确认**，防与总开关误触混排。

### 2.3 FR-MC703 · 特性矩阵

- **键集**：[`keys` §2](keys.md#2-特性矩阵tab特性矩阵--fr-mc703)。  
- **每项**：布尔 + **依赖说明**（例：`FEATURE_AGENT_FUTURES` 依赖 [**`design/api`**](../../../../design/api.md) 合约 PATH 已登记）；**OFF** → 运行时早失败，与 [`exchange-agent/overview` §5](../../agent/exchange-agent/overview.md)（旧 **§10.5**、`FEATURE_*` 映射）、[`trade-assistance.md`](../../agent/exchange-agent/trade-assistance.md) **§8** **门闸对签**。

### 2.4 FR-MC704～705 · 交易护栏 · 默认值

- **键集**：[`keys` §3](keys.md#3-交易护栏--默认值tab交易护栏--fr-mc704705)。  
- **服务端校验**：白名单清空、`cooldown` 下限、`bps` 越界、枚举非法 → **拒绝写入** + §5 机器码。

### 2.5 FR-MC706 · 渠道编排只读

- Telegram **编排摘要只读**（[`keys` §4.1](keys.md#41-编排摘要只读--fr-mc706)）；不写 Bot `callback`/卡片正文。`configVersion` 与 `exchange-agent` / `telegram` 读 BFF **一致**。

### 2.6 FR-MC709 · Telegram Bot 运行参数（非密钥）

- **键集**：[`keys` §4.2](keys.md#42-非密钥运行参数可写--fr-mc709)。  
- **服务端校验**：locale 非法、URL 模板占位符缺失、**模板含疑似 Token 形态**、**任一条** **`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT` / `_ZH_CN` / `_ZH_TW` / `_EN` 超长或占位符不在白名单** → **拒绝写入** + [`§5`](functions.md#5-错误码草案) 机器码（可扩展 **`ADMIN_TELEGRAM_POLICY_REJECT`** **`design` 冻结**）。  
- **对签**：[`telegram/admin-bot-config`](../../agent/telegram/admin-bot-config.md) **FR-TG-ADMIN-02、FR-TG-ADMIN-06**。

### 2.7 FR-MC710 · Telegram Bot 凭证（`secretRef`）

- **`TELEGRAM_BOT_TOKEN_SECRET_REF`**：仅 **vault 引用**；UI **掩码**；**二次确认 + 审计**；**导出 JSON/YAML _strip_** 或可还原秘密（[`keys` §4.3](keys.md#43-凭证引用可写--fr-mc710--高危)、[`telegram/admin-bot-config` FR-TG-ADMIN-03](../../agent/telegram/admin-bot-config.md)）。  

### 2.8 FR-MC711 · Webhook 运维与自检

- **运维 API**：**setWebhook** / **deleteWebhook**、**连通性自检** — **登记表** [`design/api.md`](../../../../design/api.md) **`admin/channels/telegram/*`（TBD PATH）**。  
- **须 RBAC**：建议 **双人或 `CONFIG_OPERATOR` 子角色** **`design`/IAM 冻结**。  
- **对签**：[`telegram/admin-bot-config` FR-TG-ADMIN-04～05](../../agent/telegram/admin-bot-config.md)。

### 2.9 `agent-management` 模板风控合并

- **规则**：`effectiveTradingGuardrails = merge(globalTradingAgentConfig护栏, templateRisk)`（维度由 **design/OpenAPI** 列明）。  
- **模板只可收紧**：不得把全局已设严的上界在模板侧放宽。  
- **对签**：[`agent-management · FR-AM-T07`](../agent-management/functions.md) · 模板风控与 **rules**。

### 2.10 与运行时政策 `runtime-policy` 对签

- [`runtime-policy.md`](../../agent/exchange-agent/boundaries.md)：**五层叠层**、**执行内 `configVersion` 冻结**、**Kill 优先于 Freeze**、**禁止无人值守连环写**；**仓位/大额/高频**键（`keys` §3）须在 **Risk Check** 被消费，或与 **`design`** 冻结的 **`effective*`** 字段同源。  
- **`FEATURE_AGENT_FUTURES` 默认 OFF** 与 **大额/高频升级** 以 **`runtime-policy` §4·§7·§8** 为准，与 **FR-MC703～705** 一致执行。  
- **验收**：**§4** **SC-TAC-09、SC-TAC-10**；用户侧 E2E 下限见 [`../../../metrics/trading-metrics.md`](../../../metrics/trading-metrics.md) **SC-T13**。

---

## 3. FR-MC701～711 映射摘要

| FR-MC | 简述 | keys / Tab |
|-------|------|------------|
| 701 | `GLOBAL_AGENT_SWITCH` | §1 · 全局闸 |
| 702 | `OPS_GLOBAL_AGENT_PAUSE` | §1 · 全局闸 |
| 703 | **`FEATURE_*`、`CHANNEL_*`** | §2 · 特性矩阵 |
| 704～705 | **`SYMBOL` / `AGENT_*` 护栏** | §3 · 交易护栏 |
| 706 | Telegram 编排只读 | §4.1 · 渠道 |
| 709 | **`TELEGRAM_*` 非密钥运行参数** | §4.2 · 渠道 |
| 710 | **`TELEGRAM_BOT_TOKEN_SECRET_REF`** | §4.3 · 渠道 |
| 711 | Webhook 运维动作、自检 API | §4.4；`design/api` |
| 707～708 | Diff、`admin.audit`、快照回滚 | keys §6；[`flow`](flow.md) |

---

## 4. SC-TAC 验收标准（V1）

| 编号 | Given | When | Then |
|------|--------|------|------|
| SC-TAC-01 | `GLOBAL_AGENT_SWITCH=OFF` | **模块一** Start 或 I02 创建 | **403 或灰显**；G01 明示 OFF |
| SC-TAC-02 | 某 `FEATURE_AGENT_*=OFF` | Runtime 走matrix 写 PATH | **早于交易所**拒绝 + **稳定机器码** |
| SC-TAC-03 | `symbol` ∉ `SYMBOL_ALLOWLIST` | 下单或工具执行 | **拒绝** + 审计可定位 |
| SC-TAC-04 | 写配置后 T+N | `exchange-agent` / `telegram` 拉生效配置 | **`configVersion`** **与控制台提交一致**（**FR-MC706～709** 读路径） |
| SC-TAC-05 | 角色 `CONFIG_OPERATOR` | 清空白名单或 GLOBAL 关 | **二次确认 + 审计** |
| SC-TAC-06 | `If-Match` / `configVersion` **陈旧** | PUT 全局配置 bundle | **409** `ADMIN_OPS_CONCURRENT` |
| SC-TAC-07 | 选历史快照回滚 | 确认 | **当前 = 快照语义**；版本递增规则由 **`design`/OpenAPI** 冻结 |
| SC-TAC-08 | payload 含 **未登记私键** | 保存 | **4xx** · [`rules`](rules.md) §1 |
| SC-TAC-09 | 某 **`executionId` 已 Runtime Start**（`runtime-policy` §5）且 **冻结快照** `configVersion=V1` | 运营 **`PUT` 全局配置** 升至 **`V2`**（**非** Kill，如收紧 `AGENT_COOLDOWN_SEC`） | **该 `executionId` 未终局前** **后续写路径** **仍按 V1** 护栏；**新 `execution`** **按 V2**；**可观测** `effectiveConfigSnapshotId`（**或**等价 audit）**由 **`design`** **冻结** |
| SC-TAC-10 | **`GLOBAL_AGENT_SWITCH=OFF`**（或 **`OPS_GLOBAL_AGENT_PAUSE`** **命中 Kill**） | 本会话曾拉取 **ON** 时代 **`configVersion` 快照** | **仍** **零** **新写**（**Kill > Freeze**）；**`agentState`/原因** **明示** **全局/运维闸** |
| SC-TAC-11 | 配置导出（**FR-MC707 灾备**） | 含 **§4.3** 变更后拉 YAML/JSON | **无** Bot Token **明文**、**无**可逆 **Webhook 完整秘链**（**须**等价于 strip / redact） |
| SC-TAC-12 | 有效 **`secretRef`** + **运维** setWebhook | 成功回调 | **`getWebhookInfo`** **与** **`TELEGRAM_WEBHOOK_URL_TEMPLATE`** **意图一致**（**T+N** 内；**细则 `design`**） |
| SC-TAC-13 | `TELEGRAM_BOT_TOKEN_SECRET_REF` **轮换** | 确认写入 | **`admin.audit`** **须**记录 **操作者、ref 指纹、时间**；**默认日志字段** **无** Token |

---

## 5. 错误码草案

与 [`management-console`](../management-console-v1-prd.md) **全局配置写**前缀一致（`ADMIN_*` 族）。

| code | 典型触发 |
|------|----------|
| `ADMIN_OPS_CONCURRENT` | `configVersion` / `If-Match` 冲突 |
| `ADMIN_CONFIG_DEPENDENCY_VIOLATION` | `FEATURE` 依赖不满足 |
| `ADMIN_CONFIG_MATRIX_NOT_READY` | `design/api` PATH 仍为 `TBD` 却开启高风险的 `FEATURE_AGENT_*` |
| `ADMIN_CONFIG_POLICY_REJECT` | `SYMBOL` 或与模板合并风控拒绝 |
| `ADMIN_TELEGRAM_POLICY_REJECT` | `TELEGRAM_*` URL/locale/**欢迎语长度或占位符** 等策略校验失败（**`FR-MC709`**、**`FR-TG-ADMIN-06`**） |

---

## 6. 邻域自检

| 邻域 | 核对 |
|------|------|
| **agent-management** | G01 只读 · **FR-AM-T07** §2.9 合并 |
| **telegram** | **FR-TG-ADMIN-01～06**；[`admin-bot-config`](../../agent/telegram/admin-bot-config.md) |
| **access-control** | `AGENT_MIN_VIP_TIER`、灰度/封禁、**`AGENT_ROLLOUT_BLOCKED`**；[`overview`](../access-control/overview.md)、[`functions` §2～4](../access-control/functions.md) |
| **billing-management** | **`BILLING_*`**、[`keys`](keys.md) §5 |
| **tool-management** | **`FEATURE_AGENT_*`**、**SC-MCV1-05** 口径 |
| **observability** | **`admin.audit`、Diff** 摘要 |
| **exchange-agent / runtime** | **`FR-T`** 产品线闸；[`boundaries`](../../agent/exchange-agent/boundaries.md)（**原 `runtime-policy` 叙事**回迁中） |

---

## 7. 已决议默认（V1）

| 主题 | 默认 |
|------|------|
| Dry-run | 首版 **推荐启用**；极小变更豁免须 **`design` 书面 + MR** |
| **GLOBAL 关 / 清空白名单** | **双人审批** 建议启用 |
| **写后生效** | **事件广播**；G01 轮询 **≤30s** 与 **agent-management G01** 口径对齐 |

