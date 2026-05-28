# Billing Management · 规则与约束

1. **语义**：**Agent 消耗计费** **必须以** **`PER_EXECUTION_FINAL`** **为单次核销边界**；**S5 默认** **`ENTITLEMENT_DEBIT`（轨 B）**。
2. **幂等（核销 · 轨 B · 主链）**：**同一 `executionId`** **至多一条成功 `ENTITLEMENT_DEBIT`**（**`SC-B20`**）。**`idempotencyKey`** **须** **绑定 `executionId`**（**`FR-B05`**）；**建议后缀** **`:rail-b:entitlement-debit`** — **同窗** [`commerce-model` §5.1](commerce-model.md)。**重复请求** **须** **安全重放** **得等价 **`billingTraceId`/状态**。
3. **幂等（扣费 · 轨 A · 非 Agent S5）**：**历史 Token 账务** **仍适用** **`SC-B08`**（**`CHARGE`**）；**不** **与 Agent 消耗 S5 组合** — **OpenAPI 对读**。
4. **幂等（退款）**：须提供 **`refundIdempotencyKey`**（或同窗名）；**同一 `billingTraceId`** **成功冲正至多一次**（**`SC-B15`**）。
5. **权限**：财务 / 运营 / 只读 **分列**。**平台级导出**（**`FR-MC507`**）仅 **财务或具 `billing.export` 角色**。**用户侧**（**`FR-B12`～`FR-B16`**）仅 **本人数据**。**商业层**（**`FR-MC509～512`**）**编辑** **须** **双签同窗** **FR-MC502**。
6. **数据**：导出须 **水印**、脱敏、下载时效（**产品定稿**）。
7. **与 exchange-agent**：实例 Pause 与 **暂停扣费** 可不同步；UI **须**区分说明。
8. **退款（`FR-MC505`）**：须绑定原 **`billingTraceId`/`executionId`**；**是否允许部分退款** **`design` 冻结**；账务 **须**与子账户账本 **对账等价**（冲正或反向划转，**同窗 PRD**）。
9. **用户级 vs 平台级流水**：用户 API **禁止**越权查他人；平台 API **须**管理台 SSO。**导出列**脱敏级别可不同；**月度 rollup** 须满足 **SC-B14**（与当月明细可加总核对）。
10. **商业阻断（Phase 2）**：**配额为零** **不得** **静默降级为套餐外按量后付**（**`FR-B21`**）；**`ENTITLEMENT_DEBIT` 返回 `INSUFFICIENT`** **时** **S5** **终止** **不得** **fallback 子账户 Token 扣费**（**同窗** [`flow.md`](flow.md)）。

---

## 流水 ledger 项类型（OpenAPI 枚举占位）

**与** **`agent-management` §7.1 `code`** **不同**：后者为 **I02 准入/阻断**；本条为 **账单与对账** 上的 **扣费/退款** 形态。

| 值（示意名） | 含义 |
|--------------|------|
| **`ENTITLEMENT_DEBIT`** | **Agent 消耗主链**：**订阅/包** 额度核销（**`SC-B20`**；**绑定 `executionId`、`capabilitySkuId`/`packGrantId`**） |
| **`CHARGE`** | **轨 A 历史/对读**：**Token/USDT 扣费**（**`SC-B08`**；**非 Agent S5 默认**） |
| **`REFUND`** | **退款/冲正**（绑定 **`originalBillingTraceId`**，**`refundIdempotencyKey`**，**`SC-B15`**） |
| **`ADJUSTMENT`** | **手工调账**（**V1 默认不下发用户自助**）；若启用 **须同窗 ADR + OpenAPI** |
| **`SUBSCRIPTION_PERIOD_OPEN`**（示意） | **账期开立**（**可选**：月度订阅线；**OpenAPI MR 终裁**） |
| **`PACK_GRANT`**（示意） | **加购包** 额度 **入账**（**与 FR-B18 同窗**） |

**`billingTraceId`** 须在 **`ENTITLEMENT_DEBIT`** 与由其衍生的 **`REFUND`** 之间可追溯；**观测** **可 join** **`executionId`**（**D-5**）。导出列与同名字段以 **`billing-schemas.yaml`** / **`design/api`** 终裁。

---

**文档版本**：0.3.0 · **维护**：账务 + 后台 owner · **本版**：**Agent 消耗仅轨 B**；**轨 A 移出 S5 组合规则**。**承** **0.2.1**。
