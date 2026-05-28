# UI 走查 — 2026-05-27--skill-publish-effective

> designer.review · 2026-05-26

## 走查范围

- Admin **`/ai/tool-registry`**（侧栏 **技能与工具** · 统计卡 · Tab · 技能表 · `SkillOperationDrawer`）
- 对照 `brief.md`（AC-8 列表/履历/正文/Publish）、`test/e2e-report.md`（E2E-01～03）
- **AC-7** Prompt `skillSpecRef` 错误文案：代码走查 `usePromptPackEditor.ts`（本轮未在 `/prompts/strategy` 做页面复现）

## 环境

- Admin http://127.0.0.1:5173 · API http://127.0.0.1:8080
- 样本技能：`skill.spot.limit_order`（生效指针 **0.2.0-e2e**；履历含 **0.1.0-mvp DEPRECATED**）

## 检查项

| # | 项 | 级别 | 结果 | 备注 |
|---|-----|------|------|------|
| 1 | 信息架构与 brief 路由一致（`/ai/tool-registry`、侧栏入口） | P0 | 通过 | H1「技能与工具」；`pageId` 脚注与 API 路径可见 |
| 2 | **AC-8** 列表展示 API 数据（skillId、版本、lifecycle 相关态） | P0 | 通过 | 统计 **11/11**；表含 `skill.spot.limit_order` 等；E2E-01 已验 |
| 3 | 抽屉：概览（用户流程 · 下单方式 · Publish 入口） | P0 | 通过 | 点行打开抽屉；**Runtime 已发布** + 当前 `skillSpecVersion` 徽章 |
| 4 | 抽屉：「对话与下单要求」版本履历 + 正文预览 | P0 | 通过 | 履历可切换 **PUBLISHED/DEPRECATED**；正文 `# Skill` Markdown 非空（≈4.5k 字） |
| 5 | Publish Modal 与错误/提交态 | P0 | 通过 | E2E-03：成功 toast、回退展示单调版本文案；按钮 **提交中…** 可观测 |
| 6 | 与存量 Admin 视觉一致（深色 `admin-panel`、表头、抽屉层级） | P0 | 通过 | 对齐 product-doc 原型布局（统计区 + Tab + 三列表） |
| 7 | 查询/外部/变更 Tab 占位与说明 | P0 | 通过 | brief 本期仅占位；页脚联调说明已写明 |
| 8 | Tab 角标 **14** vs API **11** 行 / 统计 **11/11** | P1 | 待迭代 | Tab 计数来自本地 catalog 全量；表格为 API merge 后行数，易误导运营 |
| 9 | 列表「已冻结」vs 抽屉「Runtime 已发布」 | P1 | 待迭代 | catalog `frozen` 与 API `PUBLISHED` 双轨；建议列表增加 **lifecycle** 或改文案避免矛盾 |
| 10 | **AC-7** Prompt 页门禁提示 UI | P1 | 代码已接 | `PROMPT_SKILL_REF_INVALID` 等中文后缀已映射；E2E-04 未跑，产品验收可抽测 `/prompts/strategy` |
| 11 | 正文预览区 Markdown 排版（长文滚动） | P2 | 建议 | 等宽 `<pre>` 可读；后续可考虑折叠目录或渲染预览 |

## 问题清单

| ID | 级别 | 摘要 | 负责人 |
|----|------|------|--------|
| — | — | 无 P0 | — |
| UI-P1-01 | P1 | Tab「可帮用户下单」角标与统计/表格行数对齐（建议以 API `items.length` 或 merge 后计数） | frontend-agent（可选迭代） |
| UI-P1-02 | P1 | 列表行状态徽章与 API `lifecycle` / Runtime 发布态统一展示 | frontend-agent（可选迭代） |
| UI-P1-03 | P1 | 产品验收时抽测 Prompt Publish 未发布 `skillSpecRef` 的 toast/inline 文案 | product-agent / test-agent |

## 结论

- [x] **通过**（无 P0）
- [ ] 不通过

与 `brief.md` **含页面** 范围及 **AC-8** 主流程一致；E2E P0 已覆盖列表 → 履历/预览 → Publish。P1 为运营可读性，不阻塞 `ui_reviewed`。

## 下一棒

- **product-agent**：`/pipeline-product-accept 2026-05-27--skill-publish-effective`
