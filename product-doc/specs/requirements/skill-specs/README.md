# Skill Specs（写路径操作契约 · SSOT）

**路径**：`specs/requirements/skill-specs/`。

**需求层闭环（A 阶段）**：[`requirements-closure.md`](./requirements-closure.md) — **DoD 勾选 · 追溯矩阵 · B 阶段开放项**。**Production Runtime（写路径读规范）**：[`production-runtime.md`](./production-runtime.md)。

**所属体系**：**[PRS](../prompt-runtime/README.md) L0**。**改什么去哪** → **[PRS §4](../prompt-runtime/README.md#prs-where-to-edit)**。

**用途**：满足 **`read_skill_operation_spec`**（**FR-T11** / **FR-AO04**）— 每笔 **A 类写** 在 **类型 A 之前** 须可解析的 **参数 / 校验 / 确认卡 / 缺槽 / 拒答**。**不是** SYSTEM Prompt（PRS **L1** `prompts/`）。

**登记 SSOT（行级）**：[`trade-assistance` §4/§8.2](../domains/agent/exchange-agent/trade-assistance.md)。

**模板**：[`TEMPLATE.md`](./TEMPLATE.md)。

---

## 1. 与 PRS / MNRA 分工

| 子系统 | 管什么 | 本目录 |
|--------|--------|--------|
| **PRS** | Prompt 拼装、Publish、Safety | **不** 替代 |
| **MNRA** | 读侧行情 Facts / phase / hints | **不适用** 写路径 |
| **Skill Specs（本篇）** | 写路径 **操作 syscall 手册** | **是** |

**编排顺序**：`read_skill_operation_spec` → 参数校验 → 类型 A → `call_exchange_write` — [`confirmation-flow` §1](../domains/agent/agent-orchestration/confirmation-flow.md)。

> **Prompt 运营包**：Publish 按 **`scenarioId` → `pp-*`**（[`governance-map`](../prompts/governance-map.md)）。Skill 正文可 **引用** `prompts/trading/buy.md` 等 **延展条文**，**≠** 须各发 `pp-trading-buy` / `pp-trading-sell`。

---

## 2. 状态定义（勿与「有条项」混淆）

| 状态 | 含义 | **能否** 作为 FR-T11 Publish 正文 |
|------|------|:----------------------------------:|
| **`contract-complete`** | 单文件 **§1～§6 自包含**；Runtime **无需** 再打开其它 `skill.*` | **能** |
| **`draft` / 骨架** | 仅元数据、「待补」「同窗 §X」、**无完整校验表** | **不能** |
| ~~`mvp-ready`~~ | **已弃用标签**（曾误标「增量引用稿」） | **勿用** |

**金样（评审对照）**：[`skill.spot.limit_order`](./spot/skill.spot.limit_order.md) — 五段式 + 缺槽禁 confirm + 拒答表 **均在同一文件**。

---

## 3. 目录与清单（S-01～S-09）

**Skill 清单（产品侧）**：[`product/prompt-governance-checklist.md`](../../../product/prompt-governance-checklist.md) **§五**。

| 编号 | `skillId` | 文件 | 状态 |
|:----:|-----------|------|------|
| S-01 | `skill.spot.flash_convert` | [`spot/skill.spot.flash_convert.md`](./spot/skill.spot.flash_convert.md) | **contract-complete** |
| S-02 | `skill.spot.limit_order` | [`spot/skill.spot.limit_order.md`](./spot/skill.spot.limit_order.md) | **contract-complete** |
| S-03 | `skill.futures.market_order` | [`futures/skill.futures.market_order.md`](./futures/skill.futures.market_order.md) | **contract-complete** |
| S-04 | `skill.futures.limit_order` | [`futures/skill.futures.limit_order.md`](./futures/skill.futures.limit_order.md) | **contract-complete** |
| S-05 | `skill.futures.take_profit_stop` | [`futures/skill.futures.take_profit_stop.md`](./futures/skill.futures.take_profit_stop.md) | **contract-complete** |
| S-06 | `skill.margin.cross_market_order` | [`margin/skill.margin.cross_market_order.md`](./margin/skill.margin.cross_market_order.md) | **contract-complete** |
| S-07 | `skill.margin.cross_limit_order` | [`margin/skill.margin.cross_limit_order.md`](./margin/skill.margin.cross_limit_order.md) | **contract-complete** |
| S-08 | `skill.wealth.subscribe` | [`wealth/skill.wealth.subscribe.md`](./wealth/skill.wealth.subscribe.md) | **contract-complete** |
| S-09 | `skill.wealth.redeem` | [`wealth/skill.wealth.redeem.md`](./wealth/skill.wealth.redeem.md) | **contract-complete** |

**暂缓**：`skill.spot.oco`、`skill.spot.bracket`（[`product.md` §非目标](../product.md)）；`skill.margin.transfer_*`（主站）— **仅** `FR-T05` 条文，**无** S-编号正文。

### 3.1 逻辑改单（`cancel`→`order`）

| `skillId` | 文件 | 状态 |
|-----------|------|------|
| `skill.spot.amend_limit_order` | [`spot/skill.spot.amend_limit_order.md`](./spot/skill.spot.amend_limit_order.md) | **contract-complete** |
| `skill.futures.amend_limit_order` | [`futures/skill.futures.amend_limit_order.md`](./futures/skill.futures.amend_limit_order.md) | **contract-complete** |

**抽检**：[`evals/skill-contract.md`](../evals/skill-contract.md)。

---

## 4. `scenarioId` ↔ `skill_spec`（写路径）

| `scenarioId` | `skillId` | Skill Spec |
|--------------|-----------|------------|
| `trade.spot.flash_convert` | `skill.spot.flash_convert` | [`spot/skill.spot.flash_convert.md`](./spot/skill.spot.flash_convert.md) |
| `trade.spot.limit_order` | `skill.spot.limit_order` | [`spot/skill.spot.limit_order.md`](./spot/skill.spot.limit_order.md) |
| `trade.futures.market_order` | `skill.futures.market_order` | [`futures/skill.futures.market_order.md`](./futures/skill.futures.market_order.md) |
| `trade.futures.limit_order` | `skill.futures.limit_order` | [`futures/skill.futures.limit_order.md`](./futures/skill.futures.limit_order.md) |
| `trade.futures.take_profit_stop` | `skill.futures.take_profit_stop` | [`futures/skill.futures.take_profit_stop.md`](./futures/skill.futures.take_profit_stop.md) |
| `margin.cross.market_order` | `skill.margin.cross_market_order` | [`margin/skill.margin.cross_market_order.md`](./margin/skill.margin.cross_market_order.md) |
| `margin.cross.limit_order` | `skill.margin.cross_limit_order` | [`margin/skill.margin.cross_limit_order.md`](./margin/skill.margin.cross_limit_order.md) |
| `wealth.subscribe` | `skill.wealth.subscribe` | [`wealth/skill.wealth.subscribe.md`](./wealth/skill.wealth.subscribe.md) |
| `wealth.redeem` | `skill.wealth.redeem` | [`wealth/skill.wealth.redeem.md`](./wealth/skill.wealth.redeem.md) |

**PRS**：[`registry`](../prompts/library/scenarios/registry.md) **写路径** 行 **`skill_spec`** 列。

---

## 5. 阅读顺序（建议）

1. **本篇 §2～§3**（状态 + 清单）  
2. **金样** [`skill.spot.limit_order`](./spot/skill.spot.limit_order.md)  
3. 按业务线抽查：现货 S-01～02、合约 S-03～05、全仓 S-06～07、理财 S-08～09  
4. [`production-runtime.md`](./production-runtime.md)（写路径读规范 · 观测 · Admin 协查）  
5. [`trade-via-agent`](../flows/trade-via-agent.md) · [`PRS`](../prompt-runtime/README.md)

---

## 6. Publish 与开放项

**Publish SSOT**：[`PUBLISH.md`](./PUBLISH.md) · [`manifest.yaml`](./manifest.yaml)

```bash
python3 specs/requirements/skill-specs/scripts/check_skill_contract_complete.py
```

| 项 | 说明 |
|----|------|
| **tick/step/minNotional** | 条文已写 **规则**；**数值** 须 symbol 元数据 / OpenAPI MR |
| **`conditionOrder` PATH** | S-05 已写 **TBD → FR-T05**；矩阵冻结后解除运行时闸 |
| **Runtime bundle** | **规格对齐** · [`published/runtime-bundle.json`](./published/runtime-bundle.json) |
| **Admin 原型** | **`/ai/tool-registry`** · 登记 + §1～§6 抽屉 + Enable（**非** Runtime Publish UI）· [`tool-registry-reconciliation`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) |
| **所内实现** | BFF / 编排 / Eval 真跑 — [`MR-B-BFF-IMPLEMENTATION.md`](./MR-B-BFF-IMPLEMENTATION.md) |

### 6.1 规格仓闭合状态（L0 正文）

**规格 + 原型已对齐（A）**：详见 [`requirements-closure.md`](./requirements-closure.md) **§3**（**所内实现** 见 **§4**）。

| 范围 | 状态 |
|------|------|
| **11 × `publishRequired` + 2 × amend** | **contract-complete** · CI `check_skill_contract_complete.py` |
| **OCO / Bracket / 划转** | **无正文**（产品边界 · 仅登记） |
| **Eval 条文** | [`evals/skill-contract.md`](../evals/skill-contract.md) **已登记**；**运行时抽检** → **SK-B03** |
| **Publish → Runtime** | **规格+原型已对齐** — [`PUBLISH` §7](./PUBLISH.md) · **所内** [`MR-B-BFF-IMPLEMENTATION.md`](./MR-B-BFF-IMPLEMENTATION.md) |

---

**文档版本**：1.6.2 · **维护**：产品 + Agent Runtime owner · **本版**：**§6 统一「规格+原型对齐」表述**。**承** 1.6.1。
