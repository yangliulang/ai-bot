# 小团队轻量管控（LITE-MODE）

**适用**：需求侧与开发侧合计 **≈2 人**（如 **1 需求 + 1 开发**），需 **降低流程负担**、仍保留 **可追溯 SSOT**。

**与全文 `contract-closure.md` 的关系**：本文 **日常优先**；[`contract-closure.md`](contract-closure.md) **不删**，在 **扩编**、**对外宣称「生产契约已冻结」**、**法务/审计/多方验收** 时 **再按该文 §2～§5、§8～§10** 启用。**对客「已支持」三闸速查**（**不替代** **`contract-closure` §1.2**）：[`domains/agent/agent-orchestration/implementation-alignment.md`](domains/agent/agent-orchestration/implementation-alignment.md) **§13.1** — **闸 1** **已含** **`runtime-freeze` §3** **写键最小编排**（**详** **§13.1 表**、**同窗** **`contract-closure` §1.2 款 4**）。

**A 阶段 ≠ B 阶段（防误读）**：[`product.md`](product.md) **`design/api` 占位/延期** **与** **OpenAPI 子集** **可支撑「进开发」**；**对客说「生产已可用」** **仍须** **[`contract-closure` §1.2](contract-closure.md#12-可对签必要条件六款齐备)** **六款** **或** **同窗** **[`§3.0` 分期叙事](contract-closure.md#cc-p1-doc-vs-b)**。**关单副读** → **[§0 速链](closure-remaining.md#closure-remaining-quicklinks)** · **[PRS 改什么去哪](prompt-runtime/README.md#prs-where-to-edit)** · **[§6 执行视图](closure-remaining.md#cc-exec-solve-path)** · **[§6.4 首节表](closure-remaining.md#cc-problem-to-action)** **；** **剩余开放项一键表** → [`closure-remaining` §7](closure-remaining.md#cc-remaining-open-items) · **走读缺口粘贴** **[§7.1](closure-remaining.md#cc-remaining-gap-paste)** · **闭环路径** **[§7.5](closure-remaining.md#cc-remaining-open-close-path)** · **MR 执行清单** **[§7.6](closure-remaining.md#cc-closure-exec-checklist)**。**「未完」语义统一口径** → **[未完成语义 SSOT](closure-remaining.md#cc-unfinished-semantics)**（**与 §1.1～§7.5 同窗**）。

---

## 1. 日常只维护三处（真相源）

| # | 放哪 | 写什么 | 谁主责 | 何时改 |
|---|------|--------|--------|--------|
| **A** | [`product.md`](product.md) | 方向、**本版范围**、**非目标** | 需求 | 范围或取舍变化时 |
| **B** | 相关 **`domains/...` 域正文** | 本条能力的 FR/边界/验收表述 | 需求（开发可对条目标注实现差异） | 做该能力时 |
| **C** | **OpenAPI**（`specs/openapi/`）+ [`design/api.md`](../design/api.md) **对应行/矩阵** | PATH/字段与 **实现一致**；仍为占位处 **明确写「未对外承诺」或书面延期** | 开发为主，需求校对 | 动接口或矩阵含义时 |

**原则**：会议或口头结论 **必须** 落实进 **A / B / C 之一**，不另造「第三套」纪要当 SSOT。**对上 Coobit 私网 HTTP**：实现 **默认** 经 `openapi-ai`（Skill/CLI/MCP **等官方包**）；**制品须 pin**；**仅能调用白名单所载 PATH**。**≠** **可删除** **`specs/openapi`**、**`design/api` 矩阵**或 **`agent-coobit-api-allowlist`** — **契约 SSOT** 与宿主 **同窗** — [`product.md`](product.md) **方向**、[`integrations/exchange/overview.md`](integrations/exchange/overview.md)。

**本 Git 仓库边界（防找错仓）**：**`product/`** + **`specs/`** **不** **维护** **Execution Gateway / Coobit Adapter** **可执行实现**；**CC-P1-07 DoD B**（Runtime 接线、对拍）**在** **所内工程/Runtime 仓库** **验收** — [`product/README` 篇首](../../product/README.md)、[`ADR-004` 后果段](../design/adr/004-intent-centric-execution-and-canonical-trading-model.md)、[`CC-P1-07`](contract-closure.md#cc-p1-07)。

---

## 2. 单次 MR（小迭代）最小描述

合并前 MR 描述建议 **固定下文 1～4**（常规）；**不必** 粘贴 `contract-closure` §9/§10 全文。**宣称** **生产已可用 / 已闭环** 时 **须** **另写第 5 条**：

1. **能力与范围**：一句话 + 链到 **`product.md` 或域 §**（若相关）。  
2. **契约**：链 **OpenAPI 路径或 `design/api` 行**（若有）；无接口改动写「无」。  
3. **风险命中**：**计费 / 交易写 / 外网或第三方数据** — 命中哪类写一句；都没有写 **「无」**。  
4. **自测**：一条命令、一个场景或「已本地/所内验证」说明。  
5. **（仅当 MR 或发布说明宣称某能力「生产已可用 / 已闭环」）**：附 **`contract-closure` §1.2** **六款** **或** **§3 `release-notes` 等价列表** **之** **证据链**，并 **对照** [`domains/agent/agent-orchestration/implementation-alignment.md`](domains/agent/agent-orchestration/implementation-alignment.md) **§13.1** — **闸 1** **须** **可链** **`runtime-freeze` §3** **对应** **`scenarioId` 小节**（**写路径**）**或** **附** **N/A** **可读理由**（**只读键**）** — **禁止** **仅凭 v0.3 域文或占位寄存器行** **宣称**。**可选粘贴** **[`closure-remaining` §7.6](closure-remaining.md#cc-closure-exec-checklist)** **A/B/C 勾选块**（**与** **§9/§2.1** **同窗编排**）。

**主态 / 协查（触及则写一句）**：MR 若修改 **`executionId` 主态归并**、**`admin/observability/*` 时间线** **或** **模块八 `FR-MC801`**，**须** **同窗** [`Runtime/execution-transition-matrix.md`](Runtime/execution-transition-matrix.md) **§2.2**、[`observability/overview.md`](observability/overview.md) **§2.4**；**API** **已返回 `transitionTrigger` 时** **控制台/UI** **勿** **静默丢弃**（**`SC-OM-04`** — [`observability-management/functions.md`](domains/admin/observability-management/functions.md)）。

**用户副本 / 交易槽位（触及则写一句）**：MR 若改 **Telegram 类型 A 模板**、**`trade-via-agent` 主路径话术**、**或** **报价/数量解析**：**建议** **点检** [`contract-closure.md`](contract-closure.md) **§1.3**、[`runtime-consistency.md`](Runtime/runtime-consistency.md) **§7**、**JV-12** / **`eval.runtime.user_visible_phase_copy`** / **`eval.trade.slot_quote_base_clarify`** **之一**。

**合并纪律**：**代码与域/OpenAPI 有同窗修改**，避免「只改实现不改条文」长期漂移。

---

## 3. 发版 / 对外交代：半页纸（关门）

若本版本需要向 **老板 / 交易所 / 外包** 说明「能靠什么、不能靠什么」，**更新一篇** **[`product/release-notes.md`](../../product/release-notes.md)**（单文件、可追加版本小节），至少包含：

- **本版承诺能力**（列表）  
- **明确不承诺 / 仍为 TBD**（列表）  
- **已知风险或待补**（矩阵占位、环境未就绪等）  
- **计费 / 合规**（若本版触及：各 **一句**）  
- **主态边 × 观测**（若本版动 **Runtime 主态**、**`FR-MC801` 时间线** 或 **`transitionTrigger`**：**一句** **是否** **已与** [`observability/overview.md`](observability/overview.md) **§2.4** **及** **PRD §11** **对签**）  
- **关联 tag / MR**（可选）

> 两人模式下，此半页 **替代** `contract-closure` 全表 + PRD §13 **整表勾选** 作为 **发版关门**；若日后多方会签，再打开 `contract-closure` 与 PRD 附录。

**3.1 当前仓库快照（TBD 明细不下沉新文件）**：最新一节已写入 **[`product/release-notes.md`](../../product/release-notes.md)**（与各 **CC-P0/P1**、**`design/api` 矩阵**、**PRD §13** 勾法一致）；本节 §3 仍管 **「写什么」**，**「此刻到底哪些未承诺」** 以 **该文件从新到旧第一节** 为准。**对内系统工程叙事**（Runtime / Gateway / 意图中心）见 **[`architecture.md`](../design/architecture.md)「与通用 Agent 栈之对照」** — **不必**单独写入对外半页纸 **除非** **`release-notes`** **该版已宣称**。

---

## 4. `spec.md` / 升格叙事

- **日常**：**不强制** 为每个 MR 推进 [`spec.md`](spec.md) Status 或 [`contract-closure` §5.1](contract-closure.md#cc-stage4-spec-gate)。  
- **需要对外说「生产契约已冻结」或融资/合作方要件** 时：再按 **`contract-closure` §5.1** + **`spec.md`** 篇首规则执行。

---

## 5. 何时从 LITE-MODE 加回重流程

满足 **任一** 即可默认切换为 **`contract-closure` 全文节奏**：

- 干系人 **>2** 或 **明确 RACI**；  
- **监管 / 法务** 要对文档与实现 **留痕对签**；  
- **多环境并行** 或 **外包按 FR 验收**；  
- 需要 **PRD §13** 级 **发布清单** 作为合同附件。

---

## 6. 索引

| 文档 | 用途 |
|------|------|
| [`product.md`](product.md) | 产品方向与范围 SSOT |
| [`requirements/README.md`](README.md) | 需求目录总索引（含 **推荐阅读顺序**） |
| [`contract-closure.md`](contract-closure.md) | 大团队用 · 关单 / 升格 · **本模式 Optional** |
| [`closure-remaining.md`](closure-remaining.md) | **P0/P1**：本仓可推进 vs **须所内** **速查**（**不**替代 `contract-closure` DoD）；**[§0 速链](closure-remaining.md#closure-remaining-quicklinks)** · **[§6 执行 / §6.4 首节](closure-remaining.md#cc-exec-solve-path)**（[`§6.4` 粘贴表](closure-remaining.md#cc-problem-to-action)）；**剩余开放项一键** **[§7](closure-remaining.md#cc-remaining-open-items)** · **走读缺口** **[§7.1](closure-remaining.md#cc-remaining-gap-paste)** · **闭环路径** **[§7.5](closure-remaining.md#cc-remaining-open-close-path)** · **MR 执行清单** **[§7.6](closure-remaining.md#cc-closure-exec-checklist)** |
| [`domains/agent/agent-orchestration/implementation-alignment.md`](domains/agent/agent-orchestration/implementation-alignment.md) | **编排实现对齐**；**宣称闭环时** **同窗** **§13.1** **三闸**（**闸 1** **→** **`runtime-freeze` §3** **等**） |
| [`product/release-notes.md`](../../product/release-notes.md) | 发版半页纸（关门） |
| [`architecture.md`](../design/architecture.md) | **对内对齐**：**「与通用 Agent 栈之对照」**（Runtime / Gateway / 意图中心）；**同窗** ADR-004 / **`release-notes`** **（文档小节）** / **`contract-closure` §8** |

**修订**：改本文时 **无需** 动 `standards/Log.md`（本文不在 `standards/` 下）；若同步改了 `standards/` 内文件，仍须遵守该目录 **Log** 纪律。**最近对齐（2026-05-14）**：**§13.1 闸 1** **与** **`runtime-freeze` §3**、**`contract-closure` §1.2 款 4** **同窗** — **`implementation-alignment` v1.2.14+**。**同日**：篇首 **A≠B** **防误读** **链** **`contract-closure` §1.2/§3.0** **与** [`closure-remaining` §7](closure-remaining.md#cc-remaining-open-items) **·** **[§7.1](closure-remaining.md#cc-remaining-gap-paste)**。**增补（2026-05-17）**：§1 **原则段** 补 **`openapi-ai` 宿主 vs 契约** — 同窗 [`product.md`](product.md)、[`integrations/exchange/overview.md`](integrations/exchange/overview.md)。**增补（2026-05-14）**：§1 **补** **规格仓/工程仓边界**（**CC-P1-07 DoD B**）— **与** [`product/README`](../../product/README.md) **篇首** **同窗**。**增补（2026-05-14）**：§3.1 **补** **`architecture` 架构语言** **句读**；§6 **索引表** **增** **`architecture.md`** **一行**。
