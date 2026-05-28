# Registry toolId/skillId 幂等

> 功能 ID：`2026-05-28--registry-tool-idempotency`  
> 产品 Agent 定稿 · Phase-3 **P1** · closure **CC-P1-03** · **MR-E** · **`SC-MCV1-05` / `SC-OBS01`**

## 背景

Phase-3 已交付 **`skill-contract-eval-staging`**（**SK-B03 · eval.skill.* P0** **done**）。closure **CC-P1-03**（**黄 · MR-E**）仍要求 **所内可重复** 验收：**DB/镜像** **`toolId`/`skillId`** **与** **`trade-assistance` §8** **幂等**；**Enable** **`matrixStatus`** **不得 TBD 假开**（**SC-MCV1-05**）；**观测** **`agent.tool.call`** **可 join** **`scenarioId`**（**SC-OBS01**）。

ADR-002 裁断：**逻辑 SSOT** = **`design/api.md` + `trade-assistance` §4/§8**；**运行时 registry 镜像** **须投影对齐**，**不得** 另造第三套 ID。本仓已有：

- **`runtime-bundle.json`** · **11** 篇 **PUBLISHED** **`skillId`**
- **`exchange_tool_schema_registry.py`** · B 类读 **`toolId`** 切片
- **`orchestration_flow_catalog.py`** · **`scenarioId`** 登记
- **Admin Observability** · **`GET …/tool-calls`** · timeline

本包把 **镜像对拍 + Enable 门禁 + OBS join 断言** 固化为 **Python 模块 + Admin 只读 API + pytest + 证据模板**，对齐 **`admin/tool-management.yaml`** **Registry 列表** 语义（**不** 在本包交付完整 Enable/Policy CRUD）。

## 用户故事

- 作为 **架构/QA**，我希望 **`GET /api/v1/admin/tools/registry/idempotency-audit`** 返回 **skill/tool 差集为空**，可登记 **MR-E** 关单证据。
- 作为 **运营**，我希望 **`matrixStatus=TBD`** 的工具 **不得** 被 Enable（**SC-MCV1-05**），API/模块 **可观测拒绝**。
- 作为 **排障**，我希望 timeline 上 **`agent.tool.call`**（或 **`trading.exchange_private`** 写类）**同一 `executionId`** **可 join** **`scenarioId`**（**SC-OBS01** 方向）。

## 验收标准

- [x] **AC-1**：新增 **`registry_idempotency`**（路径见 `backend/notes.md`）暴露 **`REGISTRY_AUDIT_VERSION = "0.1.0"`** 及 **`load_registry_mirror()`**（**skillIds[]** · **toolIds[]** · **scenarioIds[]** · 来源见实现备注）。
- [x] **AC-2**：**`assert_skill_registry_idempotent(mirror, ssot_skills)`**：**`runtime-bundle`** **PUBLISHED** **`skillId` 集合** **等于** 镜像 **A 类** **`stableId` 集合**（**无缺失、无多余**）。
- [x] **AC-3**：**`assert_tool_registry_idempotent(mirror, ssot_tools)`**：**`exchange_tool_schema_registry`** **登记 `toolId`** **等于** 镜像 **B 类** **`stableId` 集合**（**同窗** **`read.*`** 三工具 + 可扩展 SSOT manifest）。
- [x] **AC-4**：**`assert_enable_allowed(matrix_status)`**：**`TBD` / `draft`** → **`False`** + **`code=REGISTRY_MATRIX_TBD`**；**`frozen` / `ready`** → **`True`**（**SC-MCV1-05**）。
- [x] **AC-5**：**`assert_obs_tool_call_scenario_join(events, registry_tool_ids)`**：对含 **`toolId`**（或写类 **`methodPathSummary`** 映射）之事件，**同一 timeline** **须** 存在 **`scenarioId`** **于** **`agent.orchestration.step`** **或** **`agent.tool.call`/`trading.exchange_private` summary**（**SC-OBS01** 方向）。
- [x] **AC-6**：**`GET /api/v1/admin/tools/registry`** → **200**，**`items[]`** 含 **`stableId`、`entryClass`（A|B|C）、matrixStatus、scenarioId?`**；**A 类** 行 **`stableId`** **覆盖** AC-2 全集。
- [x] **AC-7**：**`GET /api/v1/admin/tools/registry/idempotency-audit`** → **200**，**`ok=true`**（审计通过时），**`skillMismatches[]` / `toolMismatches[]`** 为空，**`auditVersion=0.1.0`**。
- [x] **AC-8**：**`server/tests/test_registry_tool_idempotency.py`**（新）覆盖 AC-2～AC-5、AC-6～AC-7：**P0 全绿**；含 **至少 1 条 P1**（如 **`assert_enable_allowed("TBD")`** 或 **缺 scenario join 负例**）。
- [x] **AC-9**：**`eval/evidence/registry-idempotency-audit.md`** **§1～§3** 已填：**命令**、**日期**、**pytest 摘要**、**依赖包**、**MR-E / CC-P1-03** 勾选说明。

## 范围

### 本期包含

- **Registry 镜像加载 + 幂等断言模块**（AC-1～AC-5）。
- **Admin 只读 API**：**`GET …/tools/registry`**、**`GET …/tools/registry/idempotency-audit`**（AC-6～AC-7）。
- **pytest + 证据模板**（AC-8～AC-9）。
- **SSOT manifest**（计划 **`data/registry/ssot_manifest.json`** 或等价）：**B 类** **`read.*` toolId** 真源切片，**不** 手抄全量 §8.3。
- **文档**：`backend/notes.md` 引用 **ADR-002**、**`trade-assistance` §6/§8**、**`tool-management/functions`** **镜像验收句**。

### 本期不包含

- **完整 Tool Management CRUD**（Policy PUT · Enable POST · Schema 编辑 — 见 **`tool-management.yaml`** 后续包）。
- **生产 DB registry 表迁移**（本包 **投影** 自 bundle + 代码常量；**须** 与未来 DB **同窗 API 形状**）。
- **C 类外网工具全量登记**（manifest **可** 含 **`draft`** 行 · **默认 disabled**）。
- **Hosted / CC 红项**、**Gateway CC-P1-07**。
- **改 `trade-assistance` §8 正文**（仅实现对拍）。

## 界面与交互（无页面）

**含页面：否**。验收 = **pytest + Admin Registry/Audit API + 证据文件**；**不** 改 **`/ai/tool-registry`** 页面（skill-publish 已 **done**）。E2E **N/A**。

## 非功能要求

- 审计模块 **纯函数** 优先；**不得** 在 evidence 写入 Secret。
- Registry API **Admin Bearer** 与存量 Admin 一致。
- 时间 UTC（`BACKEND_SPEC` §2.1）。

## 实现备注

| 项 | 路径（计划） |
|----|----------------|
| 镜像/审计 | `application/registry_idempotency.py`（新） |
| SSOT manifest | `data/registry/ssot_manifest.json`（新 · B 类读工具） |
| Skill 真源 | `data/skill_specs/runtime-bundle.json` |
| Tool 读切片 | `application/exchange_tool_schema_registry.py` |
| 场景登记 | `application/orchestration_flow_catalog.py` |
| Admin 路由 | `api/routers/v1/admin_tool_registry.py`（新） |
| 测试 | `tests/test_registry_tool_idempotency.py` |
| 规格 SSOT | ADR-002 · `trade-assistance.md` §6/§8 · `contract-closure.md` **MR-E** |
| 依赖 | **`skill-publish-effective`** **done**（bundle import） |

## 待确认问题

- [x] Q1：**含页面：否** → `skips: [frontend.integrate, test.e2e, designer.review]`。
- [x] Q2：本包 **只读 Registry + audit**；**Enable** 仅 **门禁函数** + pytest，**不** 强交付 POST enable 路由。
- [ ] Q3：所内 **DB registry 表** 若后续落地，**须** 复用 **`idempotency-audit`** 响应形状（P1 · 非 AC 阻塞）。
