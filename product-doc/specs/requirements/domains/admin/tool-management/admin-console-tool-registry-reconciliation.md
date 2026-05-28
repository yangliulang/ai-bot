# 运营台 · 技能与工具页对齐（`ai.tool-registry`）

**路径**：`specs/requirements/domains/admin/tool-management/admin-console-tool-registry-reconciliation.md`  
**读者**：产品、后台、Skill/Prompt 联调  
**端到端鸟瞰**：[`flow/e2e-closed-loop.md`](../../../../flow/e2e-closed-loop.md) **阶段 F · `TOOL_REG`** · [**运营台 Demo IA 锚点表**](../../../../flow/e2e-closed-loop.md#admin-demo-ia-e2e)  
**原型 SSOT**：`src/admin/src/pages/tools/*` · 登记册 [`skillRegistryCatalog.ts`](../../../../src/admin/src/pages/tools/skillRegistryCatalog.ts)（同窗 [`skill-specs/manifest.yaml`](../../../skill-specs/manifest.yaml)）  
**低保真**：[`admin-console/page-specs.md`](../../admin-console/page-specs.md) · **路由**：[`demo-routing.md`](../../admin-console/demo-routing.md)

---

## 0. Demo 对齐快照（2026-05-27 · `src/admin`）

| 项 | 原型 |
|----|------|
| **路由 · pageId** | `/ai/tool-registry` · `ai.tool-registry` |
| **页眉** | 标题「技能与工具」；Tag **可下单技能**、**预览环境**；说明段 + **恢复默认开关** |
| **统计（三卡）** | **可下单技能 · 已启用** x/14 · **查询与外部工具 · 已启用** x/n · **开关变更记录** 条数 |
| **Tab** | **可帮用户下单**（A 类 **14** 条 + 搜索框）· **查询类工具**（B **5** 条）· **外部检索**（C **3** 条）· **变更记录**（localStorage 审计） |
| **A 类表列** | 技能 · 用户怎么用 · 实际下单方式 · 适用场景 · 是否启用 |
| **B/C 表列** | 工具 · 能做什么 · 状态（已开放/暂未开放/规划中）· 是否启用 |
| **行交互** | A 类 **整行点击** → 右侧抽屉；启用 Switch **阻止冒泡** |
| **抽屉** | **概览** · **对话与下单要求**；底栏 **复制技能编号** + 关闭；宽 ≤880px |
| **刻意无** | **新建技能**、**发布到 Runtime** 按钮、页顶 **Runtime 已发布 x/n**、页顶 **说明就绪** |

**遗留路由（重定向）**：`/ai/skill-specs`、`/tools`、`/tools/registry`、`/ai/tool-policies` → `/ai/tool-registry`。

**`publishRequired` 登记**：当前 **11** 条须 Publish 门禁（Prompt **`skillSpecRef`**）；**不**在运营台展示 x/11 统计（**SC-TM-17～18** → 所内 MR-B）。

---

## 1. 抽屉 · 概览 Tab（`SkillOperationOverview`）

| 块 | 内容 |
|----|------|
| **元数据** | 技能编号、规范版本、主场景、能力开放（矩阵中文）、预览启用、规范完整度（§1～§6 已齐 / 待补 / 无 Git） |
| **适用场景** | **scenarioId 列表**（寄存器反查）· 链 **`/ai/runtime-orchestration?scenario=`** |
| **业务说明** | §1 Identity 摘要（若有） |
| **指标卡** | 必填项 / 校验条数 / 确认展示项 / 拒答情形（有 view 时） |
| **预览** | 必填参数表（最多 6 行）+ 链到 spec Tab；确认规则摘要 + **查看全部** |

---

## 2. 抽屉 · 对话与下单要求 Tab（**SC-TM-14**）

**Segmented 分节**（产品向文案，非工程标题）：

| key | 标签 | 对应 L0 |
|-----|------|---------|
| `params` | 需要的信息 | §2 Parameters |
| `validation` | 校验规则 | §3 Validation |
| `confirm` | 确认内容 | §4 Confirmation |
| `unknown` | 待澄清 | Unknown slots |
| `refusal` | 不予办理 | §5 Refusal |
| `api` | 对接交易所 | §6 API |

**折叠**：**查看完整原文（研发对照）** — Git Markdown 全文（可选）。

**无 view 且无正文**：加载中 / 未找到 / 暂未开放说明（**SC-TM-15** · `matrixStatus=tbd` 或 `specNote`）。

---

## 3. 与其它面对位

| 模块 | 关系 |
|------|------|
| **Prompt `ai.prompt-strategy`** | **仅** `skillSpecRef` **发布门禁**（**SC-PM-21** · `promptPublishGate`）；**不**托管 Skill §1～§6 — [`prompt-strategy-reconciliation`](../prompt-management/admin-console-prompt-strategy-reconciliation.md) §0 |
| **运行场景 `ai.runtime-orchestration`** | **只读** 技能范围；**说明就绪** Tag **仅** 出现在场景抽屉，**非** 本页统计 |
| **执行详情** | **`agent.skill.spec_read`** · 技能规范卡（**SC-OM-05**） |
| **生产 Registry API** | [`admin/tool-management.yaml`](../../../../openapi/admin/tool-management.yaml) · **Demo 未接线**（**FR-TM01** B 阶段） |
| **Runtime Publish** | [`PUBLISH.md` §7.1](../../../skill-specs/PUBLISH.md#71-admin-原型--交付边界srcadmin) · Vitest `skillPublish/*` **不对** 运营演示 |

---

## 4. FR / SC 速查

| FR/SC | Demo 承载 |
|-------|-----------|
| **FR-TM06** | 整页 |
| **SC-TM-13** | 列表 + 抽屉概览 |
| **SC-TM-14** | spec Tab 分节 |
| **SC-TM-15** | tbd / 无正文技能 |
| **SC-TM-16** | 启用开关 + 页眉「预览环境」 |
| **SC-TM-17～18** | **无 UI**（所内） |
| **SC-TM-19** | **Prompt** 侧 · 非本页按钮 |

---

## 5. 维护约定

- **改 IA / 表列 / 抽屉**：先改 **本篇 §0～§2**，再改 [`page-specs.md`](../../admin-console/page-specs.md)、[`config.md`](config.md)、[`demo-routing.md`](../../admin-console/demo-routing.md)、`skillRegistryUiCopy.ts`。
- **改登记册条数**：同步 `skillRegistryCatalog.ts` · `manifest.yaml` · `trade-assistance` §4。
- **实质需求变更**：同窗 [`product/roadmap.md`](../../../../product/roadmap.md) 横切 · 技能登记行。

---

**文档版本**：0.1.0 · **2026-05-27** · **维护**：后台 + Skill owner
