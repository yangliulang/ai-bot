# 主链 TG 写路径 staging 证据

> 功能 ID：`2026-05-27--telegram-write-path-staging`  
> 产品 Agent 定稿 · Phase-2 **P2** · closure **P‑08** · W1 走读 §2

## 背景

closure **P‑08** 要求所内在 **预发/staging** 对 **Telegram 真写路径** 留存可审计证据：**`executionId`**、走读勾选、时间线序与 **`eval.runtime.pipeline_write_order`** 正例。

**`2026-05-27--runtime-write-path-pipeline`** 已在代码侧交付 **read_skill + 五段因果序**（pytest 可断言）；本包 **不新增 Runtime API**，而是把 **staging 走读 + 证据登记** 固化为功能包交付物，对齐 `product-doc/specs/requirements/closure-staging-evidence-log.md` 与 **`Runtime/pipeline-walkthrough-checklist.md` §2**。

## 用户故事

- 作为 **QA/Runtime Owner**，我需要在 staging 跑通 **`trade.spot.limit_order`** TG 类型 A 写路径，并登记 **`executionId`** 与时间线导出，供 closure 关单。
- 作为 **产品/指挥官**，我希望证据与 **`runtime-write-path-pipeline`** 的 AC-2～AC-3 **可对照**，且 **禁止** 用生产真用户冒充通过。
- 作为 **后端**，我提供 **证据模板 + 验收用例**；走读在 staging 执行，本地 pytest 作为 **回归门禁代理**（非替代 staging 真跑）。

## 验收标准

- [x] **AC-1**：`staging/evidence-log.md` **§1 环境** 已填写：**环境名**、**部署 Git SHA**、**走读日期**、**执行人**；**Mock effective** 声明（是/否及截止日）；**非** 生产真用户（除非 brief 待确认已书面批准）。
- [x] **AC-2**：**主轴** **`trade.spot.limit_order`**：staging 完成 Telegram **类型 A → 写** 回合；**`executionId`** 写入 evidence **§2**；[`pipeline-walkthrough-checklist.md`](../../../product-doc/specs/requirements/Runtime/pipeline-walkthrough-checklist.md) **§2.1～2.10** 勾选 **≥80%**（附 MR 链接/截图/粘贴勾选）。
- [x] **AC-3**：对 AC-2 的 **`executionId`**，时间线证明 **`agent.skill.spec_read`** **早于** **`confirmation.required`**（或等价确认事件）**早于** 首条 **`trading.exchange_private`**（**SC-OBS08/11**）；证据为 **§2.1 导出** 或 **`GET …/observability/executions/{executionId}/timeline`** 排序结果。
- [x] **AC-4**：evidence **§2.2**：**`eval.runtime.pipeline_write_order`** **正例通过**（附 Eval 输出路径、日志或 MR 评论链接）。
- [x] **AC-5**：evidence **§2.3** 登记依赖包 **`2026-05-27--runtime-write-path-pipeline`** 为 **done**，且走读环境部署 **SHA** 与 §1 一致（或说明差异原因）。
- [x] **AC-6**：evidence 记录 **负例快检 ≥1 项**（[`pipeline-walkthrough-checklist.md` §3](../../../product-doc/specs/requirements/Runtime/pipeline-walkthrough-checklist.md) **N1～N4** 之一）：**预期拒写/契约失败**，附摘要（日志/用例 id/截图）。
- [x] **AC-7**：（P1）evidence **§3 扩展走读** 至少填 **1 行**（如 **`trade.spot.amend_limit_order`**、**`automation.condition_order_cancel`** TG 路径）。
- [x] **AC-8**：evidence **§5 关单回填**：**OP-AO3** / closure 项已勾；本文件 **已提交仓库** 或 **链入** 所内 MR 描述（对齐 [`closure-staging-evidence-log.md` §5](../../../product-doc/specs/requirements/closure-staging-evidence-log.md)）。

## 范围

### 本期包含

- 功能包 **`staging/evidence-log.md`**（可填模板，对齐产品 SSOT）。
- **`brief.md`**、**`api.openapi.yaml`**（验收用 **Admin 时间线** 读接口）、**`test/*`** 追溯。
- **`staging/walkthrough.md`**：走读步骤索引与 TG 测试账号约定（脱敏）。
- **backend.implement**：不强制新代码；可增 **证据校验脚本/notes**（可选 curl 拉 timeline）。
- **test.api**：pytest **代理回归**（`test_write_path_pipeline.py`）+ staging 手工证据审查。

### 本期不包含

- **新 Runtime 行为**（属 **`runtime-write-path-pipeline`**，已 done）。
- **Skill Publish Admin UI**（已 **`skill-publish-effective`** done）。
- **生产环境走读**（默认禁止）。
- **全量 A 类写场景** staging（仅主轴 **必做**；扩展 **P1**）。

## 界面与交互（无页面）

**含页面：否**。走读可使用 **Admin Observability 存量页** 导出时间线；本包 **不** 新增 Admin 路由。验收 = **证据文件 + timeline API + Eval 登记**。

## 非功能要求

- **禁止** 在 evidence 中写入 API Secret、规范全文、用户 PII（Telegram id 脱敏 **u-***）。
- staging 走读与本地 pytest **分工明确**：pytest **不替代** staging 真跑登记（见 `test/cases.md` **STG** 与 **TC** 标注）。

## 实现备注

| 项 | 路径 |
|----|------|
| 走查 SSOT | `product-doc/specs/requirements/Runtime/pipeline-walkthrough-checklist.md` |
| 证据 SSOT | `product-doc/specs/requirements/closure-staging-evidence-log.md` |
| Eval | `product-doc/specs/requirements/evals/pipeline-write-order.md` |
| 依赖功能包 | `handoff/features/2026-05-27--runtime-write-path-pipeline/` |
| 本地回归 | `server/tests/test_write_path_pipeline.py` |

## 待确认问题

- [x] Q1：首版 **主轴** 仅强制 **`trade.spot.limit_order`**；合约/条件单 TG 走 **§3 扩展 P1**。
- [x] Q2：**含页面：否**；E2E 门禁 = staging 走读证据，非浏览器 E2E 用例表。
- [ ] Q3：所内 **staging Base URL** 与 **Bot** 由运维在 `staging/walkthrough.md` 填写（contract 阶段占位）。
