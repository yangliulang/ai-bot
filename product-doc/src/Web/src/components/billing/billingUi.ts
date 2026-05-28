/** 配额卡片视觉分类（仅 UI） */
export function quotaBucketAccent(sku: string): "analyze" | "trade" | "pack" | "default" {
  if (sku.includes("analyze")) return "analyze";
  if (sku.includes("trade")) return "trade";
  if (sku.includes("pack")) return "pack";
  return "default";
}
