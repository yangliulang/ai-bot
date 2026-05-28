---
name: start-product-doc-prototypes
disable-model-invocation: true
description: >-
  Starts the product-doc interactive prototypes under product-doc/src: Web user
  prototype (Vite 5175) and admin console demo (Vite 5176). Use when the user
  invokes this skill, asks to run product prototypes, 「产品原型」「启动 Web/Admin 原型」, or paths like product-doc/src/Web and product-doc/src/admin.
---

# 启动产品原型（product-doc：`Web` + `admin`）

## 范围

两套 **Vite + React** Demo，独立于仓库根目录的 `admin/`、`deeplink/` 联调栈；仅用于产品与交互原型预览。

| 目标 | 目录（相对仓库根） | 默认端口 | package `name` |
|------|-------------------|----------|----------------|
| **Admin 控制台 Demo** | `product-doc/src/admin` | **5176** | `coobit-admin-console-demo` |
| **用户侧 Web 原型** | `product-doc/src/Web`（注意大小写 **`W`**） | **5175** | `coolbit-agent-user-web-prototype` |

端口见 `product-doc/src/admin/vite.config.ts`（**5176** · `strictPort`）、`product-doc/src/Web/vite.config.ts`（**5175**）；与 **`deeplink` 5174**、根目录 Vue **`admin/`**（常见 **5173**）无关。

## 你要做的事

在用户**显式使用本技能**或明确要启动上述原型时：

1. 在对应目录执行 `npm run dev`，**后台长期运行**，不要与同一会话里的其他长跑命令塞进一条前台阻塞命令。
2. 若用户只要其中一套，只启动那一套并说明 URLs。

### Admin 原型

```bash
cd product-doc/src/admin && npm run dev
```

启动后通常为：`http://127.0.0.1:5176`

### Web 原型

```bash
cd product-doc/src/Web && npm run dev
```

- 如遇缓存怪异，可用：`npm run dev:fresh`（先 `clean` 再 `--force`）。

启动后通常为：`http://127.0.0.1:5175`

### 两套同时开

两个独立后台进程：分别在 **`product-doc/src/admin`** 与 **`product-doc/src/Web`** 各执行一次 `npm run dev`。

## 依赖

若报错缺模块或 lock 不一致，在**各自**子目录执行 `npm ci`（存在 `package-lock.json` 时）或 `npm install`。

## 避免重复启动

可先查看 Cursor **terminals**：若该目录下已有 `vite` 在跑，提示可能已占用 **5176/5175**，勿盲目再启（除非用户要求重启）。

## 端口冲突

若 **5176 / 5175** 被占用，**不要擅自杀进程**：说明情况，让用户处理或按其本地端口约定改对应 `vite.config.ts`。**Admin Demo 启用 `strictPort`**，不会因冲突而静默改端口。

## 与「全套联调」的区别

日常 Admin + Deeplink + Server 见 `.cursor/skills/start-chainup-stack/SKILL.md`；本技能**只**负责 `product-doc/src/` 下两套原型静态前端，**不包含** `server/` 或根目录 `admin/`、`deeplink/`。
