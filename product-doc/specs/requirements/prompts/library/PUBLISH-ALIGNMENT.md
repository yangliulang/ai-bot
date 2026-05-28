# Library 拼装 ↔ 运营 Publish 对齐说明

**路径**：`specs/requirements/prompts/library/PUBLISH-ALIGNMENT.md`  
**性质**：**读法 SSOT** — 说明 **Git `library/`** 与 **Admin `pp-*` 发布包** 的分工，**不**替代 [`governance-map.md`](../governance-map.md) 或 [`ASSEMBLY.md`](./ASSEMBLY.md)。

---

## 1. 两层载体（对照）

| 载体 | 路径 / 形态 | 何时用 | 写什么 |
|------|-------------|--------|--------|
| **拼装库（PRS L1c）** | `library/packs/*`、`INITIAL_SYSTEM.*`、`scenarios/registry` | Runtime **按 `scenarioId` 拼 SYSTEM** | 片段字母（C/E/S/IT…）、冷启动 L1～L3、类型 A 注入 |
| **运营发布包** | `pp-*`（Publish） | 管理台 **版本线 / SC-PM-21** | **六段**行为正文（见 [`promptBodyTemplates.ts`](../../../../src/admin/src/data/promptBodyTemplates.ts)） |

**禁止**把 `INITIAL_SYSTEM.zh-CN.md` **整段**当作某一个 `promptPackId` 的 Publish 正文；也 **禁止**用单包 Publish **替代** registry 的 **C + IT + A** 拼装序。

---

## 2. `INITIAL_SYSTEM` 与 `pp-*` 映射

| 拼装层 | `INITIAL_SYSTEM` / `packs` | 运营包（Publish） |
|--------|---------------------------|-------------------|
| **L1 认知根** | [`core-runtime-root.*`](./packs/core-runtime-root.zh-CN.md) | **`pp-system-core`**（行为子集，无 Tool API 表） |
| **L2 错误对用户** | [`fragment-errors-user-visible.*`](./packs/fragment-errors-user-visible.zh-CN.md) | 通常 **并入** `pp-system-core` 或 PRS 注入，**不单占包** |
| **L3 安全** | [`fragment-safety.*`](./packs/fragment-safety.zh-CN.md) | **`pp-safety-global`** |
| **澄清 / 输出横切** | （无单文件；见 PRS 块 3～5 示意） | **`pp-runtime-clarify`**、**`pp-runtime-output-contract`** |
| **L4 意图** | `fragment-intent-{trade,analysis,monitoring}` | **不**各发 `pp-intent-*` |
| **L5 类型 A** | [`fragment-confirmation-type-a.*`](./packs/fragment-confirmation-type-a.zh-CN.md) | **不**占 `promptPackId` |
| **L6 场景延展** | `prompts/trading/*`、`prompts/analysis/*` 条文 | **写路径** `pp-trading-*`；**读侧** 仅 **`pp-analysis-core`** |

维护顺序：**先改** `packs/*.md` **或** 条文目录 → **再同步** `INITIAL_SYSTEM.*` 粘贴版（见 `INITIAL_SYSTEM` 文首说明）。

---

## 3. 六段 Publish vs 拼装字母

| Publish 六段 | 主要来源 |
|--------------|----------|
| Identity | `pp-system-core` + 场景包 Identity |
| Scenario Context | **TRADING** 包 · 必填 `scenarioId` 语义 |
| Behavioral Rules | 场景包 + 延展条文（`by-scenario.md`） |
| Capability Awareness | 可选 · 写/读边界 |
| Clarify Rules | 场景包 **或** `pp-runtime-clarify` 横切 |
| Output Contract | 场景包 **或** `pp-runtime-output-contract` 横切 |

拼装表 **字母列**（C/E/S/IT…）仍在 [`scenarios/registry.md`](./scenarios/registry.md)；**`promptPackId` 列** 与 [`governance-map`](../governance-map.md) **须同窗**（CI：`check_governance_map_vs_registry.py`）。

---

## 4. 研发 checklist（增量）

1. 改 **Publish 行为** → 管理台 / `promptBodyTemplates.ts` + **governance-map**。  
2. 改 **拼装片段** → `library/packs` + **registry 字母列** + 必要时 `INITIAL_SYSTEM.*`。  
3. 改 **`scenarioId` 绑定** → registry **`promptPackId` 列** + governance-map + **Demo mock**（`mockPromptData.ts`）。  
4. MR 前运行 **两条** Python 脚本（见 [`library/README`](./README.md) §5 第 8 步）。

---

## 上级

[`README.md`](./README.md) · [`../governance-map.md`](../governance-map.md)

---

**文档版本**：1.0.0 · **维护**：产品 + Prompt owner · **本版**：**Library ↔ Publish 对齐初版**。
