# Agent 实例能力扩展（I02 / I04 / I05）

> 功能 ID：`2026-05-26--admin-agent-instance-write`  
> 产品 Agent 定稿 · `contract_ready`

## 背景

**存量**：Admin 已具备 **I01/I03** 实例列表与详情、**I06** 删除、**R01–R06** Runtime、**L01–L03** 日志深链（`inventory.md` §2.3）。**2026-05-25** 服务端已挂载 **I02 创建**、**I04 子账户登记/解绑**、**I05 `instanceOverrides` 白名单 PATCH**（`admin_agent_instances.py` · `test_admin_p1_ops.py`），但 **`admin/FE_HANDOFF.md`** 中 **实例写路径 UI 与 API client 仍未交付**。

本功能包将 **OpenAPI I02/I04/I05** 与 **Admin 运营写路径** 收口为可验收闭环：运营可在控制台 **创建实例**、**登记/解绑子账户 ID**、**编辑白名单参数**；**API 密钥**仍由用户 **Deeplink** 完成（与 SSOT **I04**「登记 subUid，密钥不走 Admin 明文」一致）。

## 用户故事

- 作为 **运营**，我希望在 **实例列表** 为指定 **Telegram 用户** 创建 Agent 实例，以便无需手工写库即可开通。
- 作为 **运营**，我希望在 **实例详情** 修改 **`instanceOverrides`**（语言/冷却/偏好币对等），以便个性化策略而不越权改 Secret。
- 作为 **运营**，我希望在详情页 **登记或解绑** **`exchangeSubAccountUserId`**，并与 **交易 API 绑定状态** 列一致，以便协查 Deeplink 绑定进度。

## 验收标准

- [x] **AC-1**：**`POST /api/v1/admin/agents/instances`** Body 含 **`telegramUserId`**（数值串）；可选 **`templateId`**、**`templateVersion`**、**`exchangeSubAccountUserId`** → **201**，响应含 **`instanceId`**（`inst_` 前缀）、**`userId`**、**`templateId`**、**`runtimeInstanceState`**。
- [x] **AC-2**：同一 **`telegramUserId`** 再次 **POST** 创建 → **422**，**`code=AGENT_QUOTA_EXCEEDED`**（每 tg 用户一行实例，V1）。
- [x] **AC-3**：**`PATCH /api/v1/admin/agents/instances/{instanceId}`** Body **`instanceOverrides`** 仅含白名单键（**`preferredLanguage`**、**`cooldownPreferenceSec`**、**`symbolPreference`**、**`voiceOutputEnabled`**）→ **200**，**`GET` 详情** 回显合并结果；含未登记键（如 **`secretApiKey`**）→ **422** **`VALIDATION_ERROR`** 且 **`details.unknownKeys`** 非空。
- [x] **AC-4**：**`POST …/instances/{instanceId}/binding`** Body **`subAccountId`** 或 **`exchangeSubAccountUserId`** → **200**，详情 **`exchangeSubAccountUserId`** 更新；**`DELETE …/binding`** → **204**，详情 **`tradingApiBindingStatus=NONE`** 且 **`instanceId`** 不变。
- [x] **AC-5**：实例已存在且用户经 **`POST /api/v1/me/agent/bindings/trading-api`**（或 **`api-binding/confirm`**）完成密钥托管后，**`GET` 详情** **`tradingApiBindingStatus=BOUND`**；**AC-4** 解绑后恢复 **NONE**（实例行仍在）。
- [x] **AC-6**：**`CHAINUP_AGENT_AGENT_RUNTIME_GLOBAL_DISABLED=true`** 时 **POST I02** → **422**，**`code=AGENT_GLOBAL_OFF`**（门禁与 **G01** 一致）。
- [x] **AC-7**：Admin **`/agents/instances`** 提供 **「创建实例」** 表单（**`telegramUserId`** 必填；可选模板/子账户字段）→ 提交成功 **toast**、列表刷新且可见新 **`instanceId`**。
- [x] **AC-8**：Admin **`/agents/instances/{instanceId}`** 可 **编辑 `instanceOverrides`**（表单或受控 JSON，至少支持 **`preferredLanguage`**）→ 保存后详情区展示 PATCH 结果。
- [x] **AC-9**：实例详情提供 **「登记子账户」** 与 **「解绑 API 托管」**（二次确认）→ 调用 **AC-4** 接口后 **绑定状态** 列与按钮态正确刷新。

### I02 门禁（本期 API 断言子集）

| 条件 | 预期 `code`（422） |
|------|-------------------|
| 全局关闸 | `AGENT_GLOBAL_OFF` |
| 重复 tg | `AGENT_QUOTA_EXCEEDED` |
| 活跃封禁 / 灰度未入白名单 | `AGENT_USER_BLOCKED` / `AGENT_ROLLOUT_BLOCKED`（有则测，无则 P1） |

**本期不验收**：计费 **`AGENT_BILLING_BLOCKED`**、模板 **`AGENT_TEMPLATE_DISABLED`** 全矩阵（依赖计费/模板种子，另包或 P1）。

## 范围

### 本期包含

- **功能包 OpenAPI**：`POST /instances`、`PATCH /instances/{id}`、`POST|DELETE /instances/{id}/binding`（增量 schema）。
- **`admin/`**：**`agent-instances.ts`** 写 API；**`AgentInstancesListPage`** 创建；**`AgentInstanceDetailPage`** I05 编辑 + I04 绑定/解绑（只读展示可保留，须可写）。
- **pytest**：映射 **AC-1～AC-6**（可扩展现有 **`test_admin_p1_ops.py`** 或功能包专用文件）；**E2E** 覆盖 **AC-7～AC-9**。
- 与 **`product-doc/specs/openapi/admin/agent-management.yaml`** **I02/I04/I05** 路径对齐（字段 camelCase）。

### 本期不包含

- **I06 删除**（已实现；不在本包重复验收）。
- **I08 导出**、模板 **T02–T08** 全向导、计费前置全链路。
- Admin 代填 **API Key/Secret**（仍 **Deeplink / me bindings**）。
- **换绑自动 Pause** 执行策略（SSOT 可配置关闭；默认行为不另开包）。
- **Observability** tool/llm Tab（见 **`2026-05-26--admin-observability`**，已 done）。

## 界面与交互（含页面）

| 路由 | 行为 |
|------|------|
| **`/agents/instances`** | **创建实例** 入口（Modal/Drawer）；列表列含 **`instanceId`**、**`userId`**、**`agentState`**、绑定状态；失败展示 **`message`** / **`code`** |
| **`/agents/instances/:instanceId`** | **实例参数（I05）** 可编辑保存；**子账户（I04）** 登记/解绑；保留 Runtime/删除/日志深链 |

**加载/错误**：提交中禁用按钮；**404** 详情不存在；**422** 展示服务端 **`message`**（含 **`unknownKeys`**）。

## 非功能要求

- 写操作须 **Admin Bearer**（与存量 Admin 路由一致）。
- **不含 Secret** 字段入参/回显；**`instanceOverrides`** 拒绝越权键。
- 创建/绑定成功后 **列表/详情** 须刷新，避免 stale 绑定状态。

## 待确认问题

- [x] Q1：I04 是否托管 API 密钥？— **否**；Admin 仅 **`exchangeSubAccountUserId`**；**BOUND** 仍靠 Deeplink/`bindings/trading-api`。
- [x] Q2：每 tg 是否仅一实例？— **是**（**AC-2** / `AGENT_QUOTA_EXCEEDED`）。
- [x] Q3：I05 白名单键？— 以 **`instance_overrides.py`** 四键为准，与 OpenAPI 一致。
