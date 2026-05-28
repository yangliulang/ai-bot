# Runtime · 未知态（UNKNOWN）

**主叙约定**：**`504` / `UNKNOWN` 平台需求下限** 以 **本文** 为准；**`stableReason` 映射与收口** → [`error-normalization.md`](./error-normalization.md)；**补偿、队列、用户可见副本** → [`recovery.md`](./recovery.md)；**REST↔WS 对账次序** → [`reconciliation.md`](./reconciliation.md)；**幂等键与检查点挂起** → [`design/api.md`](../../design/api.md)、[`persistence.md`](./persistence.md)。

**职责**：当上游返回 **执行状态不可判定**（典型：**HTTP `504`**、读超时、上游 JSON **`code`** 明示未知/超时），平台运行时 **须**保留 **`UNKNOWN`**（或等价枚举），**禁止**直接降级为 **成功**或 **终局失败**。

**同窗**（短）：[`error-normalization.md`](./error-normalization.md)；[`recovery.md`](./recovery.md)；[`reconciliation.md`](./reconciliation.md)；[`persistence.md`](./persistence.md)；[`../risk/unknown-stall-policy.md`](../risk/unknown-stall-policy.md)（**Δt/查单有界 · §1** **+** **用户追问状态机 §2**）；[`integrations/exchange/overview.md`](../integrations/exchange/overview.md)（上游 **`504`** 文档语义）。**横向全表** → [`boundaries.md`](./boundaries.md)。

---

## 上游事实（索引）

GitBook **OpenApi 基本信息**：**`504`** — 请求可能已到达核心，**结果未知**。**语义归属 `integrations`**；**平台状态机**归属本文。

---

## 平台需求下限

### 状态枚举

- **须**区分：**`UNKNOWN`**（或 **`EXECUTION_UNKNOWN`**） vs **成功** vs **业务拒绝** vs **终局系统失败**。  
- **`UNKNOWN`** **禁止**直接映射为用户可见「已失败成交」类断言（措辞 **`exchange-agent`** FR 可对签）。

### 与幂等与持久化

- **`UNKNOWN`** **须**能与 **`design`** 登记的 **客户端订单号 / `operationId`** 组合 **发起查询**（查询 PATH **不归本文**）。  
- 检查点 **须**允许 **挂起在 UNKNOWN** 直至 **对账或超时策略** 结案 — 同窗 [`persistence.md`](./persistence.md)。

### 收口与无进展（产品下限）

**原则**：**`UNKNOWN` / `unknown_pending`** **允许** **在对账闭环前** **暂态停留**；**禁止** **无限期** **无用户可解释、无运营可处置** **之** **「静默悬挂」**（**须** **可观测** **可区分** **「推进中」** **vs** **「卡死」**）。

**须（MUST）**：

1. **可观测**：**须** **存在** **维度或派生指标**（**如** **`execution_state=UNKNOWN`** **`executionId` 轴** **、** **最后事件 ts、最后查单 ts**）**使** **协查** **能回答**「**是否仍在对账**」**与**「**多久无进展**」**—** **同窗** [`observability/overview.md`](../observability/overview.md) **§2**。  
2. **闭环路径**：**须** **至少** **具备** **之一**：**(a)** **对账/查单** **收敛到** **可采信终局** **并** **驱动** **Runtime 主态** **离** **`unknown_pending`**（**见** [`reconciliation.md`](./reconciliation.md)）；**(b)** **超时或策略** **收敛到** **`failed` / `cancelled`** **等终局** **且** **`stableReason`/用户 copy** **可解释**；**(c)** **显式** **人工/运营处置** **入口**（**工单或管理动作**）**与** **审计痕迹** — **不得** **仅** **停在** **无终局、无下一步** **之** **内部状态**。  
3. **数值与分级**：**具体** **告警阈值、最大挂起时长、分级 SLA** **由** **`exchange-agent` / `risk` / `eval`** **宿主** **冻结**（**条文聚合** [`../risk/unknown-stall-policy.md`](../risk/unknown-stall-policy.md)；**OpenAPI / 配置键名** **`design`** **收束**）；**本文** **要求** **该冻结** **须** **与同执行** **`executionId`** **可追溯** **且** **≥** **运营最小可接受** **协查窗口**（**与** [`recovery.md`](./recovery.md) **Retry/退避上限** **无逻辑冲突**）。

**仍不可判** **且** **未满足** **上述闭环** → **主叙事** **留在** **UNKNOWN** **`unknown_pending`** **—** **禁止** **借对账** **冒充** **业务成功**（[`reconciliation.md`](./reconciliation.md) **§2**）。

---

## 用户可见副本下限（Then · 与 Telegram / `FR-T05` 同窗）

**原则**：**UNKNOWN** **≠** **失败成交** **≠** **成功终局**；**用户侧** **须** **可区分** **「仍在查」** **与** **「已结案」**。

| **须（MUST）** | **说明** |
|----------------|----------|
| **禁止 SUCCESS 占位** | **不得** **使用** **暗示已成交、已买入/卖出完成** **的最终语气**，**直至** **对账或策略** **收敛** **（** **同窗** [`architecture.md`](../../design/architecture.md) **504 叙事** **）**。 |
| **须可读下一步** | **至少** **其一**：**(a)** **请稍后/我们正在核对** **（** **有** **Δt 或次数上界** **时** **宜** **明示** **）**；**(b)** **指引** **主站或协查** **`executionId`**；**(c)** **超时策略** **下的** **失败/取消** **之** **`stableReason`** **摘要** — **同窗** [`recovery.md`](./recovery.md)、[`../risk/unknown-stall-policy.md`](../risk/unknown-stall-policy.md)。 |
| **与卡片一致** | **类型 A 已确认** **之** **语义** **若** **进入 UNKNOWN**，**后续** **追发** **不得** **与用户已确认** **之** **方向/数量** **矛盾** **（** **除非** **新轮次** **新** **`executionId`** **）**。 |

**抽检**：[`evals/scenarios.md`](../evals/scenarios.md) **`eval.obs.504_unknown_write`**、**`eval.runtime.user_visible_phase_copy`**、**`eval.unknown.*`**；**旅程** [`product/journey-validation.md`](../../../product/journey-validation.md) **JV-06、JV-12、JV-16**。

---

## 收口检查

- [ ] **观测**存在 **`execution_state=UNKNOWN`**（或等价维度）  
- [ ] **`error-normalization.md`** 已声明 **`504`/超时** 默认进入 **`UNKNOWN`** 分支（非业务成功码）  
- [ ] **`exchange-agent` / `risk` / `eval`** 已登记 **UNKNOWN 无进展** **阈值与处置路径**（**与** **本文** **「收口与无进展（产品下限）」** **对签**）  
- [ ] **用户追问状态机** **已** **对签** [`unknown-stall-policy` §2](../risk/unknown-stall-policy.md) **与** **`eval.unknown.*`**

---

**文档版本**：0.4.2 · **维护**：Agent Runtime owner · **本版**：**增** **用户可见副本下限** **§** **与** **抽检指针**。**承** 0.4.1。
