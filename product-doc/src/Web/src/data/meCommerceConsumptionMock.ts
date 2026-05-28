/** 同窗 admin mockBillingLedger · FR-WEB08～09 / commerce-model §5.3 */

export type ConsumptionDebitStatus = "SUCCESS" | "INSUFFICIENT" | "FAILED" | "AWAITING_FINAL";

export type ConsumptionSceneType =
  | "现货"
  | "杠杆"
  | "合约"
  | "闪兑"
  | "问答"
  | "分析"
  | "行情查询";

export type MeCommerceConsumptionRow = {
  key: string;
  time: string;
  sceneType: ConsumptionSceneType;
  capabilitySkuId: string;
  debitStatus: ConsumptionDebitStatus;
  consumedUnits?: number;
  tokens?: number;
  /** 纯数字 · naming-standard §1 · OpenAPI ExecutionId */
  executionId: string;
  billingTraceId: string;
};

export type MeCommerceMonthlyMeteringRow = {
  key: string;
  month: string;
  entitlementDebits: number;
  analyzeDebits: number;
  tradeDebits: number;
  tokensObserved: number;
  notes: string;
};

export const MOCK_ME_COMMERCE_CONSUMPTIONS: MeCommerceConsumptionRow[] = buildMockConsumptions();

export const MOCK_ME_COMMERCE_MONTHLY: MeCommerceMonthlyMeteringRow[] = [
  {
    key: "m1",
    month: "2026-05",
    entitlementDebits: 218,
    analyzeDebits: 86,
    tradeDebits: 132,
    tokensObserved: 84220,
    notes: "进行中",
  },
  {
    key: "m2",
    month: "2026-04",
    entitlementDebits: 941,
    analyzeDebits: 312,
    tradeDebits: 629,
    tokensObserved: 312880,
    notes: "已结算",
  },
  {
    key: "m3",
    month: "2026-03",
    entitlementDebits: 883,
    analyzeDebits: 298,
    tradeDebits: 585,
    tokensObserved: 287650,
    notes: "已结算",
  },
];

function buildMockConsumptions(): MeCommerceConsumptionRow[] {
  const seed: MeCommerceConsumptionRow[] = [
    {
      key: "l1",
      time: "2026-05-11 14:32:08",
      sceneType: "合约",
      capabilitySkuId: "cap.agent.trade",
      debitStatus: "SUCCESS",
      consumedUnits: 1,
      tokens: 1856,
      executionId: "20260511143208001",
      billingTraceId: "bt-7f2a-001",
    },
    {
      key: "l2",
      time: "2026-05-11 14:31:44",
      sceneType: "现货",
      capabilitySkuId: "cap.agent.trade",
      debitStatus: "SUCCESS",
      consumedUnits: 1,
      tokens: 420,
      executionId: "20260511143144002",
      billingTraceId: "bt-7f2a-002",
    },
    {
      key: "l3",
      time: "2026-05-11 14:28:12",
      sceneType: "杠杆",
      capabilitySkuId: "cap.agent.trade",
      debitStatus: "INSUFFICIENT",
      tokens: 2390,
      executionId: "20260511142812003",
      billingTraceId: "bt-883-fail",
    },
    {
      key: "l4",
      time: "2026-05-10 21:06:33",
      sceneType: "问答",
      capabilitySkuId: "cap.agent.analyze",
      debitStatus: "SUCCESS",
      consumedUnits: 1,
      tokens: 890,
      executionId: "20260510210633004",
      billingTraceId: "bt-an-qa-01",
    },
    {
      key: "l5",
      time: "2026-05-10 20:40:11",
      sceneType: "分析",
      capabilitySkuId: "cap.agent.analyze",
      debitStatus: "SUCCESS",
      consumedUnits: 1,
      tokens: 1540,
      executionId: "20260510204011005",
      billingTraceId: "bt-an-02",
    },
    {
      key: "l6",
      time: "2026-05-10 18:02:00",
      sceneType: "行情查询",
      capabilitySkuId: "cap.agent.analyze",
      debitStatus: "AWAITING_FINAL",
      tokens: 310,
      executionId: "20260510180200006",
      billingTraceId: "bt-recon-pending-9",
    },
  ];
  const cycle: ConsumptionSceneType[] = ["合约", "现货", "杠杆", "闪兑", "问答", "分析", "行情查询"];
  const next = [...seed];
  for (let i = seed.length + 1; i <= 23; i++) {
    const day = ((i * 3) % 28) + 1;
    const hh = 8 + (i % 12);
    const mm = (i * 7) % 60;
    const ss = (i * 11) % 60;
    const seq = String(100 + i).padStart(3, "0");
    next.push({
      key: `l${i}`,
      time: `2026-05-${String(day).padStart(2, "0")} ${String(hh).padStart(2, "0")}:${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`,
      sceneType: cycle[(i - 1) % cycle.length],
      capabilitySkuId: i % 3 === 0 ? "cap.agent.analyze" : "cap.agent.trade",
      debitStatus: i % 7 === 0 ? "INSUFFICIENT" : "SUCCESS",
      consumedUnits: i % 7 === 0 ? undefined : 1,
      tokens: 180 + (i * 191) % 2400,
      executionId: `202605${String(day).padStart(2, "0")}${String(hh).padStart(2, "0")}${String(mm).padStart(2, "0")}${String(ss).padStart(2, "0")}${seq}`,
      billingTraceId: `bt-demo-${i}`,
    });
  }
  return next;
}
