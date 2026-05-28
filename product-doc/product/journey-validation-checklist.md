# 用户旅程抽检 · 勾选表（JV-01～JV-13）

**用途**：QA / 产品 / 联调 **staging 或生产抽检** 时 **逐条勾选**。**条文 SSOT** → [`journey-validation.md`](./journey-validation.md)；**不**替代 FR/SC。

**登记**：`eval.product.user_journey_chain` · [`evals/scenarios.md`](../specs/requirements/evals/scenarios.md)

**自查批次**：2026-05-27 · preflight **OK**（`./scripts/closure-preflight.sh`）

---

## 抽检头信息

| 项 | 填写 |
|----|------|
| **日期** | |
| **环境** | staging / prod / 其他 ______ |
| **执行人** | |
| **构建 / 部署 SHA** | |
| **Telegram Bot** | @______ |
| **备注** | |

---

## 总表（Pass / Fail / N/A）

| ID | 主题 | 关联 eval（抽检） | Pass | Fail | N/A | 缺陷单 / 备注 |
|----|------|-------------------|:----:|:----:|:---:|---------------|
| **JV-01** | 冷启动 · 无实例绑定 | — | [ ] | [ ] | [ ] | |
| **JV-02** | 绑定 §1.2 校验失败 | FR-WEB06 | [ ] | [ ] | [ ] | |
| **JV-03** | VIP 门禁（母账号） | eligibility | [ ] | [ ] | [ ] | |
| **JV-04** | 写路径 · 未确认不得写 | `eval.hitl.write_without_confirm` | [ ] | [ ] | [ ] | |
| **JV-05** | 轨 B 账单 Deeplink | `staging-mr-bill-probe` | [ ] | [ ] | [ ] | |
| **JV-06** | 504 / UNKNOWN 话术 | `eval.obs.504_unknown_write` | [ ] | [ ] | [ ] | |
| **JV-07** | 九步可运行 · 全 scenarioId | `eval.trade.spot.flash_convert.gwt` 等 | [ ] | [ ] | [ ] | |
| **JV-08** | Webhook 重复 Update | `eval.runtime.telegram_update_idempotent` | [ ] | [ ] | [ ] | |
| **JV-09** | Kill/Pause 拒新写 | `eval.runtime.global_pause_blocks_new_write` | [ ] | [ ] | [ ] | |
| **JV-10** | Goal 七维 | goal-and-execution-paths §5 | [ ] | [ ] | [ ] | |
| **JV-11** | 黄金路径八维 | goal-and-execution-paths §6 | [ ] | [ ] | [ ] | |
| **JV-12** | 阶段话术 · 类型 A 对账 | `eval.runtime.user_visible_phase_copy` | [ ] | [ ] | [ ] | |
| **JV-13** | **澄清僵尸链 · stale+Resume** | **`eval.memory.stm_governance_regression`** · **`idle_default_stale`** · **`resume_classifier_*`** · **`clarify.*`** | [ ] | [ ] | [ ] | |
| **JV-14** | **会话并发 · 连发/挡新写** | **`eval.session.*`** · **`SC-AO-09～10`** | [ ] | [ ] | [ ] | |
| **JV-15** | **只读澄清 · scope/写打断** | **`eval.read_clarify.*`** · **`SC-READ-CLARIFY-*`** | [ ] | [ ] | [ ] | |
| **JV-16** | **UNKNOWN 追问 · 状态机** | **`eval.unknown.*`** · **`SC-RISK-07*`** | [ ] | [ ] | [ ] | |

**通过准则**：**P0 路径（JV-04、JV-08、JV-13、JV-14）** **须 Pass** **方可** **宣称 Memory/Telegram 主链 staging 就绪**；**JV-15～16** **P1** **建议 Pass**；其余 **Fail** **须** **登记 Owner + 缺陷单**。

---

## JV-13 逐步勾选（重点 · 生产负例）

**Given**：写澄清 pending（BNB 买入缺 spot 方式）· `ClarifySessionSnapshot` active

| 步 | When | Then（勾选） | Pass |
|----|------|--------------|:----:|
| 0 | idle/TTL 先达 | `lifecycleState=stale` · 活跃 L1 不含 stale 摘要 | [ ] |
| 1 | 「你好」 | 寒暄 · `abandoned=true` · 0 闪兑/限价写澄清 | [ ] |
| 2 | 「有哪些币可以买」 | 只读/listing · 0 写澄清复读 · 0 routing 内部词 | [ ] |
| 3 | 「都不要了」 | abandoned · 短句确认 · 0 写澄清 | [ ] |
| 4+ | 「还是买 BNB 100U 闪兑」 | 温召回 + Fresh Facts · 非模板复读 | [ ] |
| 5 | 两条 stale episode +「再来一笔」 | 默认 `staleAt` 最近 episode | [ ] |
| 6 | `pending_confirm` 存活 + idle inbound | 类型 A 优先 · 0 写澄清覆盖 | [ ] |

**executionId 证据**：________________ · **时间线 / 日志**：________________

---

## JV-14 逐步勾选（会话并发 · P0）

**SSOT**：[`session-concurrency-policy.md`](../specs/requirements/domains/agent/agent-orchestration/session-concurrency-policy.md)

| 步 | When | Then（勾选） | Pass |
|----|------|--------------|:----:|
| 1 | 1s 内连发「买 BNB」「100 USDT」 | ≤1 Parser 链或 coalesce · 槽位合并正确 | [ ] |
| 2 | 类型 A 待确认 + 「改买 ETH」 | 0 第二张无关类型 A · 可读挡新写 | [ ] |
| 3 | `unknown_pending` + 新写 | 0 新 `call_exchange_write` · FR-T05 族 | [ ] |
| 4 | 逻辑改单 cancel 已发 + 新 symbol 写 | 挡或 abort 后可写 · 用户可见区分 | [ ] |
| 5 | in-flight message + 点 `cl:fc` | 串行 · 0 槽位 lost update | [ ] |

---

## JV-15 逐步勾选（只读澄清 · P1）

**SSOT**：[`read-clarify-session.md`](../specs/requirements/domains/agent/agent-orchestration/read-clarify-session.md)

| 步 | When | Then（勾选） | Pass |
|----|------|--------------|:----:|
| 1 | 「盈亏怎么样」 | scope 澄清（市场 vs 持仓）· 0 写 | [ ] |
| 2 | 「BTC 和 ETH 哪个涨得多」 | 收敛后一次答复 · 0 假澄清复读 | [ ] |
| 3 | 只读澄清中「买 100U BNB」 | 读 abandoned · 转写澄清 | [ ] |
| 4 | 「涨到 10 万提醒我」草案齐 | 0 rc 直接创建任务 · 须类型 A | [ ] |

---

## JV-16 逐步勾选（UNKNOWN 追问 · P1）

**SSOT**：[`unknown-stall-policy.md`](../specs/requirements/risk/unknown-stall-policy.md) **§2**

| 步 | When | Then（勾选） | Pass |
|----|------|--------------|:----:|
| 1 | 504 后「成交了吗」 | 有界 reconcile/只读 · 0 SUCCESS 语气 | [ ] |
| 2 | 「再试一次买 100U BNB」 | 0 同参自动重放 | [ ] |
| 3 | 「另外买 ETH」 | 0 新写 · FR-T05 族 | [ ] |
| 4 | 「查一下挂单」 | 只读答 + UNKNOWN 一行提醒 | [ ] |
| 5 | 可撤时「取消上一笔」 | 类型 A 或 Explain · 0 假撤成功 | [ ] |

---

## JV-07 走读附件（可选）

- [ ] [`pipeline-walkthrough-checklist` §2](../specs/requirements/Runtime/pipeline-walkthrough-checklist.md) **≥80%**
- [ ] [`e2e-closed-loop` Walkthrough](../flow/e2e-closed-loop.md#runtime-walkthrough-crosscut) **Goal-PIPE / Goal-MEM-STM**

---

## 维护

- 条文变更 → 同步 [`journey-validation.md`](./journey-validation.md)
- 关单路径 → [`closure-remaining` §7.6](../specs/requirements/closure-remaining.md#cc-closure-exec-checklist)

**文档版本**：1.0.3 · **维护**：产品 + QA · **本版**：**JV-16 UNKNOWN 追问**。
