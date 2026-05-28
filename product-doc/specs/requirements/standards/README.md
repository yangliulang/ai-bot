# 书写规范（Requirements 侧）

本目录约定 **PRD、交互流程、业务流程** 三类产出的书写方式，以及 **合并请求与文档生命周期** 的核对习惯；路径与 SSOT 与 **[`../README.md`](../README.md)**、**[`../spec.md`](../spec.md)** 一致。

| 文档 | 用途 |
|------|------|
| [`prd-standard.md`](prd-standard.md) | 域级 / 切片级 PRD 与 FR/SC 条目的结构、编号与元数据 |
| [`interaction-flow-standard.md`](interaction-flow-standard.md) | 终端交互与 Telegram 卡片级流程（状态、文案、字段下限） |
| [`business-process-standard.md`](business-process-standard.md) | `flows/` 业务步骤级编排与跨域对齐 |
| [`review-and-change-standard.md`](review-and-change-standard.md) | MR 评审清单、变更摘要模板、文档状态与术语权威 |
| [`prompt-standard.md`](prompt-standard.md)、[`tool-standard.md`](tool-standard.md)、[`api-standard.md`](api-standard.md)、[`naming-standard.md`](naming-standard.md)、[`review-process.md`](review-process.md) | **薄索引**：链向 PRD / 交互 / `design/api` / `tools` / `prompts` / 评审主文，避免重复条文 |
| [`STANDARDS-ADOPTION.md`](STANDARDS-ADOPTION.md) | **标准落地**：MR 动作、Wave 分批、把 `domains`/`flows`/`domains/agent/telegram` 存量对齐 **用起来** |
| [`Log.md`](Log.md) | **`standards/` 目录修订履历**（凡改本目录规范须追加） |

人类可读叙事仍归 **`product/`**；契约 SSOT 仍以 **`product.md`**、`domains/`、`design/` 正文为准。

## 如何把现有存量「对齐标准」用起来

必读 **[`STANDARDS-ADOPTION.md`](STANDARDS-ADOPTION.md)**：约定 **每条 MR** 勾选 **§3 摘要**、自检 **prd / business-process / interaction** §6～§8，以及 **`flows`/`domains/agent/telegram`/`domains` 分批 Wave**。

---

## 推荐阅读顺序

0. **[`STANDARDS-ADOPTION.md`](STANDARDS-ADOPTION.md)** — **操盘台账**：谁先动、自检贴哪。
1. [`prd-standard.md`](prd-standard.md) — **存放位置、FR/SC、邻域边界**。  
2. [`business-process-standard.md`](business-process-standard.md) — 跨系统步骤链落在 **`flows/`**。  
3. [`interaction-flow-standard.md`](interaction-flow-standard.md) — 会话与卡片下限 **`domains/agent/telegram/`**（常与 flows 同一 MR）。  
4. [`review-and-change-standard.md`](review-and-change-standard.md) — MR **勾选与变更摘要**（可与 **`contract-closure`** 并行；**关单导航** **[`closure-remaining` §0 速链](../closure-remaining.md#closure-remaining-quicklinks)**）。  
5. 变更 **`standards/`** 条文后：**[`Log.md`](Log.md)** **顶部追加一条**（必填）。

主链路关系：**PRD** 定义「要什么与如何验收」→ **业务流程** 定义「谁先谁后及跨界点」→ **交互** 定义「终端上长什么样、用户点什么」。**MR 与变更摘要** 见 [`review-and-change-standard.md`](review-and-change-standard.md)。

---

## 推荐工作流（先规范、后存量）

1. **定稿三本规范**：[`prd-standard.md`](prd-standard.md)、[`business-process-standard.md`](business-process-standard.md)、[`interaction-flow-standard.md`](interaction-flow-standard.md) — 章节齐全、自检可用、交叉引用一致。  
2. **冻结改动闸门**：规范正文变更须 **[`Log.md`](Log.md)** 追加 + [`review-and-change-standard.md`](review-and-change-standard.md) **§3**（按需）。  
3. **再改存量需求**：按 [`prd-standard.md`](prd-standard.md) §6、[`business-process-standard.md`](business-process-standard.md) §6、[`interaction-flow-standard.md`](interaction-flow-standard.md) §8 **逐项对齐** `domains/`、`flows/`、`domains/agent/telegram/`；**同一业务主题** 优先 **同一 MR** 联动三类文档。

---

## 维护说明

- **修订履历**：凡变更 `standards/` 内文档，**必须**在 [`Log.md`](Log.md) **顶部追加一条**（最新在上）。  
- **变更规范本身**：走文档评审；若改动影响契约收口语义，同步核对 [`contract-closure.md`](../contract-closure.md) **并兼读** **[`closure-remaining` §0 速链](../closure-remaining.md#closure-remaining-quicklinks)**（**MR/粘贴缺锚**）。  
- **Cursor 角色 Skill**：`.cursor/skills/product-manager`、`interaction-designer`、`systems-architect` 等可将本目录列为必读（可选）。
