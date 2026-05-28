# 存量项目 — product.plan 可复制 Prompt

> 新开 Chat，选用 **`/pipeline-product-plan`**（或 `@product-agent.mdc`），将下方整段粘贴，并按注释替换占位符。  
> 先填好 [inventory.md](inventory.md)，再执行本 Prompt。

---

## Prompt（复制从下一行到「---」结束）

```text
/pipeline-product-plan

你是 product-agent。遵守 handoff/conventions/product.md 与 handoff/pipeline/checklists/product-plan.md。

## 输入

1. @handoff/product/inventory.md（存量切口，以 §4「本阶段要做」为主）
2. @<PRD_PATH>（全量 PRD；只参考 inventory §6 标明的章节 + 非功能，不要为 PRD 里「已实现」章节新建 backlog 行）
3. 若已有 roadmap：@handoff/roadmap/phase-<N>.md

## 任务

创建或更新 handoff/roadmap/phase-<N>.md：

1. **阶段目标**：1～3 句，只描述本阶段要证明/交付什么（来自 inventory §1、§4）
2. **功能 backlog 表**：仅包含
   - inventory §4「本阶段要做」
   - inventory §3「进行中」中需要本阶段闭环的项
   - inventory §2「需补契约」表中的项（若有）
3. **不要**把 inventory §2「已实现」且无需补契约的项写成 `planned`（可省略，或在备注写「存量已实现」）
4. **依赖与顺序**：根据 inventory 与 PRD 写清；首个 `product.contract` 候选 = inventory 指定的「第一个定稿候选」（须 P0、无依赖、可单功能包闭环）
5. **本阶段不做**：来自 inventory §5
6. **非功能**：来自 inventory §7 或 PRD 非功能节
7. **不写**各功能包内的 brief、OpenAPI、测试用例（模式 1 只排期）

## 功能 ID

- 格式 `YYYY-MM-DD--kebab-slug`（双横线 `--`）
- 优先采用 inventory / 进行中表里的「建议功能 ID」；缺失时用今天日期 + 合理 slug

## 状态

- 新列入且未建包：`planned`
- 若指挥官说明某功能包已存在且 phase 非 done：roadmap 状态与功能包 `status.yaml` 对齐（`contract_ready` / `in_dev` / `done`）

## 完成后

- 对照 product-plan.md 检查清单自检，列出未勾选项（应为无）
- 回复中明确：**下一行指挥官应执行的命令**（例：`/pipeline-product-contract YYYY-MM-DD--slug`）
- **不要**在本步创建功能包或写 brief

---

## 占位符替换表

| 占位符 | 替换为 |
|--------|--------|
| `<PRD_PATH>` | `pipeline.project.yaml` 里 `project.prd.primary`（本仓：`product-doc/product/roadmap.md`）；规划时建议同时 `@product-doc/specs/requirements/closure-completion-matrix.md` |
| `<N>` | 阶段号，如 `1` |

---

## 填好 inventory 后的自检（指挥官人工，2 分钟）

- [ ] §2 已实现与代码/发布记录一致
- [ ] §4 每项能用一句话说清用户价值
- [ ] §4 同时 `in_dev` 不超过 1 个（建议）
- [ ] 第一个 contract 候选无依赖、可单包闭环
- [ ] §5「本阶段不做」已写，避免 scope creep

确认后再开 Chat 执行上方 Prompt；通过后再：

```text
/pipeline-product-contract <第一个定稿候选的功能 ID>
```

---

## 相关文档

- [inventory 模板](inventory.md)
- [指挥官手册](../pipeline/COMMANDER.md)
- [产品规范](../conventions/product.md)
- [规划检查清单](../pipeline/checklists/product-plan.md)
