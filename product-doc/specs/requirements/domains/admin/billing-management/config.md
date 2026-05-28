# Billing Management · 配置与 IA

**域叙事**：[`overview.md`](overview.md)；**模块五 FR 表**：[`functions.md`](functions.md) §2。

## 1. 环境与健康

| Env / 标识 | 说明 |
|------------|------|
| `BILLING_MODE` | **`shadow`** **\|** **`enforce`** · 同窗 [`keys` §5](../trading-agent-config/keys.md) |
| **`PHASE2_COMMERCE_RAILS_ENABLED`** | **`false` 默认** · 启用后 Runtime/BFF **可走轨 B HTTP**；**不**扩写 **CC-P0-03** — [`commerce-model` §5.2](commerce-model.md) |

## 2. IA（与 **FR-MC501～508** · **FR-MC509～512（规划）** 对位）

**运营台 IA · 轨 B 梳理 SSOT**：[`admin-console-billing-pages-reconciliation.md`](admin-console-billing-pages-reconciliation.md)（**§0 对齐快照** · 历史四页归档 · P0～P3）。

**运营台侧栏（`admin-console` / `src/admin`）** — **三项**（Demo 简化 IA）：

| 入口 | 路由 | 职责 |
|------|------|------|
| 计费总览 | `/billing/overview` | **运行健康**（MC501/506/512 摘要）· 商业运营入口（**无**运营台 MC502 定价 Tab） |
| 商业运营 | `/billing/operations` | Tab：**订阅套餐** \| **资源管理** \| **计费规则** \| **订阅订单** \| **用户消耗** |
| 执行核销追踪 | `/billing/ledger` | MC503/504 · 按 execution |

`/billing` → overview；旧路径（`/billing/pricing`、`/billing/subscriptions` 等）**重定向**至上表对应 Tab。

**Phase 2（当前）**：

- **FR-MC512 演示**：**计费总览** 内 **配额阻断** Statistic（链 **商业运营**）；**FR-MC509 目录编辑** → **`/billing/operations?tab=rules`**（非独立 commerce 页）。
- **FR-MC509～510**：**Demo** 已提供 **目录 PATCH + 双签 Modal**（`CommerceCapabilityCatalogEditor` · **If-Match/409**）；**生产** IAM/审计流水 **所内 MR**。
- **Admin 可选接线**：`VITE_USE_BILLING_COMMERCE_API` / **`VITE_USE_BILLING_LEDGER_API`** + `VITE_API_BASE_URL`（`npm run dev` **BFF mock**）；**MR-BILL 走读** → [`staging-mr-bill-runbook.md`](staging-mr-bill-runbook.md)。

**执行账单**页内 **Tab**：账单列表（Runtime 主筛）· 单笔追踪；退款为表格多选 + 弹窗；异步导出 / 对账（MC507/508）见规格，控制台不占独立 Tab。低保真交互与空态/权限文案见 [`admin-console/page-specs.md`](../../admin-console/page-specs.md)「计费与账务」节。

| 控制台 Tab / 区 | **FR**（主承载） | 说明 |
|-----------------|-----------------|------|
| **概览 / 计费健康** | **FR-MC501**、**506** | **`BILLING_MODE`、`effectiveMinChargeUsdt`、`BILLING_TOKEN_RATE` 生效摘要**；网关失败 **`CHARGE_GATEWAY_ERROR`** |
| **定价 · Token 费率** | **FR-MC502** | **编辑 `BILLING_TOKEN_RATE`** · 双签 · `keys` MR · **Demo 无运营台 Tab** |
| **定价 · 最小扣费与其它** | **FR-MC502**（或全局 Tab，**ADR**） | **`effectiveMinChargeUsdt`、`BILLING_SETTLE_POLICY`** · **Demo 无运营台 Tab** |
| **流水 · 平台列表** | **FR-MC504** | 全站或按 **`userId`** 筛选；列表与 **FR-MC507** 导出 **同源** |
| **协查 · 单笔** | **FR-MC503** | **`userId`、`executionId`、`billingTraceId`**；跳转 **observability** |
| **冲正 / 退款工单** | **FR-MC505** | 审批队列 · [`flow.md`](flow.md)、[`rules.md`](rules.md) |
| **流水 / 月度 · 异步导出** | **FR-MC507** | 明细 CSV **与** 自然月 rollup（**同窗 FR-B16**）；水印见 [`rules.md`](rules.md) |
| **对账导出 / PSP 占位** | **FR-MC508** | **财务字段模板**、PSP **映射**只读 · §3 |
| **商业 · SKU / 映射矩阵** | **FR-MC509**（规划） | **套餐、Capability、`scenarioId`→扣额** 规则；**双签** **同窗** **Token 费率** |
| **商业 · 用户权益协查** | **FR-MC510**（规划） | **订阅、包余额、消耗**；**join `executionId`** |
| **商业 · 阻断健康** | **FR-MC512**（规划） | **配额用尽** 聚合；可 **并入** **FR-MC501** **同屏** |

**说明**：FR-MC506 可与 **FR-MC501** 同屏，由 **`design`/ADR**。

## 3. PSP / 网关展示边界

控制台 **不写** PSP 连接器实现代码；仅需 **枚举** PSP 映射字段（与 **`integrations`/payment-gateway** 同窗），供 **FR-MC508** **对签字段占位**。

---

**文档版本**：0.3.4 · **维护**：产品与后台 IA owner · **本版**：**商业运营五 Tab**（含计费规则）· 总览 **无** MC502 定价页。**承** **0.3.3**。
