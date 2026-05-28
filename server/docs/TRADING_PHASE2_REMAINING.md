# 交易场景 Phase 2 — 剩余工作与分步交付

对照 [`product-doc/product/roadmap.md`](../../product-doc/product/roadmap.md)（交易写路径见 specs / 遗留 [`development-roadmap.md`](../../product-doc/development-roadmap.md) §2）与运行时寄存器 [`orchestration_flow_catalog.py`](../chainup_agent/application/orchestration_flow_catalog.py)。

## 现状总览（2026-05-25）

| 阶段 | 场景 | 服务端 readiness | HTTP 写/读 | Telegram | TRADING Prompt |
|------|------|------------------|------------|----------|----------------|
| **2.1** | `trade.spot.flash_convert` | ready | ✅ | ✅ | ✅ 0018 |
| **2.1** | `trade.spot.limit_order` | ready | ✅ | ✅ | ✅ 0018 |
| **2.2** | `trade.spot.open_orders` / `cancel_order` | ready | ✅ | ✅ 撤单直调 | — |
| **2.3** | `trade.futures.market_order` / `limit_order` | ready | ✅ | ✅ | ✅ 0023 |
| **2.3** | `trade.futures.cancel_order` | ready | ✅ `POST …/cancel` | ✅ `EXECUTE_FUTURES_CANCEL` | — |
| **2.4** | `margin.cross.market_order` / `limit_order` | ready | ✅ | ✅ 双确认 | ✅ 0024 |
| **2.5** | `automation.condition_order` | ready | ✅ 创建 | ✅ 类型 A · `cop`/`cox` | ✅ 0025 |
| **2.5** | `automation.condition_orders_read` | ready | ✅ `GET …/condition-orders` | ✅ 只读列表 | — |
| **2.5** | `automation.condition_order_cancel` | ready | ✅ `POST …/cancel-condition` | ✅ 类型 A · `ccp`/`ccx` | — |
| **2.x** | `trade.spot.amend_limit_order` | ready | ✅ | ✅ | ✅ 0026 |
| **§6** | `trading.reconcile`（504/UNKNOWN） | ready | ✅ `POST|GET …/trading/reconcile` | —（HTTP 联调） | — |
| 产品扩展 | `trade.spot.oco` / `bracket` | **stub** | CC-P1-01 冻结 · FR-T05 | — | — |

只读 / 闲聊（`read.*`、`wealth.holdings_read`、`chat.faq`）已在 Phase 1 交付。

---

## 分步计划

### Step 2.3a — 合约 HTTP 写（**本轮**）

- `POST /api/v1/agent/trade/futures/order` → Coobit `POST /fapi/v1/order`
- `CHAINUP_AGENT_FEATURE_AGENT_FUTURES`（默认 `true`，与现货开关对称）
- 意图策略：`trade.futures.*` 槽位齐全 → `CONFIRM_TYPE_A`（HTTP 可直接写；TG 暂提示联调路径）
- 寄存器 `readiness=ready`

**验收**：`pytest server/tests/test_futures_trade.py`；绑定用户 HTTP 200/400 与 timeline `trading.exchange_private`。

### Step 2.3b — 合约 Telegram Type-A（**已完成**）

- `telegram_flash_pending.py`：`ump`/`umx`（市价）、`ulp`/`ulx`（限价）+ pending 表
- `telegram_bound_reply` · `CONFIRM_TYPE_A`：`trade.futures.market_order` / `limit_order`
- 确认规则 `confirmation_rules_evaluate`（`futures` key）
- 可选 LLM preamble：`CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_FUTURES_MARKET_CONFIRM` / `…LIMIT_CONFIRM`

### Step 2.3c — 合约 TRADING Prompt 种子（**已完成**）

- Alembic **`0023`**：`pack_trading_futures_market_order_v1`、`pack_trading_futures_limit_order_v1`
- `TRADING_PROMPT_ASSEMBLY_SCENARIO_IDS` 已扩展

### Step 2.4 — 全仓杠杆（**已完成**）

- `POST /api/v1/agent/trade/margin/order` → Coobit `POST /sapi/v2/margin/order`
- `CHAINUP_AGENT_FEATURE_AGENT_MARGIN`（默认 `true`）
- 寄存器 **`margin.cross.market_order` / `margin.cross.limit_order`** · `readiness=ready`
- Telegram **双确认**：`xm1/xm2`（市价）、`xl1/xl2`（限价）
- Alembic **`0024`** TRADING 种子

### Step 2.5 — 条件单（**已完成 · 含查/撤**）

- `POST /api/v1/agent/trade/futures/condition-order` → Coobit `POST /fapi/v1/conditionOrder`
- `GET /api/v1/agent/trade/futures/condition-orders` → `GET /fapi/v1/openOrders` + 条件单启发式筛选
- `POST /api/v1/agent/trade/futures/cancel-condition` → `POST /fapi/v1/cancel`
- `POST /api/v1/agent/trade/futures/cancel` → 合约普通撤单（`trade.futures.cancel_order`）
- 场景键 **`automation.condition_order`** / **`automation.condition_orders_read`** / **`automation.condition_order_cancel`**
- Telegram：创建 **`cop`/`cox`**；撤销 **`ccp`/`ccx`**；合约撤单 **`EXECUTE_FUTURES_CANCEL`**
- Alembic **`0025`** TRADING 种子 · `pack_trading_automation_condition_order_v1`
- 验收：`pytest server/tests/test_futures_cancel_condition_trade.py` · `test_condition_trade.py`

### Step 2.x — 现货改单 / OCO（**已完成改单 · OCO 仍 stub**）

- `POST /api/v1/agent/trade/spot/amend-limit-order` → Coobit **`POST /sapi/v2/cancel` → `POST /sapi/v2/order`**
- 场景键 **`trade.spot.amend_limit_order`**（CC-P0-02 逻辑改单）
- Telegram **类型 A**（`smp`/`smx` · 「确认修改」+ 新旧对比 + 先撤后挂披露）
- Alembic **`0026`** TRADING 种子 · `pack_trading_spot_amend_limit_order_v1`
- **`trade.spot.oco` / `trade.spot.bracket`**：寄存器 **`stub`** · 意图 **`STUB_NOT_EXECUTABLE`**（CC-P1-01 PATH 未冻结）

### Step §6 — 504/UNKNOWN 对账（**已完成**）

- **`POST /api/v1/agent/trading/reconcile`**、**`GET …/reconcile/status`**
- 复用改单 **`CANCEL_SUCCEEDED_REPLACE_FAILED`**（**`AGENT_SPOT_AMEND_CANCEL_SUCCEEDED_REPLACE_FAILED`**）+ 时间线 **`exchangeOutcome=unknown`**
- 查单：现货 **`GET /sapi/v2/order`**（**`fetch_signed_spot_order_json`**）、合约 **`GET /fapi/v1/order`**
- 改单失败 **`details.reconcileSuggested`** / **`reconcilePath`**
- 验收：**`pytest tests/test_trading_reconcile.py`**

**后续（非 P0）**：所有 **`post_signed_*` 写** 在 HTTP **504** 时统一 **`AGENT_EXCHANGE_WRITE_UNKNOWN`** + 时间线 **`exchangeOutcome=unknown`**（当前以查单/改单/部分 TG callback 为主）。

---

## 关键文件索引

| 能力 | 文件 |
|------|------|
| 寄存器 | `application/orchestration_flow_catalog.py` |
| 意图裁决 | `application/agent_intent_pipeline.py` |
| 现货写（模板） | `application/agent_spot_trade.py` |
| 合约写 | `application/agent_futures_trade.py` |
| 条件单写 | `application/agent_futures_condition_trade.py` |
| §6 对账 | `domain/trading_reconcile.py` · `application/agent_trading_reconcile.py` · `api/routers/v1/agent_trading_reconcile.py` |
| OpenAPI 签名 | `infrastructure/exchange/coobit_openapi.py` |
| TG 编排 | `application/telegram_bound_reply.py` |
| 环境开关 | `core/config.py` |

---

## 建议优先级（排除计费/绑定）

产品侧排期见 [`product-doc/product/roadmap.md`](../../product-doc/product/roadmap.md) 与 [`closure-completion-matrix.md`](../../product-doc/specs/requirements/closure-completion-matrix.md)（P0 对账已交付；后续按 **W1** / **P‑01～P‑08** 派工）。
