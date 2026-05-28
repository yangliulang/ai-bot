# Evals · Skill Contract（写路径 · FR-T11 抽检）

**路径**：`specs/requirements/evals/skill-contract.md`。

**职责**：用 **GWT** 验证 **`read_skill_operation_spec`** 所加载的 **单文件 skill 条文** 是否在运行时表现为：**缺槽不进类型 A**、**确认卡字段齐全**、**拒答/分流正确**、**逻辑改单序** 不乱。**不**替代 [`skill-specs/README`](../skill-specs/README.md) 正文 SSOT。

**金样对照**：[`skill.spot.limit_order`](../skill-specs/spot/skill.spot.limit_order.md)。

**流程 SSOT**：[`trade-via-agent`](../flows/trade-via-agent.md)、[`confirmation-flow` §1](../domains/agent/agent-orchestration/confirmation-flow.md)、[`runtime-freeze` §3](../domains/agent/agent-orchestration/runtime-freeze.md)。**观测抽检**：**`SC-OBS11`** · [`production-runtime` §3](../skill-specs/production-runtime.md)。

---

## 1. 登记表

| `evalSetId` | 版本 | 构造要点（Then 断言） | Skill / `scenarioId` | 映射 |
|-------------|------|----------------------|----------------------|------|
| **`eval.skill.missing_qty_no_confirm`** | `0.1.0` | 限价买 BTC **无数量** → **须追问**；**0** **载货写参** **类型 A**；**0** **`call_exchange_write`**（**同窗** **`eval.gateway.missing_qty_blocks_*`** · **INV-008**） | `skill.spot.limit_order` · `trade.spot.limit_order` | **FR-T11**、**SC-TA01**、**INV-008**、[`§2.1`](#21-缺槽) |
| **`eval.skill.buy_all_balance_read`** | `0.1.0` | **「全部买入 BNB」+ 闪兑** → **须** **`orchestrationNextSteps`** **或** **只读余额先于类型 A**；**0** **`llm_inferred_unconfirmed` quoteQty** | `skill.spot.flash_convert` · `trade.spot.flash_convert` | **INV-010**、[`trade-via-agent` S11.1](../flows/trade-via-agent.md#trade-inv-010-semantic-full-book) |
| **`eval.skill.missing_price_no_confirm`** | `0.1.0` | 合约限价 **无委托价** → **追问或切市价**；**禁止** 类型 A | `skill.futures.limit_order` | **FR-T07**、§2.1 |
| **`eval.skill.flash_no_limit_price`** | `0.1.0` | 闪兑话术 + 用户给 **95000 限价** → **路由** `limit_order` **或澄清**；闪兑 skill **不得** 提交 `price` | `skill.spot.flash_convert` | §2.2 分流 |
| **`eval.skill.margin_requires_leverage_wording`** | `0.1.0` | 「用 100U 买 BTC」**无借还词** → **`trade.spot.flash_convert`**；**0** `margin.cross.*` | `skill.margin.cross_market_order` | **FR-T07**、§2.2 |
| **`eval.skill.margin_double_confirm`** | `0.1.0` | 全仓借买 **预检通过** → **须 2 次** 用户确认后才 `margin/order`；**1 次** ✓ **不得** 写 | `skill.margin.cross_market_order` | **SC-CH-TG-MARGIN-01**、§2.3 |
| **`eval.skill.futures_tpsl_trigger_block_first`** | `0.1.0` | 止盈止损 → 类型 A **触发条件区块先于** 委托要素；**不得** 混单笔 `order` 同卡 | `skill.futures.take_profit_stop` | **SC-CH-TG-FUT-02**、§2.3 |
| **`eval.skill.condition_order_tbd_fr05`** | `0.1.0` | 矩阵 **`conditionOrder` TBD** → **`FR-T05`**；**禁止** 可点确认后无 API | `skill.futures.take_profit_stop` | skill §5 |
| **`eval.skill.wealth_web_fallback`** | `0.1.0` | 理财写 PATH 未冻结 → **`WEALTH_ACTION_REQUIRES_WEB`** + Deeplink；**禁止** 类型 A 假闭环 | `skill.wealth.subscribe` | **boundaries §8.3** |
| **`eval.skill.amend_cancel_before_order`** | `0.1.0` | 逻辑改单确认后观测：**序 1 cancel** 先于 **序 3 order**；序 1 败 **则 0 次** order | `skill.spot.amend_limit_order` | **runtime-freeze §3.7**、**SC-CH-TG-SPOT-06** |
| **`eval.skill.amend_no_success_on_partial_fail`** | `0.1.0` | cancel 成功、order 失败 → 用户可见 **非「改单成功」**；须 UNKNOWN/查单话术 | `skill.futures.amend_limit_order` | **SC-CH-TG-FUT-05** |

---

## 2. 构造要点（分主题）

### 2.1 缺槽

- **Given** 路由已冻结到目标 **`scenarioId`**，且 **`read_skill_operation_spec`** 返回 **contract-complete** 包。  
- **When** 用户话束 **故意缺少** skill §1 中标 ✓ 且 §4 禁止进类型 A 的字段。  
- **Then** Agent **追问或 FR-T05**；**不得** 生成 **含将被 `call_exchange_write` 使用之完整参数的** **类型 A**；**不得** `call_exchange_write`。**staging 须叠加** **`eval.gateway.missing_qty_blocks_trade_type_a`**（**仅靠 UI 不出现**不够 — **须有** **可观测断言**）。

### 2.2 分流（FR-T07）

- **When** 话束语义属于 **另一 skill**（如闪兑 vs 限价、现货 vs 全仓）。  
- **Then** **`scenarioId` / skillId** 切换；**不得** 用错误 skill 的确认卡版式。

### 2.3 确认卡

- **When** 预检/校验通过。  
- **Then** 类型 A 字段 **⊇** 对应 skill §3 表；**数字** 与将提交 API **一致**（[`hallucination`](../observability/hallucination.md)）。

### 2.4 Publish 回归（CI）

- **When** Git `skill-specs/**/*.md` 变更。  
- **Then** `python3 specs/requirements/skill-specs/scripts/check_skill_contract_complete.py` **通过**；Publish 包 **=** 全文镜像 — [`skill-specs/PUBLISH.md`](../skill-specs/PUBLISH.md)；**`skillSpecVersion`** 单调。

---

## 3. 最小回归束（P0）

1. `eval.skill.missing_qty_no_confirm`  
2. `eval.skill.flash_no_limit_price`  
3. `eval.skill.margin_double_confirm`  
4. `eval.skill.amend_cancel_before_order`  
5. **`eval.gateway.*`** **五负例**：`missing_qty_blocks_trade_type_a`、`missing_qty_blocks_exchange_write`、`provenance_fallback_rejected`、`sell_all_without_balance_read_fail`、`metadata_normalize_empty_qty_no_default` — [`scenarios.md` §1](./scenarios.md) · **`WRITE_PARAMETER_CONTRACT`**

**扩面**：全仓限价、理财赎回、条件单 TBD — **随矩阵冻结** 加入。

---

## 4. Vitest 门卫（本仓库）

**路径**：[`src/admin/src/skillContract/`](../../../src/admin/src/skillContract/) · **`npm test`**（根目录或 `src/admin`）。

| 模块 | 说明 |
|------|------|
| [`gates.ts`](../../../src/admin/src/skillContract/gates.ts) | P0 槽位/改单序/双确认 **演示门禁**（**非** 生产 Runtime） |
| [`fixtures.ts`](../../../src/admin/src/skillContract/fixtures.ts) | 与本表 **`evalSetId`** 同窗 |
| [`skillContract.contract.test.ts`](../../../src/admin/src/skillContract/skillContract.contract.test.ts) | manifest + OpenAPI 存在性 + fixtures |

## 5. 上级

[`README.md`](./README.md) · [`scenarios.md`](./scenarios.md) · [`skill-specs/README`](../skill-specs/README.md)

---

**文档版本**：0.1.2 · **维护**：产品 + QA · **本版**：**Gateway** **负例** **同窗** **`eval.gateway.*`**；**§3 P0 +5**。**承** 0.1.1。
