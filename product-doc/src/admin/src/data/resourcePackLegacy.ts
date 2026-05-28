/** 旧字符串 SKU → 数字资源 ID（session 迁移） */
export const LEGACY_RESOURCE_PACK_SKU_TO_ID: Record<string, string> = {
  pack_sub_analyze_starter: "2001",
  pack_sub_trade_starter: "2002",
  pack_sub_monitor_starter: "2003",
  pack_sub_analyze_pro: "2011",
  pack_sub_trade_pro: "2012",
  pack_sub_monitor_pro: "2013",
  pack_sub_analyze_enterprise: "2021",
  pack_sub_trade_enterprise: "2022",
  pack_sub_monitor_enterprise: "2023",
  pack_analyze_50: "3001",
  pack_trade_100: "3002",
  pack_monitor_30d: "3003",
};

export function normalizeResourceId(raw: string): string {
  return LEGACY_RESOURCE_PACK_SKU_TO_ID[raw] ?? raw;
}

export const NUMERIC_RESOURCE_ID = /^\d+$/;
