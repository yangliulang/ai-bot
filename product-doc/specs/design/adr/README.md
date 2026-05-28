# 架构决策（ADR）

一条决策一个文件，建议命名：`001-short-title.md`。

模板可包含：状态、上下文、决策、后果、与需求文档的引用。

## 索引

| 编号 | 文件 | 摘要 |
|------|------|------|
| **ADR-001** | [`001-telegram-confirm-before-coobit-write.md`](001-telegram-confirm-before-coobit-write.md) | Telegram **「类型 A」**确认闸门 **先于** Coobit **写**；`callback_data` 短键、`answerCallbackQuery`、CI/CR 清单 |
| **ADR-002** | [`002-tool-skill-registry-ssot.md`](002-tool-skill-registry-ssot.md) | **`skillId`/`toolId`**：**`design/api` + `trade-assistance`** **为逻辑 SSOT**；**DB** **仅镜像**（[`contract-closure`](../../requirements/contract-closure.md) **CC-P1-03**） |
| **ADR-003** | [`003-external-tools-compliance-and-budget.md`](003-external-tools-compliance-and-budget.md) | **C 类 `tool.web.*`**：**速率/PII/Disclaimer/`agent-context` 预算**（**CC-P1-02**） |
| **ADR-004** | [`004-intent-centric-execution-and-canonical-trading-model.md`](004-intent-centric-execution-and-canonical-trading-model.md) | **意图中心化执行** + **Canonical Trading Model**；**Skill 不直连交易所字段**；**Gateway + Adapter**（[`CC-P1-07`](../../requirements/contract-closure.md)）；**系统工程叙事** → [`architecture.md`](../architecture.md) **「与通用 Agent 栈之对照」** |

**导读**：[`architecture.md`](../architecture.md) **「与通用 Agent 栈之对照」** — Runtime / Gateway / 意图中心 vs Prompt+Tool-only；与 **ADR-001～004** **并列阅读** **不** **替代** **各 ADR 正文**。

**关单余量（MR 首节）**：[`closure-remaining` §0](../../requirements/closure-remaining.md#closure-remaining-quicklinks) · [§6 / §6.4](../../requirements/closure-remaining.md#cc-exec-solve-path)（[**§6.4 问题→动作**](../../requirements/closure-remaining.md#cc-problem-to-action)）；**主契约** [`contract-closure`](../../requirements/contract-closure.md)。
