# Staging 走读 · 证据登记（W1～W3 回填用）

**路径**：`specs/requirements/closure-staging-evidence-log.md`。

**用途**：所内在 **预发/staging** 跑通写路径后，**在本文件或 MR 评论** 填写证据；关单时链到 [`closure-remaining` §7.6 B 组](closure-remaining.md#cc-closure-exec-checklist)。

**走读勾选 SSOT**：[`Runtime/pipeline-walkthrough-checklist.md`](Runtime/pipeline-walkthrough-checklist.md) **§2**。

**禁止**：在生产真用户账户上做本表走读（除非已书面批准）。

---

## 1. 环境

| 项 | 填写 |
|----|------|
| **环境名** | staging / dev / other: ______ |
| **部署版本 / Git SHA** | ______ |
| **走读日期** | YYYY-MM-DD |
| **执行人** | ______ |
| **是否使用 Mock `effective`** | 是 / 否 — 若 **是**，**截止接真 B3 日期**：______ |

---

## 2. 主轴走读 · `trade.spot.limit_order`

| 项 | 填写 |
|----|------|
| **`executionId`** | ______ |
| **`sessionId`（可选）** | ______ |
| **Telegram 测试账号（脱敏）** | u-*** |
| **走读勾选完成率** | ___ / ___ 项（**目标 ≥80%** §2.1～2.10） |
| **勾选表附件** | MR 链接 / 勾选截图 / 粘贴勾选结果 |

### 2.1 时间线序（SC-OBS08 / SC-OBS11）

- [ ] 存在 **`agent.skill.spec_read`**（`skillId` + `skillSpecVersion`）
- [ ] **`spec_read` 时间** **早于** **`confirmation.required`**
- [ ] **`user.confirmed`** **早于** **首条交易所写事件**
- [ ] **时间线导出**（JSON/截图/运营台导出）：`________________`

### 2.2 Eval

- [ ] **`eval.runtime.pipeline_write_order`** §2 正例 **通过**
- [ ] 负例 **P-N1**（跳过确认）**拒绝** — 若测了：证据 ______

### 2.3 关联 MR

| MR | URL | 状态 |
|----|-----|------|
| **MR-RT-B4** | ______ | open / merged |
| **MR-SK-B1** | ______ | |
| **MR-SK-B2** | ______ | |
| **MR-SK-B3**（W2） | ______ | |
| **MR-BILL-B1** | ______ | open / merged |
| **MR-BILL-B2** | ______ | |

### 2.4 轨 B 计费（MR-BILL · 可与走读并行）

**Runbook**：[`billing-management/staging-mr-bill-runbook.md`](domains/admin/billing-management/staging-mr-bill-runbook.md)（本地 Dev BFF · curl · Vitest 对照）。**一键探针**：`ORIGIN=http://localhost:5173 ./scripts/staging-mr-bill-probe.sh`（**exit=0** 后粘贴下方）。

| 项 | 填写 |
|----|------|
| **`PHASE2_COMMERCE_RAILS_ENABLED`** | true / false |
| **S2 测试 `userId` + `scenarioId`** | ______ |
| **S2 阻断（remaining=0）证据** | 日志 / 截屏 ______ |
| **S5 `executionId` + `billingTraceId` join** | ______ |
| **仅 B 路径日志样例** | ______ |
| **Admin `VITE_USE_BILLING_*` 走读** | commerce / ledger API Tag 截屏 ______ |

---

## 3. 扩展走读（W2～W3 · 按需增行）

| `scenarioId` | `executionId` | 结论 | 备注 |
|--------------|---------------|------|------|
| `trade.spot.flash_convert` | | | |
| `trade.futures.market_order` | | | |
| _其他_ | | | |

---

## 4. Skill Eval（W3 · SK-B03）

| `evalSetId` | 通过 | 证据链接 |
|-------------|:----:|----------|
| `eval.skill.missing_qty_no_confirm` | [ ] | |
| `eval.skill.amend_cancel_before_order` | [ ] | |
| _（见 skill-contract.md 登记表）_ | | |

---

## 5. 关单回填检查

- [ ] [`closure-remaining` §7.6](closure-remaining.md#cc-closure-exec-checklist) **OP-AO3**、**OP-SKILL 所内** 已勾
- [ ] [`contract-closure` §8](contract-closure.md) **顶行** 已登记（适用 MR）
- [ ] 本文件 **已提交** 至规格仓 **或** 链入所内 MR **描述**

---

**文档版本**：0.1.0 · **维护**：QA + Runtime owner
