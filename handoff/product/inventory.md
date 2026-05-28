# 存量切口清单（inventory）

> **用途**：项目已开发一段时间后接入流水线时，划清「PRD 全量」与「本阶段 backlog」的边界。  
> **模式**见 `pipeline.project.yaml` → `project.onboarding.mode`（[onboarding-modes.md](../conventions/onboarding-modes.md)）。  
> **维护**：§2/§4 可由 `./scripts/advance-phase.sh` 自动更新（continuing）；§1/§5/§6 建议人工。

最后更新：`2026-05-28`（**Phase-4 plan-reset soft** · backlog 表已清空，四项 → **queued**）  
对应 roadmap：`handoff/roadmap/phase-4.md`（manifest `roadmap.active_phase` = **4** · 待 **replan**）

---

## 1. 切口说明（一句话）

**接入前（～2026-05-25）**：Phase1 运行时 + TG 绑定/会话 + 交易写路径（现货/合约/杠杆/条件单）+ 504 对账 HTTP **已在 `server/` 落地**；**Admin 控制台** 对应页面 **已在 `admin/` 落地**（[`admin/FE_HANDOFF.md`](../../admin/FE_HANDOFF.md) 条目 **均已 `[x]`**）。  
**接入后 Phase-1（2026-05-26）**：流水线 6 个功能包（504 扩面、Observability、NLU/欢迎语/narrate、实例写路径 FE）已 **done**。  
**Phase-3（2026-05-27 收束）**：closure **W2～W3** — 管线 Eval/编排对拍、Prompt Runtime 写路径、Skill Eval staging、Registry 幂等、Memory STM 基线 — **均已 done**（见 §2 末五行 · [`phase-3.md`](../roadmap/phase-3.md)）。  
**Phase-2（2026-05-26 收束）**：closure **P‑04～P‑08** — 写路径管线、Publish 生效链、契约收口、Admin 九场景网关 UI、TG staging 证据 — **均已 done**（见 §2 · [`phase-2.md`](../roadmap/phase-2.md)）。

---

## 2. 已实现（代码已有，本阶段默认不建包、不走 7 步）

> 仅作对照与依赖说明；phase-close 会把各阶段 `done` 项**追加**到下方表格。  
> **真源对照**：[`server/docs/PHASE1_ACCEPTANCE.md`](../../server/docs/PHASE1_ACCEPTANCE.md) · [`server/docs/TRADING_PHASE2_REMAINING.md`](../../server/docs/TRADING_PHASE2_REMAINING.md) · [`server/docs/API_INTEGRATION_GUIDE.md`](../../server/docs/API_INTEGRATION_GUIDE.md) · [`admin/FE_HANDOFF.md`](../../admin/FE_HANDOFF.md)（Admin FE 勾选清单）

<!-- PP:INVENTORY_S2:BEGIN -->

| 模块 / 能力 | 代码位置或路由（可选） | 发布版本 / 日期（可选） | 备注 |
|-------------|------------------------|-------------------------|------|
| **子账户与 OpenAPI 绑定** | `api-binding/*` · `me/agent/bindings/trading-api` · `onboarding/initiate` | 接入前 · AC-01 | validate/confirm 落库 Fernet；**无**自动开立子账户（`subaccount/create` → DEFERRED） |
| **Telegram Webhook 与会话** | `POST /webhook/telegram/{botToken}` · Admin `channels/telegram/webhook` | 接入前 · AC-02 | 未绑定引导；已绑定 → 门禁→意图→只读/`chat.faq`；现货/合约等 Type-A 见交易行 |
| **意图 NLU · 场景目录 · 只读路由** | `intent/recognize` · `scenarios` · `routing/execute` | 接入前 · AC-03 | `keyword_v1` + 可选 LLM；`read.market.*` / `read.account.balance` 等只读已通 |
| **门禁（Phase1 子集）** | `access/evaluate` · `access/reasons` | 接入前 · AC-04 | 全局关/运营暂停/未绑定阻断；**不含** VIP 实时/计费/地区完整验收 |
| **可计费执行骨架** | `execution/accept` · `finalize` · `GET …/execution/{id}` | 接入前 · AC-05 | `agent_execution` 锚点 + TG 轮次 accept→finalize；**不含** 真实按量扣费入账 |
| **Admin 登录与 JWT** | `POST /api/auth/login` · `register`（空库） | 接入前 · AC-06a | `CHAINUP_AGENT_ADMIN_CONSOLE_JWT_SECRET` 生产强制 Bearer |
| **Admin · AI Settings（Provider/Model）** | `GET\|PATCH /api/v1/admin/ai/*` | 接入前 · AC-06b | 删除 Provider 204、模型冲突 409 等 |
| **Admin · Agent 实例只读** | `GET …/admin/agents/instances*` | 接入前 · AC-06c | 列表/详情无 Secret 泄漏 |
| **Admin · 绑定运维** | `GET\|DELETE …/admin/agent/trading-bindings` | 接入前 · AC-06d | 列表无密钥列；DELETE 204 |
| **Admin · 执行记录列表/删** | `GET\|DELETE …/observability/executions*` | 接入前 · AC-06e | 与 `agent_execution` 一致；**timeline/tool-calls/llm** 见下行 Observability |
| **Prompt 包治理（CRUD/Publish）** | `admin/prompt-packs` · `internal/prompts/effective` | 接入前 · AC-09f～r | 仅 **PUBLISHED** 生效；`variableSchema` / denylist 校验；registry↔routing 同源 |
| **现货写 · 闪兑/限价** | `trade/spot/flash-convert` · `limit-order` | 接入前 · Step 2.1 | TG Type-A + TRADING 种子 0018 |
| **现货写 · 挂单/撤单** | `trade/spot/open-orders` · `POST …/trade/spot/cancel` | 接入前 · Step 2.2 | `trade.spot.open_orders` / `cancel_order` readiness=ready |
| **现货写 · 逻辑改单** | `trade/spot/amend-limit-order` | 接入前 · Step 2.x | cancel→对账→order；TG `smp`/`smx` |
| **合约写 · 市价/限价/撤单** | `trade/futures/order` · `…/cancel` | 接入前 · Step 2.3 | TG `ump`/`umx`/`ulp`/`ulx`/`EXECUTE_FUTURES_CANCEL` |
| **全仓杠杆 · 市价/限价** | `trade/margin/order` | 接入前 · Step 2.4 | 双确认 `xm1/xm2` · `xl1/xl2` |
| **条件单 · 创建/列表/撤销** | `condition-order` · `condition-orders` · `cancel-condition` | 接入前 · Step 2.5 | 场景 `automation.condition_*`；TG `cop`/`cox`/`ccp`/`ccx` |
| **504/UNKNOWN 对账 HTTP** | `POST\|GET /api/v1/agent/trading/reconcile` | 接入前 · Step §6 | `domain/trading_reconcile.py`；与 Phase-2 包 **契约收口**（`2026-05-26--trading-reconcile` **done**）不同层 |
| **Deeplink 绑定主路径** | `deeplink/` · `me/agent/bindings/trading-api` | 接入前 | 与 confirm 语义等价；见 `API_INTEGRATION_GUIDE` §4.1 |
| **只读 · 行情/余额/理财持仓/FAQ** | `routing/execute` · `chat.faq` | 接入前 | `read.market.*` · `read.account.balance` · `wealth.holdings_read` |
| **Observability Admin（列表+扩展）** | `admin/observability/executions*` · tool-calls · llm | Phase-1 · 2026-05-26 | 功能包 `2026-05-26--admin-observability` **done**；对齐 `API_ADMIN_OBSERVABILITY_EXECUTIONS.md` |
| **写路径 504 UNKNOWN 全局扩面** | 各 `post_signed_*` 写 + TG callback | Phase-1 · 2026-05-26 | 功能包 `2026-05-26--trading-write-unknown-global` **done**；依赖上行对账 HTTP |
| **NLU LLM 默认策略（API）** | `intent/recognize` · `admin/ai/defaults` | Phase-1 · 2026-05-26 | 功能包 `2026-05-26--nlu-llm-strategy` **done**；`/ai-settings` UI 债见 §4 |
| **开通欢迎语（API+运行时）** | `channels/telegram/bot` runtimeParams · TG 投递/幂等 | Phase-1 · 2026-05-26 | 功能包 `2026-05-26--telegram-welcome` **done**；补齐 AC-09o 缺口 |
| **Telegram 场景 LLM narrate** | `gateway_defaults.telegramLlmNarrate` · 9 场景 | Phase-1 · 2026-05-26 | 功能包 `2026-05-26--telegram-llm-narrate` **done** |
| **Admin Agent 实例写路径（I02/I04/I05）** | `POST/PATCH …/instances` · `binding` | Phase-1 · 2026-05-26 | 功能包 `2026-05-26--admin-agent-instance-write` **done**；FE：`agent-instances.ts` · 创建/覆盖/登记解绑（FE_HANDOFF 2026-05-25） |
| **Admin FE · 登录/注册/JWT** | `admin/` · `/login` | 接入前 · 2026-05-13～23 | `admin-auth.ts` · Bearer 注入 · 401 跳登录（FE_HANDOFF） |
| **Admin FE · AI Settings（Provider/Model/defaults）** | `AiSettingsPage.vue` · `/ai-settings` | 接入前 · 2026-05-13～20 | Provider CRUD · 模型目录 · `PATCH defaults` · 编排预算；**不含** 九场景 narrate 开关 UI（见 §4） |
| **Admin FE · Prompt 策略/安全/编辑器** | `/prompts/strategy` · `/prompts/safety` · `/prompts/editor/:id` | 接入前 · 2026-05-15～21 | 新建草稿/模板复制 · `title` 列 · fork/versions/rollback · `variableSchema` · publish |
| **Admin FE · 运行场景与编排策略** | `/ai/runtime-orchestration` | 接入前 · 2026-05-20 | `flowSummary` / `executionSteps` Drawer · `GET orchestration/policy` |
| **Admin FE · 准入 Access Control** | `/access` | 接入前 · 2026-05-15 | 白名单/封禁/VIP/灰度 · 对接 `access/*` Admin API |
| **Admin FE · 人工确认规则** | `/ai/confirmation-rules` | 接入前 · 2026-05-20 | 列表/编辑/启用 · `POST …/reset` |
| **Admin FE · Telegram 渠道配置** | `/system/channels/telegram` | 接入前 · 2026-05-20 | Bot 四段 · Webhook · self-test · `runtimeParams` PATCH（含欢迎语键） |
| **Admin FE · Observability 执行协查** | `/observability` · `/runtime/executions/:id` | 接入前 · 2026-05-13～25 | 列表/详情/时间线 · tool-calls/llm Tab · DELETE 执行 · UTC+8 展示 |
| **Admin FE · Agent 实例运维 UI** | 实例列表/详情 | 接入前 · 2026-05-14～20 | **I06** 删除 · **R01–R06** Runtime · **L01–L03** 日志深链 · G01 横幅 |
| **Admin FE · 运行时探针/联调** | `/system/agent-runtime-probe` 等 | 接入前 · 2026-05-13～14 | intent/recognize · spot quote/flash · routing/execute · 时间线枚举扩展 |
| **Skill Publish 生效链（DB + Admin + Runtime 读）** | `admin/skill-specs/*` · `internal/skills/effective` · `runtime/skill-operation-spec/effective` | Phase-2 · 2026-05-26 | 功能包 `2026-05-27--skill-publish-effective` **done**；迁移 `0029` + bundle 种子 11 skills |
| **Admin FE · 技能与工具（Publish）** | `/ai/tool-registry` · `SkillOperationDrawer` | Phase-2 · 2026-05-26 | 同上功能包；B/C/审计 Tab 占位；P1：Tab 计数与 lifecycle 徽章对齐 |

| 写路径管线（read_skill + 事件序） | 2026-05-27--runtime-write-path-pipeline | phase 2 done | **P‑04** · **P‑05** · W1 **MR-RT-B4**；含 TG/时间线；**含页面：否** · 2026-05-27 收口
| Skill Publish 生效链 | 2026-05-27--skill-publish-effective | phase 2 done | **P‑07** · W1 **SK-B1～B3/B5**；**含页面：是** · 2026-05-26 收口
| Admin AI 网关开关 UI | 2026-05-27--admin-ai-settings-gateway-ui | phase 2 done | Phase-1 FE 债 · `/ai-settings?tab=runtime` 网关策略 · 2026-05-27 收口
| 504 对账契约收口 | 2026-05-26--trading-reconcile | phase 2 done | **P‑03** / Recovery；**含页面：否** · 2026-05-26 收口
| 条件单查撤契约收口 | 2026-05-26--condition-order-list-cancel | phase 2 done | Step 2.5 · **含页面：否** · 2026-05-28 收口
| 合约撤单契约收口 | 2026-05-26--futures-cancel | phase 2 done | Step 2.3 · **含页面：否** · 2026-05-28 收口
| 主链 TG 写路径 staging 证据 | 2026-05-27--telegram-write-path-staging | phase 2 done | **P‑08** · `exec-3d132b3ad3ad44` · evidence 已填 · 2026-05-26 收口
| 管线 Eval + 编排 freeze 对拍 | 2026-05-28--pipeline-eval-orchestration-align | phase 3 done | **OP-AO3** · `eval.runtime.pipeline_write_order` · `runtime-freeze` §3 · W2 Eval；**含页面：否**
| Prompt Runtime 写路径拼装链 | 2026-05-28--prompt-runtime-assembly-write | phase 3 done | **CC-P1-04** · **OP-PR** · AC-09a～f · 写路径 TRADING 扩面；**含页面：否**
| Skill 契约 Eval staging | 2026-05-28--skill-contract-eval-staging | phase 3 done | **OP-SKILL B** · W3 **SK-B03** · `eval.skill.*` P0 真跑；**含页面：否**
| Registry toolId/skillId 幂等 | 2026-05-28--registry-tool-idempotency | phase 3 done | **CC-P1-03** · MR-E · `SC-MCV1-05` / `SC-OBS01`；**含页面：否**
| Memory STM 会话基线 | 2026-05-28--memory-stm-session | phase 3 done | **OP-MEM** · `eval.memory.session_clear_stm` · LTM 默认 OFF；**含页面：否**
<!-- PP:INVENTORY_S2:END -->

### Admin 前端页面索引（`admin/FE_HANDOFF.md` · 全部已交付）

> 下列路由 **勿** 再排 `planned`；细节与验收以 FE_HANDOFF 各节「FE 任务清单」为准。

| 路由 / 页面 | 主要 API / 能力 | FE_HANDOFF 章节（日期） |
|-------------|-----------------|-------------------------|
| `/login` | `POST /api/auth/login` · `register` | 2026-05-23 Admin register |
| `/ai-settings` | `GET\|PATCH /api/v1/admin/ai/*` | 2026-05-13～20 AI Settings |
| `/prompts/strategy` | `prompt-packs` CRUD · publish · 新建草稿 | 2026-05-15～21 策略/发布/title |
| `/prompts/safety` | `prompt-safety` · intercepts | 2026-05-20 安全防护 |
| `/prompts/editor/:promptPackId` | fork · versions · rollback · If-Match PATCH | 2026-05-20 编辑器 |
| `/ai/runtime-orchestration` | `GET scenarios` · `orchestration/policy` | 2026-05-20 执行流程编排 |
| `/ai/confirmation-rules` | confirmation-rules CRUD · reset | 2026-05-20 人工确认规则 |
| `/access` | Admin access-control | 2026-05-15 准入管理 |
| `/system/channels/telegram` | telegram/bot · webhook · runtimeParams | 2026-05-20 Bot 接入页 |
| `/observability` · `/runtime/executions` | observability/executions* · timeline · tool-calls · llm | 2026-05-13～25 可观测性 |
| Agent 实例列表/详情 | instances* · binding · I06 DELETE | 2026-05-14～25 实例 Runtime/日志/写路径 |
| `/system/agent-runtime-probe` | intent · routing · spot trade 调试 | 2026-05-13～14 探针 |
| `/ai/tool-registry` | `GET\|POST /api/v1/admin/skill-specs/*` · Publish | 2026-05-26 技能与工具 · `skill-publish-effective` **done** |

**Phase-2 Admin FE 债已清**：`/ai-settings?tab=runtime` 九场景 NLU/narrate 网关 — 功能包 `2026-05-27--admin-ai-settings-gateway-ui` **done**（2026-05-27）。

### 需补契约的已实现项（可选）

| 能力 | 建议功能 ID | 原因 |
|------|-------------|------|
| 条件单查/撤（运行时已有） | `2026-05-26--condition-order-list-cancel` | Step 2.5 已实现；Phase-2 **done** — 契约+pytest 收口 2026-05-28 |
| 合约撤单（运行时已有） | `2026-05-26--futures-cancel` | Step 2.3 已实现；Phase-2 **done** — 契约+pytest 收口 2026-05-28 |
| 504 对账 HTTP（运行时已有） | `2026-05-26--trading-reconcile` | Step §6 已实现；Phase-2 已 **done**（契约收口，非重做） |

---

## 3. 进行中 / 半成品（优先进 backlog）

| 能力 | 当前状态 | 阻塞 / 风险 | 建议功能 ID |
|------|----------|-------------|-------------|
| _（无半成品）_ | — | Phase-4 **已 reset** | 四项在 **backlog queued** · 待 **`/pipeline-product-plan`** |

---

## 4. 本阶段要做（→ 写入 roadmap backlog）

> **continuing**：由 `backlog.yaml` 切片 + `advance-phase.sh` 更新本节。  
> **brownfield 首次**：人工填写后运行 `./scripts/seed-backlog-from-inventory.sh`。  
> **与 roadmap 对齐**：[`handoff/roadmap/phase-4.md`](../roadmap/phase-4.md)

<!-- PP:INVENTORY_S4:BEGIN -->

| 优先级 | 能力名 | 一句话用户价值 | 依赖 | 建议功能 | ID |
| --- | --- | --- | --- | --- | --- |

<!-- PP:INVENTORY_S4:END -->

**指挥官下一步**：

```text
/pipeline-product-plan
```

（可附 `@product-doc/product/roadmap.md` 或 PRD 变更说明；plan 后 `./scripts/sync-backlog-from-phase.sh`）

---

## 5. 本阶段明确不做

- **roadmap P0-1 / P0-2**：纯 specs / 文档冻结项，不进入本阶段 backlog（见 `product-doc/product/roadmap.md`）
- **closure 红项（CC-P0-*）**：Hosted  rollout、矩阵延期格、账务三线、财务专户、D-5/D-7 观测等 — 须所内/运维，**非**本仓单 MR
- **P‑06 Gateway 主实现**（`call_exchange_write` 工程仓）— Phase-2 **不**排入主表
- **计费真实入账 / VIP 实时 / 地区合规** 完整门禁 — Phase1 清单 **N/A**，另立项
- **子账户自动开立** — `subaccount/create` 恒 DEFERRED
- **`trade.spot.oco` / `trade.spot.bracket`** — 寄存器 **stub**（CC-P1-01）
- **理财写路径（subscribe/redeem）**、观测聚合大盘、Memory LTM 全闭环（B）等 — 见 closure 矩阵灰/黄项，**非** Phase-4 四项范围
- **CC-P0-01 Hosted/tag** — W3 运维项，**不**进 Phase-4 backlog（除非指挥官单独立项）
- **单 MR 堆叠**：P0 管线 + Publish + Gateway — 遵守 `closure-internal-sprint` 并行纪律

---

## 6. 与 PRD 的对应关系（从哪里读 PRD）

| PRD 章节 / 位置 | 如何处理 |
|-----------------|----------|
| `product-doc/product/roadmap.md` · P0 / 阶段 A～D | §4 backlog 对齐；**已实现**对照 §2，不标 `planned` |
| `product-doc/specs/requirements/closure-completion-matrix.md` · **W1～W3** | Phase-2/3 已收口；Phase-4 对齐 **OP-BILL** · **MR-BILL-B1/B2** |
| `product-doc/development-roadmap.md` §第一阶段 | HTTP 清单参考；**非** backlog SSOT（遗留文档） |
| `server/docs/PHASE1_ACCEPTANCE.md` §1～6 | §2「接入前」勾选真源 |
| `server/docs/TRADING_PHASE2_REMAINING.md` | §2 交易写路径 Step 2.1～§6 |
| Phase-1 六项功能包 `handoff/features/2026-05-26--*` | 已 **done** → §2 末六行 + `phase-1.md` |
| `admin/FE_HANDOFF.md` | §2 Admin FE 行 + 上表路由索引；**全部 `[x]`** 表示 FE 已对接，不等价于产品 closure 全绿 |

PRD 路径（见 `pipeline.project.yaml` → `project.prd.primary`）：

- `product-doc/product/roadmap.md`

---

## 7. 非功能（本阶段共识，可选）

| 项 | 值 |
|----|-----|
| API 基址 | http://127.0.0.1:8080 |
| Admin | http://127.0.0.1:5173 |
| Deeplink | http://127.0.0.1:5174 |
| 时间 | API JSON 默认 UTC（`server/docs/BACKEND_SPEC.md` §2.1） |

---

## 8. 后续迭代（不必重走完整存量流程）

1. 在 **`handoff/product/backlog.yaml`** 调整未进当前 phase 的 `queued` / `deferred` 与优先级（本阶段行由 **plan + sync-backlog** 维护）。
2. 当前 phase 全部 `done` 后：`./scripts/advance-phase.sh`（或 `/pipeline-product-phase-close`）。
3. **roadmap 变更、需废弃本阶段未交付项**：`./scripts/plan-reset.sh`（或 `/pipeline-product-plan-reset`）→ `/pipeline-product-plan`。
4. **产品文档变更、指定 phase 对齐 / 返工规划**：`/pipeline-product-phase-realign phase-N`（见 `checklists/phase-realign.md`）。
5. 新开阶段：`/pipeline-product-plan`（自动 `./scripts/sync-backlog-from-phase.sh`）→ `/pipeline-product-contract`。

---

## 9. 变更记录

| 日期 | 变更 | 操作人 |
|------|------|--------|
| 2026-05-26 | 接入流水线 · 创建 inventory 模板 | product-agent |
| 2026-05-26 | 从 `PHASE1_ACCEPTANCE` / `TRADING_PHASE2_REMAINING` / Phase-1·2 roadmap **恢复 §2～§7** | product-agent |
| 2026-05-28 | Phase-3 五项 **planned** · `/pipeline-product-plan` · §4 切片 | product-agent |
| 2026-05-28 | Phase-4 四项 **planned** · OP-BILL · `active_phase=4` · §4 切片 | product-agent |
| 2026-05-28 | **plan-reset soft** · phase-4 归档 → `.archive/phase-4-20260527-150421.md` · 4 ID → queued | plan-reset.rb |
| 2026-05-26 | Phase-2 七项 **done** · `advance-phase.sh` 收束 · §2 rollover · §4 清空待下一迭代 | product-agent |
