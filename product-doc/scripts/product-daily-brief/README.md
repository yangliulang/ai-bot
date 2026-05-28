# 产品日报 → 飞书 Webhook（本地调度）

对齐设计文档：[specs/design/requirements-daily-report-feishu.md](../../specs/design/requirements-daily-report-feishu.md)。

本仓库**仅支持本地**：用本机 cron / launchd（macOS）等定时调用脚本；不向 GitHub Actions 提交密钥。

## 行为说明

- 统计 **前一个自然日**（`Asia/Shanghai` 日历）内，**当前检出分支** 上触及以下路径的提交：
  - `specs/requirements/`（必选）
  - `product/`（默认开启，可用环境变量关闭）
- **定时前请先 `git fetch` / `git pull`**，否则会按你本机克隆里的历史统计（可能落后于远端）。
- 群发正文：**产品模版**（摘要线索 + Owner 占位 + 按桶统计）；排障可加 `INCLUDE_TECH_APPENDIX=1`。无变更时发固定短讯。

## 一次性配置（密钥不进仓库）

1. 复制 `feishu.env.example` → 同目录下 `feishu.env`。  
2. 填写 `FEISHU_WEBHOOK_URL`，按需填写 `FEISHU_WEBHOOK_SECRET`、`PRODUCT_BRIEF_REPO_URL`。  
3. **`feishu.env` 已列入 `.gitignore`，勿提交。**

```bash
cd /path/to/Agent/scripts/product-daily-brief
cp feishu.env.example feishu.env
# 编辑 feishu.env
```

可选：授予执行权限（若直接跑 shell 封装脚本）：

```bash
chmod +x scripts/product-daily-brief/send-with-local-env.sh
```

## 本地试运行（不呼叫飞书）

```bash
cd /path/to/Agent

npm run brief:dry-run
# 等价：node scripts/product-daily-brief/send-feishu-daily-brief.mjs --dry-run

# 指定被统计日（调试）
REPORT_DATE_OVERRIDE=2026-05-20 npm run brief:dry-run
```

## 真实推送（读本机 feishu.env）

```bash
cd /path/to/Agent
npm run brief:send
```

等价：`bash scripts/product-daily-brief/send-with-local-env.sh`（会先 `cd` 到仓库根再执行 Node）。

也可自行 export 环境变量后直接：

```bash
export FEISHU_WEBHOOK_URL='https://open.feishu.cn/open-apis/bot/v2/hook/xxxx'
node scripts/product-daily-brief/send-feishu-daily-brief.mjs
```

## 定时调度（示例）

保证 **同一时间机器已开机**，且 **`cd` 的目录是你日常 `git pull` 的本仓路径**。  
macOS/Linux 请将下面路径与 Node 路径改成你机器上的值（Homebrew Apple Silicon Node 常为 `/opt/homebrew/bin/node`，Intel 常为 `/usr/local/bin/node`，也可用 `which node`）。

### crontab（工作日每天 北京时间 09:00）

```cron
TZ=Asia/Shanghai
PATH=/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin

0 9 * * 1-5 cd /path/to/Agent && git pull --ff-only >/dev/null 2>&1; /bin/bash scripts/product-daily-brief/send-with-local-env.sh >> /tmp/product-daily-brief.log 2>&1
```

说明：`cron` 环境极简，务必写清 **PATH**、`cd` **绝对路径**、**node 绝对路径**。`git pull` 失败仍会尝试发报（仅用本地已有提交）；按需改成由你信任的同步方式。

### macOS launchd（可选）

用 `plist` 在 `/Library/LaunchDaemons/` 或 `~/Library/LaunchAgents/` 调同上命令；或使用系统「快捷指令 / 日历提醒」触发上述 shell。**不在此仓库内置 plist**（每台机器路径不同）。

## 环境变量

| 变量 | 说明 |
|------|------|
| `FEISHU_WEBHOOK_URL` | 必填（非 dry-run）。也可用 `feishu.env`。 |
| `FEISHU_WEBHOOK_SECRET` | 可选。签名校验。 |
| `FEISHU_DRY_RUN` / `--dry-run` | 仅打印正文。 |
| `REPORT_TZ` | 默认 `Asia/Shanghai`。 |
| `REPORT_DATE_OVERRIDE` | `YYYY-MM-DD`，调试用统计日。 |
| `INCLUDE_PRODUCT` | 默认 true；`0`/`false` 则只扫 `specs/requirements/`。 |
| `INCLUDE_TECH_APPENDIX` | `1` 时文末附加文件路径。 |
| `PRODUCT_BRIEF_REPO_URL` | 文末「仓库」链接（也可用 `REPOSITORY_URL`）。若曾设 `GITHUB_REPOSITORY`（极少本地用）仍可拼链接。 |

## 依赖

- Node **18+**
- `git` 在 `PATH` 中（定时任务请在 crontab 里写好 `PATH`）
