# 闭环完成度矩阵（一览 · 2026-05）

**路径**：`specs/requirements/closure-completion-matrix.md`。

**用途**：回答「**还有什么没解决**」— **一条表** **看状态**。**不** 替代 [`contract-closure.md`](contract-closure.md) DoD。

**图例**：

| 状态 | 含义 |
|------|------|
| **绿 · A** | 本 Git **规格/原型/CI** 已闭合，**可评审、可派所内** |
| **黄 · B** | 条文齐，**须所内 MR + staging 证据** |
| **红 · CC** | 契约/运维/会签，**不能对外宣称生产已冻结** |
| **灰 · 非目标** | V1 **刻意不做** |

**所内开工** → [`closure-internal-sprint.md`](closure-internal-sprint.md) · **走读** → [`pipeline-walkthrough-checklist.md`](Runtime/pipeline-walkthrough-checklist.md) · **勾选** → [`closure-remaining` §7.6](closure-remaining.md#cc-closure-exec-checklist)。

**本仓自检** → 仓库根目录 **`scripts/closure-preflight.sh`**（Skill + registry + bundle + Vitest）。**`P0` / `L1～L7` / `CC-P0` / `W1` 与主链 `P-01` 分工** → [`product/roadmap.md` · 优先级与编号对照](../../product/roadmap.md)。

---

## 0. 今日行动（W1 · 复制即用）

| 顺序 | 谁 | 动作 | 模板 |
|:----:|-----|------|------|
| 1 | 全员 | 跑 **`./scripts/closure-preflight.sh`** | — |
| 2 | PM/TL | 建 **3 张工单**（RT-B4、SK-B1、SK-B2） | [`closure-work-item-templates.md`](closure-work-item-templates.md) |
| 3 | Runtime | 开 MR，粘贴 [`internal-sprint` §3.1](closure-internal-sprint.md#mr-rt-b4-pipeline) | 阶段标 **B** |
| 4 | BFF | 开 MR-B1/B2，粘贴 **§3.2** | 可与 3 **并行** |
| 5 | QA | staging 走读后填 | [`closure-staging-evidence-log.md`](closure-staging-evidence-log.md) **§2** |

**W1 完成定义**：走读 **§2.1～2.10 ≥80%** + **§2** 证据表 **有 `executionId`** + **三张 MR** 已开（可未合并）。

---

## 1. 端到端写路径（你关心的主链）

| ID | 主题 | 状态 | 本仓已交付 | 仍须（所内/运维） |
|----|------|:----:|------------|-------------------|
| **P-01** | 概念十步 / S1～S10 对照 | **绿** | [`domain-model.md`](Runtime/domain-model.md) | — |
| **P-02** | Risk 闸 R1～R4 | **绿** | domain-model §2 | Runtime **实现各时点** |
| **P-03** | Receipt / Timeline / 计费三轨 | **绿** | domain-model §3 | 用户话术 copy deck |
| **P-04** | `read_skill` 先于类型 A | **绿** | production-runtime、SC-OBS11、Admin 卡 | **SK-B02** 真编排 |
| **P-05** | 管线事件序 | **绿** | Eval + `writePathPipelineOrder` Vitest | staging **`eval.runtime.pipeline_write_order`** |
| **P-06** | `call_exchange_write` / Gateway | **黄** | ADR-004 文档、CC-P1-07 | **所内工程仓 Gateway** |
| **P-07** | Publish 生效读规范 | **黄** | bundle、OpenAPI 草案、控制台原型 | **SK-B01～B03** DB/BFF |
| **P-08** | 用户 Telegram 真下单 | **黄** | flows、telegram §2.5 | **MR-RT-B4** + B3 + Gateway **联调** |

---

## 2. 契约关单（CC-P0 / P1）

| ID | 状态 | 关单动作 |
|----|:----:|----------|
| **CC-P0-01** Hosted/tag | **红** | [`openapi/HOSTED-ROLLOUT-CHECKLIST.md`](../openapi/HOSTED-ROLLOUT-CHECKLIST.md) · MR 稿 [`contract-closure` §3.4](contract-closure.md#cc-p0-mr-github-full) |
| **CC-P0-02** 矩阵延期格 | **红** | 所内 PATH 冻结或延期终版 · §4/§7 MR |
| **CC-P0-03** 账务三线 | **红** | 生产 baseUrl · shadow→enforce · 实现 MR |
| **CC-P0-04** 财务专户 | **红** | §2.1 会签 + 首填 |
| **CC-P0-05** D-5/D-7 观测 | **红** | §10.3.1 勾选 · UNKNOWN Runbook |
| **CC-P1-04** Prompt Runtime B | **黄** | MR-B 会签 · [`§7.2～§7.4`](closure-remaining.md#cc-ac09-closure-matrix) |
| **CC-P1-06** Telegram Webhook | **红** | setWebhook 生产实测 |
| **CC-P1-07** Gateway 实现 | **黄** | [`internal-sprint` §3.4](closure-internal-sprint.md#mr-gw-gateway) |
| **CC-P1-03** Registry 幂等 | **黄** | MR-E |
| **CC-P1-01** OCO/bracket 写 | **灰** | [`product.md`](product.md) 非目标 |

---

## 3. 横切能力

| ID | 状态 | 本仓 | 所内 |
|----|:----:|------|------|
| **OP-AO3** 编排 §3 对拍 | **黄** | runtime-freeze、walkthrough | 轨迹/单测 · **MR-RT-B4** |
| **OP-SKILL** L0 + Publish | **绿** / **黄** | 规格+原型 **绿**；真跑 **黄** | SK-B01～05 |
| **OP-PR** Prompt 拼装 | **黄** | runtime-injection 条文 | AC-09a～f 实现 |
| **OP-MEM** Memory | **黄** | **memory-runtime §14.6**、**clarify-session**、Eval P0 已登记 | **STM §16 硬闸 + §2.3 + stale/Resume** 实现 MR · 所内 CI P0 eval |
| **OP-NAR** 盘感 | **黄** | market-intelligence、schemas | phase 注入 + Publish |
| **OP-09Q** registry↔routing | **绿** | GHA + Python 脚本 exit=0 | 非 GHA 宿主另配流水线 |
| **OP-BILL** Phase 2 商业轨 | **绿** / **黄** | OpenAPI + `productionRuntime` S2/S5 + Admin Commerce 演示卡 **绿**；所内 HTTP **黄** | **MR-BILL-B1/B2** · [`closure-internal-sprint`](closure-internal-sprint.md) |

---

## 4. 本仓 CI / 原型（可自证「A 已闭合」）

| 检查 | 命令 / 位置 |
|------|-------------|
| Skill 正文完整 | `python3 specs/requirements/skill-specs/scripts/check_skill_contract_complete.py` |
| Publish bundle | `node …/build_runtime_publish_bundle.mjs --check` |
| Registry ⊆ routing | `python3 …/check_registry_vs_routing_engine.py` |
| 写路径时间线序 | `cd src/admin && npm test -- writePathPipelineOrder` |
| 时间线+spec_read | `npm test -- mock.timeline.contract` |
| GHA | `.github/workflows/skill-contract-consistency.yml` · `prompt-registry-consistency.yml` |

---

## 5. 所外交付包（无法在本 Git 关闭）

**单一工单附件**：复制 [`closure-internal-sprint.md` §2](closure-internal-sprint.md) **勾选表** + 对应 **§3 MR 粘贴稿**。

| 周 | 交付物 | 验收 |
|:--:|--------|------|
| W1 | MR-RT-B4 + SK-B1/B2 | pipeline-walkthrough §2 ≥80% |
| W2 | SK-B3 + MR-GW-01 | eval.pipeline staging + Gateway PATH |
| W3 | CC-P0-01 + eval.skill.* | Hosted URL + §7.6 B 组勾选 |
| W4（可选） | MR-B Prompt · Memory/NAR MR | §7.2～§7.4 右列证据 |

---

## 6. 对外话术边界（避免误承诺）

**可以说**：需求与原型 **可对签**；写路径 **产品顺序** 已冻结；Admin **演示** 时间线符合 SC-OBS08/11。

**不能说**：生产 Runtime 已闭环；Hosted 契约已冻结；OCO/bracket 经 Agent 可写；按 execution 单价计费；Memory LTM 默认 ON。

**升格** [`spec.md`](spec.md) / 对客「生产承诺」→ 仅当 [`contract-closure` §5.1](contract-closure.md#cc-stage4-spec-gate) **P0+相交 P1 证据齐**。

---

**文档版本**：0.1.2 · **维护**：产品 + 收口 owner · **本版**：**§3 OP-BILL**（Phase 2 商业轨 · 规格/原型 **绿** · 所内 **黄**）。**承** **0.1.1**。
