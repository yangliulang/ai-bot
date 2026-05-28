# Skill Specs · 需求层闭环（L0 写路径）

**路径**：`specs/requirements/skill-specs/requirements-closure.md`。

**用途**：声明 **本 Git 仓库内** **Skill 操作规范（L0）** 在 **需求阶段（A）** 的 **闭环范围、DoD 与追溯矩阵**。**不**替代 [`contract-closure.md`](../contract-closure.md) **全文**；**不**宣称 **Runtime Publish / 生产 Hosted** 已关闭（**B** → **OP-SKILL** [**§7.5**](../closure-remaining.md#cc-remaining-open-close-path)）。

**本仓范围（统一表述）**：

| 层级 | 含义 | **是否在本仓宣告完成** |
|------|------|:----------------------:|
| **规格对齐** | `specs/` 正文、FR/SC、OpenAPI 草案、Eval 条文、`runtime-bundle.json`、CI 门卫 | **是**（§3） |
| **原型对齐** | `src/admin` Demo：登记镜像、规范解析预览、Publish **交互叙事**（本地/可选 Mock，**非**生产落库） | **是**（§3.4～§3.6） |
| **所内实现** | BFF、DB、`read_skill_operation_spec` 真链路、`eval.skill.*` 真跑、Registry API | **否**（§4 · [`MR-B-BFF-IMPLEMENTATION.md`](./MR-B-BFF-IMPLEMENTATION.md)） |

**同窗 OP 索引**：[`closure-remaining.md` · OP-SKILL](../closure-remaining.md#cc-remaining-open-close-path)。

---

## 1. 闭环定义（两阶段）

| 阶段 | 含义 | **本篇是否宣告完成** |
|------|------|:--------------------:|
| **A · 需求文档闭合** | FR/SC、L0 正文、登记、Eval 条文、OpenAPI 草案、Admin 预览 IA、CI 门卫 **均在 `specs/` 可对签** | **是**（**§3 勾选**） |
| **B · 可对客 / 生产** | `read_skill_operation_spec` **Publish 生效**、Hosted、**`eval.skill.*` 真跑**、Registry API、矩阵数值冻结 | **否**（**§4 开放项**） |

**与 [`contract-closure` §3.0](../contract-closure.md#cc-p1-doc-vs-b) 对齐**：**可进开发 / 评审** **≠** **§1.2 六款全开** **≠** **对外「生产契约已冻结」**。

---

## 2. 追溯矩阵（需求真源）

| 主题 | 需求 / 设计 SSOT | 验收 / 抽检 | 契约 / 登记 |
|------|------------------|-------------|-------------|
| **写前读规范 · FR-T11** | [`trade-assistance` §2](../domains/agent/exchange-agent/trade-assistance.md) | [`confirmation-flow`](../domains/agent/agent-orchestration/confirmation-flow.md) **SC-TA*** | [`trade-assistance` §4](../domains/agent/exchange-agent/trade-assistance.md) |
| **单行登记 · FR-TS07** | 同上 **§4·§8** | — | [`manifest.yaml`](./manifest.yaml) |
| **L0 正文 S-01～S-09 + amend** | [§3 清单](./README.md#3-目录与清单s-01s-09) | [`evals/skill-contract.md`](../evals/skill-contract.md) | 各 `skill.*.md` |
| **Publish 规则** | [`PUBLISH.md`](./PUBLISH.md) | §4 DoD · CI | [`prompt-management/functions` §1.4](../domains/admin/prompt-management/functions.md) |
| **PRS 派工** | [`prompt-runtime/README` §4](../prompt-runtime/README.md#prs-where-to-edit) | — | L0 = `skill-specs/` |
| **路由寄存器** | [`routing-engine` §2](../domains/agent/agent-orchestration/routing-engine.md) | [`registry` `skill_spec` 列](../prompts/library/scenarios/registry.md) | **§4 表同窗** |
| **流程专节** | [`trade-via-agent`](../flows/trade-via-agent.md)、[`wealth-via-agent`](../flows/wealth-via-agent.md) | 流程 GWT | — |
| **概念管线对签** | [`Runtime/domain-model`](../Runtime/domain-model.md) **§1～§4** | 走读 / 所内 MR-B4 | — |
| **控制台镜像** | [`tool-management/functions` FR-TM06](../domains/admin/tool-management/functions.md) | **SC-TM-13～16** | [`admin-console/demo-routing`](../admin-console/demo-routing.md) |
| **OpenAPI 草案** | [`PUBLISH` §6](./PUBLISH.md) | — | [`skill-operation-spec-schemas.yaml`](../../openapi/components/skill-operation-spec-schemas.yaml)、[`admin/prompt-management.yaml`](../../openapi/admin/prompt-management.yaml) |
| **CI** | 本篇 §3 | Vitest P0 | [`skill-contract-consistency.yml`](../../.github/workflows/skill-contract-consistency.yml) |

---

## 3. 需求层 DoD（A 阶段 · 可勾选）

**MR 宣称「Skill L0 需求已闭合」时，下列条目须全部为真（**本仓 `specs/` + 已挂 CI**）：

### 3.1 正文与清单

- [x] **11** 篇 `publishRequired: true` 技能 **`contract-complete`**（§1～§6 自包含）— `check_skill_contract_complete.py`
- [x] **2** 篇逻辑改单 **contract-complete**（`skill.spot|futures.amend_limit_order`）
- [x] **OCO / Bracket / 划转** 在 **§4·manifest** 登记为 **非目标 / 主站 / FR-T05**（**无** L0 正文，**非** 欠账）
- [x] [`README.md`](./README.md) **S-01～S-09** 与 **§4 `scenarioId` 映射** 同窗
- [x] [`TEMPLATE.md`](./TEMPLATE.md) 与金样 [`skill.spot.limit_order`](./spot/skill.spot.limit_order.md) 可对评审

### 3.2 编排与产品边界

- [x] [`trade-assistance` §4](../domains/agent/exchange-agent/trade-assistance.md) **操作规范列** 链至 Git 文件（**含** 改单 **2** 行）
- [x] [`product.md` §非目标](../product.md) **与** OCO/Bracket **登记** 一致
- [x] [`routing-engine`](../domains/agent/agent-orchestration/routing-engine.md) **写路径 `scenarioId`** 与 **§4** **无未登记漂移**（**09q** registry 脚本同窗）
- [x] [`confirmation-flow`](../domains/agent/agent-orchestration/confirmation-flow.md) **类型 A** 与 **§3 确认卡** 叙事一致

### 3.3 Eval 与门卫

- [x] [`evals/skill-contract.md`](../evals/skill-contract.md) **登记** **P0 束**（**≥4** 条）与 **分主题构造要点**
- [x] **Vitest**：`src/admin/src/skillContract/` + **`skillRegistry*`**（**`npm test`**）
- [x] **Python**：`check_skill_contract_complete.py` + **`check_registry_vs_routing_engine.py`**（**skill-contract-consistency** workflow）

### 3.4 控制台（需求 + Demo 对齐）

- [x] **FR-TM06**、**SC-TM-13～16** 已写入 [`tool-management/functions.md`](../domains/admin/tool-management/functions.md)
- [x] [`admin-console-tool-registry-reconciliation.md`](../domains/admin/tool-management/admin-console-tool-registry-reconciliation.md) **§0** · [`admin-console`](../admin-console/README.md)、[`config.md`](../domains/admin/tool-management/config.md)、[`demo-routing`](../admin-console/demo-routing.md) **标明** `/ai/tool-registry` **原型 SSOT（非生产 Registry / 非 Runtime Publish UI）**
- [x] [`page-specs` · `ai.tool-registry`](../admin-console/page-specs.md) **低保真** 已载

### 3.5 Publish 与 OpenAPI（文档轨）

- [x] [`PUBLISH.md`](./PUBLISH.md) **数据流、`skillSpecVersion`、`PROMPT_SKILL_REF_INVALID`**
- [x] [`prompt-management/functions`](../domains/admin/prompt-management/functions.md) **Publish 技能全文** 与 **§1.4** 同窗
- [x] OpenAPI **组件** + **admin 路径草案** 已登记（**所内接线**见 §4）

### 3.6 Runtime Publish · 原型与规格对齐（非生产实现）

**叙事 SSOT**：[`PUBLISH.md`](./PUBLISH.md)。**下列为规格/原型可对签，不等于所内已上线。**

- [x] **规格**：[`published/runtime-bundle.json`](./published/runtime-bundle.json)（import 参考快照）+ [`build_runtime_publish_bundle.mjs`](./scripts/build_runtime_publish_bundle.mjs) + CI **`--check`**
- [x] **规格**：[`MR-B-BFF-IMPLEMENTATION.md`](./MR-B-BFF-IMPLEMENTATION.md)（所内 MR 拆单 + DDL 草案）
- [x] **原型**：`/ai/tool-registry` — 登记、§1～§6 解析、**启用/停用**（**SC-TM-16**）；**不** 展示 Runtime 发布 UI（**SC-TM-17～18** → MR-B）；Prompt **Runtime 技能范围（发布门禁）** 校验（**SC-PM-21** 演示口径）· [`PUBLISH.md` §7.1](./PUBLISH.md#71-admin-原型--交付边界srcadmin)
- [x] **原型**：Prompt 编辑器 — **`skillSpecRef` Publish 门禁** 提示（**SC-PM-21** · `promptPublishGate`）
- [x] **可选联调**：`src/admin` 内 **OpenAPI 路径 Mock**（`skillSpecBff*`）— **仅** 本地 `npm run dev`，**非** 关单交付物
- [x] **SC-TM-13～16、19**、**page-specs** 已覆盖登记/抽屉/启用与 Prompt 门禁；**SC-TM-17～18** **所内** Publish UI（**Demo 刻意不展示** · [`PUBLISH` §7.1](./PUBLISH.md#71-admin-原型--交付边界srcadmin)）

### 3.7 Production Runtime 读规范（`read_skill_operation_spec` · 规格 + 原型）

**SSOT**：[`production-runtime.md`](./production-runtime.md)。**所指**：编排/终端写路径在 **类型 A 前** 加载 **已发布** 技能全文 — **非** Admin「发布按钮」本身。

| 维度 | 状态 | 落点 |
|------|------|------|
| **规格 · 写路径序 / 失败 / 观测** | **已对齐** | 本篇 **§1～§3**；**FR-T11**、**FR-AO04**、**SC-OBS11**、**SC-OM-05** |
| **原型 · 执行详情** | **已对齐** | **`runtime.execution-detail`**：**Timeline** **`agent.skill.spec_read`** + **总览「技能规范」卡**（`SkillSpecReadSummary` · Demo **`exec-aa11`**） |
| **原型 · 读 API 演示** | **已对齐** | `readSkillOperationSpec`（本地/Mock）；**Publish** 快照同窗 **SC-TM-17** |
| **原型 · 槽位门禁** | **已对齐（下限）** | `skillContract/gates.ts` + Vitest（**非** Telegram E2E） |
| **所内 · 真 Runtime** | **开放** | **SK-B02** · [`MR-B-BFF-IMPLEMENTATION` §2 MR-B4](./MR-B-BFF-IMPLEMENTATION.md) |

---

## 4. B 阶段开放项（不阻塞 A，但阻塞「全闭环 / 对客 B」）

| ID | 主题 | 所内须完成 | 入口 |
|----|------|------------|------|
| **SK-B01** | **Publish 落库** | **规格**：`runtime-bundle.json`；**原型**：控制台 Publish 交互；**所内**：prompt-management DB | [`PUBLISH.md`](./PUBLISH.md) · [`published/`](./published/README.md) |
| **SK-B02** | **Runtime 读规范** | **规格+OpenAPI**；**原型**：本地/Mock 读路径演示；**所内**：编排 `read_skill_operation_spec` | [`MR-B-BFF-IMPLEMENTATION.md`](./MR-B-BFF-IMPLEMENTATION.md) |
| **SK-B03** | **Eval 真跑** | P0：`missing_qty`、`flash` 分流、`margin` 双确认、`amend` 序 | [`evals/skill-contract.md`](../evals/skill-contract.md) |
| **SK-B04** | **Registry 生产 API** | **CC-P1-03** DB/镜像与 §8 幂等 | [`tool-management/functions`](../domains/admin/tool-management/functions.md)、**MR-E** |
| **SK-B05** | **矩阵数值** | tick/step/minNotional、**conditionOrder** PATH 解冻 | [`design/api.md`](../../design/api.md)、**§4·§7** MR |

---

## 5. 变更纪律（维持 A 闭合）

1. **改 L0 正文** → 同 MR 更新 **`manifest.yaml`**（若 `publishRequired`）、**`trade-assistance` §4**、**`registry` `skill_spec` 列**（若 `scenarioId` 变）。  
2. **改登记行** → 同步 **`skillRegistryCatalog`**（Demo 单源）与 **§8.2**。  
3. **新增 `publishRequired` 技能** → 须 **contract-complete** 后 CI 才绿。  
4. **禁止** 仅在控制台改正文 **不同步** Git（[`PUBLISH` §1](./PUBLISH.md)）。

---

## 6. 上级索引

| 文档 | 关系 |
|------|------|
| [`skill-specs/README.md`](./README.md) | L0 SSOT · **§6.1** 状态摘要 |
| [`closure-remaining.md` · OP-SKILL](../closure-remaining.md#cc-remaining-open-close-path) | 关单总表 |
| [`contract-closure.md`](../contract-closure.md) | 全产品 DoD（**不** 因本篇替代） |
| [`product.md`](../product.md) | 范围与非目标 |

---

**文档版本**：1.3.0 · **维护**：产品 + Agent Runtime owner · **本版**：**§3.7** 对齐 [`production-runtime.md`](./production-runtime.md) **与** 执行详情原型。**承** 1.2.0。
