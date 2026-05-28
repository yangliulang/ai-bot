---
name: branch-all
disable-model-invocation: true
description: >-
  Creates or switches to the same Git branch in server/, admin/, and deeplink/
  from each repo's current HEAD, then pushes that branch to origin (git push -u).
  Use when the user invokes branch-all / 三栈开分支, or asks to branch all three
  projects.
---

# 三栈同分支创建并推送（server / admin / deeplink）

## 何时使用

用户**显式使用本技能**时执行。用户必须提供 **分支名**；若本轮消息未给出，先询问再给分支名后再操作。

## 仓库根与目标目录

以**当前 Cursor 工作区根**为准（须存在顶层目录 `server/`、`admin/`、`deeplink/`，且各自为 **独立 Git 仓库**）。以下称该根为 `$ROOT`。

## 执行步骤

对三个目录各执行一遍（可用 `git -C "$ROOT/<dir>"`），**分支名**统一为用户指定的 `$BRANCH`（去掉首尾空格；拒绝空字符串）。

1. **校验是 Git 仓库**  
   `git -C "$ROOT/<dir>" rev-parse --git-dir` 失败则报错并跳过该项，汇总结果。

2. **工作区状态**  
   `git -C "$ROOT/<dir>" status --porcelain` 非空时：**不要强行覆盖**。向用户说明哪些仓库有未提交变更，请其先提交/暂存（`git stash`）或明确同意在本技能下继续；未得确认则中止该仓库的建分支操作。

3. **创建并切换分支**  
   - 若本地已存在同名分支：`git -C ... switch "$BRANCH"`（或等价 `checkout`），并记录「已存在，仅切换」。  
   - 否则：`git -C ... switch -c "$BRANCH"`（或 `checkout -b "$BRANCH"`）。

4. **推送到远程（默认必做）**  
   对每个已成功切到 `$BRANCH` 的仓库：

   ```bash
   git -C "$ROOT/<dir>" push -u origin "$BRANCH"
   ```

   - **`origin` 未配置**、`push` 权限不足、或远端已存在**不同历史**的同名校验失败时：**如实记录 stderr 摘要**（勿贴 token），**继续**处理下一目录，除非用户要求「必须三仓全成功才算完成」。  
   - **禁止**使用 **`push --force`** / **`--force-with-lease`**（含对 `main` / `master`），除非用户在本轮**显式**要求且符合其仓库安全规则。

5. **结果汇报**  
   每个目录输出：当前路径、操作（新建 / 仅切换）、当前 `git branch --show-current`、**`push` 成功与否**（或跳过原因：无 `origin` 等）。

## 注意

- **不从远端拉取**除非用户要求；本技能先在每个仓库的**当前 HEAD** 上建分支，再 **push** 该分支。  
- 若某目录不是 Git 仓库或某步失败，单独说明，不影响其余目录的尝试（除非用户要求全部成功才继续）。  
- 不修改用户全局或仓库级 `git config`。
