---
name: stop-chainup-stack
disable-model-invocation: true
description: >-
  Gracefully stops local dev listeners for ChainUp admin (Vite ~5173), deeplink
  (5174), and server (8080). Use when the user invokes this skill, asks to stop
  all three projects/kill vite+api, teardown full-stack dev, or "全部停掉服务".
---

# 停掉 Admin + Deeplink + Server（本仓联调）

## 你要做的事

在用户**显式使用本技能**时，收口停掉与本仓默认本地联调相关的 **三路监听**：

| 端口 | 常见归属 |
|------|-----------|
| **8080** | `server/`（`uv`/uvicorn，`chainup-agent-api`） |
| **5173** | `admin/`（Vite 默认端口；未改配置时） |
| **5174** | `deeplink/`（`vite.config.ts` 固定端口） |

`admin/` 若在其它端口拉起过 Vite（例如 **5173 被占**），端口法可能**扫不到**：需改用「按 PID 说明」一节或让用户在对应终端前台 `Ctrl+C`。

## 推荐顺序（先温和后强制）

1. **先看 Cursor 长跑终端**：若在 IDE 里是前台 `npm run dev` / `uv run …`，最优是让用户或你在**对应终端会话**发送 **Ctrl+C**（子进程最全、日志最清晰）。
2. **按监听端口收口 PID**（本机常用 `lsof`；见下）。先 **`TERM`（默认 `kill`）**，**仅在仍占用端口且用户明确要求时**再用 `KILL`（`-9`）；**未经允许不要默认 `-9`**。

### macOS / Linux（监听端口 → PID）

在**工作区根**或任意目录执行皆可；下面为 **POSIX sh** 友好写法——对每个端口：`lsof -nP -iTCP:<port> -sTCP:LISTEN -t`，对得到的 PID **`kill`**（SIGTERM）。

```sh
for port in 8080 5174 5173; do
  pids=$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "Stopping LISTEN on :$port -> $pids"
    kill $pids 2>/dev/null || true
  fi
done
```

注意：

- **`8080` / `5174` / `5173` 可能被本机其它应用占用**。执行前可先 **展示**将要 `kill` 的 PID（`lsof …`），若明显不是本项目（例如 Docker、其它 Python 服务），**不要杀**：向用户说明并改为仅停 Cursor 已知终端里的进程。
- **uvicorn `--reload`** 可能产生父子进程；若端口仍监听，可先等 1–2s 再 `lsof` 复查；必要时在确认仍是本栈道程后 **`kill`** 残留监听 PID。

## 验证

停完后可任选：

```sh
lsof -nP -iTCP:8080 -sTCP:LISTEN || true
lsof -nP -iTCP:5174 -sTCP:LISTEN || true
lsof -nP -iTCP:5173 -sTCP:LISTEN || true
```

无 LISTEN 行即表示对应端口已释放（或本来就不在本机）。

## 与启动技能对齐

三套服务的启动约定见 sibling：`.cursor/skills/start-chainup-stack/SKILL.md`。

## Windows

若用户在 **Windows** 上且无 `lsof`/上述脚本，不要做端口盲杀：**说明环境限制**，请用户在三个终端分别结束任务，或使用其本机等价工具（如按端口查 PID 的后台命令）在用户确认后再操作。
