# 运营台 · 提示词治理对齐（`ai.prompt-strategy`）

**路径**：`specs/requirements/domains/admin/prompt-management/admin-console-prompt-strategy-reconciliation.md`  
**读者**：产品、后台、Prompt/Skill 联调  
**端到端鸟瞰**：[`flow/e2e-closed-loop.md`](../../../../flow/e2e-closed-loop.md) **阶段 F · `PROMPT_CFG`** · [**运营台 Demo IA 锚点表**](../../../../flow/e2e-closed-loop.md#admin-demo-ia-e2e)  
**原型 SSOT**：`src/admin/src/pages/prompt/*` · mock [`mockPromptData.ts`](../../../../src/admin/src/data/mockPromptData.ts)  
**低保真**：[`admin-console/page-specs.md`](../../admin-console/page-specs.md) · **路由**：[`demo-routing.md`](../../admin-console/demo-routing.md)

---

## 0. Demo 对齐快照（2026-05-27 · `src/admin`）

| 项 | 原型 |
|----|------|
| **路由 · pageId** | `/prompts/strategy` · `ai.prompt-strategy`；`/prompts/safety` · `ai.prompt-safety`（SAFETY 类独立页） |
| **页眉** | 标题「提示词治理」；Tag **本地预览** / **已接 API** / **已接 API · 16 包补齐** / **接口不可用** |
| **页顶** | `PromptGovernanceIntro`（四类正文 · 16 包 · Prompt ≠ Skill 宿主） |
| **列表范围** | **排除** `kind=SAFETY`（安全防护在 `/prompts/safety`） |
| **筛选** | 关键字（`q`，兼容旧 `id`/`title`）· 治理类型 **`kind`**（`system`/`trading`/`analysis`/`all`）· 生命周期 **`life`**（`draft`/`published`/`all`） |
| **列表列** | Prompt ID · 名称 · 类型 · 版本/草稿/生效 · 状态 · **Runtime 技能范围** · **阶段**（`showLifecycleColumn`）· 更新时间 · 操作 |
| **行交互** | 行点击 → **`?pack=`** 详情抽屉；「详情」同抽屉；「编辑」→ `/prompts/strategy/:id/edit` |
| **新建** | 「新建草稿」→ 从模板 fork 或空白（`PromptCreateDraftModal`） |

**遗留路由**：`/prompts`、`/prompts/system`、`/prompts/scenarios` → `/prompts/strategy`。

**API（可选）**：`VITE_USE_PROMPT_API` + `VITE_API_BASE_URL` → `GET /api/v1/admin/prompt-packs`；远端缺包时 **mock 补齐 16 包**（`remote+mock-ssot` · `mergeGovernancePromptPacks.ts`）。

---

## 1. 编辑器（`PromptPackEditorPage`）

| 块 | 内容 |
|----|------|
| **元数据** | `scenarioId` · `skillSpecRef` **只读**；**发布门禁 · Runtime 技能范围** Alert（**SC-PM-21**） |
| **正文** | Publish **六段**（Identity … Output Contract）；**不**托管 Skill §1～§6 |
| **侧栏** | **发布校验追溯**（`PROMPT_*` / `admin.prompt.publish_blocked`）；**拼装追溯（演示）**（**SC-PM-22**） |
| **发布** | 预检 + 发布 Modal；**须** 技能登记册 Publish 门禁（`validateSkillSpecRefForPublish`） |

---

## 2. 与其它面对位

| 模块 | 关系 |
|------|------|
| **技能与工具** | Skill §1～§6 **在** `ai.tool-registry`；本页 **仅** `skillSpecRef` 指针 |
| **运行场景** | 只读 **Runtime 技能范围**；场景抽屉 **说明就绪** **非** 本页 |
| **执行详情** | **拼装追溯** 卡（**SC-PM-22**）· `promptBindingTimeline` |
| **安全防护** | `pp-safety-global` 等 → **`/prompts/safety`** |

---

## 3. FR / SC 速查

| FR/SC | Demo 承载 |
|-------|-----------|
| **SC-PM-21** | 编辑器发布门禁 Alert + `skillSpecRef` |
| **SC-PM-22** | 编辑器拼装追溯 + 执行详情 Prompt 追溯卡 |
| **16 包治理** | mock + 可选 API 补齐 · [`governance-map.md`](../../../prompts/governance-map.md) |

---

## 4. 维护约定

- **改 IA / 列表 / 筛选 URL**：先改 **本篇 §0**，再改 [`page-specs.md`](../../admin-console/page-specs.md) **`ai.prompt-strategy`**、[`config.md`](config.md) §1.1b、[`demo-routing.md`](../../admin-console/demo-routing.md)。
- **实质需求变更**：同窗 [`product/roadmap.md`](../../../../product/roadmap.md) 横切 · Prompt 治理行。

---

**文档版本**：0.1.0 · **2026-05-27** · **维护**：后台 + Prompt owner
