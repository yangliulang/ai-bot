# 评审、变更追溯与文档生命周期

**适用**：合并请求（MR）或版本发布前，对 **`domains/`**、**`flows/`**、**`domains/agent/telegram/`**、**`product.md`** 改动的 **一致性核对**；不在此替代 [`contract-closure.md`](../contract-closure.md) 的 **契约收口定义**，与之 **叠加使用**。**关单粘贴缺锚 / 本节派工**：[**`closure-remaining` §0 速链**](../closure-remaining.md#closure-remaining-quicklinks) · [**§6 / §6.4**](../closure-remaining.md#cc-exec-solve-path)。

---

## 1. 文档状态（建议用语）

| 状态 | 含义 |
|------|------|
| **草案** | 可大范围改动；**不对**外承诺「已实现」 |
| **评审中** | 口径收敛；接口矩阵仍为 **TBD** 的能力须在正文标明 |
| **已冻结（需求阶段）** | 条文稳定；后续改动走 **显式变更记录** 或 MR 说明 |
| **受 design/api 解冻牵动** | 矩阵从 **TBD→冻结** 时须执行 [`contract-closure.md`](../contract-closure.md) **§4** 核对 |

域文档表头的 **状态** 字段应与上表一致或映射清晰。

---

## 2. MR 评审清单（跨文档）

评审人可按改动范围勾选（**不必全选**）：

**PRD / `domains/`**

- [ ] 新增或修改的 **FR** 具备 **触发 / 行为 / 边界**（见 [`prd-standard.md`](prd-standard.md) §4）  
- [ ] **邻域表**已更新；无「silent」扩张范围  
- [ ] **`design/api.md`** 仍为 **TBD** 的能力 **未**写成确定句式  

**`flows/`**

- [ ] 步骤 **S*** 与 **FR / domains §** 可追溯  
- [ ] **写路径** 与 **ADR-001**、**`telegram`** **类型 A** 一致  
- [ ] [`flows/README.md`](../flows/README.md) 索引已更新（新文件时）  

**`domains/agent/telegram/`**

- [ ] 卡片 / 按钮变更 **有** **`overview.md` §** 依据或同 MR 修改 **`overview.md`**  
- [ ] **Billing Deeplink** 与会话入口下限满足 [`README.md`](../domains/agent/telegram/README.md)  

**设计与收口**

- [ ] 涉及对外承诺时对照 [`contract-closure.md`](../contract-closure.md)  
- [ ] MR 合并描述 **缺闭环锚** / **不明「本 MR 关哪条 CC」** → **先点开** **[`closure-remaining` §0 速链](../closure-remaining.md#closure-remaining-quicklinks)** · **[§6 / §6.4](../closure-remaining.md#cc-exec-solve-path)** **再登记** [`contract-closure` §8](../contract-closure.md)｜ **N/A**  
- [ ] `design/api.md` **版本脚注**（若触及矩阵/登记表）由架构侧确认是否需要递增  
- [ ] **`risk/` 与运营闸**：变更 **Kill、Feature 闸、`SYMBOL_*`、`AGENT_*` 护栏或高危配置审计** 时，对照 [`risk/acceptance.md`](../risk/acceptance.md) **`SC-RISK*`** 与 [`contract-closure.md`](../contract-closure.md) **§4**；**无触达** **标 N/A**

**链接与规范目录**

- [ ] **Markdown**：正文内 **`[]()`** 链接 **括号成对**，**表格内** **链接** **勿** **嵌反引号** **破坏** **解析**（参见 **`prompt-management/config`** 历次修订）  
- [ ] 变更 **`specs/requirements/standards/`** 时 **[`Log.md`](Log.md)** **已** **顶部** **追加**（必填）

**叙事**

- [ ] 若影响用户理解，[`product/`](../../../product/README.md) 相关篇 **已同步或已建跟进项**  

**Roadmap**

- [ ] **[`product/roadmap.md`](../../../product/roadmap.md)**（必要时 **[`product/roadmap/README.md`](../../../product/roadmap/README.md)**）：若本次 MR **新增或实质修改** **`specs/requirements`** 需求口径（`product.md` / `domains/` / `flows/` / `telegram/` 域条，或与 **横切 Runtime / Skill / Eval / closure 专卷** 等 **P0·阶段·横切叙事**），**须** **同窗** 更新 Roadmap（**TL;DR**、**「规格体系快照」L1～L7** — 择要补丁层、横切主题表、阶段/例行节奏、维护沿革）；**豁免** — 见 [`product/roadmap/README.md` §维护约定](../../../product/roadmap/README.md) **`需求变更须同步路线图`**；**不适用** → **勾选 N/A** 并简述  

---

## 3. MR / 版本说明中的「变更摘要」模板（推荐）

在 MR 描述或发布说明中粘贴并填写：

```markdown
## 需求文档变更摘要
- **范围**：`domains/` / `flows/` / `domains/agent/telegram/` / `product.md`（勾选适用项）
- **主因**：<一句话>
- **FR/SC**：新增 <…>；修订 <…>；废止 <…>（无则写「无」）
- **契约**：design/api / contract-closure / ADR 联动：<无 | 见 #xxx>
- **风险 / 护栏**：[`risk/acceptance`](../risk/acceptance.md) `SC-RISK*`、`trading-agent-config/keys` §1～§3：<已核对 | N/A>
- **索引**：spec.md / flows/README / telegram.md §：<已更新 | N/A>
- **Roadmap**：[`product/roadmap.md`](../../../product/roadmap.md) **已同窗更新（含按需补丁「规格体系快照」分层表）** — 或 **豁免 N/A 已说明** — 细则见 **[`product/roadmap/README` §维护约定](../../../product/roadmap/README.md)**
- **待办**：<TBD 项或后续 PR>
- **Log**：若改动 **`specs/requirements/standards/`**，[`Log.md`](Log.md) **已追加**（必填；格式见该文件文首）
```

---

## 4. 规范目录修订履历（`Log.md`）

凡修改 **`specs/requirements/standards/`** 下任一 `.md`：**同一 MR** 须在 [**`Log.md`**](Log.md) **顶部**追加记录（最新在上），见该文件 **适用范围** 与 **记录格式**。  
此举与 **§3 变更摘要** 互补：摘要面向 MR 读者全文；**Log** 面向 **`standards/`** 连续修订史。

---

## 5. 术语（Glossary）权威

- **同一术语多个含义**：在 **权威域** **术语表** 定义；其他文档 **只引用**（不复述冲突定义）。  
- **同名章节不同义**（例：两个 §7.4）：**表头互引** + 文中 **写全文件名**。  

详见 [`prd-standard.md`](prd-standard.md) §2～§3。

---

## 6. 回溯与审计（需求侧）

- **Git 历史**为条文变更主追溯手段；重大口径变更建议在 MR 摘要中 **点名受影响 FR**。  
- **运营配置 Key**、行为枚举 **以 [`config.md`](../domains/admin/management-console-v1-prd.md) 与对应域 FR **单一登记**为准；MR 说明是否需 **`config.md` §13** 一类勾选联动（若适用）。
