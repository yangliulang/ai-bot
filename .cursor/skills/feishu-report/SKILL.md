---
name: feishu-report
disable-model-invocation: true
description: >-
  Sends Feishu messages via scripts/feishu-direnjie-openclaw-message.sh (OpenClaw).
  Modes: (1) same-day work summary from FE_HANDOFF / PHASE1_ACCEPTANCE / roadmap
  plus roadmap completion % vs product-doc/product/roadmap.md (legacy HTTP %仍用 development-roadmap.md);
  (2) QA test report when /qa hands off after acceptance. Use for feishu-report /
  飞书汇报 / 测试报告上报 / 当日工作汇报.
---

# 飞书当日工作汇报（文档 + 路线图 + 完成度 + 发送）

## 何时使用

| 模式 | 触发 |
|------|------|
| **当日工作汇报** | 用户 **`/feishu-report`**、**飞书汇报**、**当日工作汇报** |
| **QA 测试报告** | **`/qa`** 完成验收后按 [`qa/SKILL.md`](../qa/SKILL.md) 将 **`$QA_REPORT`** 交给本技能；或用户 **测试报告上报 / 发飞书测试报告** |

两种模式均：**先写好正文 → 再调脚本发送**（默认真实发送；用户若说「试发 / dry-run」则先 `--dry-run`）。

## QA 测试报告模式（`/qa` 交接）

**输入**：`/qa` 已产出的 **`$QA_REPORT`**（结构见 `qa/SKILL.md`「测试完成 → 飞书上报」），**不要**再编造未测结论。

**步骤**

1. 通读 **`$QA_REPORT`**，仅做排版压缩（删冗余、保留表格行与 AC/缺陷 ID）；**不**改通过/失败事实。  
2. 飞书标题行保持 **`【测试报告】$DATE · $SCOPE`** 或等价。  
3. **（可选）** 若 `$QA_REPORT` 含 Phase/§ 范围，可附 **路线图完成度** 一句（见下文「路线图完成度」），**勿**为凑百分比改 QA 结论。  
4. **发送命令**与下文「发送命令」一节相同：`cd "$ROOT/scripts"` 后  
   `bash ./feishu-direnjie-openclaw-message.sh -- "$MSG"`（试发加 `--dry-run`）。  
5. 交付用户：说明已 dry-run / 已发送；失败则贴**非密钥**错误并提示检查 `./.feishu-direnjie.env` 与 `openclaw`。

**与当日工作汇报的区别**：QA 模式**不强制**重读 `FE_HANDOFF.md`；完成度为可选。用户若同时要「当日综合汇报」，先完成 QA 发送，再单独跑**当日工作汇报**模式（或合并为一条消息时须用户确认，避免超长）。

---

## 当日工作汇报模式

用户**显式要当日开发/交付汇总**时执行：先**读文档、归纳当天完成项**，再**对照路线图统计完成百分比**，最后**调用飞书脚本发出**。

## 路径（相对工作区根 `$ROOT`）

| 用途 | 路径 |
|------|------|
| 前端对接与勾选进度 | `admin/FE_HANDOFF.md` |
| Phase1 验收清单 | `server/docs/PHASE1_ACCEPTANCE.md` |
| Phase2 交易交付对照 | `server/docs/TRADING_PHASE2_REMAINING.md` |
| 产品阶段与优先级 | `product-doc/product/roadmap.md` |
| 遗留 HTTP 阶段计分（25 项） | `product-doc/development-roadmap.md` |
| 实现变更真源（辅助） | `server/docs/BACKEND_SPEC.md`（文首/文末 **变更表**） |
| 发送脚本 | `scripts/feishu-direnjie-openclaw-message.sh` |

## 汇报日 `$DATE`

- **默认**：本机当前日历日 `YYYY-MM-DD`（`date +%Y-%m-%d`）。  
- **可覆盖**：用户在本轮消息里写了日期（如「按 2026-05-18 汇报」）则用之。

## 分析步骤（先做再写正文）

1. **读 `admin/FE_HANDOFF.md`**  
   - 文首写明「最新条目在**顶部**」：从文件开头向下扫描。  
   - 收集所有 **`## YYYY-MM-DD`** 小节标题中 **`YYYY-MM-DD` = `$DATE`** 的区块（可多个）。  
   - 在每个匹配区块内摘录：小节标题行、**`- [x]`** 已完成 FE 任务（可压缩为条目列表）、**运维联调**里有页面路径则一笔带过。  
   - 若无 `$DATE` 级小节：写明「当日 FE_HANDOFF 无对应 dated 小节」，可**仅概括**当日 git 或与 Phase1 Refs 的交叉结论（见第 5 步），避免编造。

2. **读 `server/docs/PHASE1_ACCEPTANCE.md`**  
   - 对照 FE_HANDOFF / roadmap 里出现的 **AC-xxxx**、**迁移编号**、**scenarioId** 等 Refs，摘 2～5 条与**当日条目最相关**的验收项：哪些 **`- [x]`**、哪些仍 **`- [ ]`**（如实抄写勾选状态，勿擅自改为已验收）。  
   - 统计 **§1～§6**（路线图 §1.1～1.5 + Admin 收口）内 **AC-*** 勾选：`已勾选数 / 可勾选总数`（**不含** §0 前置、§7「不包含」、§8 产品-doc 对照表），供完成度 **§1.x** 与 **§4.x（Admin 子集）** 佐证。  
   - 若无直接对应：写「当日文档增量主要落在 FE 交付清单；Phase1 清单未单列该日」即可。

3. **读 `product-doc/product/roadmap.md`**  
   - 用 **P0**、**阶段 A～D**、**「当前最应该做的三件事」** 与当日 FE/验收摘要**对齐**（一两句），**不要**展开全文。  
   - 若需 **W1 派工语境**，可读 `product-doc/specs/requirements/closure-completion-matrix.md` **§0**（一句带过）。

4. **（遗留 HTTP 完成度）读 `product-doc/development-roadmap.md`**  
   - 仅用于下文 **25 项 `### N.M` 计分**；新规划叙事以 `product/roadmap.md` 为准。

5. **（可选）Git 交叉验证**  
   若第 1 步几乎无内容，可对 `server/`、`admin/`、`deeplink/` 执行 **`git log --since="$DATE 00:00:00"`**（或等价本日范围）**`--oneline`**，各取少量提交摘要**辅助**「当天推进」，**勿**贴分支名/哈希以外的敏感信息。

6. **路线图完成度（必做，紧接归纳之后、发送之前）**  
   对照 **遗留** **`product-doc/development-roadmap.md`** 的 **`### N.M`** 计分单元（25 项），结合 **`TRADING_PHASE2_REMAINING.md`**、**`PHASE1_ACCEPTANCE.md`**、**`BACKEND_SPEC.md` 变更表**、**`FE_HANDOFF.md`**（Admin 相关）判定每项得分，**禁止**无依据填 100%。正文「路线图位置」一句须引用 **`product/roadmap.md`** 的 **P0 / 阶段**。

### 计分单元（共 25 项）

路线图 **`### 1.1` … `### 7.3`** 各计 **1** 分，满分 **25**：

| 阶段 | 单元 |
|------|------|
| 第一阶段 | 1.1、1.2、1.3、1.4、1.5 |
| 第二阶段 | 2.1、2.2、2.3、2.4、2.5 |
| 第三阶段 | 3.1、3.2、3.3 |
| 第四阶段 | 4.1、4.2、4.3、4.4 |
| 第五阶段 | 5.1、5.2、5.3 |
| 第六阶段 | 6.1、6.2 |
| 第七阶段 | 7.1、7.2、7.3 |

### 单项得分（三档）

| 得分 | 含义 | 判定要点（满足其一即可，取高不就低时需保守） |
|------|------|---------------------------------------------|
| **1.0** | 已完成 | 本仓 **端到端可用**（API + 主要用户路径）；或 `TRADING_PHASE2_REMAINING` 表内该 § **ready ✅** 且 HTTP+Telegram（若路线图要求）均 ✅；或 Phase1 对应 **AC 组**在当次核对中 **全部 `[x]`** 且与 § 范围一致 |
| **0.5** | 部分 | **stub/占位**、仅 HTTP 无 TG、仅关键词/只读子集、Phase1 **明示 N/A 子集**外仍有骨架；或 AC 组 **半数以上仍 `[ ]`** 但 `BACKEND_SPEC` 变更表显示近期已落地主路径 |
| **0** | 未开始 | 无实现痕迹；或路线图 **首版排除/引导主站** 且本仓 **无** 降级 API/话术 |

**§ 与证据源映射（优先读右侧文档）**

| 路线图 § | 主要证据 |
|----------|----------|
| 1.1～1.5 | `PHASE1_ACCEPTANCE.md` §1～§5（AC-01*～AC-05*） |
| 2.1～2.5 | `TRADING_PHASE2_REMAINING.md`「现状总览」表 + Step 小节 |
| 3.1 | `read.*` / `wealth.holdings_read` 只读 + Phase2 表「只读已在 Phase1」 |
| 3.2～3.3 | `BACKEND_SPEC` / 寄存器；无 subscribe/redeem/tasks API → **0** 或 **0.5**（仅查询类） |
| 4.1 | Admin 实例/模板/灰度：`PHASE1` AC-06 + `FE_HANDOFF`；模板 CRUD 未齐 → **0.5** |
| 4.2 | Prompt 管理：`FE_HANDOFF` 提示词条目 + Admin API |
| 4.3 | Tool Registry：多数未齐 → **0** 或 **0.5**（若有 internal tools 文档） |
| 4.4 | AI Settings：AC-06b |
| 5.1～5.3 | 计费：`PHASE1` §5e「扣费不在验收」→ 执行骨架 **0.5**，真实扣费 **0** |
| 6.1～6.2 | Observability 执行列表 AC-06e；504 对账 API 未齐 → 6.1 **0.5**、6.2 **0** |
| 7.1～7.3 | 贯穿：Type-A / secretRef / 错误码 — 有交易写路径则 7.2 **1.0**，7.1/7.3 **0.5～1.0** 据实现保守给 |

**计算公式**

- **阶段完成%** = `round(该阶段得分之和 / 该阶段项数 × 100)`（整数，四舍五入）。  
- **全路线完成%** = `round(全部得分之和 / 25 × 100)`。  
- 飞书中同时写 **「得分 X/25」**，避免只报百分比引起误解。

**当日增量（可选一句）**

- 对比 `BACKEND_SPEC` / `FE_HANDOFF` 中 **`$DATE`** 变更：哪些 § 从 0.5→1.0 或新点亮；无则写「当日无路线图计分单元档位变化」。

## 飞书正文模板（简体中文，可适度压缩）

组装为**一条**完整消息（飞书纯文本），建议结构：

```text
【工作汇报】$DATE
一、前端交付（FE_HANDOFF）
- …
二、验收 / Phase1（PHASE1_ACCEPTANCE）
- …
三、路线图位置（product/roadmap · P0/阶段）
- …
四（可选）、当日提交摘要（git）
- …
五、路线图完成度（遗留 development-roadmap.md · 计分 25 项）
- 全路线：__%（__/25）
- 第一阶段 §1.1～1.5：__%（__/5）
- 第二阶段 §2.1～2.5：__%（__/5）
- 第三阶段 §3.1～3.3：__%（__/3）
- 第四阶段 §4.1～4.4：__%（__/4）
- 第五阶段 §5.1～5.3：__%（__/3）
- 第六阶段 §6.1～6.2：__%（__/2）
- 第七阶段 §7.1～7.3：__%（__/3）
- 说明：依据 TRADING_PHASE2_REMAINING / PHASE1_ACCEPTANCE / BACKEND_SPEC 变更表；Phase1 AC 勾选 __/__
- 当日档位变化（若有）：…
```

语气：事实陈述；**不**包含密钥、**.env**、**App Secret**、**完整 webhook URL**。

## 发送命令（必须遵守）

1. **工作目录**：`cd "$ROOT/scripts"`（与脚本内 `SCRIPT_DIR` 一致，便于加载 `./.feishu-direnjie.env`）。  
2. **试发**（用户要求或首次验证）：  
   `bash ./feishu-direnjie-openclaw-message.sh --dry-run -- "$MSG"`  
3. **正式发送**：  
   `bash ./feishu-direnjie-openclaw-message.sh -- "$MSG"`  

其中 **`$MSG`** 为整段汇报正文。多行时先在 shell 里赋好变量再传，避免未转义的换行/引号破坏命令；**不要把密钥写进消息或 echo 到日志**。

脚本行为摘要：可读取同目录 **`./.feishu-direnjie.env`** 覆盖 **`FEISHU_APP_*`**、**`OPENCLAW_FEISHU_*`**；依赖本机已安装可用的 **`openclaw`**。若发送失败，原样贴**非密钥**错误信息并提示检查 env 与 OpenClaw。

## 交付给用户

- 简述**当日归纳依据**（引用了哪些 dated 小节 / AC / §）及**完成度口径**（25 项三档、主要证据文件）。  
- 说明已 **`--dry-run`** 或已**真实发送**。  
- **禁止**在聊天中打印 **App Secret** 或完整凭据。
