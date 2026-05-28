# PRD（V1 八大模块）↔ Admin Console IA 对齐

**PRD**：`[domains/admin/management-console-v1-prd.md](../domains/admin/management-console-v1-prd.md)` **§3**  
**IA**：`[sitemap.md](sitemap.md)` · **模块/功能/页面命名** `[naming-alignment.md](naming-alignment.md)` **v3**

## 对齐策略


| 策略                | 说明                                                                                                                          |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **共存**            | PRD §3 仍为 **业务能力与 FR 归因** SSOT；**本 IA** 为 **运营视图与菜单** SSOT                                                                  |
| **Runtime 可视化优先** | 新 IA **首栏**为 **运行运营**（执行记录 + 执行详情内嵌 Queue/Events）；PRD 分散在观测、编排叙事中，由 [runtime-to-ui-mapping.md](runtime-to-ui-mapping.md) 收口；**执行详情 · Timeline** **与** **`transitionTrigger`/`observability` §2.4/`SC-OM-04`** **对签**（[page-specs](page-specs.md)、PRD §11） |


## 模块映射表


| PRD §3 模块                | 子域锚点（不变）                                     | Admin Console IA **一级（运营中文）**                                                                                                                       |
| ------------------------ | -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 一 · Agent Management     | agent-management/*                           | **AI 治理**：**实例管理**（`/agents/instances`；旧 `**/agents/config`** 等 **Demo**→重定向）；多租户时再补 Template 运维                                                    |
| 二 · Prompt Management    | prompt-management/*                          | **AI 治理**：**提示词治理** · **安全防护**                                                                                                                      |
| 三 · Tool Management      | tool-management/*                            | **AI 治理**：**运行场景** + **技能与工具**（`ai.tool-registry` · [`tool-registry-reconciliation`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) §0）；**无** Demo Runtime Publish UI；**所内** API · `admin/tool-management.yaml` |
| 四 · AI Settings          | ai-settings/*                                | **全局参数**：模型配置（`ai.settings`）                                                                                                                        |
| 五 · Billing & Settlement | billing-management/*                         | **计费与账务**                                                                                                                                           |
| 六 · Access Control       | access-control/*                             | **准入与风控**                                                                                                                                           |
| 七 · Trading Agent Config | trading-agent-config/*                       | **全局参数** · 全局交易参数                                                                                                                                   |
| 八 · Logs & Observability | observability-management/* + observability/* | **日志与监控**；**执行记录 / 详情** 主要归入 **运行运营**，与模块八 API 联合；**`FR-MC801` 时间线** **`transitionTrigger`** **同窗** **§2.4** |


## 导航命名差异（给运营/研发的说明）


| PRD 习惯叫法                   | IA 页面 ID / 路由名                                                                                                                                                   |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 模块八「执行检索」/ 运行事件            | **执行详情**内 **Events** + **日志检索**（FR-MC802）；MVP **不设**独立「运行事件」侧栏                                                                                                   |
| 实例详情里的 Runtime             | `runtime.execution-detail` **专注「编排执行」**；**Timeline** **`transitionTrigger`** 见 [runtime-to-ui-mapping](runtime-to-ui-mapping.md)；长期 Instance Runtime 另里程碑评估                                                                                               |
| Telegram / 其它 **触达渠道** 运营面 | **不设**一级「外部对接」；归入 **全局参数** · **渠道管理**（`sys.channels`，列表 + 分渠道详情）。**Agent Runtime 模型策略** 在 **全局参数** · **模型配置**（`ai.settings`）；**模型供应商 / 网关 Infra** 归平台网关，与运营策略拆面。 |


## 不变项

- **FR/SC 验收** 仍以各 `domains/admin/<子域>/` 与 [`contract-closure.md`](../contract-closure.md) 为准；MR **缺闭环锚** 兼读 [**`closure-remaining` §0**](../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../closure-remaining.md#cc-exec-solve-path)。  
- **G01 全局闸**（PRD）：`**src/admin` Demo** **不设** `sys.global-gate` 独立页；横幅与 `**GLOBAL_AGENT_SWITCH`** 叙事见 **agent-management**、Runtime freeze、**design/api**。
- **「AI 治理」页内职责与交付顺序建议**（防菜单膨胀）：见 `[admin-console/README.md](README.md)`。

