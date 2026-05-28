---
name: push-all
disable-model-invocation: true
description: >-
  Commits all changes on the current branch in server/, admin/, and deeplink/
  and pushes each to its remote tracking branch. Use when the user invokes
  push-all / 三栈提交推送, or asks to commit and push all three repos.
---

# 三栈提交并推送（server / admin / deeplink）

## 何时使用

用户**显式使用本技能**时执行。每个目录是**独立 Git 仓库**，在**各自当前分支**上提交并 `push`。

## 仓库根与目标目录

以**当前 Cursor 工作区根**为 `$ROOT`；依次处理 `server/`、`admin/`、`deeplink/`。

## 提交说明（commit message）

- 若用户在本轮消息中给了提交说明，**原样用作** commit message（可用 HEREDOC 避免换行/特殊字符问题）。  
- 若未给出：先询问一句清晰的提交说明再继续；**不要**在用户未确认前批量提交。

## 每个目录的执行步骤

对 `<dir>` in `server` `admin` `deeplink`：

1. **校验仓库**  
   `git -C "$ROOT/<dir>" rev-parse --git-dir` 失败则记录并跳过。

2. **是否有变更**  
   `git -C "$ROOT/<dir>" status --porcelain` 为空则记录「无变更，跳过提交推送」并继续下一个。

3. **暂存**  
   `git -C "$ROOT/<dir>" add -A`  
   若暂存区包含明显敏感文件（如 `.env`、凭据文件），**警告用户**并中止该仓库提交（除非用户明确坚持且已知晓风险）。

4. **提交**  
   使用 HEREDOC 传递 message，例如：

   ```bash
   git -C "$ROOT/<dir>" commit -m "$(cat <<'EOF'
   <用户确认后的提交说明>
   EOF
   )"
   ```

   遵守仓库 **pre-commit** hook；若 hook 修改了文件导致需再次暂存，按 hook 提示修复后**新建一次提交**（不要随意 `commit --amend` 除非用户明确要求且符合其 git 规则）。

5. **推送**  
   ```bash
   git -C "$ROOT/<dir>" push -u origin "$(git -C "$ROOT/<dir>" branch --show-current)"
   ```  
   仅使用常规范式推送：**禁止** `push --force` 到 `main`/`master`，禁止用户未要求的 `--no-verify`（除非用户在本轮明确说出）。

## 结果汇报

按目录列出：是否有提交、commit 简短 hash（若有）、`push` 是否成功、远端错误或需设置 upstream 的提示。

## 注意

- 用户规则若要求「仅在被要求时创建 commit」：本技能**即**用户主动要求的批量提交场景。  
- 不 `git push` 到用户未配置的 remote；若缺少 `origin` 或无写权限，如实报告。
