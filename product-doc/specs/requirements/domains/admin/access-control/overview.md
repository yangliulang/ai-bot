# 域需求：Access Control（后台 — 准入与限制）

| 项 | 内容 |
|----|------|
| **产品** | ChainUp AI Agent（Coobit 单所） |
| **文档** | `specs/requirements/domains/admin/access-control/overview.md` |
| **状态** | **规划已落 `design/api` 登记表 + 待补充条**；OpenAPI **TBD**，与 [`agent-management` §7.1](../agent-management/functions.md)、**用户摘要 §8.2** **填链 MR** 闭合。 |
| **PRD 位置** | **[`../management-console-v1-prd.md`](../management-console-v1-prd.md) · §9 模块六**（**FR-MC601～607**） |
| **互引** | [`management-console-v1-prd.md`](../management-console-v1-prd.md) **附录 A · §5.1**（**`AGENT_MIN_VIP_TIER`** · [`keys`](../trading-agent-config/keys.md)）；[`../../agent/onboarding/overview.md`](../../agent/onboarding/overview.md)；[`../../agent/exchange-agent/overview.md`](../../agent/exchange-agent/overview.md)、[`../../agent/exchange-agent/trade-assistance.md`](../../agent/exchange-agent/trade-assistance.md) **FR-T02**；[`../../agent/exchange-agent/boundaries.md`](../../agent/exchange-agent/boundaries.md)（**Kill / 叠层 / 渠道边界**）；[`../agent-management/overview.md`](../agent-management/overview.md)、[`../agent-management/functions.md`](../agent-management/functions.md) **§2.1 I02、§7.1**；[`../billing-management/overview.md`](../billing-management/overview.md)；[`../../../risk/README.md`](../../../risk/README.md)；[`../../../../design/api.md`](../../../../design/api.md)（**用户摘要 / I02 HTTP**）；[`../../../contract-closure.md`](../../../contract-closure.md)；[**`closure-remaining` §0**](../../../closure-remaining.md#closure-remaining-quicklinks) · **[§6 / §6.4**](../../../closure-remaining.md#cc-exec-solve-path) |

---

## 1. 目的（摘要）

统一 **「谁可开通 Agent / 谁在灰度桶内 / 谁被合规或运营封禁 / 最低会员与 KYC 事实」**：与 **运行时门禁**（[`exchange-agent` · **FR-T02**](../../agent/exchange-agent/trade-assistance.md)、[`boundaries` · Kill/叠层](../../agent/exchange-agent/boundaries.md)）及管理台 **`agentState` / block reason**（附录 A）**同源或可推导**，**禁止**运营台与用户触达侧 **两套冲突口径**。

**管理台创建实例（I02）**：本域参与 **前置链第 2 步**（[`config.md` §4](config.md)；[`agent-management` **§2.1 I02**](../agent-management/functions.md)）；失败 **`code`** **须**落入 [`agent-management` §7.1](../agent-management/functions.md) **已登记枚举** **`design`/OpenAPI 同窗冻结**。

---

## 2. 本版包含 / 不包含

| 判定 | 内容 |
|------|------|
| **包含（V1 目标）** | **FR-MC601～607**（[`functions.md` §2](functions.md)）；**SC-AC**（[`functions.md` §3](functions.md)）；[**`eligibility-runtime.md`**](eligibility-runtime.md)（准入顺序、结果信封、运行时反应、**capabilities**）；灰度与白名单运营、合规/运营封禁、KYC **只读镜像**、`AGENT_MIN_VIP_TIER` **控制台编辑链路**（**数值真源**与 **[`keys` §3](../trading-agent-config/keys.md)** **对 PR**）；[`config`](config.md) **IA、`I02`**；[`flow`](flow.md)；[`rules`](rules.md)。 |
| **不包含** | **重写**交易所 **KYC 状态机**（以合规主系统为 SSOT）；**计费策略**本体（[`billing-management`](../billing-management/overview.md)）；**全局 `FEATURE_*`、`SYMBOL_*`**（[`trading-agent-config`](../trading-agent-config/overview.md)）；**子账户/API 就绪**门禁（[`onboarding/overview`](../../agent/onboarding/overview.md) + **FR-T02 第 3 道**）。 |

---

## 3. FR / SC 索引（SSOT：`functions.md`）

| 类型 | 位置 |
|------|------|
| FR-MC601～607 | [`functions.md` §2](functions.md) |
| SC-AC（V1） | [`functions.md` §3](functions.md) |
| 与 **§7.1** 映射 / 待登记 `code` | [`functions.md` §4](functions.md) |

---

## 4. 配置与 `configKey` 边界

| 键 / 概念 | 真源 |
|-----------|------|
| **`AGENT_MIN_VIP_TIER`** | **[`trading-agent-config/keys.md`](../trading-agent-config/keys.md) §3**；本域提供 **运营编辑与审批 UX**；**禁止**在 billing / agent-management **另造编辑入口**（可 **只读摘要**）。 |
| **名单 / 封禁策略** | **本域 SSOT**（存储形态 **`design`/ADR**）；映射到 **附录 A** 可读字段与用户摘要 **`design`** 契约。 |

---

## 5. 规划里程碑（非排期）

| 阶段 | 交付物 |
|------|--------|
| **M1** | **I02** 第 2 步 **可查因**、`§7.1` **闭环**、`SC-AC-01～03` **可走通** |
| **M2** | **白名单/灰度** 导入审批 + **双人复核**（[`rules`](rules.md)）+ **`SC-AC-04～07`** |
| **M3** | **KYC/地域/测评** **只读镜像**齐备、与主站 **`userId`** join；**延后项**单列 ADR |

---

## 6. 文档索引（阅读顺序）

| 顺序 | 文档 | 说明 |
|------|------|------|
| 1 | [`functions.md`](functions.md) | FR / SC / 错误码对齐 |
| 2 | [`eligibility-runtime.md`](eligibility-runtime.md) | 准入顺序、结果信封、灰度命中、会话违约、缓存、事件与 **capabilities** |
| 3 | [`config.md`](config.md) | **`I02`**、附录 A、`AGENT_MIN_VIP_TIER` |
| 4 | [`flow.md`](flow.md) | 放白、封禁、VIP 降级 |
| 5 | [`rules.md`](rules.md) | SSOT、审计、billing **分域** |

*维护：产品 + 合规/风控 + 后台 owner。*
