/**
 * 编排层 Resolver 结构化输出 — 与 `specs/openapi/components/orchestration-runtime-schemas.yaml`
 * 之 `AgentTradeResolverOutput` 同窗（TS 侧 SSOT 供所内 BFF import）。
 *
 * 规格：INV-008 / confirmation-flow §1 步骤 2 · runtime-invariants §0
 */

export type AgentTradeResolverOutput = {
  /**
   * 粗粒度阶段（所内可扩展枚举）。
   * 例：`trade`、`read_only`、`clarify`
   */
  intent: string;
  /**
   * 语义挂件：如 ALL_IN（满仓/清仓）、用户显式 FULL_BOOK 等 — 网关侧可映射 INV-010。
   */
  semanticIntent?: string;
  /**
   * 已路由到的 L0 skill；缺参或未路由可为空。
   */
  skillId?: string;
  /**
   * 已从用户/解析器 **显式** 收敛的槽位（**不** 含静默默认经济数量）。
   */
  resolved: Record<string, string | number | boolean | null>;
  /**
   * 仍缺的 L0 写槽键；空数组表示「对当前 skill 条目完备」（仍须再过校验与血缘门）。
   */
  missing: string[];
};

/** `skill.spot.flash_convert` 槽位输入（L0 摘要）。 */
export type FlashConvertResolverInput = {
  symbol?: string | null;
  side?: string | null;
  type?: string | null;
  quantity?: string | null;
  quoteQty?: string | null;
};

/** `skill.spot.limit_order` 槽位输入（L0 摘要）。 */
export type SpotLimitOrderResolverInput = {
  symbol?: string | null;
  side?: string | null;
  type?: string | null;
  price?: string | null;
  quantity?: string | null;
  quoteQty?: string | null;
  timeInForce?: string | null;
};

export type SpotLimitOrderResolverOptions = {
  /**
   * 当 API 必选或会话已选定 TIF 时由编排打开 — `skill.spot.limit_order` L0 §1。
   */
  requireTimeInForce?: boolean;
};
