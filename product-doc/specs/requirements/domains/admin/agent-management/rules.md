# Agent Management · 规则与约束

本文档为 [`overview.md`](overview.md)、[`functions.md`](functions.md) 中 **MUST** 类约束的 **展开版**；与 **附录 A**、**exchange-agent**、**`contract-closure`** 冲突时以 **书面 OVERRIDE** 为准——**本域 `functions` §8「已决议默认」** 为 **V1 工程缺省**。

---
**关单余量（MR 首节）**：[`closure-remaining` §0](../../../closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../../closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../../closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../../contract-closure.md)。

## 1. 审计（不可降级）

**须审计**的动作（**非穷举**，实现侧须用 **白名单注册**避免漏网）：

| 类别 | 动作类型（示例） | 须记录字段 |
|------|------------------|------------|
| 模板 | `TEMPLATE_CREATED`、`TEMPLATE_PUBLISHED`、`TEMPLATE_DISABLED`、`TEMPLATE_ENABLED`、**`TEMPLATE_CLONED`**、**`TEMPLATE_DRAFT_DELETED`**（及归档类占位） | `templateId`、`templateVersion`、diff 快照 id；**克隆**须含 **源 templateId/version** |
| 实例 | `INSTANCE_CREATED`、`INSTANCE_DELETED`、`INSTANCE_BIND`、`INSTANCE_UNBIND`、`INSTANCE_OVERRIDES_UPDATED`、**`INSTANCE_LIST_EXPORTED`** | `instanceId`、`userId`、变更前后 ref；**导出**含 **筛选摘要** |
| 运行 | `RUNTIME_START`、`RUNTIME_PAUSE`、`RUNTIME_RESUME`、`RUNTIME_STOP`、**`RUNTIME_BATCH_PAUSE`/`RUNTIME_BATCH_STOP`** | `instanceId`、`reasonCode`、发起者；**批次**含 **`batchId`**、成功/失败计数 |
| 日志 | `LOG_SENSITIVE_VIEW`、`LOG_EXPORT_REQUESTED` | 目标范围、审批单 id（若有） |

**保留期**：与 **合规**一致，**不低于** `observability` 对管理台审计的要求；本域 **不**定具体月数。

---

## 2. 删除与在途风险

1. **默认**：存在 **未终局**交易执行、**未平仓**风险敞口、或 **exchange-agent / risk** 定义的 **禁止删除**标志时 → **禁止硬删**，API **4xx** + **明确 `code`**。  
2. **软删**：**允许**在更多场景隐藏实例，但 **须**保证 **计费与合规**仍可按 `instanceId` **追溯**（与 **billing** 会签）。  
3. **级联**：删除实例 **不得**破坏 **子账户本身**；仅 **解绑 Agent 关系**。

---

## 3. Pause / Resume / OPS 语义

1. **实例 Pause**：**仅**影响 **该实例**调度；**须**有 **原因码**（对内）与 **对用户可见文案**（可映射自原因码）。  
2. **OPS 全局 Pause**：影响 **配置范围内所有用户/实例**；与 **实例 Pause** **独立存储**，UI **不得**混为一谈。  
3. **展示**：当两者同时生效，**两行都显示**；**Resume 实例**在 **OPS 仍 on** 时 **可能仍不可执行**——按钮 **可置灰**并提示 **全局原因**。  
4. **Pause ≠** 单次 LLM/工具失败；**不得**用「Pause」指代 **可自动恢复**的瞬时错误。

---

## 4. 密钥与敏感数据

1. **永不**：在 **任何**管理台 API 响应、WebSocket、日志 Tab **默认视图**中出现 **交易所 API Secret**、**明文私钥**。  
2. **可展示**：`agentTradingApiKeyId`、`subAccountBindingRef`、`agentSubAccountStatus`（附录 A §8.2 子集）等 **引用类**字段。  
3. **换绑**：**旧绑定**作废须 **服务端** revoke，**不**信赖前端清屏。

---

## 5. RBAC（最小集合 · V1）

角色名为 **占位**；**映射要求**：所内 **`IAM`/权限中心**配置 **须导出**或与下表 **`1:1` 能力行**可走查（建议使用 **同名 permission code**，如 **`agent.template.publish`**）。 **`TechSupport`** 对 **受限字段实例改**须在 **工单/审批**链路可审计（见 **`observability-management`** 若有）。

| 资源 / 动作 | Viewer | Ops | RiskAdmin | TechSupport |
|-------------|--------|-----|-----------|-------------|
| 模板列表/详情（只读） | ✓ | ✓ | ✓ | ✓ |
| 模板创建/发布/停用 | ✗ | ✓ | ✓（可限） | ✗ |
| **模板克隆（T09）** | ✗ | ✓ | ✓（可限） | ✗ |
| **草稿模板删除（T10）** | ✗ | ✓ | ✓（可限） | ✗ |
| 实例列表/详情 | ✓ | ✓ | ✓ | ✓ |
| **实例列表导出（I08）** | ✗ | ✓ | ✓ | ✓（须审批） |
| 实例创建/删除 | ✗ | ✓ | ✗ | ✗ |
| 子账户换绑 | ✗ | ✓ | ✓ | ✗ |
| 实例参数改 | ✗ | ✓ | ✗ | ✓（可限字段） |
| Runtime 命令 | ✗ | ✓ | ✓ | ✓（可限） |
| **批量 Runtime（R06）** | ✗ | ✓ | ✓ | ✗（默认） |
| 日志摘要 | ✓ | ✓ | ✓ | ✓ |
| 日志原文 / 导出 | ✗ | ✗ | ✓ | ✓（须审批策略） |

**原则**：**分离**「能看业务」与「能改运行状态」与「能看隐私」。

---

## 6. 模板停用与存量实例（V1 默认）

**停用**后 **确定项**：**禁止**新建实例（`I02`）。  

**存量实例**：**默认** **路径 A**——**允许继续运行**，直至运营 **人工 Pause / 迁移 / 模板升级任务**。**路径 B**（停用触发 **异步批量 Pause** + 通知）**不作为默认**；若启用须 **产品开关 + 独立 Runbook**，并在 **`contract-closure`** 备案。

---

## 7. Agent Logs 与 observability 边界

1. **Schema、索引、保留、采样、导出审批** → **`observability` / `observability-management` SSOT**。  
2. 本模块 **只允许**：**限定在实例上下文**的查询参数与 **列映射**；**禁止**自创 **未登记**事件类型名。  
3. **`executionId` 关联**：为三日志 **最低**公共键（与 PRD **P3** 一致）。

---

## 8. 全局门禁与实例命令优先级（冻结规则）

下列规则须在 **任一**控制台入口 **一致**（BFF **不得**自作主张放宽）；与 [`functions.md`](functions.md) **§5.1 G01**、**§3 R06** 同文：

1. **`GLOBAL_AGENT_SWITCH` OFF**：**禁止** **新建实例（I02）**、**Start**、**Resume** 及任何导致 **新执行进入可计费成功路径** 的操作；**UI 须灰显**对应入口。  
2. **同条件下仍须允许**（运维 **止损**）：**Pause**、**Stop**、**R06 批量 Pause / 批量 Stop**——**不得**因全局 OFF **无依据地整批拒绝**上述命令（**合规特批开关**另计，默认 **关闭**）。  
3. **用户级 `agentState` 为 BLOCKED 类**：实例命令 **不改变**门禁结论；**可**允许 **Stop**（与 **functions §8** 一致）。  
4. **实例 Pause**：在 **未被全局/用户级门禁覆盖的语义下**，仍 **阻断**该实例新执行。

---

## 9. 错误码与对用户暴露

- **对内**：稳定 `code`（如 `AGENT_TEMPLATE_DISABLED`），**可查**运维手册。  
- **对终端用户**（若错误经主站透出）：**不得**暴露 **内部 stack**；映射 **简短可行动**文案（见 **exchange-agent / Telegram** UX skill）。  
- **幂等**：同一 **Start** 重试 → **同一**业务结果与 **同一** `code`（成功侧）。

---

## 10. 控制台形态与 IAM（V1 摘要）

**V1** **以运营后台为主**；**同源 API** 由 **IAM** 统一鉴权（与 [`functions.md`](functions.md) **§8「已决议默认」** 第 4 条一致）。**不做**独立「用户端 Admin 产品线」；若未来分支须在 **`contract-closure`** 单独立项。
