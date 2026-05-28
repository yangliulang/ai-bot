# Runtime · 错误归一化（上游 → 平台）

**职责**：把 **多上游**错误（交易所 JSON `code`、HTTP 状态、LLM/Telegram/推送通道响应）映射为平台 **`stableReason`**（或等价稳定键）、观测字段与用户副本 **管道入口** 的 **契约层**。  
**不**抄写上游码表 — **交易所整数码表**：GitBook；**载荷形状摘要**：[`integrations/exchange/error-codes.md`](../integrations/exchange/error-codes.md)。

**同窗**（短）：[`observability/overview.md`](../observability/overview.md)；[`design/api.md`](../../design/api.md) **附录 · `stableReason`↔Taxonomy**；[`design/architecture.md`](../../design/architecture.md)；[`unknown-state.md`](./unknown-state.md)；[`recovery.md`](./recovery.md)；[`integrations/exchange/error-codes.md`](../integrations/exchange/error-codes.md)。**横向全表** → [`boundaries.md`](./boundaries.md)。

## 分层（平台侧）

| 层 | 用途 |
|----|------|
| **上游原始** | HTTP 状态、`body.code`、`body.msg`、供应商专有头 |
| **归一化键** | **`stableReason`**（命名与枚举须在 **`design`** 登记表 **或** 专用附录冻结） |
| **观测** | trace **须**保留 **`upstreamCode`**（若有）+ **`httpStatus`** + **`stableReason`** |

---

## 边界

| 归属 | 写什么 |
|------|--------|
| **`integrations/*`** | 上游 **载荷形状**、文档中的 **字面含义** |
| **本文** | **映射规则归谁维护**；**可重试准入** → [`recovery.md`](./recovery.md)；**`504`/超时须进 UNKNOWN 语义**（非业务成功）→ [`unknown-state.md`](./unknown-state.md) |
| **`domains/agent/exchange-agent`** | **业务稳定码**（如 **`FR-T05`**、主站回退码）与 **用户可读段落** — **须**可追溯到 **`stableReason` 或等价键** |

---

## 映射表 SSOT（须冻结）

| 交付物 | 建议位置 |
|--------|-----------|
| 交易所 **`code`/`httpStatus` → `stableReason`** | **`design/api.md`** 附录表 **或** **`exchange-agent`** 附录（二选一，禁止双 SSOT）；**与** [`api.md`](../../design/api.md) **附录 · `stableReason`↔Taxonomy** **同窗** |
| LLM/Telegram/FCM **→ `stableReason`** | 同上分区表 **或** **分供应商子表** |

**Failure → 处置与字段链路索引**（**非** **码表**）→ [`failure-matrix.md`](./failure-matrix.md)。

**可重试准入**（何种 **`stableReason`** 进入 Planner 重试）→ [`recovery.md`](./recovery.md) **须**引用映射表 **版本**。

---

## 收口检查

- [ ] **`504`/超时** 默认映射 **不经**「业务成功」类 **`stableReason`**（→ **`unknown-state`**）  
- [ ] **观测**可按 **`stableReason`** 聚合告警  

---

**文档版本**：0.2.3 · **维护**：Agent Runtime owner · **本版**：**映射表 SSOT** **链** **`api.md` Taxonomy 附录**。**承** 0.2.2。
