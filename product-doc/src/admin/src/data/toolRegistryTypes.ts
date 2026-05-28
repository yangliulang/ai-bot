export type RegistryEntryClass = "A" | "B" | "C";

export interface ToolRegistryRow {
  /** skillId 或 toolId */
  stableId: string;
  entryClass: RegistryEntryClass;
  /** 表意简述（§4） */
  summary: string;
  /** B/C：能力锚点；A 类与 exchangeAction 同窗 */
  anchor: string;
  /** A 类：用户流程（产品实现文案） */
  userFlow?: string;
  /** A 类：交易所写操作说明 */
  exchangeAction?: string;
  /** 仅 A 类：skillSpecVersion（Git 规范元数据表或登记 fallback） */
  skillSpecVersion?: string;
  matrixStatus: "frozen" | "tbd" | "draft";
  defaultEnabled: boolean;
}
