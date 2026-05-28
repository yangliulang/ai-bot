# Prompt 治理清单（产品侧 · 非 SSOT）

**用途**：运营与产品对齐「要写哪些 Prompt 包、优先级与 Skill 对照」。**不**替代契约；条文与发布 SSOT 见 [`specs/requirements/prompts/README.md`](../specs/requirements/prompts/README.md)、[`prompt-management`](../specs/requirements/domains/admin/prompt-management/overview.md)。

**2026-05 升级说明**：已删除旧版根目录 `Prompt/Prompt List.md`（P-01～P-21 派工表）。新模型为 **按 `scenarioId` 的 TRADING 包 + 统一 ANALYSIS 包 + SYSTEM 运行时块**；正文只写 LLM **认知与行为**，不写 Gateway / Billing / Canonical。

---

## 一、与规格 SSOT 的关系

| 说明 | 链接 |
|------|------|
| **Git 条文七目录 + library** | [`specs/requirements/prompts/`](../specs/requirements/prompts/README.md) |
| **`scenarioId` ↔ `promptPackId` 映射（规格索引）** | [`specs/requirements/prompts/governance-map.md`](../specs/requirements/prompts/governance-map.md) |
| **写路径按场景速查** | [`specs/requirements/prompts/trading/by-scenario.md`](../specs/requirements/prompts/trading/by-scenario.md) |
| **`scenarioId` 拼装表** | [`library/scenarios/registry.md`](../specs/requirements/prompts/library/scenarios/registry.md) |
| **发布后治理 / 拼装** | [`prompt-management/overview`](../specs/requirements/domains/admin/prompt-management/overview.md)、[`runtime-injection`](../specs/requirements/domains/admin/prompt-management/runtime-injection.md) |
| **Admin Demo 正文模板（六段结构）** | [`src/admin/src/data/promptBodyTemplates.ts`](../src/admin/src/data/promptBodyTemplates.ts) |
| **Library 拼装 vs Publish** | [`specs/requirements/prompts/library/PUBLISH-ALIGNMENT.md`](../specs/requirements/prompts/library/PUBLISH-ALIGNMENT.md) |
| **关单与 AC-09** | [`closure-remaining.md`](../specs/requirements/closure-remaining.md) |

---

## 二、正文写法（统一六段）

每份运营 Prompt 包正文建议结构（与 Demo 模板一致）：

1. **Identity** — 全局身份，不含具体交易细则  
2. **Scenario Context** — 当前 `scenarioId` / 场景语义  
3. **Behavioral Rules** — 必须澄清什么、禁止什么  
4. **Capability Awareness**（可选）— 写/读操作边界  
5. **Clarify Rules**（可选）— 缺参时如何问  
6. **Output Contract**（可选）— clarify / intent 输出边界  

**不要写进 Prompt**：Tool API、Billing、Gateway、Canonical Schema、余额校验实现。

---

## 三、发布包清单（Admin 对齐 · 16 包）

### SYSTEM（3）

| `promptPackId` | 说明 |
|----------------|------|
| `pp-system-core` | 全局行为原则 |
| `pp-runtime-clarify` | 澄清规则 |
| `pp-runtime-output-contract` | 结构化输出契约 |

### SAFETY（1）

| `promptPackId` | 说明 |
|----------------|------|
| `pp-safety-global` | 安全防护块 |

### ANALYSIS（1 · 不按主题拆包）

| `promptPackId` | 说明 |
|----------------|------|
| `pp-analysis-core` | 所有只读分析/监控对话共用；能力清单见运行场景与 Registry，**不**再建 `pp-analysis-market-*` 等 |

### TRADING（11 · 按写路径 `scenarioId`）

| `promptPackId` | `scenarioId`（主） |
|----------------|-------------------|
| `pp-trading-spot-limit` | `trade.spot.limit_order` |
| `pp-trading-spot-flash` | `trade.spot.flash_convert` |
| `pp-trading-spot-amend` | `trade.spot.amend_limit_order` |
| `pp-trading-futures-market` | `trade.futures.market_order` |
| `pp-trading-futures-limit` | `trade.futures.limit_order` |
| `pp-trading-futures-amend` | `trade.futures.amend_limit_order` |
| `pp-trading-futures-tpsl` | `trade.futures.take_profit_stop` |
| `pp-trading-margin-market` | `margin.cross.market_order` |
| `pp-trading-margin-limit` | `margin.cross.limit_order` |
| `pp-trading-wealth-subscribe` | `wealth.subscribe` |
| `pp-trading-wealth-redeem` | `wealth.redeem` |

**确认链 / 风险披露**：叙事条文仍在 [`prompts/confirmation/`](../specs/requirements/prompts/confirmation/README.md)，由 Runtime 拼装注入，**不**单独占运营「场景包」编号。

---

## 四、旧派工表 → 新模型（对照）

| 已废弃做法 | 现行做法 |
|------------|----------|
| P-09～P-12 四个分析 Prompt 包 | 仅 `pp-analysis-core` + 能力 Registry |
| P-05 / P-06 按 buy/sell 各发一包 | 按 `scenarioId` 发 TRADING 包（side 在场景内表达） |
| P-01～P-04 意图各一包 | 意图由路由/Runtime；Prompt 只写场景行为 |
| 根目录 `Prompt/Prompt List.md`（已删） | 本篇 + `prompts/` 条文 |

`specs/requirements/prompts/trading/buy.md` 等 **Git 条文** 仍作评审下限与 skill 延展引用，**≠** 须拆成多个发布包。

---

## 五、Skill 操作规范（MVP）

写路径须与 [`skill-specs/`](../specs/requirements/skill-specs/README.md) 同窗发布。MVP 清单：

| Skill ID | 规格路径 |
|----------|----------|
| `skill.spot.flash_convert` | `skill-specs/spot/skill.spot.flash_convert.md` |
| `skill.spot.limit_order` | `skill-specs/spot/skill.spot.limit_order.md` |
| `skill.spot.amend_limit_order` | `skill-specs/spot/skill.spot.amend_limit_order.md` |
| `skill.futures.market_order` | `skill-specs/futures/skill.futures.market_order.md` |
| `skill.futures.limit_order` | `skill-specs/futures/skill.futures.limit_order.md` |
| `skill.futures.amend_limit_order` | `skill-specs/futures/skill.futures.amend_limit_order.md` |
| `skill.futures.take_profit_stop` | `skill-specs/futures/skill.futures.take_profit_stop.md` |
| `skill.margin.cross_market_order` | `skill-specs/margin/skill.margin.cross_market_order.md` |
| `skill.margin.cross_limit_order` | `skill-specs/margin/skill.margin.cross_limit_order.md` |
| `skill.wealth.subscribe` | `skill-specs/wealth/skill.wealth.subscribe.md` |
| `skill.wealth.redeem` | `skill-specs/wealth/skill.wealth.redeem.md` |

暂缓：`skill.spot.oco`、`skill.spot.bracket`、主站转账类 — 见 [`closure-remaining`](../specs/requirements/closure-remaining.md)。

---

## 六、建议优先级

| 优先级 | 内容 |
|--------|------|
| P0 | `pp-system-core`、`pp-runtime-clarify`、`pp-runtime-output-contract`、`pp-safety-global` |
| P0 | 意图路由联调用的首条写路径：`pp-trading-spot-limit` + `skill.spot.limit_order` |
| P1 | 其余 TRADING 包 + `pp-analysis-core` |
| P1 | `prompts/confirmation/*` 条文与 Telegram 卡片对齐 |
| P2 | `prompts/shared/*` 术语与格式；`prompts/safety/*` 与 Publish 扫闸 |

---

*维护：产品 + Prompt owner · 与 Admin Demo [`mockPromptData.ts`](../src/admin/src/data/mockPromptData.ts) 同步修订。*
