import type { MockPromptPack } from "../../data/types";
import { buildGateTrace, validatePublishDemoStructured } from "./promptPublishRejectTrace";

/** 预览：将常见占位符替换为演示值 */
export function renderPromptPreview(markdown: string): string {
  return markdown
    .replace(/\{\{\s*symbol\s*\}\}/gi, "BTCUSDT")
    .replace(/\{\{\s*quantity\s*\}\}/gi, "0.01")
    .replace(/\{\{\s*interval\s*\}\}/gi, "1h");
}

/** @deprecated 优先使用 validatePublishDemoStructured / runPromptPublishGate */
export function validatePublishDemo(
  pack: MockPromptPack,
  scenarioIdField: string,
  body: string,
): { ok: boolean; reasons: string[] } {
  const trace = buildGateTrace(validatePublishDemoStructured(pack, scenarioIdField, body));
  return { ok: trace.ok, reasons: trace.reasons };
}
