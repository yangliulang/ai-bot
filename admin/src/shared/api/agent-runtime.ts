// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能: 场景 **`flowSummary`/`executionSteps`/`closureStatus`** · **`GET …/scenarios/{id}`**（FE_HANDOFF Phase2）
// 作者: 杨永的Agent
// 日期: 2026-05-18
// 修改功能: **`EligibilityEnvelope.requiresMainSite`**（AC-09l · FE_HANDOFF）
// 作者: 杨永的Agent
// 日期: 2026-05-18
// 修改功能: **`IntentRecognizeResponse.effectiveLocale`**（FE_HANDOFF 2026-05-18）
// 作者: 杨永的Agent
// 日期: 2026-05-15
// 修改功能: **GET /scenarios** 响应 **`orchestrationRegistryVersion`**、场景项 **`title`/`category`/`riskLevel`**（FE_HANDOFF · 运行编排页）
// 日期: 2026-05-14
// 修改功能: **现货限价** `POST …/trade/spot/limit-order`（LimitOrderMeta · FE_HANDOFF §2.2）
// 日期: 2026-05-14
// 修改功能: **`RoutingExecuteResponse.executionId`**（落库锚点 · FE_HANDOFF）
// 日期: 2026-05-14
// 修改功能: `routing/execute` Body 可选 **`marketDataLimit`**（depth/trades · FE_HANDOFF）
// 日期: 2026-05-14
// 修改功能: intent/recognize Body 扩展 sessionId 等；Response 对齐 NLU + plan（FE_HANDOFF）
// 日期: 2026-05-18
// 修改功能: **`GET …/trade/spot/open-orders`** · **`POST …/trade/spot/cancel`**（FE_HANDOFF 现货当前委托 / 撤单）
// 日期: 2026-05-13
// 修改功能: Phase2.1 现货闪兑 `GET/POST …/agent/trade/spot/quote|flash-convert` 与类型（FE_HANDOFF）
// 日期: 2026-05-13
// 修改功能: `AgentEvaluateAccessBody` 可选 `telegramChatId`；`capabilities` 补充字段说明
// 日期: 2026-05-12
// 修改功能: Phase1 `/api/v1/agent/*`（含门禁/意图/场景/execution/绑定快照）；routing/execute 增补 `symbol` 与响应 `exchangeReadPreview`

import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const PREFIX = 'v1/agent'
const SPOT_TRADE_PREFIX = 'v1/agent/trade/spot'

async function normalizeKyError(error: unknown): Promise<never> {
  if (error instanceof HTTPError) {
    const cloned = error.response.clone()
    const body: unknown = await cloned.json().catch(() => null)
    if (
      body !== null &&
      typeof body === 'object' &&
      'message' in body &&
      typeof (body as { message: unknown }).message === 'string'
    ) {
      const code =
        'code' in body && typeof (body as { code: unknown }).code === 'string'
          ? (body as { code: string }).code
          : undefined
      throw new AppError((body as { message: string }).message, {
        status: error.response.status,
        code,
      })
    }
  }
  throw await toAppError(error)
}

/** GET /access/reasons */
export interface AgentAccessReasonItem {
  code: string
  summary: string
}

export interface AgentAccessReasonsResponse {
  reasons: AgentAccessReasonItem[]
}

export async function getAgentAccessReasons(): Promise<AgentAccessReasonsResponse> {
  try {
    return await httpClient.get(`${PREFIX}/access/reasons`).json<AgentAccessReasonsResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** POST /access/evaluate */
export interface AgentEvaluateAccessBody {
  userId: string
  channel?: string
  scenarioId?: string
  /**
   * Telegram 会话 ID（`chat.id`，数值）。
   * 私聊常与 `userId`（tg_id）相同；群 / 超级群 / 话题等不同。
   * Phase1 若按 chat_id 配置环境放行名单，应传此字段以对齐 webhook 门禁。
   */
  telegramChatId?: number
}

export interface AgentEligibilityEnvelope {
  allowed: boolean
  code?: string | null
  reason?: string | null
  locale?: string | null
  /**
   * 扩展能力/诊断字段（JSON 对象，以后端为准）。
   * 示例键：`phase1Allowlist`、`bindingVerified`、`telegramChatId`（可与请求的 `telegramChatId` 对照）。
   */
  capabilities?: Record<string, unknown> | null
  evaluatedAt?: string | null
  eligibilityDecisionId?: string | null
  /**
   * **AC-09l**：是否在「欠托管绑定」语境下提示 **主站 / H5** 引导。
   * - **`true`**：通常 **`allowed=false`** 且 **`AGENT_SUBACCOUNT_REQUIRED`**（未绑定且无放行）。
   * - **`false`**：**`allowed=true`**（放行会话或 **`bindingVerified=true`**）。
   * - **`null` / 字段省略**：封禁 / 灰度 / 全局关闸等其它阻断语义（见 BACKEND_SPEC §3）。
   */
  requiresMainSite?: boolean | null
}

export async function postAgentAccessEvaluate(
  body: AgentEvaluateAccessBody,
): Promise<AgentEligibilityEnvelope> {
  try {
    return await httpClient.post(`${PREFIX}/access/evaluate`, { json: body }).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** POST /intent/recognize */
export interface AgentIntentRecognizeBody {
  text: string
  userId?: string
  channel?: string
  /** 渠道会话键，编排回放 / 可观测（可选） */
  sessionId?: string | null
  /** 当前 execution 锚点（可选） */
  executionId?: string | null
  /** BCP-47 / 产品 locale（可选） */
  locale?: string | null
  /** 上一轮已提交 scenarioId，用于跟进句消歧（可选） */
  previousScenarioId?: string | null
}

export interface AgentIntentCandidate {
  scenarioId: string
  score: number
}

/** NLU：scenarioId 假设条目（keyword_v1） */
export interface AgentIntentScenarioCandidateDraft {
  scenarioId: string
  confidence: number
}

/** NLU 草案（可替换为 LLM 结构化 JSON） */
export interface AgentIntentNluDraft {
  source: 'keyword_v1'
  primaryIntentFamily: string
  scenarioIdCandidates: AgentIntentScenarioCandidateDraft[]
  slots: Record<string, string>
  orderTypeHint: 'market' | 'limit' | 'unknown'
  clarifyHints: string[]
}

export type AgentIntentPlanNextStep =
  | 'CLARIFY'
  | 'ROUTE_READ_SKILL'
  | 'ROUTE_CHAT_FAQ'
  | 'CONFIRM_TYPE_A'
  | 'RESOLVE_FLASH_NOTIONAL'
  | 'RESOLVE_TRADE_NOTIONAL'
  | 'EXECUTE_SPOT_CANCEL'
  | 'EXECUTE_FUTURES_CANCEL'
  | 'BLOCKED_FEATURE'
  | 'STUB_NOT_EXECUTABLE'
  | 'UNKNOWN'

/** 裁决层输出（对接 Bot / Execution 编排） */
export interface AgentIntentPolicyPlan {
  nextStep: AgentIntentPlanNextStep
  resolvedScenarioId?: string | null
  clarify: string[]
  policyCodes: string[]
  note?: string | null
}

export interface AgentIntentRecognizeResponse {
  scenarioId: string | null
  confidence: number
  candidates: AgentIntentCandidate[]
  nlu?: AgentIntentNluDraft | null
  plan?: AgentIntentPolicyPlan | null
  /** 服务端意图路由版本串（可观测 / 回放） */
  orchestrationVersion?: string | null
  /** 与 nlu.source 一致时由服务端回填 */
  nluSource?: string | null
  /** 生效语言：`zh-Hans` | `zh-Hant` | `en` 等（Phase1 FE_HANDOFF 2026-05-18） */
  effectiveLocale?: string | null
}

export async function postAgentIntentRecognize(
  body: AgentIntentRecognizeBody,
): Promise<AgentIntentRecognizeResponse> {
  try {
    return await httpClient.post(`${PREFIX}/intent/recognize`, { json: body }).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** GET /scenarios · Phase2 执行流程登记 */
export interface AgentExecutionFlowStep {
  stepKey: string
  labelZh: string
  order: number
}

export type AgentScenarioReadiness = 'stub' | 'ready' | 'phase1_stub'

export interface AgentScenarioListItem {
  scenarioId: string
  summary: string
  /** 人类可读执行流程（列表优先展示） */
  flowSummary?: string | null
  readiness: AgentScenarioReadiness
  /** 中文短标题（后端寄存器） */
  title?: string | null
  /** read | trade | margin | wealth | automation | chat */
  category?: string | null
  /** low | medium | high */
  riskLevel?: string | null
  /** FROZEN | TBD | PLACEHOLDER */
  closureStatus?: string | null
  executionSteps?: AgentExecutionFlowStep[]
}

export interface AgentScenariosResponse {
  scenarios: AgentScenarioListItem[]
  /** 与控制台寄存器 bundle 对齐，如 `2026.05-orc-v1` */
  orchestrationRegistryVersion?: string | null
}

export interface AgentScenarioDetail {
  scenarioId: string
  summary: string
  flowSummary: string
  readiness: AgentScenarioReadiness
  title?: string | null
  category?: string | null
  riskLevel?: string | null
  closureStatus?: string | null
  flowAnchor?: string | null
  specRefs?: string[]
  promptBindingHint?: string | null
  executionSteps: AgentExecutionFlowStep[]
  orchestrationRegistryVersion?: string | null
}

export async function getAgentScenarios(): Promise<AgentScenariosResponse> {
  try {
    return await httpClient.get(`${PREFIX}/scenarios`).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAgentScenarioDetail(scenarioId: string): Promise<AgentScenarioDetail> {
  const id = scenarioId.trim()
  if (!id) throw new AppError('scenarioId 不可为空', { status: 400 })
  try {
    return await httpClient.get(`${PREFIX}/scenarios/${encodeURIComponent(id)}`).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** POST /routing/execute */
export interface AgentRoutingExecuteBody {
  scenarioId: string
  userId: string
  channel?: string
  utteranceSnapshot?: string
  /** `read.market.ticker` | `read.market.depth` | `read.market.trades` 等只读行情场景由服务端校验 */
  symbol?: string
  /**
   * `read.market.depth`（每侧档位数）/ `read.market.trades`（成交条数上限），整数 **1～100**，默认服务端 **20**。
   */
  marketDataLimit?: number
}

export interface AgentRoutingExecuteResponse {
  routed: boolean
  scenarioId?: string | null
  note?: string | null
  /** 与 Admin `GET …/observability/executions/{executionId}/timeline` 对齐 */
  executionId?: string | null
  /** Phase1：只读所内 JSON 摘要（过滤后），无密钥 */
  exchangeReadPreview?: Record<string, unknown> | null
}

export async function postAgentRoutingExecute(
  body: AgentRoutingExecuteBody,
): Promise<AgentRoutingExecuteResponse> {
  try {
    return await httpClient.post(`${PREFIX}/routing/execute`, { json: body }).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** POST /execution/accept */
export interface AgentExecutionAcceptBody {
  userId: string
  scenarioId?: string
  channel?: string
  idempotencyKey?: string
}

export interface AgentExecutionAcceptResponse {
  executionId: string
  state: string
  createdAt: string
}

export async function postAgentExecutionAccept(
  body: AgentExecutionAcceptBody,
): Promise<AgentExecutionAcceptResponse> {
  try {
    return await httpClient.post(`${PREFIX}/execution/accept`, { json: body }).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export interface AgentExecutionStatusResponse {
  executionId: string
  userId: string
  scenarioId?: string | null
  state: string
  createdAt: string
  updatedAt?: string | null
}

export async function getAgentExecution(executionId: string): Promise<AgentExecutionStatusResponse> {
  try {
    return await httpClient.get(`${PREFIX}/execution/${executionId}`).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export interface AgentExecutionFinalizeBody {
  executionId: string
  outcome: 'SUCCESS' | 'FAILED' | 'CANCELLED'
  note?: string
}

export interface AgentExecutionFinalizeResponse {
  executionId: string
  state: string
  finalizedAt: string
}

export async function postAgentExecutionFinalize(
  body: AgentExecutionFinalizeBody,
): Promise<AgentExecutionFinalizeResponse> {
  try {
    return await httpClient.post(`${PREFIX}/execution/finalize`, { json: body }).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

// --- Phase1 onboarding / binding snapshot (§1.1)

export type AgentTradingApiBindingStatus = 'NONE' | 'BOUND'

/** GET /api-binding/status ?userId= */
export interface AgentApiBindingStatusResponse {
  telegramUserId: number
  agentTradingApiBindingStatus: AgentTradingApiBindingStatus
  openapiBaseUrl?: string | null
  bindingId?: number | null
  tgUsername?: string | null
  updatedAt?: string | null
}

export async function getAgentApiBindingStatus(
  userId: string,
): Promise<AgentApiBindingStatusResponse> {
  try {
    return await httpClient
      .get(`${PREFIX}/api-binding/status`, { searchParams: { userId } })
      .json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** GET /subaccount/status ?userId= */
export interface AgentSubaccountStatusResponse {
  telegramUserId: number
  subaccountReady: boolean
  agentSubAccountId: string | null
  tradingApiBindingStatus: AgentTradingApiBindingStatus
}

export async function getAgentSubaccountStatus(
  userId: string,
): Promise<AgentSubaccountStatusResponse> {
  try {
    return await httpClient
      .get(`${PREFIX}/subaccount/status`, { searchParams: { userId } })
      .json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** POST /onboarding/initiate */
export interface AgentOnboardingInitiateBody {
  telegram?: { tg_id?: string | null }
}

export interface AgentOnboardingInitiateResponse {
  onboardingId: string
  telegramUserId: number
  nextStep: 'bind_trading_api' | 'complete'
  agentTradingApiBindingStatus: AgentTradingApiBindingStatus
}

export async function postAgentOnboardingInitiate(
  body: AgentOnboardingInitiateBody,
): Promise<AgentOnboardingInitiateResponse> {
  try {
    return await httpClient.post(`${PREFIX}/onboarding/initiate`, { json: body }).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** POST /subaccount/create — Phase1 恒为 DEFERRED，非真实创建 */
export interface AgentSubaccountCreatePhase1Response {
  accepted: boolean
  status: 'DEFERRED_EXCHANGE_CONSOLE'
  code: string
  message: string
}

export async function postAgentSubaccountCreate(): Promise<AgentSubaccountCreatePhase1Response> {
  try {
    return await httpClient.post(`${PREFIX}/subaccount/create`, { json: {} }).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

// --- Phase 2.1 — spot quote + MARKET flash-convert（须托管绑定；见 BACKEND_SPEC §3.3）

/** GET /trade/spot/quote */
export interface AgentTradeSpotQuoteResponse {
  scenarioId: string
  symbol: string
  symbolOrder: string
  /** 公开 ticker 摘要（后端过滤，无密钥） */
  quotePreview: Record<string, unknown>
}

export async function getAgentTradeSpotQuote(
  userId: string,
  symbol: string,
): Promise<AgentTradeSpotQuoteResponse> {
  try {
    return await httpClient
      .get(`${SPOT_TRADE_PREFIX}/quote`, {
        searchParams: { userId, symbol },
      })
      .json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** POST /trade/spot/flash-convert */
export interface AgentTradeSpotFlashConvertBody {
  userId: string
  symbol: string
  side: 'BUY' | 'SELL'
  /** 十进制字符串；MARKET BUY 时为计价资产数量（amount） */
  volume: string
  newClientOrderId?: string | null
}

export interface AgentTradeSpotFlashConvertResponse {
  scenarioId: string
  orderId: string | null
  orderIdString: string | null
  clientOrderId: string | null
  status: string | null
  symbol: string | null
  side: string | null
  type: string | null
  exchangeOrderPreview: Record<string, unknown>
}

export async function postAgentTradeSpotFlashConvert(
  body: AgentTradeSpotFlashConvertBody,
): Promise<AgentTradeSpotFlashConvertResponse> {
  try {
    return await httpClient.post(`${SPOT_TRADE_PREFIX}/flash-convert`, { json: body }).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** POST /trade/spot/limit-order · LIMIT，`volume`=base 数量 */
export interface AgentTradeSpotLimitOrderBody {
  userId: string
  symbol: string
  side: 'BUY' | 'SELL'
  /** base 数量十进制字符串 */
  volume: string
  price: string
  timeInForce?: 'GTC' | 'IOC' | 'FOK' | null
  newClientOrderId?: string | null
}

export interface AgentTradeSpotLimitOrderResponse {
  scenarioId: string
  orderId: string | null
  orderIdString: string | null
  clientOrderId: string | null
  status: string | null
  symbol: string | null
  side: string | null
  type: string | null
  exchangeOrderPreview: Record<string, unknown>
}

export async function postAgentTradeSpotLimitOrder(
  body: AgentTradeSpotLimitOrderBody,
): Promise<AgentTradeSpotLimitOrderResponse> {
  try {
    return await httpClient.post(`${SPOT_TRADE_PREFIX}/limit-order`, { json: body }).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** GET /trade/spot/open-orders · Coobit GET /sapi/v2/openOrders */
export interface AgentTradeSpotOpenOrdersResponse {
  scenarioId: string
  symbol?: string | null
  symbolOrder?: string | null
  orders: Record<string, unknown>[]
}

export async function getAgentTradeSpotOpenOrders(
  userId: string,
  opts?: { symbol?: string; limit?: number },
): Promise<AgentTradeSpotOpenOrdersResponse> {
  const searchParams: Record<string, string | number> = { userId }
  const sym = opts?.symbol?.trim()
  if (sym) searchParams.symbol = sym
  if (opts?.limit != null && Number.isFinite(opts.limit)) {
    searchParams.limit = opts.limit
  }
  try {
    return await httpClient
      .get(`${SPOT_TRADE_PREFIX}/open-orders`, { searchParams })
      .json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** POST /trade/spot/cancel · Coobit POST /sapi/v2/cancel */
export interface AgentTradeSpotCancelBody {
  userId: string
  symbol: string
  orderId?: string | null
  newClientOrderId?: string | null
}

export interface AgentTradeSpotCancelResponse {
  scenarioId: string
  orderId?: string | null
  orderIdString?: string | null
  clientOrderId?: string | null
  status?: string | null
  symbol?: string | null
  side?: string | null
  type?: string | null
  exchangeOrderPreview: Record<string, unknown>
}

export async function postAgentTradeSpotCancel(
  body: AgentTradeSpotCancelBody,
): Promise<AgentTradeSpotCancelResponse> {
  try {
    return await httpClient.post(`${SPOT_TRADE_PREFIX}/cancel`, { json: body }).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
