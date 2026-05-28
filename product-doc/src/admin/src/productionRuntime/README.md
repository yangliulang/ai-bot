# productionRuntime · 契约对签订阅（非生产后端）

本仓库定位为 **需求 + Admin 原型**；**可上线的 Agent/BFF/Gateway 实现由专门开发团队在所内工程仓库交付**。本目录下 TypeScript **不是** 「本仓必须维护的运行时代码」，而是：**给原型与 MR 文档用的、可跑的契约小样**（同窗 Vitest，便于和需求/OpenAPI **对表达、防漂移**）。

若你只需要规格与 YAML，以 **`specs/`**、`specs/openapi/` 为准；下列模块 **可当作开发团队的参考算术/伪代码**，可复制或重写，**不**绑架所内栈选型。

| 模块 | 用途 |
|------|------|
| `writePathPipelineOrder.ts` | 写路径事件五段序（`eval.runtime.pipeline_write_order`） |
| `executionGatewayWriteBarrier.ts` | Gateway 写前四断言（**MR-B §9**、`eval.gateway.*`、INV-008～010） |
| `tradeResolverTypes.ts` | `AgentTradeResolverOutput` 等与 OpenAPI **`orchestration-runtime-schemas`** 同窗 |
| `tradeWriteResolverGate.ts` | 闪兑 / **现货限价** Resolver、`build*` 输出拼装、载货类型 A 门禁（INV-008） |
| `internalTradeResolverAdapter.ts` | `postInternalAgentOrchestrationTradeResolver` — 同窗 **`internal/agent-orchestration.yaml`** |
| `internalBillingEntitlementsAdapter.ts` | **`GET|POST`** 同窗 **`internal/billing-entitlements.yaml`** · `getInternalBillingEntitlementsBalance` / `postInternalBillingEntitlementsDebit` / `postInternalCommercePackGrantsApply`（**`fetch` 占位**） |
| `commerceEntitlementS5Settle.ts` | **S5**：`executeConsumptionSettlement` — **`ENTITLEMENT_DEBIT`** · **`deriveEntitlementDebitIdempotencyKey`**（**SC-B20**） |
| `commerceEntitlementS2Evaluate.ts` | **S2 一键**：`evaluateCommerceEntitlementS2Gate` — **`balance` HTTP** + **`runCommerceEntitlementPreflight`** · **透传** **`BillingEntitlementsHttpError`** |
| `commerceEntitlementPreflightGate.ts` | **`consume-and-bill` · S2** · 轨 B 额度门禁纯函数小样（**`phase2CommerceRailsEnabled` 关默认放行**）；同窗 **`internal/billing-entitlements.yaml`** **balance / debit** |
| `billingCapabilityMap.ts` | **`BILLING_CAPABILITY_MAP` 小样**：**`scenarioId → capabilitySkuId`**（Demo 与 Admin mock 同窗） |
| `consumptionBillingHost.ts` | **MR-BILL-B1/B2 宿主**：**`runConsumeAndBillS2CommerceGate`** · **`runConsumeAndBillS5Settlement`** · **`parseConsumptionBillingHostConfigFromEnv`** |
| （Admin UI）`api/billingCommerceClient.ts` | **FR-MC509～512** · **`GET …/admin/billing/commerce/*`**；同窗 **`dev/billingCommerceBffMiddleware.ts`** |
| `writePathConsumeAndBillOrchestrator.ts` | **MR-RT-B4 × MR-BILL** 同窗：**`runWritePathConsumeAndBill`**（S2 → S5 · **ENTITLEMENT_ONLY** · balance **5xx fail-closed**） |
| `allInOrchestration.ts` | INV-010 · **`orchestrationNextSteps`**（只读补槽） |
| `orchestrationReadBalanceFill.ts` | **只读补槽执行小样** · `quoteQty` 落盘 |
| `clarifyKeyboard.ts` | **澄清 inline_keyboard** 载荷 · **`SC-CH-TG-10`** |
| `telegramClarifyOutbound.ts` | **`telegramOutbound`** 出站提示聚合 |
| `clarifyOrchestrationPipeline.ts` | **Resolver → 补槽 → 再 Resolver** Demo 管线 |
| `telegramInboundFeedback.ts` | **Telegram §2.3.1** · **`sendChatAction(typing)`** 调度 · **`SC-CH-TG-09`** |

**规格同窗**：[`specs/requirements/skill-specs/MR-B-BFF-IMPLEMENTATION.md`](../../../../specs/requirements/skill-specs/MR-B-BFF-IMPLEMENTATION.md) §9 · [`runtime-invariants.md`](../../../../specs/requirements/Runtime/runtime-invariants.md) · [`evals/scenarios.md`](../../../../specs/requirements/evals/scenarios.md) `eval.gateway.*`。

**开发团队可选用**：编排层在拼装 `canonicalPayload` / `confirmationSnapshot` 后可对照 `runExecutionGatewayWriteBarrier` 的断言顺序；或仅阅读 OpenAPI/`specs` 中的同一规则，自行用目标语言实现。
内部 HTTP 草稿与组件 `InternalTradeResolverRequest` 的对照见 `postInternalAgentOrchestrationTradeResolver`（`internalTradeResolverAdapter.ts`）。
