/** 与 specs/requirements/domains/agent/agent-orchestration/routing-engine.md §1～§4 对签的 Demo 镜像（节选可扩展） */

import { ORCHESTRATION_VERSION_DISPLAY } from "../../../data/orchestrationConstants";

export type ScenarioCategory = "read" | "write" | "wealth" | "monitoring";

/** 闭环口径：overview §6 / contract-closure（仅作 Runtime 元数据，主表用 opsRuntimeStatus） */
export type ClosureStatus = "FROZEN" | "TBD" | "PLACEHOLDER";

export type ScenarioRiskLevel = "low" | "medium" | "high";

export interface ScenarioRegistryRow {
  scenarioId: string;
  category: ScenarioCategory;
  /** 运营主展示：场景名称 */
  scenarioTitle: string;
  /** 运营主展示：执行流程（人话） */
  flowSummary: string;
  /** 运营主展示：风险等级 */
  riskLevel: ScenarioRiskLevel;
  typicalGoal: string;
  /** 内部锚点 · 详见 Drawer */
  flowAnchor: string;
  specRefs: string[];
  closureStatus: ClosureStatus;
  promptBindingHint: string;
}

export { ORCHESTRATION_VERSION_DISPLAY };

/** closureStatus → 运营可见状态 */
export function opsRuntimeStatusLabel(status: ClosureStatus): string {
  if (status === "FROZEN") return "已启用";
  if (status === "TBD") return "测试中";
  return "已暂停";
}

export function opsRuntimeStatusColor(status: ClosureStatus): "success" | "warning" | "default" {
  if (status === "FROZEN") return "success";
  if (status === "TBD") return "warning";
  return "default";
}

const RISK_LABEL: Record<ScenarioRiskLevel, string> = {
  low: "低风险",
  medium: "中风险",
  high: "高风险",
};

const RISK_COLOR: Record<ScenarioRiskLevel, string> = {
  low: "blue",
  medium: "gold",
  high: "red",
};

export function scenarioRiskTag(level: ScenarioRiskLevel) {
  return { label: RISK_LABEL[level], color: RISK_COLOR[level] };
}

export const MOCK_SCENARIO_REGISTRY: ScenarioRegistryRow[] = [
  {
    scenarioId: "market.read_quote",
    category: "read",
    scenarioTitle: "实时行情摘要",
    flowSummary: "分析 → 读行情 → 返回结果",
    riskLevel: "low",
    typicalGoal: "实时价量摘要",
    flowAnchor: "market-intelligence · read-analyze-and-search-via-agent",
    specRefs: [
      "domains/agent/exchange-agent/market-intelligence.md",
      "flows/read-analyze-and-search-via-agent.md",
    ],
    closureStatus: "FROZEN",
    promptBindingHint: "命中后解析 promptPackRef（TRADING/ANALYZE 大类）",
  },
  {
    scenarioId: "market.read_microstructure",
    category: "read",
    scenarioTitle: "盘口与成交概览",
    flowSummary: "读取盘口 → 汇总展示",
    riskLevel: "low",
    typicalGoal: "盘口、公共成交",
    flowAnchor: "同上 · trade-assistance §8.3 只读",
    specRefs: ["domains/agent/exchange-agent/trade-assistance.md §8.3", "flows/read-analyze-and-search-via-agent.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "B 类只读工具链",
  },
  {
    scenarioId: "market.read_deep_analysis",
    category: "read",
    scenarioTitle: "K 线与指标解读",
    flowSummary: "分析 → 解读 → 返回",
    riskLevel: "low",
    typicalGoal: "K 线 / 指标 + 解读",
    flowAnchor: "read-analyze-and-search-via-agent",
    specRefs: ["flows/read-analyze-and-search-via-agent.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "分析意图 + 可选 C 类外网预算",
  },
  {
    scenarioId: "futures.read_funding",
    category: "read",
    scenarioTitle: "资金费率摘要",
    flowSummary: "读资金费率 → 返回",
    riskLevel: "low",
    typicalGoal: "资金费率摘要",
    flowAnchor: "读流；写切换 trade-via-agent",
    specRefs: ["flows/read-analyze-and-search-via-agent.md", "flows/trade-via-agent.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "升写前须单轮 scenario 收敛（FR-AO02）",
  },
  {
    scenarioId: "research.rss_or_macro",
    category: "read",
    scenarioTitle: "宏观与外链简报",
    flowSummary: "检索来源 → 汇总（asOf 可见）",
    riskLevel: "medium",
    typicalGoal: "简报 / 外链研究",
    flowAnchor: "来源与 asOf 须可见",
    specRefs: ["flows/read-analyze-and-search-via-agent.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "C 类合规与 ADR-003",
  },
  {
    scenarioId: "research.sentiment_and_news",
    category: "read",
    scenarioTitle: "情绪与舆情摘要",
    flowSummary: "检索 → 合规收口 → 返回",
    riskLevel: "medium",
    typicalGoal: "社媒情绪 + 新闻等 C 类编排收口",
    flowAnchor: "read-analyze · trade-assistance §8.4",
    specRefs: ["flows/read-analyze-and-search-via-agent.md", "domains/agent/exchange-agent/trade-assistance.md §8.4"],
    closureStatus: "FROZEN",
    promptBindingHint: "v0.1 稳定键；须带 scenarioId（FR-AO05）",
  },
  {
    scenarioId: "orders.read_activity",
    category: "read",
    scenarioTitle: "订单与成交查询",
    flowSummary: "私域读单 → 结构化返回",
    riskLevel: "low",
    typicalGoal: "在途委托、近期成交（私域读）",
    flowAnchor: "portfolio-insight · FR-T02",
    specRefs: ["domains/agent/exchange-agent/portfolio-insight.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "只读 · 无类型 A",
  },
  {
    scenarioId: "portfolio.read_pnl_exposure",
    category: "read",
    scenarioTitle: "盈亏与敞口",
    flowSummary: "读持仓 → 叙事摘要",
    riskLevel: "low",
    typicalGoal: "盈亏 / 敞口叙事",
    flowAnchor: "SC-PI01/02 · portfolio-insight",
    specRefs: ["domains/agent/exchange-agent/portfolio-insight.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "禁止 ticker 顶替成交叙事",
  },
  {
    scenarioId: "trade.spot.flash_convert",
    category: "write",
    scenarioTitle: "现货闪兑",
    flowSummary: "风险检查 → 确认 → 成交",
    riskLevel: "medium",
    typicalGoal: "现货闪兑 / 市价族",
    flowAnchor: "trade-via-agent · trade-assistance §8.2 · 类型 A",
    specRefs: ["flows/trade-via-agent.md", "domains/agent/exchange-agent/trade-assistance.md §8.2"],
    closureStatus: "FROZEN",
    promptBindingHint: "交易侧 TRADING · 须满足类型 A 与 FR-AO01～04",
  },
  {
    scenarioId: "trade.spot.limit_order",
    category: "write",
    scenarioTitle: "现货限价交易",
    flowSummary: "风险检查 → 确认 → 下单",
    riskLevel: "medium",
    typicalGoal: "现货限价主路径",
    flowAnchor: "trade-via-agent · FR-AO01 步骤序",
    specRefs: ["flows/trade-via-agent.md", "domains/agent/agent-orchestration/confirmation-flow.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "须先 read_skill_operation_spec",
  },
  {
    scenarioId: "trade.futures.market_order",
    category: "write",
    scenarioTitle: "合约市价单",
    flowSummary: "风险检查 → 二次确认 → 下单",
    riskLevel: "high",
    typicalGoal: "合约市价写",
    flowAnchor: "trade-via-agent · 矩阵已载能力",
    specRefs: ["flows/trade-via-agent.md", "design/api.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "skill.futures.* · scenarioId 寄存器一致",
  },
  {
    scenarioId: "trade.futures.limit_order",
    category: "write",
    scenarioTitle: "合约限价单",
    flowSummary: "风险检查 → 确认 → 下单",
    riskLevel: "medium",
    typicalGoal: "合约限价写",
    flowAnchor: "同上",
    specRefs: ["flows/trade-via-agent.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "—",
  },
  {
    scenarioId: "margin.cross.market_order",
    category: "write",
    scenarioTitle: "全仓杠杆市价",
    flowSummary: "风险检查 → 强确认 → 下单",
    riskLevel: "high",
    typicalGoal: "全仓杠杆市价（示意键）",
    flowAnchor: "trade-via-agent 专节 · 全仓 · 矩阵",
    specRefs: ["flows/trade-via-agent.md", "design/api.md"],
    closureStatus: "TBD",
    promptBindingHint: "PATH 未全冻结前对外 TBD",
  },
  {
    scenarioId: "margin.cross.limit_order",
    category: "write",
    scenarioTitle: "全仓杠杆限价",
    flowSummary: "风险检查 → 确认 → 下单",
    riskLevel: "high",
    typicalGoal: "全仓杠杆限价",
    flowAnchor: "同上",
    specRefs: ["flows/trade-via-agent.md"],
    closureStatus: "TBD",
    promptBindingHint: "—",
  },
  {
    scenarioId: "margin.cross.transfer_in",
    category: "write",
    scenarioTitle: "全仓资金划转",
    flowSummary: "校验 → 确认 → 划转",
    riskLevel: "medium",
    typicalGoal: "全仓划转（示意）",
    flowAnchor: "矩阵 + boundaries TRANSFER_REQUIRES_WEB",
    specRefs: ["flows/trade-via-agent.md", "domains/agent/exchange-agent/boundaries.md"],
    closureStatus: "PLACEHOLDER",
    promptBindingHint: "族名占位 · 须 MR 会签后再承诺",
  },
  {
    scenarioId: "wealth.holdings_read",
    category: "wealth",
    scenarioTitle: "理财持仓查询",
    flowSummary: "读持仓 → 返回",
    riskLevel: "low",
    typicalGoal: "理财只读持仓/到期",
    flowAnchor: "wealth-via-agent",
    specRefs: ["flows/wealth-via-agent.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "FEATURE_AGENT_WEALTH 闸",
  },
  {
    scenarioId: "wealth.recommend",
    category: "wealth",
    scenarioTitle: "理财推荐",
    flowSummary: "读产品 → 排序展示",
    riskLevel: "low",
    typicalGoal: "推荐/排序（只读或导向写）",
    flowAnchor: "wealth-via-agent",
    specRefs: ["flows/wealth-via-agent.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "—",
  },
  {
    scenarioId: "wealth.subscribe",
    category: "wealth",
    scenarioTitle: "理财申购",
    flowSummary: "校验 → 确认 → 申购",
    riskLevel: "medium",
    typicalGoal: "理财申购",
    flowAnchor: "wealth-via-agent · 类型 A · FR-AO04",
    specRefs: ["flows/wealth-via-agent.md", "domains/agent/agent-orchestration/confirmation-flow.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "合约下单与现货一致的确认序下限（含类型 A）",
  },
  {
    scenarioId: "wealth.redeem",
    category: "wealth",
    scenarioTitle: "理财赎回",
    flowSummary: "校验 → 确认 → 赎回",
    riskLevel: "medium",
    typicalGoal: "理财赎回",
    flowAnchor: "同上",
    specRefs: ["flows/wealth-via-agent.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "—",
  },
  {
    scenarioId: "monitoring.price_condition",
    category: "monitoring",
    scenarioTitle: "到价/指标提醒",
    flowSummary: "条件满足 → 通知用户",
    riskLevel: "medium",
    typicalGoal: "到价/指标类条件",
    flowAnchor: "automation-alerts · task-scheduler",
    specRefs: ["flows/automation-alerts.md", "domains/agent/agent-orchestration/task-scheduler.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "taskId 状态机 state-machine.md",
  },
  {
    scenarioId: "monitoring.scheduled_pull",
    category: "monitoring",
    scenarioTitle: "定时复盘",
    flowSummary: "定时拉取 → 汇总通知",
    riskLevel: "low",
    typicalGoal: "定时 / Pull 复盘",
    flowAnchor: "automation-alerts",
    specRefs: ["flows/automation-alerts.md", "domains/agent/agent-orchestration/task-scheduler.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "须具备矩阵/PATH 依据（contract-closure §1）",
  },
  {
    scenarioId: "monitoring.event_trigger",
    category: "monitoring",
    scenarioTitle: "事件触发通知",
    flowSummary: "事件检测 → 通知",
    riskLevel: "medium",
    typicalGoal: "事件类触发",
    flowAnchor: "automation-alerts · v0.1 稳定键",
    specRefs: ["flows/automation-alerts.md", "domains/agent/agent-orchestration/task-scheduler.md"],
    closureStatus: "FROZEN",
    promptBindingHint: "与 Pull 调度边界对签",
  },
];
