# Staging 走读证据 — 2026-05-27--telegram-write-path-staging

> 对齐 SSOT：[`closure-staging-evidence-log.md`](../../../product-doc/specs/requirements/closure-staging-evidence-log.md)  
> 走查勾选：[`pipeline-walkthrough-checklist.md`](../../../product-doc/specs/requirements/Runtime/pipeline-walkthrough-checklist.md) **§2**

**禁止**：在生产真用户账户上走读（除非已书面批准并在此注明）。

---

## 1. 环境

| 项 | 填写 |
|----|------|
| **环境名** | 所内本机联调（Agent API + Telegram Bot 同机） |
| **部署版本 / Git SHA** | 与工作区 `2026-05-27--runtime-write-path-pipeline` **done** 实现一致（本地未单独打 release tag） |
| **走读日期** | 2026-05-26 |
| **执行人** | 产品协助登记（指挥官提供 `executionId`） |
| **是否使用 Mock `effective`** | **是** — 本地 Skill effective 走 bundle/mock；**截止接真 B3**：按所内运维排期 |
| **Agent API Base URL** | `http://127.0.0.1:8080` |
| **Telegram Bot（脱敏）** | 所内测试 Bot（token 不入库） |

**说明**：非生产真用户；Telegram 测试账号 **u-***7961**（`user_id` 末四位脱敏）。

---

## 2. 主轴走读 · `trade.spot.limit_order`

| 项 | 填写 |
|----|------|
| **`executionId`** | **`exec-3d132b3ad3ad44`** |
| **`sessionId`（可选）** | — |
| **Telegram 测试账号（脱敏）** | u-***7961 |
| **走读勾选完成率** | **9 / 10** 项（**90%**，§2.1～2.10；见下表摘要） |
| **勾选表附件** | 本文件 §2.1 + [`pipeline-walkthrough-checklist.md`](../../../product-doc/specs/requirements/Runtime/pipeline-walkthrough-checklist.md) §2 |

### 2.1 时间线序（SC-OBS08 / SC-OBS11）

- [x] 存在 **`agent.skill.spec_read`**（`skillId` + `skillSpecVersion`）
- [x] **`spec_read` 时间** **早于** **`confirmation.required`**
- [x] **`user.confirmed`** **早于** **首条交易所写事件**
- [x] **时间线导出**（JSON/截图/运营台导出）：

**关键事件序（DB `agent_execution_event`，共 13 条）**：

| seq | `eventName` | `created_at` (UTC) |
|-----|-------------|-------------------|
| — | `agent.skill.spec_read` | `2026-05-26T12:37:40.837710` · `skillId=skill.spot.limit_order` · `skillSpecVersion=0.2.0-e2e` |
| — | `confirmation.required` | `2026-05-26T12:37:40.842211` |
| — | `user.confirmed` | `2026-05-26T12:39:17.063597` |
| — | `trading.exchange_private` | `2026-05-26T12:39:17.688066` |

**序断言**：`assert_write_path_pipeline_order`（13 events）→ **ORDER_OK**（2026-05-26 本机 DB 复核）。

**Admin API**：`GET /api/v1/admin/observability/executions/exec-3d132b3ad3ad44/timeline` 在本机需 Bearer（JWT 已配置）；等价校验见功能包 `scripts/verify_timeline_order.py`（有 token 时可复跑）。

**走读 §2 勾选摘要（9/10）**：S1～S2、R1～R2、S4/5b、S5、S6、R3、2.6 类型 A、S8、2.9 时间线、2.10 编排 — **已验**；S9 回执与终局对拍 — **未单独截图**（扣 1 项）。

### 2.2 Eval

- [x] **`eval.runtime.pipeline_write_order`** §2 正例 **通过**（**代理**：`server/tests/test_write_path_pipeline.py` **7 passed**，含五段因果序；对齐 [`evals/pipeline-write-order.md`](../../../product-doc/specs/requirements/evals/pipeline-write-order.md)）
- [x] 负例 **P-N1**（跳过确认）**拒绝** — 见 §4 **N1**（pytest `test_invalid_skill_blocks_before_type_a_markup`）

**所内 Eval runner 链接**：待运维链入 MR；本关单以 **staging 真 `executionId` + pytest 代理** 双轨登记。

### 2.3 关联 MR / 功能包

| 项 | 填写 |
|----|------|
| **`runtime-write-path-pipeline`** | **done** · SHA 与 §1 一致：**是**（同工作区部署） |
| **MR-RT-B4** | 能力已合入单体仓；所内 MR URL 由 Runtime Owner 补链 |

---

## 3. 扩展走读（P1 · 按需增行）

| `scenarioId` | `executionId` | 结论 | 备注 |
|--------------|---------------|------|------|
| `trade.spot.amend_limit_order` | （pytest 合成） | **代理通过** | `test_telegram_amend_confirm_write_path_timeline`（TC-07）；TG staging 未另登记 id |
| `automation.condition_order_cancel` | | | 未测 |
| `trade.futures.cancel_order` | | | 未测 |

---

## 4. 负例快检（AC-6 · §3 checklist）

| # | 注入 | 预期 | 证据 |
|---|------|------|------|
| N1 | 跳过类型 A 直写 | 拒 · SC-TA01 | `server/tests/test_write_path_pipeline.py::test_invalid_skill_blocks_before_type_a_markup` — **0** `trading.exchange_private` |
| N2 | 缺数量进类型 A | 0 类型 A | 未在本环境手测；pytest 见 `eval.skill.missing_qty` 族 |
| N3 | spec_read 在确认之后 | 契约失败 | 未手测；由 `assert_write_path_pipeline_order` 覆盖 |
| N4 | Kill 开仍起新写 | FR-T05 | 未手测 |

---

## 5. 关单回填检查（AC-8）

- [x] [`closure-remaining`](../../../product-doc/specs/requirements/closure-remaining.md) **OP-AO3**、**OP-SKILL 所内** 已勾（随 P‑08 证据入库；细节见 closure 矩阵当周行）
- [x] 本文件 **已提交** 至仓库 **或** 链入所内 MR 描述
- [x] `product.accept` 可引用本文件路径
