# Prompt Library（可拼装资产 · Git）

**路径**：`specs/requirements/prompts/library/`。

**性质**：本目录提供 **可直接粘贴 / 经由 Runtime 拼接** 的 **完整 SYSTEM 包与片段**（`.prompt.*.md` / `fragment-*.md`），作为 **`prompt-management` 发布物** 的 **Git 侧镜像与 MR 评审载体**。  
**条文下限 SSOT** 仍为 **[`../system/system.md`](../system/system.md)**、[`../shared/`](../shared/) **与各场景目录**；**卡片模板正文** **不**在此维护 — [`prompt-management/overview`](../../domains/admin/prompt-management/overview.md)。

**产品原则（用户侧）**：**凡用户提出的问题与诉求，须在 Telegram 内推进解决**（对话内澄清、只读查询、类型 A、重试与边界说明）。**不得**默认把处置责任推卸到独立 App 或浏览器；**唯一例外**同窗 [`shared/response-format` §1](../shared/response-format.md) **`requires_main_site`** **窄口子**（须与 **`exchange-agent/boundaries`** **冻结一致**）。

**索引**：[`../README.md`](../README.md)

---

## 1. 目录

```text
library/
├── README.md                    # 本篇 · 库说明与版本策略
├── PUBLISH-ALIGNMENT.md         # 拼装库 ↔ 运营 pp-* 六段 Publish 对齐读法
├── ASSEMBLY.md                  # 默认拼装顺序与占位符
├── INITIAL_SYSTEM.zh-CN.md      # 冷启动整段粘贴：L1+L2+L3（简中）
├── INITIAL_SYSTEM.en.md         # 冷启动整段粘贴：L1+L2+L3（英文桶）
├── packs/
│   ├── core-runtime-root.zh-CN.md / core-runtime-root.en.md
│   ├── fragment-errors-user-visible.zh-CN.md / .en.md
│   ├── fragment-safety.zh-CN.md / .en.md
│   ├── fragment-intent-{trade|analysis|monitoring}.zh-CN.md / .en.md
│   ├── fragment-confirmation-type-a.zh-CN.md / .en.md
│   └── fewshot-narrative-analysis.zh-CN.md / .en.md   # ANALYSIS Few-shot（非 L1～L6 · 须 Publish）
├── scenarios/
│   └── registry.md              # scenarioId → 拼装配方（全表）
└── scripts/
    ├── check_registry_vs_routing_engine.py   # MR 前：registry ↔ routing-engine 对签
    └── check_governance_map_vs_registry.py   # MR 前：governance-map ↔ registry · promptPackId
```

---

## 2. 与 `prompt-management` 的分工

| 归属 | 说明 |
|------|------|
| **Git（本库）** | 评审 diff、离线对齐条文、开源协作；**library-*** 语义版本见下 |
| **后台发布** | `promptPackId` / `promptPackVersion` **单调递增**、**LOCKED** 包只读 — [`prompt-management/overview`](../../domains/admin/prompt-management/overview.md)、[`runtime-injection`](../../domains/admin/prompt-management/runtime-injection.md) |
| **观测** | `scenarioId`、`promptPackVersion`、`resolvedPromptBinding` — [`observability/overview` §2.3](../../observability/overview.md) |
| **关单派工 · AC-09 检核** | [`closure-remaining` §7.2～§7.4](../../../closure-remaining.md#cc-ac09-closure-matrix) · **[§7.5](../../../closure-remaining.md#cc-remaining-open-close-path)** · **[§7.6](../../../closure-remaining.md#cc-closure-exec-checklist)** — Runtime 拼装链 / `requires_main_site` / 欢迎语 / 时间线粒度 / **registry↔routing CI**（**与** [`runtime-injection`](../../domains/admin/prompt-management/runtime-injection.md) **同窗**） |

**入库流程（建议）**：MR 改 Git → 评审对签条文 → 运维/研发 **搬运或同步** 至管理台发布 → Runtime **仅引用已发布版本**。

---

## 3. 版本策略（`library-*`）

| 片段 | 初始标签 |
|------|-----------|
| **整套库** | `library-0.2.4`（**L1 Memory/Market Facts · Few-shot 镜像 library-0.1.0**） |
| **单文件** | 文首 **YAML 注释块** 或 **表格「对齐条文版本」** — 见各 `packs/*.md` |

**Breaking**（改写模型义务）：上调 **minor**；纯措辞优化：**patch** 级记录在各自文件脚。

---

## 4. 阅读顺序

0. [`PUBLISH-ALIGNMENT.md`](./PUBLISH-ALIGNMENT.md) — **library 片段 vs `pp-*` Publish**（**勿**把 `INITIAL_SYSTEM` 当作单包正文）  
1. [`ASSEMBLY.md`](./ASSEMBLY.md)  
2. **冷启动一次粘贴**：[`INITIAL_SYSTEM.zh-CN.md`](./INITIAL_SYSTEM.zh-CN.md) **或** [`INITIAL_SYSTEM.en.md`](./INITIAL_SYSTEM.en.md)（**仅** L1+L2+L3；**后续**仍须 **`scenarioId` → L4～L6**）  
3. [`packs/core-runtime-root.zh-CN.md`](./packs/core-runtime-root.zh-CN.md)（英文桶 → [`.en.md`](./packs/core-runtime-root.en.md)）— **与 INITIAL 正文分块同源**  
4. [`scenarios/registry.md`](./scenarios/registry.md) — 按命中 **`scenarioId`** 追加片段；**§5** **英文桶映射**  
5. [`market-runtime-payload.md`](../../domains/agent/exchange-agent/market-runtime-payload.md) — **FACT SOURCE 键** `userVisibleMarketData` / `marketInsightData`、**别名** `read.market.*` → `market.read_*`、**对客 MUST NOT**（与 **read-analyze**、**routing §1.1** 同窗）  
6. 条文深读仍走 [`../README.md`](../README.md) **§3**

---

## 5. 研发集成 checklist（Runtime / 拼装器）

1. **取键**：从编排得到正式 **`scenarioId`**（同窗 [`routing-engine`](../../domains/agent/agent-orchestration/routing-engine.md)）。  
2. **查表**：[`scenarios/registry.md`](./scenarios/registry.md) 得 **`promptPackId`**、**C / E / S / IT|IA|IM / A** 与 **延展条文**；全表映射 [`governance-map.md`](../governance-map.md)。  
3. **按序拼装**：[`ASSEMBLY`](./ASSEMBLY.md) **L1→L6** 自上而下合并为 **SYSTEM**（或等价分段）；**用户消息与工具结果不入 SYSTEM**。  
4. **语种**：**`effective_locale` = `en`** → **L1 + L2～L5** 全部选用 **`*.en.md`**；**简中 / 繁中** → **`core-runtime-root.zh-CN.md`** + **`*.zh-CN.md`**（繁中可在发布管线微调用词）。  
5. **运行时上下文**：若注入 **`user_visible_message`** / **`requires_main_site`** — **键名下限** [`runtime-injection` §2.4](../../domains/admin/prompt-management/runtime-injection.md)；**块 5 行情/记忆键** → [`ASSEMBLY` §2](./ASSEMBLY.md)、[`registry` §1.2](./scenarios/registry.md)；**占位符示意** [`ASSEMBLY` §2](./ASSEMBLY.md)；**用户话术原则** [`shared/response-format` §1](../shared/response-format.md)。  
6. **禁忌**：**勿**向 SYSTEM 注入密钥或 Cookie；线上 **仅引用** [`prompt-management`](../../domains/admin/prompt-management/overview.md) **已发布** **`promptPackVersion`** — **同窗** [`observability` §2.3](../../observability/overview.md)。  
7. **Few-shot（ANALYSIS）**：**勿**混入 SYSTEM — [`packs/fewshot-narrative-analysis.*.md`](./packs/fewshot-narrative-analysis.zh-CN.md) **→** **管理台 Publish**（**FR-PM05 §2.5.1**）。  
8. **文档对签**：更新 **`scenarioId`** / **`promptPackId`** 行后自仓库根目录运行（**均须** **FAIL=0**）：  
   `python3 specs/requirements/prompts/library/scripts/check_registry_vs_routing_engine.py`  
   `python3 specs/requirements/prompts/library/scripts/check_governance_map_vs_registry.py`

---

**文档版本**：1.0.12 · **维护**：产品 + Prompt owner · **本版**：**Few-shot Git 镜像 + §5 checklist**。**承** 1.0.11。
