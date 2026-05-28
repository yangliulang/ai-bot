/**
 * 人工确认规则 — 风控运营语义（风险条件 → 处理动作）
 */

export type RiskLevel = "low" | "medium" | "high";

export type RuleAction = "force_confirm" | "second_confirm" | "otp_confirm" | "block_auto_execute";

export type ScenarioKey =
  | "spot"
  | "futures"
  | "convert"
  | "wealth"
  | "leverage"
  | "transfer"
  | "conditional_order";

export type TriggerFieldKey = "nominal_usdt" | "leverage" | "operation_scope" | "custom";

export type TriggerOpKey = "gt" | "gte" | "lt" | "lte" | "eq" | "contains";

export interface TriggerConditionRow {
  fieldKey: TriggerFieldKey;
  operator: TriggerOpKey;
  /** 展示用原值，如 50000、20、文案描述 */
  value: string;
}

export interface ConfirmationRuleDefinition {
  id: string;
  title: string;
  /** 规则说明 */
  summary: string;
  riskLevel: RiskLevel;
  /** 触发条件（构造器行） */
  triggerConditions: TriggerConditionRow[];
  /** 适用场景（多选枚举） */
  scenarios: ScenarioKey[];
  /** 命中后的处理动作 */
  action: RuleAction;
  defaultEnabled: boolean;
}

export const RISK_LEVEL_OPTIONS: { value: RiskLevel; label: string }[] = [
  { value: "low", label: "低风险" },
  { value: "medium", label: "中风险" },
  { value: "high", label: "高风险" },
];

export const SCENARIO_OPTIONS: { value: ScenarioKey; label: string }[] = [
  { value: "spot", label: "现货交易" },
  { value: "futures", label: "合约交易" },
  { value: "convert", label: "闪兑" },
  { value: "wealth", label: "理财申购" },
  { value: "leverage", label: "杠杆调整" },
  { value: "transfer", label: "资金划转" },
  { value: "conditional_order", label: "条件单/计划委托" },
];

export const TRIGGER_FIELD_OPTIONS: { value: TriggerFieldKey; label: string }[] = [
  { value: "nominal_usdt", label: "名义本金（USDT 等值）" },
  { value: "leverage", label: "杠杆（倍）" },
  { value: "operation_scope", label: "操作范围" },
  { value: "custom", label: "其他" },
];

export const TRIGGER_OPERATOR_OPTIONS: { value: TriggerOpKey; label: string }[] = [
  { value: "gt", label: ">" },
  { value: "gte", label: "≥" },
  { value: "lt", label: "<" },
  { value: "lte", label: "≤" },
  { value: "eq", label: "=" },
  { value: "contains", label: "包含" },
];

export const RULE_ACTION_OPTIONS: { value: RuleAction; label: string; hint: string }[] = [
  { value: "force_confirm", label: "强制确认", hint: "须先完成摘单确认，再继续业务执行" },
  { value: "second_confirm", label: "二次确认", hint: "在常规确认外再追加一轮风险提示与确认" },
  { value: "otp_confirm", label: "OTP 确认", hint: "须通过一次性口令等第二因素确认" },
  {
    value: "block_auto_execute",
    label: "禁止自动执行",
    hint: "命中后不得由系统自动落单，仅人工或显式确认后放行",
  },
];

export const RULE_ACTION_META: Record<RuleAction, { label: string; color: string; hint: string }> = {
  force_confirm: { label: "强制确认", color: "blue", hint: RULE_ACTION_OPTIONS[0].hint },
  second_confirm: { label: "二次确认", color: "magenta", hint: RULE_ACTION_OPTIONS[1].hint },
  otp_confirm: { label: "OTP 确认", color: "purple", hint: RULE_ACTION_OPTIONS[2].hint },
  block_auto_execute: { label: "禁止自动执行", color: "red", hint: RULE_ACTION_OPTIONS[3].hint },
};

/** 关闭「强制确认 / 禁止自动执行」类规则时额外警示 */
export function ruleActionNeedsStrongDisableGuard(action: RuleAction): boolean {
  return action === "force_confirm" || action === "block_auto_execute";
}

export function scenarioLabels(keys: ScenarioKey[]): string {
  const map = Object.fromEntries(SCENARIO_OPTIONS.map((o) => [o.value, o.label])) as Record<string, string>;
  return keys.map((k) => map[k] ?? k).join(" · ");
}

/** 数值类字段用比较符；范围/文案类用包含、等于 */
export function operatorsForField(fieldKey: TriggerFieldKey): TriggerOpKey[] {
  if (fieldKey === "nominal_usdt" || fieldKey === "leverage") {
    return ["gt", "gte", "lt", "lte", "eq"];
  }
  return ["contains", "eq"];
}

export function defaultOperatorForField(fieldKey: TriggerFieldKey): TriggerOpKey {
  const ops = operatorsForField(fieldKey);
  return ops[0];
}

/** 单条条件展示（与 formatTriggerSummary 内逻辑一致） */
export function formatTriggerLine(r: TriggerConditionRow): string {
  const fl = Object.fromEntries(TRIGGER_FIELD_OPTIONS.map((o) => [o.value, o.label])) as Record<string, string>;
  const ol = Object.fromEntries(TRIGGER_OPERATOR_OPTIONS.map((o) => [o.value, o.label])) as Record<string, string>;
  const field = fl[r.fieldKey] ?? r.fieldKey;
  const op = ol[r.operator] ?? r.operator;
  const val =
    r.fieldKey === "leverage" && r.value && !String(r.value).toLowerCase().includes("x")
      ? `${r.value}x`
      : r.fieldKey === "nominal_usdt" && r.value && !String(r.value).toUpperCase().includes("USDT")
        ? `${r.value} USDT`
        : r.value;
  return `${field} ${op} ${val}`;
}

export function formatTriggerSummary(rows: TriggerConditionRow[]): string {
  if (!rows.length) return "—";
  return rows.map(formatTriggerLine).join("；");
}

/** 内置规则（演示）：不含任何规格路径或 Runtime 字段 */
export const CONFIRMATION_RULES_CATALOG: ConfirmationRuleDefinition[] = [
  {
    id: "hitl-trade-fund-write",
    title: "交易与资金侧操作 · 强制确认",
    summary: "会改变持仓、委托或账户余额的请求，须先经用户完成摘单确认后再落单，覆盖现货/合约/划转等主要场景。",
    riskLevel: "high",
    triggerConditions: [
      { fieldKey: "operation_scope", operator: "contains", value: "改变持仓、委托或余额" },
    ],
    scenarios: ["spot", "futures", "transfer", "conditional_order", "leverage"],
    action: "force_confirm",
    defaultEnabled: true,
  },
  {
    id: "hitl-large-notional",
    title: "大额名义本金 · 二次确认",
    summary: "单笔名义本金超过平台大额阈值时，除常规确认外须再次核对关键参数与风险。",
    riskLevel: "high",
    triggerConditions: [{ fieldKey: "nominal_usdt", operator: "gt", value: "50,000" }],
    scenarios: ["spot", "futures"],
    action: "second_confirm",
    defaultEnabled: true,
  },
  {
    id: "hitl-high-leverage",
    title: "高杠杆 · 二次确认",
    summary: "杠杆超过配置上限或处于高倍档时，须再次确认强平与资金占用风险。",
    riskLevel: "high",
    triggerConditions: [{ fieldKey: "leverage", operator: "gt", value: "20" }],
    scenarios: ["futures", "leverage"],
    action: "second_confirm",
    defaultEnabled: true,
  },
  {
    id: "hitl-conditional-auto",
    title: "条件单与自动化任务",
    summary: "新建或撤销条件单、计划委托及会落单的自动化任务时，须先完成用户侧确认。",
    riskLevel: "medium",
    triggerConditions: [{ fieldKey: "operation_scope", operator: "contains", value: "条件单/自动化任务创建或撤销" }],
    scenarios: ["conditional_order", "futures", "spot"],
    action: "force_confirm",
    defaultEnabled: true,
  },
  {
    id: "hitl-wealth",
    title: "理财申购赎回",
    summary: "须通过官网或理财 H5 完成的申赎，助手仅可引导官方入口，不得越过用户确认代为提交。",
    riskLevel: "medium",
    triggerConditions: [{ fieldKey: "operation_scope", operator: "contains", value: "理财申赎且需 H5/官网" }],
    scenarios: ["wealth"],
    action: "force_confirm",
    defaultEnabled: true,
  },
  {
    id: "hitl-close-all",
    title: "一键平仓与清仓类指令",
    summary: "一键平仓、全仓 reduce-only 等强语义动作，须在确认流程中显式收口，避免误触大资金变动。",
    riskLevel: "high",
    triggerConditions: [{ fieldKey: "operation_scope", operator: "contains", value: "一键平仓或全仓清仓类" }],
    scenarios: ["futures"],
    action: "second_confirm",
    defaultEnabled: true,
  },
];

/** 演示用自定义样例（非内置）：首次无会话或执行「恢复默认」时注入，可编辑、可删除 */
export const DEMO_CUSTOM_CONFIRMATION_RULES: ConfirmationRuleDefinition[] = [
  {
    id: "custom-demo-flash-convert",
    title: "闪兑 · 大额二次确认",
    summary: "闪兑单笔名义超过运营阈值时，除常规确认外须再次核对币种与到账信息。",
    riskLevel: "medium",
    triggerConditions: [{ fieldKey: "nominal_usdt", operator: "gt", value: "10,000" }],
    scenarios: ["convert"],
    action: "second_confirm",
    defaultEnabled: true,
  },
  {
    id: "custom-demo-transfer-otp",
    title: "资金划出 · OTP 验证",
    summary: "划出类操作超过一定名义时，须通过 OTP 等第二因素校验后再继续。",
    riskLevel: "high",
    triggerConditions: [{ fieldKey: "nominal_usdt", operator: "gte", value: "5,000" }],
    scenarios: ["transfer"],
    action: "otp_confirm",
    defaultEnabled: true,
  },
  {
    id: "custom-demo-block-auto-order",
    title: "条件单机器人模板 · 禁止自动执行",
    summary: "命中特定高频/网格模板时禁止静默自动落单，须显式确认或人工介入后再执行。",
    riskLevel: "high",
    triggerConditions: [
      { fieldKey: "operation_scope", operator: "contains", value: "高频或网格类自动化模板" },
    ],
    scenarios: ["futures", "conditional_order"],
    action: "block_auto_execute",
    defaultEnabled: false,
  },
];

export function cloneDemoCustomConfirmationRules(): ConfirmationRuleDefinition[] {
  return DEMO_CUSTOM_CONFIRMATION_RULES.map((r) => ({
    ...r,
    triggerConditions: r.triggerConditions.map((row) => ({ ...row })),
    scenarios: [...r.scenarios],
  }));
}
