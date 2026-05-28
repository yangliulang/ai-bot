# UI 走查 — 2026-05-26--admin-agent-instance-write

> designer.review · 2026-05-26

## 走查范围

- `/agents/instances`（列表 · **创建实例** Modal · 查询/表格）
- `/agents/instances/inst_90576c015fe5cda698bd3543`（详情 · **I05** 实例参数 · **I04** 登记/解绑 · 存量 Runtime/日志）
- 对照 `test/e2e-report.md`（E2E-01～04 已通过）

## 环境

- Admin `http://127.0.0.1:5173` · API `http://127.0.0.1:8080`
- 样本实例：`inst_90576c015fe5cda698bd3543`（tg `88100901` · overrides `zh-Hans` · sub `sub_e2e_88100901`）

## 检查项

| # | 项 | 级别 | 结果 | 备注 |
|---|-----|------|------|------|
| 1 | 信息架构与 brief 路由一致（列表创建 · 详情 I05/I04） | P0 | 通过 | 侧栏「实例管理」；详情面包屑回列表 |
| 2 | **AC-7** 创建入口可见、Modal 字段与说明完整 | P0 | 通过 | 主按钮「创建实例」；说明含 Deeplink 不代填密钥 |
| 3 | **AC-8** 实例参数可编辑且回显 | P0 | 通过 | 四白名单字段 +「保存实例参数」；`preferredLanguage=zh-Hans` 已持久化 |
| 4 | **AC-9** 登记/解绑与二次确认、按钮态 | P0 | 通过 | E2E 已验；NONE 时「解绑 API 托管」disabled；概览徽章「未绑定托管 API」 |
| 5 | 错误/加载态（422、提交中禁用） | P0 | 通过 | toast 含 `code` + `message`（如 `AGENT_QUOTA_EXCEEDED`）；按钮 `busy` |
| 6 | 与存量 Admin 视觉一致（`admin-panel`、表头、深色主题） | P0 | 通过 | 与同模块列表/详情、Observability 面板层级一致 |
| 7 | 列表「绑定状态」可读性 | P1 | 待迭代 | brief 写绑定状态列；表头为「子账户状态」+「阻断原因」间接表达 API 未绑定，未单独列 BOUND/NONE |
| 8 | I05 表单项标签为英文 camelCase | P1 | 待迭代 | `preferredLanguage` 等与技术字段一致；可加中文副标签或 placeholder 说明（运营向） |
| 9 | 详情页较长，写操作分散多区块 | P2 | 建议 | 绑定在上、参数在下，符合运维动线；后续可考虑锚点/折叠 |

## 问题清单

| ID | 级别 | 摘要 | 负责人 |
|----|------|------|--------|
| — | — | 无 P0 | — |
| UI-P1-01 | P1 | 列表增加「托管 API」列或合并展示 `tradingApiBindingStatus`（BOUND/NONE），与 brief 列表说明对齐 | frontend-agent（可选迭代） |
| UI-P1-02 | P1 | I05 四字段增加中文展示名（保留 API 字段名作 `description`） | frontend-agent（可选迭代） |

## 结论

- [x] **通过**（无 P0）
- [ ] 不通过

与 `brief.md` 界面说明、AC-7～AC-9 一致；E2E P0 已覆盖主流程与重复创建错误态。P1 为可读性增强，不阻塞产品验收。

## 下一棒

- **product-agent**：`/pipeline-product-accept 2026-05-26--admin-agent-instance-write`
