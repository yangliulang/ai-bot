# Agent 产品线 · 绑定配置页（Web/H5）

**路径**：`specs/requirements/domains/web/agent-onboarding.md`。

**上级**：[`overview.md`](overview.md) · **编排真源**：[`../agent/onboarding/overview.md`](../agent/onboarding/overview.md)、[`../agent/onboarding/initialization-flow.md`](../agent/onboarding/initialization-flow.md)、[`flows/activate-trading-agent.md`](../../flows/activate-trading-agent.md)。

**契约映射（CC · `design/api`）**：[`overview.md` §4](overview.md)。

## 1. 目的

在 **Agent 项目（产品线 Web/H5）** 提供 **终端用户可读** 的 **Trading Agent 绑定配置页**：用户 **不须访问 Coobit 交易所主站**；单页完成 **Telegram 账号展示**、**子账户 UID（与交易所 `subUid` 同窗）**、**子账户 API Key + Secret** 录入、**保存时服务端通过交易所开放 API 校验**、**成功后** **实例创建与绑定**（编排真源 **initialization-flow §1.2**）。**触点边界**：**账单与用户账务流水** **仍在交易所站内**，见 [`agent-billing.md`](agent-billing.md)。**不与** 后台审计字段表、OpenAPI **混写**。**对上交易所 HTTP**：保存时服务端对上 Coobit 出站默认 **`openapi-ai`**（Skill 宿主），制品须 pin。**PATH/** 调用次序仍以 [`initialization-flow` §1.2](../agent/onboarding/initialization-flow.md)、[`design/api`](../../../design/api.md) 「绑定保存 · 交易所探测矩阵」、[`agent-coobit-api-allowlist`](../../integrations/exchange/agent-coobit-api-allowlist.md) **为 SSOT** — 同窗 **[`integrations/exchange/overview`](../../integrations/exchange/overview.md)**。

---

## 2. 功能需求 · `FR-WEB01～06`

| ID | 需求摘要 | 约束与同窗 |
|----|----------|------------|
| **FR-WEB01** | 提供 **Agent 产品线绑定页** 的 Web/H5 闭环入口（路由可达；**托管于 Agent 项目**，**非**交易所主站壳）；页面 **仅**承载 **单页配置**（**禁止**首版多步 onboarding 向导）。 | **`POST /api/v1/me/agent/bindings/trading-api`** **须在可归因之产品线绑定上下文（Deeplink / session / `design` 冻结）下可调**；**不须**终端用户 **登录 Coobit 交易所主站**。**保存**触发的 **交易所 API 凭据与账户态校验** **须先于** **实例创建/绑定**（同窗 **initialization-flow §1.2**）；校验失败须 **可读归因**，**禁止**误报成功。 |
| **FR-WEB02** | **文案面向终端用户**：说明 **为何需要 Key**（绑定 Agent 实例所交易子账户）、**子账户 UID 与 Key 须同属该子账户**（摘要级）、**资金安全边界**（权限模板同窗 **`permission-authorization`**）；**避免**把 Runtime / 内部模块名当作主标题。 | **子账户 UID**、Key/Secret **输入控件**可存在于页内；**成功后** **不得在**成功态 **常驻展示** Secret；与 **FR-ON02**、**SC-ON-04** 同窗。 |
| **FR-WEB03** | **醒目展示**与 Deeplink 上下文一致的 **Telegram 账号**（例如 **`@username` / 脱敏 id**），并要求用户 **目视确认**绑定对象；并与 [`telegram-binding`](../agent/onboarding/telegram-binding.md) **会话绑定**语义一致。 | Deeplink **须**符合 **官方域名 / Bot** 展示规范；**禁止**易被混淆的第三方跳转占位作为主路径。 |
| **FR-WEB04** | 明示 **拟绑定 Key** 须归属 **Agent 专用子账户 scope**（摘要级与 **`permission-authorization`** / **`design/api`** 一致）；可提供 **「权限不足 / 非子账户 Key」**类校验失败 copy。 | 细粒度权限矩阵真源 **permission-authorization** / **`design/api`**；页面为 **摘要级一致**。 |
| **FR-WEB05** | **成功路径后续引导**：① **资金划转** — 引导用户向 **Agent 专用子账户 · 币币 USDT 可用** 充值/划转以便计费与交易（同窗 [`billing` §2](../admin/billing-management/overview.md)）；② **回到 Telegram** — 打开 **官方 Telegram Bot** 继续使用（[`telegram/overview` §2.2～§2.6 · Deeplink/防钓鱼](../agent/telegram/overview.md)；**会话内卡片确认 §2.5 · 类型 A** **见** [`trade-via-agent.md`](../../flows/trade-via-agent.md)）。 | **成功态** **不显式**复述 Secret；阻断原因同窗 **activation-policy** / **runtime-provisioning** 可见话术类别。 |
| **FR-WEB06** | **保存时**：服务端须完成 **initialization-flow §1.2 项 2** 下限校验 — 请求体 **须同时携带 **`apiKey`** **与** **`apiSecret`**（**成对**参与交易所签名探测或等效路径，**禁止**「仅 Key、无 Secret」宣称完成绑定）；**①** Key 须为 **子账户** API Key（主账户 Key → **`AGENT_BIND_KEY_NOT_SUBACCOUNT`**）；**若请求携带 `agentSubAccountUid`**（绑定页 **必填**），须与该 Key **`apiSecret` 签名探测及/或母账户列表命中**在交易所解析得到的 **`subUid`** **一致**，否则 **`AGENT_BIND_SUBACCOUNT_UID_MISMATCH`**；**②** 该子账户须 **已启用**（禁用 → **`AGENT_BIND_SUBACCOUNT_DISABLED`**）；**③** Key 须已开启 **API 交易**及 **币币、杠杆、合约** 权限（缺项 → **逐项** **`TradingApiBindRejectCode`**）；**④** **全部通过**后才允许 **实例创建与绑定**。 | 错误 **`Problem.code`** **同窗** [`TradingApiBindRejectCode`](../../../openapi/components/onboarding-schemas.yaml)；**多权限缺失** 可用 `details.missingPermissions[]` **清单归因**；服务端 **经交易所开放 API** **探测 PATH / 调用次序** [**`design/api.md`**](../../../design/api.md) **「绑定保存 · 交易所探测矩阵」**（**调用身份** **`design` 冻结**，**不须**用户打开交易所主站）；前端/BFF **禁止**吞码换笼统文案。 |

---

## 3. 响应式与触控（横切）

下列与 [`agent-billing.md`](agent-billing.md) §3 **同窗**，配置页 **须同等满足**：

- **窄屏（建议 breakpoint 与主站 H5 壳一致，如 ≤1024px）**：单手路径友好（底部主导航若存在须避让安全区）；**触控优先**（如减少双击缩放延迟、主要按钮与勾选区域满足 **粗指针** 可点下限）。  
- **横竖屏与安全区**：`viewport-fit=cover` 场景下主要内容 **不被** Home Indicator 遮挡。

（实现栈与 CSS 细节归 **`specs/design/`** 或工程仓库，本篇只绑 **验收主题**。）

---

## 4. 验收 · `SC-WEB-01～06`、`SC-WEB-12`

| ID | Given / When / Then |
|----|---------------------|
| **SC-WEB-01** | **Given** 用户在 **Agent 产品线绑定页** **具备** **`FR-WEB01`** **所指可归因上下文** · **When** 录入 UID、Key/Secret 并保存 **且**服务端 **§1.2** 下限校验全部通过 · **Then** 页面呈现 **成功态**，且 **不打断** 展示下一步 **划转** 与 **回到 Telegram / 打开 Bot**（外链形态符合 **FR-WEB05**）。 |
| **SC-WEB-02** | **Given** 校验已成功，用户处于 **成功态/摘要区** · **When** 查看页面持久展示内容 · **Then** **不出现** API Secret 明文；与 **onboarding §1.3** 摘要 **无矛盾**。 |
| **SC-WEB-03** | **Given** 配置页加载 · **When** 用户查看 Telegram 区 · **Then** **可见**与本链路边界一致的 **Telegram 账号展示** **及** **官方 Bot / 域名** 提示；**多会话 / 换绑** 策略与 **telegram-binding** **摘要一致**。 |
| **SC-WEB-04** | **Given** 窄屏设备 · **When** 完成勾选与主按钮操作 · **Then** 主要控件 **可单手点击**，无 **误触级** 重叠（与 §3 触控主题一致）。 |
| **SC-WEB-05** | **Given** 后端返回阻断（校验失败、额度、权限、风控等） · **When** 页面展示错误 · **Then** 用户可见文案 **可归因**（含 **`TradingApiBindRejectCode`** / **`missingPermissions`**）且 **不归因错位**（不须暴露内部 trace）。 |
| **SC-WEB-06** | **Given** 服务端模拟 **主账户 Key / 子账户禁用 / 单项或多项权限关闭** · **When** 用户保存 · **Then** 应答 **不得**为 HTTP 200 成功绑定；页面展示 **与失败原因一致** 的提示（分别对应 **FR-WEB06** ①～③）；**不得**进入实例创建成功态。 |
| **SC-WEB-12** | **Given** 用户填写 **有效子账户 Key**，但 **`agentSubAccountUid`** **与 Key 所属 **`subUid`** **不一致** · **When** 保存 · **Then** 应答 **`Problem.code`=`AGENT_BIND_SUBACCOUNT_UID_MISMATCH`**（或同窗 HTTP **`409`**）；页面展示 **可归因** copy；**不得**进入实例创建成功态。**编号**：账单配额验收用 **`SC-WEB-14～15`**（见 [`agent-billing.md` §2.1.1](agent-billing.md)），**本篇独占 `SC-WEB-12`**。 |

---

**文档版本**：1.4.3 · **维护**：产品 + Agent Web 触点 owner · **本版**：§1 openapi-ai / 同窗链文案整理。**承** 1.4.2（含 **`SC-WEB-12`**）。
