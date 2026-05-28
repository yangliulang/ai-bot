# Telegram · 运营后台 Bot 配置

**宿主**：控制台 **模块七 · Trading Agent Config** 之 **「渠道 / Telegram Bot」** 分区（[`trading-agent-config/config.md`](../../admin/trading-agent-config/config.md)）。**`configKey` SSOT**：[`trading-agent-config/keys.md`](../../admin/trading-agent-config/keys.md) **§4**。

**密钥与明文策略**：与 [`ai-settings/overview.md`](../../admin/ai-settings/overview.md) **`secretRef`** **同窗** — **控制台、审计、`admin.audit`、导出 JSON/YAML** **禁止** Bot Token、Webhook 密文、hmac salt 等 **可还原秘密**（[`trading-agent-config/rules.md`](../../admin/trading-agent-config/rules.md) **§6** **延伸**）。

**互引**：[`overview.md`](overview.md)；[`telegram-binding.md`](../onboarding/telegram-binding.md)；[`design/api.md`](../../../../design/api.md) **「运营侧 Telegram 渠道运维 API」** **登记表行**。**`CC-P1-06`**：**Hosted/生产** **Webhook/密钥** **与** **`SC-TAC-11～13`**、**`FR-TG-ADMIN-01～06`** **实测关闭** **须** **同窗** **[`management-console-v1-prd.md`](../../admin/management-console-v1-prd.md) §13** **清单** **（** **首条** **`[ ]`** **仍须** **）**。

---

## 1. 目的

为 **单一生产 Bot（本版预设）** 提供 **可审计** 的 **连接与体验参数** 治理能力：**凭证轮换**、**Webhook 生命周期**、**非密钥运行参数**（含 **开通完成后欢迎语**）、**连通性自检**；并与 **`CHANNEL_TELEGRAM`**、运行时 **`configVersion`** **对签**。

---

## 2. 功能需求（FR-TG-ADMIN-*）

### FR-TG-ADMIN-01 · Bot 身份与健康（只读）

- **能力**：展示 **Bot `@username`、`id`、`name`**（经由 **服务端**调用 Bot API **`getMe`** 或等价缓存）；**最近一次拉取时间与错误摘要**（**不含** Token）。  
- **约束**：**`CHANNEL_TELEGRAM=OFF`** 时仍 **允许** 只读展示（便于排障），但须在 UI **明示** 渠道已关闭。

### FR-TG-ADMIN-02 · 非密钥运行参数（可写）

- **能力**：对 [`keys.md` §4.2](../../admin/trading-agent-config/keys.md) **`TELEGRAM_*`** **非密钥** 项 **版本化写入**（与 **模块七**全局 bundle **同原子语义** **`design` 冻结**，或 **独立子 bundle** **`If-Match`** — **OpenAPI 终裁**）。  
- **验收**：写入后 **Telegram BFF / 编排** **T+N** 内读到一致 **`configVersion`**（与 **SC-TAC-04** 精神一致，见 [`trading-agent-config/functions.md`](../../admin/trading-agent-config/functions.md) **§4**）。

### FR-TG-ADMIN-03 · 凭证与 `secretRef`（可写 · 高危）

- **能力**：**登记 / 轮换** **`TELEGRAM_BOT_TOKEN_SECRET_REF`**（[`keys` §4.3](../../admin/trading-agent-config/keys.md)）；UI **仅**展示 **掩码**（如 **末 4 位** 或 **指纹**）与 **版本**；**须二次确认 + `admin.audit`**。  
- **约束**：**禁止** 在 **全局配置导出** 中带出 **可还原** 秘密（[`trading-agent-config/config.md`](../../admin/trading-agent-config/config.md) **§3**）。

### FR-TG-ADMIN-04 · Webhook 运维动作

- **能力**：在 **具备 IAM** 的角色下 **触发** **setWebhook / deleteWebhook**（**具体 PATH** **`design/api` 冻结**）；**回显** **`getWebhookInfo`** **摘要**（URL、pending、last_error_date）。  
- **约束**：**推荐** **服务端** 根据 **`TELEGRAM_WEBHOOK_URL_TEMPLATE`**（[`keys` §4.2](../../admin/trading-agent-config/keys.md)）与 **当前 Token** **拼装**最终 URL — **避免** 在控制台粘贴 **含 secret 的完整 URL**。

### FR-TG-ADMIN-05 · 连通性自检

- **能力**：**一键** **`getMe` + `getWebhookInfo`**（及可选 **`sendChatAction`** **对固定 dry-run chat** **`design` 可选**）；结果 **结构化**可供 **模块八** 跳转（[`observability-management`](../../admin/observability-management/overview.md)）。

### FR-TG-ADMIN-06 · Agent 开通欢迎语（可写 · **简中 / 繁中 / 英文**）

- **能力**：在 **渠道管理 · Telegram 配置** 维护 **[`keys` §4.2](../../admin/trading-agent-config/keys.md) `TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN`、`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_TW`、`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_EN`**（**多行正文**、**空串** = **该语无专用模板**，**走** [`overview` §2.1.1](overview.md) **回退链**）；**可选** **遗留键** **`TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT`** **兼容迁移**。写入语义与 **`FR-TG-ADMIN-02`** **同窗**（`configVersion`、`admin.audit`、**PATCH `runtimeParams`** **或** bundle **`design` 终裁**）。
- **用户侧行为**：见 [`overview.md`](overview.md) **§2.1.1**（**语言解析**、**回退链**、触发：**开通完成 ∧ Telegram 已绑定**、**幂等一条**）。
- **约束**：**禁止**在文案中嵌入 **可还原秘密**；占位符 **仅允许** **`design`/OpenAPI 白名单**；**各语** **超长** **拒绝写入**或 **裁剪** **`design` 冻结**（须低于 Telegram **单条消息上限**）；**控制台** **宜** **分 Tab 或** **三列** **编辑** **避免** **混写**。

---

## 3. 非目标

- **不**在本文定义 **卡片字段全集** / **每笔交易 copy** — 见 [`interaction-flow-standard.md`](../../../standards/interaction-flow-standard.md) **§8** 与 **`trade-assistance`**。  
- **不**将 **Prompt 正文**、**Tool 矩阵** 纳入 Bot 配置 Tab — 分属 **模块二 / 三**。

---

## 4. 验收 · SC-TG-ADMIN-*

| 编号 | Given | When | Then |
|------|--------|------|------|
| **SC-TG-ADMIN-01** | 有效 `secretRef` | 打开 Bot 分区 | **getMe** 字段可见；Token **永不**明文落审计默认字段 |
| **SC-TG-ADMIN-02** | 修改 `TELEGRAM_DEFAULT_LOCALE` | 提交成功 | **`configVersion`** 递增；频道 **新会话默认语言** **T+N** 生效（**具体 T** **`design` 冻结**） |
| **SC-TG-ADMIN-03** | 轮换 `TELEGRAM_BOT_TOKEN_SECRET_REF` | 确认 | **旧 webhook 失效风险** **须**文案提示；**审计**含 **操作者、`ref` 指纹、非敏感 `webhookInfo` 快照** |
| **SC-TG-ADMIN-04** | 非法 URL 模板或 Bot API 403 | setWebhook | **4xx** + **稳定 `ADMIN_*` 族码**（与 [`trading-agent-config/functions.md` §5](../../admin/trading-agent-config/functions.md) **同窗扩展** **`design` 冻结**） |
| **SC-TG-ADMIN-05** | **按** [`overview` §2.1.1](overview.md) **回退链** **存在** **非空** **欢迎正文**（**三语键** **或** **遗留键**）；用户 **首次**达成 **开通完成 ∧ Telegram 绑定** | 系统投递 | Bot **发送一条** **解析语言后的** 欢迎语；**同一用户幂等**；**整条链无正文** → **不发送**、**不算失败** |

## 5. OpenAPI / 登记表

落地时 **须**在 [`design/api.md`](../../../../design/api.md) **登记表** **新增一行**：**「运营后台 · Telegram Bot / Webhook（模块七子面）」**，并与 **全局配置写** **`If-Match` 语义** **书面划界**（**同 bundle** vs **独立 resource** **`design` 终裁**）。

---

**文档版本**：0.2.1 · **维护**：产品 + Channels owner + 后台 owner · **本版**：**FR-TG-ADMIN-06**、**SC-TG-ADMIN-05** **三语欢迎语** **与** **`overview` §2.1.1** **同窗**；承 **0.2.0**
