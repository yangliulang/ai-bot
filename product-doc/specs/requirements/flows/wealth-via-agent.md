# 流程：经 Agent 的理财（意图分流 · 推荐 · 申购/赎回）

**定位**：用户在 **Telegram** 表达的 **理财/质押/活期/定期/收益** 等意图 → **本条**给出 **端到端产品与交互顺序**：**四类意图分流**、**推荐子策略（仅模糊诉求）**、**偏好推断、按需资产查询、产品与卡片、确认后转入产品下单技能**。**不写**单笔 OpenAPI 字段（以 [`design/api.md`](../../design/api.md) **矩阵**为准）。**对上 Coobit 私网 HTTP**：出站默认经 **`openapi-ai`**（**须 pin**）；**契约与白名单同窗** **[`integrations/exchange/overview.md`](../integrations/exchange/overview.md)**。**首版强制主站**的写路径 **须** **`WEALTH_ACTION_REQUIRES_WEB`** + Deeplink — 见 [`boundaries.md`](../domains/agent/exchange-agent/boundaries.md) **§8.3**。

**不参与**「交易写四轨」（闪兑/现货限价/全仓杠杆/合约）：理财 **单列**产品与 **`FEATURE_AGENT_WEALTH`**，与 [`trade-via-agent.md`](trade-via-agent.md) **文首**「理财不占主四轨」一致 — 实际链路 **可共用**门禁、计费、编排硬约束。**计费**：**S2** 双门禁（**Capability 额度** + **写路径 USDT · §7.4.1**）与 **S5 轨 B 核销** 同窗 [`consume-and-bill.md`](consume-and-bill.md)；**理财写边界** [`billing.md`](../domains/admin/billing-management/overview.md) **§7.3.1**。
**关单余量（MR 首节）**：[`closure-remaining` §0](../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../contract-closure.md)。

## 文首摘要

**书写规范**：[ **`business-process-standard.md`**](../standards/business-process-standard.md) §2；对齐计划：[ **`STANDARDS-ADOPTION.md`**](../standards/STANDARDS-ADOPTION.md)。


| 项                | 内容                                                                      |
| ---------------- | ----------------------------------------------------------------------- |
| **流程名**          | 经 Agent 的理财（意图分流 · 推荐 · 申购/赎回）                                          |
| **主渠道**          | Telegram；**`WEALTH_ACTION_REQUIRES_WEB`** 时主站 Deeplink                  |
| **涉及 `domains`** | **exchange-agent §8.3、billing §7.3.1、trade-assistance、telegram/overview §2.5.5** |
| **`design/`**     | **`api.md` 理财矩阵**                                                       |
| **端到端鸟瞰 · 架构语言** | [`flow/e2e-closed-loop.md`](../../../flow/e2e-closed-loop.md) **文首「架构语言」** → [`architecture` §「与通用 Agent 栈之对照」](../../design/architecture.md) |


## 参与文档

- [`../../design/api.md`](../../design/api.md) **理财矩阵**；[`../domains/agent/exchange-agent/boundaries.md`](../domains/agent/exchange-agent/boundaries.md) **§8.3**、**`FR-T05`**、**`WEALTH_ACTION_REQUIRES_WEB`**
- [`../integrations/exchange/overview.md`](../integrations/exchange/overview.md) **对上 HTTP · `openapi-ai` vs 矩阵契约**
- [`../domains/agent/exchange-agent/trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **§8.2**、**`FR-TS07`**、**`skill.wealth.*`**、**`tool.wealth.product_recommend`**
- [`../domains/agent/agent-orchestration/routing-engine.md`](../domains/agent/agent-orchestration/routing-engine.md) **§3**（**`wealth.holdings_read`、`wealth.recommend`、`wealth.subscribe`、`wealth.redeem`** 等 **`scenarioId`**）；[`../domains/agent/agent-orchestration/runtime-freeze.md`](../domains/agent/agent-orchestration/runtime-freeze.md) **§3.10**（**理财写** **最小编排**）
- [`../domains/agent/telegram/overview.md`](../domains/agent/telegram/overview.md) **§2.5.5**（理财卡片）；**§2～§2.6**（渠道闸 · Bot API）；[`../contract-closure.md`](../contract-closure.md) **§1、§4**（矩阵 **`WEALTH_*`**、解冻 MR、**`FR-T05`**）
- [`read-analyze-and-search-via-agent.md`](read-analyze-and-search-via-agent.md)（纯科普或 **不与本人资产绑定** 的排行 — 可走 B/C；**勿冒充已申购**）

## 门禁与契约（先于各步）

- **`FEATURE_TRADING=ON`** 且 **`FEATURE_AGENT_WEALTH=ON`**（[`config.md`](../domains/admin/management-console-v1-prd.md) **§5.1**）；**关理财线写** → **拒答对应写**。
- **触及子账户私有读**（持仓、可用、产品在用户侧可买性校验等）→ **FR-T02**（[`exchange-agent/overview.md`](../domains/agent/exchange-agent/overview.md)）。
- **可计费写路径**：**S2** **须** 满足 **Capability 额度**（**轨 B**）**与** **子账户 USDT 可用**（**§7.4.1** · 含 **§7.3.1 理财写** 边界）；**S5** **仅** **`ENTITLEMENT_DEBIT`** — [`consume-and-bill.md`](consume-and-bill.md)、[`commerce-model.md`](../domains/admin/billing-management/commerce-model.md)。
- **任何交易所侧写**（申购、赎回、理财侧划转若在模板内）：**每笔** **`read_skill_operation_spec` → §2.5 · 类型 A（[`telegram/overview.md`](../domains/agent/telegram/overview.md)）→ `call_exchange_write`**（与 [`agent-orchestration/overview.md` · FR-AO04](../domains/agent/agent-orchestration/overview.md) 一致）。**不可用 API 落地的写** → **§8.3**、[ **`telegram/overview.md` §2.5.5**](../domains/agent/telegram/overview.md)（类型 B / **`WEALTH_ACTION_REQUIRES_WEB`**）。
- **推荐与列表类只读**：**可** **`tool.wealth.product_recommend`** **等 B 类**（[`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **§8.2**）；**不得**谎称已代用户申购成功。
- **卡片**：理财 **不适用**限价/市价委托表 — **须在** [`telegram/overview.md`](../domains/agent/telegram/overview.md) **§2.5.5** **产品单列模板**（**金额、产品编码、账本方向 / 期限 / APR** 等以所内 **技能与模板冻结**）。

**主路径（Happy path）**：下列 **S1～S8** **与**上文 **门禁与契约**同窗。

---

### S1 · 意图识别与分流

Agent 收到与用户 **理财**相关的消息后 **先判别**四类（**可多轮澄清归入一类**）；**类目确定后**再进入后续步。**另须对齐** **exchange-agent · FR-T07**、**`scenarioId` 映射**并在编排寄存器文档化；本文 **不**穷举寄存器内 **`scenarioId`** **真名**。


| #     | **类别**    | **用户话术特征（示意）**                                       | **系统行为概要**                                                                                                                                                                                                                |
| ----- | --------- | ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **强指令直达** | 明示 **申购、买入、参与**某一 **具体产品**（含 **活期/定期** **与**币种或产品昵称） | **不**再走泛化推荐链路；**直接加载**该产品对应 **`skill`/`scenarioId`**，进入 **S8** **之前**已由产品技能约定的 **单笔申购流程**。**禁止**在此时 **额外套路式产品横评**，除非用户在 **同一轮**明确要求对比。                                                                                    |
| **2** | **持仓查询**  | **投了哪些、持仓、我有多少理财、年化/到期**等与 **既有仓位**相关                | **只读链路**：若须本人数据 → **私有读** **+ FR-T02**；按用户 **点名的产品/SKU** **精准检索**；**未点名**时可 **可读追问**要问哪一只/哪一类。**不写**。                                                                                                                     |
| **3** | **赎回**    | **赎回、取出、退出质押、到期取出来**                                 | **写链路**（若在矩阵内）：**须** **`read_skill_operation_spec`**（**`skill.wealth.redeem`** 等寄存器登记 **`skillId`**）→ **类型 A** → 写；否则 **§8.3 主站回退**（见 [`trade-assistance.md`](../domains/agent/exchange-agent/trade-assistance.md) **§8.2**）。 |
| **4** | **推荐类**   | **想理财、推荐一下、收益最高、帮我配方案、稳健一点**等 **未锁定具体 SKU** 的泛诉求     | 进入 **S2～S7**；**不得**与 **类 1** 混淆 — **类 1** **须**用户 **显式锁定产品或明确 SKU 语义**。                                                                                                                                                   |


---

### S2 · 推荐策略选择（**仅**推荐类 · 类 4）

进入 **类 4** 后，再判 **子策略**（**互斥主策略**，**实现可设默认**）：


| **子策略**    | **触发条件（示意）**                           | **输出形态**                                                                                              |
| ---------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **最高收益对比** | **最高收益、利率最高、哪个划算、收益对比、排名** 等           | **以 APR（或所内等价收益率口径）为主排序**；结合 **用户资产做可执行过滤**（可买性、币种、门槛）；**分两组呈现**：**稳健组** / **进取组**（组名与划分规则 **产品冻结**）。 |
| **组合方案**   | 用户给出 **明确金额** **且** 表达 **推荐、怎么配、按我情况** | **2～4 个产品**的 **资金分配方案**；**总额守恒**；每个产品 **单独一张带金额预填**的 **类型 A 预备卡/摘要**（**最终写**仍 **一步一确认**）。             |
| **探索推荐**   | **想理财、推荐一下、稳健点**等 **无金额**、**无强制对比词**   | **1～3 个**匹配 **推断偏好**的产品；**不做**跨产品金额切分；**可**引导用户 **补金额**（见 **S6**）。                                    |


---

### S3 · 个性化偏好推断

**须**结合 **用户画像**（风险承受、历史行为、渠道内标签 — **以所内画像服务为上限**）与 **已获知的资产/币种信息** **推断**：

- **期限**偏好（活期 vs 可锁仓）
- **风险**分层（对应 **稳健/进取** **及**组内排序权重）
- **币种**倾向

**推断仅**影响 **排序、过滤与呈现顺序**；**不得**替代 **用户显式确认** **写**。

---

### S4 · 资产查询（按需）


| **密度**  | **条件**                                                        | **用途**                            |
| ------- | ------------------------------------------------------------- | --------------------------------- |
| **必须查** | 用户 **已给金额**要方案、**按我情况推荐**、**须判断余额/可买性/最小参与额**                 | **可执行性校验**、方案落地、**组合方案** **总额守恒** |
| **建议查** | **老用户**、资产可能 **分散**、**最高收益对比** **须结合个人可买过滤**                  | **过滤不可买 SKU**、偏好币种收敛              |
| **不查**  | **纯概念解释**、**全市场收益排行** **且** **明确不结合个人资产**（**须在回复中说明**未结合本人持仓） | 降 **FR-T02** **调用**与 **合规面**      |


**查询结果** **仅用于内部决策**（偏好、风险、金额与可买性、方案可落地）；**默认不向用户罗列**完整账户明细 **除非**用户处于 **类 2** 或 **主动追问** — 与 **隐私/渠道文案** **评审**对签。

---

### S5 · 产品匹配与推荐生成

- 在 **S2 子策略** 约束下，从 **所内可售目录**（**`tool.wealth.product_recommend`** / **登记只读 API**）取 **候选集**。
- **应用** **S3 偏好** **与** **S4 资产结论** **过滤、排序、截断**（**探索推荐** **≤3**；**组合方案** **2～4**；**对比** **两组 + 组内条数上限** **产品冻结**）。
- **禁止**推荐 **矩阵未覆盖**、**已下架**或 **用户不可买**（合规/地区/KYC）**却假装可一键买入**的商品。

---

### S6 · 反问补齐（最多 1 轮、优先单问）

若 **缺一关键参数即明显跑偏**，**允许追问一次**，**优先级**如下（**从上到下**命中即停 **或** **产品自定更严规则须有 ADR**）：

1. **要组合方案但未给金额** → 问 **金额**
2. **已给金额但未约束币种** → 问 **币种**
3. **强调期限但未说清是否接受锁仓** → 问 **锁仓意愿**
4. **仅泛泛「推荐一下」** → 问 **理财目标**（期限/流动性/风险偏好 **三选一话术**）

**不得**为多填一项 **连环追问**超出 **1** 问（**可把剩余缺省记入默认策略**并在卡片 **可读披露**）。

---

### S7 · 卡片生成与展示（Telegram）

- **探索推荐**：**1～3** **张卡片**（**每组**上限 **若** **最高收益对比** **须**分拆呈现 — **以 UX 冻结为准**）。
- **每张卡片前**：**简短推荐理由**（**可**：偏好匹配、APR 档位、期限匹配）。
- **卡片正文**：由 **对应产品技能/模板** 提供 — **APR、期限、参与规则、风险须知** — **对齐** [`telegram/overview.md` §2.5.5；总则 §2～§2.6](../domains/agent/telegram/overview.md)。
- **组合方案**：多张卡 **金额预填** **且** **加总等于**用户给定总额（四舍五入规则 **所内冻结**）。

---

### S8 · 确认后进入产品申购流程

- 用户在 **卡片**上 **选定**某一产品 → **切换**至该产品 **`skill`** **专属子流程**（**活期/定期**、金额修改、风控文案、**类型 A**、提交写 **或** **主站 Deeplink**）。
- **每一产品 SKU** **可有不同**表单与校验 — **不得在**本条 **臆造字段**；**以** **`read_skill_operation_spec`** **当期条文**为准。
- **强指令直达（类 1）**：跳过 **S2～S7** 中与「泛推荐」重复的环节；**仍可**在本产品流程内 **问金额**（若未指定）。

---

**文档版本**：0.1.6 · **维护**：产品 + Agent Runtime owner · **本版**：**文首/`参与文档`** **补** **`openapi-ai`/`integrations`** **同窗**。**承 0.1.5**。**同窗**：exchange-agent §8.3、`trade-assistance` §8.2、[telegram/overview §2.5.5](../domains/agent/telegram/overview.md)、[`design/api.md`](../../design/api.md)、[routing-engine §3](../domains/agent/agent-orchestration/routing-engine.md) **`wealth.*`、`scenarioId`**。