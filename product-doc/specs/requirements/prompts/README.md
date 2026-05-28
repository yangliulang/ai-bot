# Prompts（Git 协作区 · MVP）

**范围**：**Telegram + Trading Agent + 基础 Runtime** — **不做** Prompt Platform 式多层治理。

**所属体系**：**[PRS（Prompt Runtime System）](../prompt-runtime/README.md)** — 本篇为 **L1 内容层**。**改什么去哪** → **[PRS §4 派工表](../prompt-runtime/README.md#prs-where-to-edit)**；**读侧行情（块 5）** → **[MNRA](../market-narrative-runtime/README.md)**（**勿** 用本目录 `analysis/*` 替代 Facts/phase）。

**契约 SSOT**：[`prompt-management/overview`](../domains/admin/prompt-management/overview.md)；**拼装 / Safety §7.1**：[`runtime-injection`](../domains/admin/prompt-management/runtime-injection.md)。  
**降级与枚举**：[`Runtime/fallback-policy.md`](../Runtime/fallback-policy.md) — **不设**独立 `prompts/fallbacks/`。

**书写**：[`standards/prompt-standard.md`](../standards/prompt-standard.md)。

**治理映射（`scenarioId` ↔ `promptPackId` ↔ 条文）**：[**`governance-map.md`](./governance-map.md)** · 产品清单 [`product/prompt-governance-checklist.md`](../../../product/prompt-governance-checklist.md)。

**文档版本约定**：子目录 **`README.md`**（索引导航）使用 **`1.x.0`**；场景条文（如 `system.md`、`trading/buy.md` 等）使用 **`1.x.0-mvp`**。**后缀不同不表示索引过期**，以本篇 §1 目录树与各文件脚是否一致为准。

---

## 1. 目录树（条文七件套 + `library`）

```text
prompts/
├── README.md
├── TEMPLATE-draft.md
├── library/                    # 完整可拼装提示词库（Git 镜像 · 对齐 prompt-management）
│   ├── README.md
│   ├── ASSEMBLY.md
│   ├── INITIAL_SYSTEM.zh-CN.md # 冷启动整段（L1+L2+L3）
│   ├── INITIAL_SYSTEM.en.md
│   ├── packs/
│   └── scenarios/
│       └── registry.md         # scenarioId → 片段配方（全表）
├── system/
│   ├── README.md               # Runtime Root 索引
│   └── system.md               # 全局：身份 / 边界 / Tool / 禁止项
├── intents/
│   ├── README.md               # 本目录索引
│   ├── trade.md
│   ├── analysis.md
│   └── monitoring.md          # 意图条文；无 monitoring/ 子树
├── governance-map.md           # scenarioId ↔ promptPackId ↔ 条文（索引 SSOT）
├── trading/
│   ├── README.md               # 写路径索引 · confirmation-flow / routing-engine
│   ├── by-scenario.md          # scenarioId → pp-trading-* 速查（P2）
│   ├── buy.md                  # 评审下限 · 同窗基准（≠ 独立 pp-trading-buy 包）
│   ├── sell.md                 # 评审下限 · 卖/减仓语义（≠ 独立发布包）
│   ├── futures.md
│   └── cancel.md
├── analysis/
│   ├── README.md               # 只读能力分卷索引（Publish = pp-analysis-core 一包）
│   ├── market-analysis.md     # 能力语义分卷 · 公开行情 / Funding / 盘口
│   ├── technical-analysis.md # 能力语义分卷 · 指标 / 形态
│   ├── sentiment-summary.md  # 能力语义分卷 · 舆情 / 情绪
│   └── portfolio-read.md     # 能力语义分卷 · 账户只读
├── confirmation/
│   ├── README.md               # 本目录索引
│   ├── order-confirmation.md
│   ├── risk-disclosure.md
│   └── high-risk-confirmation.md
├── safety/
│   ├── README.md               # SAFETY 索引 · §7.1 真源指向
│   ├── jailbreak.md
│   ├── privilege.md
│   └── illegal-request.md
└── shared/
    ├── README.md               # 术语 / 格式 / 话术锚 索引
    ├── glossary.md
    ├── response-format.md
    └── common-phrases.md
```

---

## 2. 治理双层（2026-05）

| 层 | 位置 | 读者 |
|----|------|------|
| **运营发布** | `promptPackId`（`pp-*`）· 六段正文 | 运营 · Admin 治理 · Publish |
| **Git 条文 + 拼装库** | 本篇 §1 七目录 + [`library/`](./library/README.md) | 研发 · 评审 · Skill 延展引用 |

- **写路径**：**一个 `scenarioId` → 一个 TRADING 包**（见 [`governance-map.md` §3](./governance-map.md#3-写路径--scenarioid--promptpackid)）；`trading/buy.md` **不是**「买单 Prompt 包」。  
- **读侧 / 监控**：**仅** `pp-analysis-core`；`analysis/*` 四卷为 **能力语义分卷**，见 [`governance-map.md` §4](./governance-map.md#4-读侧--监控--统一分析包)。  
- **`intents/*`**：拼装片段 + 路由语义，**非**各发独立 Publish 包。  
- **`confirmation/*`**：Runtime 拼装注入，**非**运营场景包编号。

---

## 3. MVP 原则

| 原则 | 说明 |
|------|------|
| **按 Runtime 场景分** | **不按**技术分包堆砌 |
| **核心两条** | **Intent**（[`intents/`](./intents/)）+ **Confirmation**（[`confirmation/`](./confirmation/)）决定理解与放行叙事 |
| **条文 vs 可粘贴库** | **七目录** **锁** **下限与评审**；[`library/README`](./library/README.md) **提供** **SYSTEM + 片段 + `scenarioId` 全表** **拼装入口**，发布仍以 **`prompt-management`** **为准** |
| **单根 System** | [`system/README`](./system/README.md) · [`system/system`](./system/system.md) **收敛全局**；Publish [`prompt-management`](../domains/admin/prompt-management/overview.md) |
| **事实 / 幻觉** | **无工具闭环不编造** — `system` §2、`trading/buy` §4、`analysis/*`（索引 [`analysis/README`](./analysis/README.md)）；[`safety/README`](./safety/README.md) · [`privilege`](./safety/privilege.md) |
| **Market Narrative · Memory** | **`system` §6**；[`common-phrases` §8](shared/common-phrases.md)；[`memory-runtime`](../Runtime/memory-runtime.md)；Walkthrough → [`e2e-closed-loop#runtime-walkthrough-crosscut`](../../flow/e2e-closed-loop.md#runtime-walkthrough-crosscut) |

---

## 4. 阅读顺序（建议）

**产品侧 Prompt 治理清单（非 SSOT）**：[**`product/prompt-governance-checklist.md`](../../../product/prompt-governance-checklist.md)（**16 包 · 六段正文**；旧 **`Prompt/Prompt List.md`** 已删除）。

0. [`governance-map.md`](./governance-map.md) → [`library/scenarios/registry.md`](./library/scenarios/registry.md)（**`scenarioId`** · 拼装 · **`promptPackId`**）  
1. [`system/README.md`](./system/README.md) → [`system/system.md`](./system/system.md) → [`confirmation/order-confirmation.md`](./confirmation/order-confirmation.md)  
2. [`intents/README.md`](./intents/README.md)（三路分流）→ [`trading/README.md`](./trading/README.md) 或 [`analysis/README.md`](./analysis/README.md)  
3. [`safety/README.md`](./safety/README.md) → [`shared/README.md`](./shared/README.md)（[`glossary`](./shared/glossary.md)、[`response-format`](./shared/response-format.md)、[`common-phrases`](./shared/common-phrases.md)）

---

## 5. 相关链（横切）

| 主题 | 文档 |
|------|------|
| **拼装提示词库（Git）** | [`library/README`](./library/README.md)、[`registry` §1.2](./library/scenarios/registry.md)、[`fewshot-narrative-analysis`](./library/packs/fewshot-narrative-analysis.zh-CN.md) |
| **`scenarioId`** | [`routing-engine`](../domains/agent/agent-orchestration/routing-engine.md) |
| **技能 / 工具登记** | [`trade-assistance` §8](../domains/agent/exchange-agent/trade-assistance.md) |
| **意图语义（簇 · 歧义）** | [`exchange-agent/intents`](../domains/agent/exchange-agent/intents.md) |
| **Telegram / 类型 A** | [`telegram/overview` §2.5 · 类型 A、§2～§2.6](../domains/agent/telegram/overview.md) |
| **会话与绑定** | [`Runtime/sessions`](../Runtime/sessions.md)、[`onboarding/telegram-binding`](../domains/agent/onboarding/telegram-binding.md) |
| **UNKNOWN / 对账** | [`Runtime/unknown-state`](../Runtime/unknown-state.md)、[`Runtime/reconciliation`](../Runtime/reconciliation.md) |
| **MNRA · 行情叙事运行时** | [`market-narrative-runtime/README`](../market-narrative-runtime/README.md)、[`scenario-matrix`](../market-narrative-runtime/scenario-matrix.md)、[`market-intelligence` §4](../domains/agent/exchange-agent/market-intelligence.md)、[`common-phrases` §8](shared/common-phrases.md) |
| **PRS 总入口** | [`prompt-runtime/README`](../prompt-runtime/README.md) |
| **Skill Specs（写路径 L0）** | [`skill-specs/README`](../skill-specs/README.md) · 金样 [`skill.spot.limit_order`](../skill-specs/spot/skill.spot.limit_order.md) |
| **Memory · STM/LTM** | [`memory-runtime` §9～§13](../Runtime/memory-runtime.md)、[`intents/analysis` §6](intents/analysis.md)、[`system/system` §6](system/system.md) |
| **关单分工（本仓 vs 所内）** | [`closure-remaining`](../closure-remaining.md)（**[§0 速链](../closure-remaining.md#closure-remaining-quicklinks)** · **[§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)** · **[§7](../closure-remaining.md#cc-remaining-open-items)** · **[§7.2～§7.4 Prompt/Runtime · AC-09](../closure-remaining.md#cc-ac09-closure-matrix)** · **[§7.5 闭环路径](../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6 MR 清单](../closure-remaining.md#cc-closure-exec-checklist)** · **[§7.1](../closure-remaining.md#cc-remaining-gap-paste)**）· [`contract-closure`](../contract-closure.md) |
| **契约收口 / MR 模板** | [`contract-closure`](../contract-closure.md)（**P1-04** **等** **CC** **见** **§2～§3**；**速链** [**`closure-remaining` §0**](../closure-remaining.md#closure-remaining-quicklinks)） |

---

**文档版本**：1.15.0 · **维护**：产品 + Prompt owner · **本版**：**§2 治理双层 · 新增 `governance-map.md` · 目录树注释对齐 16 包**。**承** 1.14.3。
