# OpenAPI Hosted / `release-*` 上线检查单（CC-P0-01）

**路径**：`specs/openapi/HOSTED-ROLLOUT-CHECKLIST.md`。

**用途**：运维 + 实现 **关闭 CC-P0-01** 时 **逐项勾选**。**MR 描述** **仍用** [`contract-closure` §3.4](../requirements/contract-closure.md#cc-p0-mr-github-full)（`【CC_P0_ID】= CC-P0-01`）。

**同窗**：[`openapi/README.md`](README.md) · [`design/api.md`](../design/api.md) 登记表 · [`OWNERS.md`](OWNERS.md)。

---

## 1. 前置

- [ ] 本仓库 `specs/openapi/*.yaml` **`info.version`** **与** `design/api` **第三列日期一致**
- [ ] [`OWNERS.md`](OWNERS.md) **行级 Owner** 已填

---

## 2. Hosted 或 Tag（二选一或并存）

### 选项 A · Hosted Swagger/Redoc

| 项 | 填写 |
|----|------|
| **环境** | staging / production |
| **URL** | `________________` |
| **锚定 Git SHA** | `________________` |
| **合并 MR** | `________________` |

- [ ] 打开 URL **可访问** 且 **与仓库 YAML 同窗版本**
- [ ] 登记表 **第 2 列** 已更新为 Hosted URL

### 选项 B · `release-*` Git tag

| 项 | 填写 |
|----|------|
| **Tag 名** | `release-________________` |
| **指向 SHA** | `________________` |

- [ ] Tag **已 push** 且 **CI 绿**
- [ ] 登记表 **第 2 列** 已链 tag

---

## 3. 矩阵与生产 PATH

- [ ] **生产 PATH** **与** [`design/api.md`](../design/api.md) **矩阵** **抽样 diff** **无未说明漂移**
- [ ] 若仅 **延期格**：**备注** **与实现一致**

---

## 4. 登记回填

- [ ] [`contract-closure` §8](../requirements/contract-closure.md) **顶行** 已登记本 MR
- [ ] [`closure-remaining` §7.6](../requirements/closure-remaining.md#cc-closure-exec-checklist) **CC-P0-01** 相关项已勾

---

**文档版本**：0.1.0 · **维护**：运维 + 接口 owner
