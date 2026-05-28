/**
 * 执行 ID 形态 · 同窗 `standards/naming-standard.md` §1 · `identity-schemas.yaml` `ExecutionId`
 */
export const EXECUTION_ID_MIN_LEN = 10;
export const EXECUTION_ID_MAX_LEN = 19;

export const EXECUTION_ID_PATTERN = /^[0-9]{10,19}$/;

export function isExecutionId(value: string): boolean {
  const t = value.trim();
  return t.length >= EXECUTION_ID_MIN_LEN && t.length <= EXECUTION_ID_MAX_LEN && EXECUTION_ID_PATTERN.test(t);
}

/** 列表合并检索：纯数字 → `executionId` 精确筛选 */
export function executionIdFromCorrelationQuery(raw: string): string | undefined {
  const q = raw.trim();
  return isExecutionId(q) ? q : undefined;
}
