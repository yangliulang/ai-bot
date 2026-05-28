---
name: deploy-jenkins
disable-model-invocation: true
description: >-
  Triggers ChainUp AI Bot Jenkins deployments (botadmin, deeplink, server-api,
  website) with a user-selected branch. Use when the user invokes deploy-jenkins,
  /deploy-jenkins, Jenkins 部署, 触发 Jenkins, or asks to deploy admin/deeplink/server/website.
---

# Jenkins 部署（chainup-ai-bot）

## 何时使用

用户**显式使用本技能**（如 `/deploy-jenkins`、「Jenkins 部署」）时执行。

## 部署项

| 选项 id | 本地目录 | Jenkins Job | 控制台 |
|---------|----------|-------------|--------|
| `botadmin` | `admin/` | `botadmin` | https://jenkins.dw2nn.com/view/chainup-ai-bot/job/botadmin/ |
| `deeplink` | `deeplink/` | `deeplink` | https://jenkins.dw2nn.com/view/chainup-ai-bot/job/deeplink/ |
| `server-api` | `server/` | `server-api` | https://jenkins.dw2nn.com/view/chainup-ai-bot/job/server-api/ |
| `website` | `official-website/` | `website` | https://jenkins.dw2nn.com/view/chainup-ai-bot/job/website/ |

## 执行流程

### 1. 确认部署目标（必做）

使用 **AskQuestion**，`allow_multiple: true`，让用户勾选要部署的项目：

- **botadmin** — Admin 管理端
- **deeplink** — Deeplink H5
- **server-api** — 后端 API
- **website** — 官网（official-website）

若用户在本轮消息中已明确「全部署 / 四个都部署 / all」，则跳过 AskQuestion，四项全选。

**未选任何一项时**：停止，提示用户至少选一个。

### 2. 确认分支名（必做）

- 用户本轮已给出分支名（如 `2026-05-21`）→ 去掉首尾空格后使用。
- 未给出 → 再 **AskQuestion** 或追问一句；可建议当前工作区 `git branch --show-current`（优先 `server/`，其次 `admin/`、`deeplink/`、`official-website/` 中第一个有效 Git 仓库）。

分支名不得为空。

### 3. 二次确认（必做）

向用户展示摘要并**等待明确同意**后再触发（可用 AskQuestion 单选「确认部署 / 取消」）：

```text
即将触发 Jenkins buildWithParameters：
- botadmin      BRANCH=<分支>
- deeplink      BRANCH=<分支>
- server-api    BRANCH=<分支>
- website       BRANCH=<分支>
（仅列出用户选中的项）
```

用户取消则中止。

### 4. 触发构建

在工作区根 `$ROOT` 执行脚本（**不要**在回复中粘贴 token）：

```bash
bash "$ROOT/.cursor/skills/deploy-jenkins/scripts/deploy.sh" "<BRANCH>" <job-id> ...
```

`<job-id>` 为选中项的 id：`botadmin`、`deeplink`、`server-api`、`website`（可多个）。

脚本从 **`$ROOT/.cursor/jenkins.env`** 读取凭据；若文件不存在，提示用户复制示例并填写：

```bash
cp "$ROOT/.cursor/jenkins.env.example" "$ROOT/.cursor/jenkins.env"
# 编辑 JENKINS_USER、JENKINS_TOKEN
```

### 5. 结果汇报

每个 Job 输出：是否触发成功、HTTP 状态码、对应 Jenkins 控制台链接。任一项失败时如实说明 stderr/HTTP 码，已成功项不必重跑（除非用户要求）。

## 凭据与安全

- **`JENKINS_USER` / `JENKINS_TOKEN`** 仅存于 `.cursor/jenkins.env`（已 gitignore），**禁止**写入 commit、PR 或聊天明文。
- 禁止 `push --force` 等与部署无关的 Git 操作；本技能只触发 Jenkins。

## 手动等价命令（调试参考）

```bash
curl -X POST 'https://jenkins.dw2nn.com/job/<job>/buildWithParameters?BRANCH=<分支>' \
  --user "$JENKINS_USER:$JENKINS_TOKEN"
```

`<job>` 取 `botadmin` | `deeplink` | `server-api` | `website`。
