# Access Control · 功能清单、需求与验收

**叙事**：[`overview.md`](overview.md)；**模块六 PRD**：[`../management-console-v1-prd.md`](../management-console-v1-prd.md) §9；**准入实现契约**：[`eligibility-runtime.md`](eligibility-runtime.md)；**VIP 数值真源**：[`../trading-agent-config/keys.md`](../trading-agent-config/keys.md) **§3 · `AGENT_MIN_VIP_TIER`**。

---

## 1. 划界

| 主题 | 说明 |
|------|------|
| **本模块** | **灰度与特征白名单**、**用户封禁**、**KYC/合规事实只读镜像**、**地域/风险测评（若 V1 纳入）**、**`AGENT_MIN_VIP_TIER` 运营编辑与审批**（与 **keys** **对 PR**）；**I02 前置链第 2 步** 之 **事实源或可观测因**（[`config` §4](config.md)）。 |
| **非本模块** | **子账户/API 绑定**（[`onboarding/overview`](../../agent/onboarding/overview.md)）；**计费余额/扣费**（[`billing-management`](../billing-management/overview.md)）；**全局产品线闸**（[`trading-agent-config`](../trading-agent-config/overview.md)）；**KYC 裁决写**（合规主系统）。 |
| **真源** | **名单/封禁策略** → 本域 **`config`/`flow`/`rules`** + **`design`/OpenAPI**；**`AGENT_MIN_VIP_TIER`** → [`keys`](../trading-agent-config/keys.md)；**I02 `code`** → [`agent-management` §7.1](../agent-management/functions.md)。 |

---

## 2. FR-MC601～607 展开（V1）

PRD 仅以 **601～607** 编号收口；下列 **拆条** 便于评审与 OpenAPI 对表 — **若**与所内 PRD 表格 **字面不一致**，以 **合同或 MR 会签** **调整编号映射**，**不**改变 **门禁语义**。

### 2.1 FR-MC601 · 灰度与渠道策略

- **对象**：**渠道**（如 Telegram / 未来 H5）× **用户段**（百分位、`userId` hash、显式名单引用 **等**，**以 `design` 冻结**）。
- **行为**：**可读**当前策略；**变更**须 **审计**；**读侧**（I02、运行时 BFF）**须在 `design` 冻结之 SLA** 内 **收敛至一致**，避免控制台与网关 **长时间口径分裂**（**SC-AC-04**）。

### 2.2 FR-MC602 · 白名单运营与复核

- **批量导入**（模板 **`design` 冻结**）、**单次增删**、**导出**（[`rules`](rules.md) **脱敏**）。
- **审批**：超过阈值或敏感桶 **须** **双人复核**（[`rules`](rules.md)）。

### 2.3 FR-MC603 · 用户封禁（合规 / 运营）

- **创建 / 查询 / 撤销**；**原因枚举** **与** **`lastProductBlockReason`** **附录 A** **对签**。
- **审计**：操作者、旧值/新值、`userId`、时效。

### 2.4 FR-MC604 · 封禁联动与时效

- **可选**：封禁 **联动** **实例 Pause**（[`agent-management` flow](../agent-management/flow.md)）；**默认**与 **欠费 Pause** **分开展示**（[`rules`](rules.md) §5）。
- **临时封禁**：**须** **到期时间** + **到期提醒/自动解封**（[`rules`](rules.md) §3）。

### 2.5 FR-MC605 · KYC 只读镜像

- **从**主数据/合规 API **拉取**（**轮询或事件**，`design` 冻结）；**管理台** **只读**展示 **与 I02 相关的字段下限**。
- **禁止**在本域 **写回** KYC **终态**（**写**走合规系统）。

### 2.6 FR-MC606 · 地域与风险测评（可选 V1）

- **若**所内 **V1 强制**：策略 **须** **同一 `code` 体系** **与** **FR-T02** **对签**；**若**仅主站约束：本域 **只读标签** + **Deeplink**（[`onboarding/overview`](../../agent/onboarding/overview.md)）。
- **未决**项 **单列** ADR，**不**在实现里 **隐式默认放行**。

### 2.7 FR-MC607 · VIP 门槛（`AGENT_MIN_VIP_TIER`）

- **编辑**：本域 IA **或** 与 **附录 A** 约定的 **单一入口**（与 [`trading-agent-config` config](../trading-agent-config/config.md) **划界**：**用户级 override** 须 **双签**后方可暴露）；数值变更 **须**与 **[`keys` §3](../trading-agent-config/keys.md)** **同一 MR** 或可合并窗口对齐。
- **比对主体**：**须取 Agent 专用子账户所隶属之母账号（主账号 · `userId`）的 VIP 等级**（摘要 **`vipTier`**、[`eligibility-runtime` §1](eligibility-runtime.md) Step **VIP**）；**禁止**按子账户独立 VIP 裁决 **`MEMBERSHIP_BLOCKED`**。
- **未达标**：**I02** **`AGENT_MEMBERSHIP_BLOCKED`**；**运行时** **FR-T02** **第 4 道** **一致**（[`exchange-agent` flow](../../agent/exchange-agent/trade-assistance.md)）。

---

## 3. SC-AC 验收标准（V1）

| 编号 | Given | When | Then |
|------|--------|------|------|
| SC-AC-01 | 用户处于 **有效封禁** | **I02** | **拒绝** + **`AGENT_USER_BLOCKED`**（§7.1） |
| SC-AC-02 | **母账号** **`vipTier`** **<** 生效中 **`AGENT_MIN_VIP_TIER`**（**非**子账户侧独立 VIP） | **I02** 或 **FR-T02 新执行** | **`AGENT_MEMBERSHIP_BLOCKED`**；**摘要字段**与 [`management-console-v1-prd` §8.2](../management-console-v1-prd.md) **对签** |
| SC-AC-03 | 用户 **不在** **灰度/白名单** **允许集** | **I02** | **拒绝** + **`AGENT_ROLLOUT_BLOCKED`**（§7.1 **须登记**） |
| SC-AC-04 | 运营 **更新**白名单/灰度 | **T+ 短窗口** | **读侧**（I02 / BFF）**一致拒绝或放行**；**无**「控制台已放白、API 仍拒」**超阈漂移** |
| SC-AC-05 | 用户 **欠费 Pause** + **合规封禁** **同时**可能出现 | 打开 **用户摘要 / 详情** | **两因** **分开展示**（[`rules`](rules.md) §5） |
| SC-AC-06 | 运营 **无**合规写权限 | 在管理台 **KYC Tab** **任意写操作** | **拒绝**或无写入口（**只读镜像**） |
| SC-AC-07 | 运营 **导出**名单 | CSV | **默认脱敏** `userId`/PII（[`rules`](rules.md) §4） |
| SC-AC-08 | 产品 **新增** I02/门禁业务 **`code`** | **MR / 契约收口窗口** | **须先**扩展 [`agent-management` §7.1](../agent-management/functions.md) **与 OpenAPI** **再合入 BFF** |

---

## 4. 与 **`agent-management` §7.1** 对齐

| 本域触发 | `code`（**V1**） |
|----------|----------------|
| 合规凌驾 | `AGENT_COMPLIANCE_RESTRICTED`（[`eligibility-runtime` §3](eligibility-runtime.md)） |
| 封禁 | `AGENT_USER_BLOCKED` |
| 地域未通过 | `AGENT_REGION_BLOCKED`（同窗登记） |
| KYC/测评未通过 | `AGENT_KYC_REQUIRED` **或** `AGENT_KYC_INSUFFICIENT`（OpenAPI **同窗收口**为一种或并列，见 [`eligibility-runtime` §1](eligibility-runtime.md)） |
| VIP 不达标 | `AGENT_MEMBERSHIP_BLOCKED` |
| 灰度/白名单之外 | **`AGENT_ROLLOUT_BLOCKED`**（**本版新增登记**） |

其余 **`GLOBAL` / OPS / billing / 模板 / 配额** **非**本域定义，但 **须在 I02 UI** **可归因排序**展示（参见 [`agent-management` I02](../agent-management/functions.md)）；否决 **优先级与归因顺序** **以** [`eligibility-runtime` §2](eligibility-runtime.md) **为准**。

---

## 5. 邻域自检

| 邻域 | 核对 |
|------|------|
| **agent-management** | **§2.1 I02** 次序、**§7.1**、附录 A **`agentState`** |
| **exchange-agent** | **FR-T02**、`agentMinVipTier` **快照口径** |
| **trading-agent-config** | **`AGENT_MIN_VIP_TIER` keys；用户 override 与本域冲突规则** |
| **billing-management** | **欠费 ≠ 合规封禁** |
| **onboarding / Key 绑定** | **§1.2 为 Agent 产品线绑定页**；KYC/合规 **等 Deeplink** **仍可指向交易所站内**（同窗 **`onboarding/overview`**） |
| **`design/api`** | **[登记表「模块六」](../../../../design/api.md)**、**EvaluateEligibility / `capabilities`**（[`eligibility-runtime` §4·§10](eligibility-runtime.md)）、**「待补充」**：**用户摘要归因**、**I02 `code` `enum`** |

---

## 6. 已决议默认（V1）

| 主题 | 默认 |
|------|------|
| **名单生效** | **异步最终一致**前提下 **控制台承诺** **「保存成功」** **即** **可审计**；**读侧 SLA** **`design` 冻结** |
| **封禁联动 Pause** | **可选开关**；**默认** **不**自动全 Pause **以免**与 billing **混淆** |

---

**文档版本**：0.1.3 · **维护**：产品 + 合规 + 后台 owner · **本版**：§5 **onboarding** **邻域自检** **对齐 Agent 绑定页**（承 **0.1.2**）。
