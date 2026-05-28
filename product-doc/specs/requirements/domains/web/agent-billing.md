# Web / H5 · Agent 账单（子账户语境）

**路径**：`specs/requirements/domains/web/agent-billing.md`。

**上级**：[`overview.md`](overview.md) · **计费真源**：[`../admin/billing-management/overview.md`](../admin/billing-management/overview.md)、[`../admin/billing-management/functions.md`](../admin/billing-management/functions.md)、[`flows/consume-and-bill.md`](../../flows/consume-and-bill.md)。

**契约映射（CC · `design/api`）**：[`overview.md` §4](overview.md)。

---

## 1. 目的

**归属**：**用户账单与权益均在交易所内部**；**主链** **`me/commerce`**（**配额/消耗/核销**）；[`billing-management`](../admin/billing-management/overview.md)、**`commerce-model`（商业分层 SSOT）** [`../admin/billing-management/commerce-model.md`](../admin/billing-management/commerce-model.md)。Telegram **Deeplink** **跳入交易所站内** UX，**不表示**计费栈迁出交易所。

在 **交易所主站 / H5**、**Agent 专用子账户（或等价用户语境）** 下，于 **`/subaccount/billing`（账单与消耗）** 提供 **Capability 配额**、**核销流水** 与 **消耗按月汇总**（**`me/commerce`**；**Token** **仅 Metering 明细维**，**非** 对客扣款单元）；支持 **CSV 导出**（**FR-B17～B20** / **FR-WEB09**）；窄屏下 **预加载 + 加载更多**。**不写** 账务 HTTP 字段表（见 **billing overview §0 · §7**、[`admin-console-web-billing-reconciliation` §0](admin-console-web-billing-reconciliation.md)）。

---

## 2. 功能需求 · `FR-WEB07～11`

| ID | 需求摘要 | 约束与同窗 |
|----|----------|------------|
| **FR-WEB07** | **Agent 消耗/配额**入口：**当前订阅与 Capability 剩余**（**`me/commerce`**）+ **演进** **消耗明细/月度**（**主列 Capability/SKU**） | **FR-B17** 为主；**空态**须说明无订阅/无消耗 |
| **FR-WEB08** | 消耗明细须含 **场景/Capability 归因**（交易与非交易任务） | 与 **单次 `executionId` 核销** 一致 |
| **FR-WEB09** | 明细展示 **核销状态**、**执行 ID**（**纯数字** · §2.2）、**可选 Metering（Token）**；支持 **CSV** | **`me/commerce` 消耗导出** |
| **FR-WEB10** | **窄屏**：流水列表 **分页**采用 **预加载下一页 + 「加载更多」**（或等价：**下一页数据在后台就绪后再允许展开**），减少用户在移动网络下的 **二次等待**；**桌面宽屏**可保留 **经典分页器**（页码 / 总数）。 | breakpoint 与主站 H5 壳一致时可与 [`agent-onboarding.md`](agent-onboarding.md) §3 **同窗**；预加载失败须 **可重试**，不得静默丢页。 |
| **FR-WEB11** | **账单码 / 余额不足** 等用户可见状态与 **billing `billCode`**、**FR-B07** 等 **同窗话术族**；列表加载中与导出中须有 **明确加载态**，避免重复提交。 | 与 **INSUFFICIENT_BALANCE** 等族 **一致**；详细码表 **OpenAPI MR** 回填，本篇只绑 **UX 下限**。 |

---

## 2.1 Phase 2 · 订阅与 Capability 配额（`FR-B17～B21`）

**契约**：[`user/commerce-me.yaml`](../../openapi/user/commerce-me.yaml) **`GET …/me/commerce/entitlements/summary`**；**商业 SSOT** [`../admin/billing-management/commerce-model.md`](../admin/billing-management/commerce-model.md)。

| ID | 需求摘要 | UX 下限 |
|----|----------|---------|
| **FR-B17** | **档位与 Capability 配额**可读：当前订阅、各 Capability **剩余额度**、加购包余额（**主站/H5** 摘要区或独立模块） | **空态**须说明「无订阅 / 无加购包」；**不得** **仅**展示 Token 流水 **而无** **配额上下文**（与 **演进主列 Capability** 叙事一致） |
| **FR-B18** | **加购包** **入账后** **额度** **须** **在摘要中可见**（**不含** PSP 支付流程 — **延后 design MR**） | 买包入口 **Deeplink** **可占位**；**到账前** **不得** **展示为已生效额度** |
| **FR-B19** | **配额用尽**：**阻断**对应 Capability **可计费执行**；**`FR-T05`** **引导升级 / 买包** | **与** **余额不足** **分开展示**（**不同 `billCode`/文案族**）；**禁止** **静默降级为套餐外按量后付** |
| **FR-B20** | **流水/月度**：**主展示** **Capability / SKU 归因**；Token **为明细列** | **FR-WEB07～09** **扩展**；CSV **宜含** **`capabilitySkuId` 或对用户等价标签** |
| **FR-B21** | **负向**：**默认不包含** **订阅周期外按单价实时累积、事后从子账户划扣** **作为主计费模式** | 产品文案 **不得** **暗示** **「超量自动扣 Token」** **为默认** |

### 2.1.1 验收 · `SC-WEB-14～15`（Phase 2 · 与 FR-B17/B19 同窗）

**编号**：**`SC-WEB-12`** **保留给** [`agent-onboarding.md`](agent-onboarding.md) **（UID≠`subUid`）**；本篇 **配额** **用** **`SC-WEB-14～15`**。

| ID | Given / When / Then |
|----|---------------------|
| **SC-WEB-14** | **Given** 用户有有效订阅与加购包 · **When** 打开账单/配额摘要 · **Then** **可见** **至少一条 Capability 剩余额度** **与** **订阅档位标识**（**与** **`commerce-me` 摘要** **语义一致**）。 |
| **SC-WEB-15** | **Given** 某 Capability **剩余为 0** · **When** 用户从 Telegram 或 H5 **触发须消耗该 Capability 的动作** · **Then** **可见** **升级/买包引导**（**非** **仅** **INSUFFICIENT_BALANCE** **若 Token 仍充足**）。 |

---

## 2.2 执行 ID（`executionId` · 用户可见列）

**SSOT**：[`standards/naming-standard.md`](../../standards/naming-standard.md) **§1** · OpenAPI **`ExecutionId`**（[`identity-schemas.yaml`](../../../openapi/components/identity-schemas.yaml)）。

| 规则 | 说明 |
|------|------|
| **字符集** | **仅** `0-9` |
| **长度** | **10～19** 位（字符串，**禁止**前导 `+` / 科学计数） |
| **列名** | 用户 H5/主站账单：**「执行 ID」**；JSON 字段 **`executionId`**（与运营/Runtime **join**） |
| **演示** | 建议 **`YYYYMMDDHHmmss` + 3 位序列**（17 位） |

**禁止**：`exec-*` slug、UUID/ULID、含字母或连字符的混排 ID **作为对客展示值**。

---

## 3. 响应式与触控（横切 · 与开通页同窗）

- **窄屏单手**：表格横向滚动或列折叠策略 **不得** 隐藏 **消耗金额** 与 **场景类型** 同时不可达（至少其一在主屏可视或通过一步展开可达）。  
- **触控**：分页或「加载更多」操作区满足 **粗指针** 可点下限；**避免** 底栏与安全区重叠导致误触。  
- **预加载语义**：向研发/测试声明的预期为 — **用户点击「加载更多」时，下一页数据应已在客户端就绪**（由后台分页接口或 BFF 聚合实现）；原型可用延时模拟。

---

## 4. 验收 · `SC-WEB-07～11`

| ID | Given / When / Then |
|----|---------------------|
| **SC-WEB-07** | **Given** 用户有订阅/消耗待展示 · **When** 打开消耗页 · **Then** 可见 **配额摘要（`me/commerce`）** + **消耗明细/月度**（或清晰 Tab），**Capability/SKU** **与核销状态可读**。 |
| **SC-WEB-08** | **Given** 消耗含交易与非交易任务 · **When** 用户浏览 **Capability/场景** 列 · **Then** **至少一条**非交易类与 **至少一条**交易类 **可同时** 被识别。 |
| **SC-WEB-09** | **Given** 用户具备导出权限 · **When** 点击导出 CSV · **Then** 文件下载且 **列齐全**（含 Capability/SKU、核销状态、**执行 ID**（纯数字 `executionId`）；**可选** Token Metering）；编码可读。 |
| **SC-WEB-10** | **Given** 窄屏且流水超一页 · **When** 系统完成下一页预加载 · **Then** 「加载更多」 **由禁用/加载态变为可点**，点击后 **立即追加** 新行 **无二次等待**（在正常网络下）；失败时出现 **重试**。 |
| **SC-WEB-11** | **Given** 配额用尽或核销拒绝 · **When** 用户从消耗页或关联入口查看说明 · **Then** 文案与 **`billCode` 族** **无矛盾**（**配额用尽** **与** **交易 USDT 不足** **分开展示**）。 |

---

## 5. 原型实现（`src/Web` · 非生产 SSOT）

**对齐 SSOT**：[`admin-console-web-billing-reconciliation.md`](admin-console-web-billing-reconciliation.md) **§0**。

| 路由 | 说明 |
|------|------|
| `/subaccount/billing` | **账单与消耗**（页眉）：页顶 **配额摘要（FR-B17）** + Tab **核销流水 / 月度 Capability** |
| `/subscription` | **订阅与购买**（升级/买包入口；配额详情链主账单） |
| `/subscription/upgrade` · `/pack` · `/checkout` | 选品 + **加密货币支付**演示（FR-B18 · PSP 量产 MR）；见 **§5.1** |
| `/subaccount/agent-billing` · `/billing/summary` | **重定向** → `/subaccount/billing` |

**Deeplink SSOT**：[`commerce-deeplink.md`](commerce-deeplink.md)（终态路径 **`/subaccount/billing`**）· **Staging**：[`staging-me-commerce-runbook.md`](staging-me-commerce-runbook.md)。

同窗 README：[`src/Web/README.md`](../../../../src/Web/README.md)。

### 5.1 Crypto 结账（演示 · 非 PSP 量产）

| 项 | 说明 |
|----|------|
| **路由** | `/subscription/checkout?kind=upgrade\|pack&sku=` |
| **组件** | `SubscriptionCheckoutPage` · `CryptoPaymentPanel` |
| **订单号** | **纯数字 14～20 位** · `src/Web/src/lib/commerceOrderId.ts`（同窗 Admin `commerceOrderId.ts`） |
| **用户支付地址** | `COMMERCE_RECEIVE_ADDRESSES` · 按网络展示完整地址 · **可复制** |
| **运营对读** | Admin **`/billing/operations?tab=orders`** 详情 **`paymentAddress`** 同窗地址族 |

### 5.2 原型文件索引（`src/Web` · 与 §0 同窗）

| 路径 | 职责 |
|------|------|
| `pages/subaccount/BillingPage.tsx` | 主账单 · Tab **核销流水 / 月度汇总** |
| `pages/subaccount/AgentBillingPage.tsx` | 旧路由 / `intent` / `start` 重定向 |
| `components/billing/CommerceQuotaOverview.tsx` | 配额摘要（**无**自动续费） |
| `components/billing/CommerceConsumptionLedger.tsx` | 核销流水 · CSV · 窄屏预加载 |
| `components/billing/CommerceMeteringMonthlyCard.tsx` | 月度 Capability 汇总 |
| `copy/agentBillingCopy.ts` · `subscriptionCopy.ts` | 页眉 **账单与消耗** 等文案 |
| `data/meCommerceConsumptionMock.ts` | 演示流水 · **纯数字 `executionId`** |
| `lib/commerceDeeplink.ts` · `lib/executionId.ts` | Deeplink · ID 校验 |
| `lib/commerceOrderId.ts` · `data/commercePaymentAddresses.ts` | 结账订单号 · 用户支付地址 |
| `pages/subscription/*` · `hooks/useCryptoCheckout.ts` | 订阅购买 · Crypto 结账 |
| `layout/WebShell.tsx` | 侧栏/底栏 **账单与消耗** |

---

**文档版本**：1.3.2 · **维护**：产品 + 主站/H5 触点 owner · **本版**：**SC-WEB-14～15**（**SC-WEB-12** 归 onboarding）。**承** **1.3.1**。
