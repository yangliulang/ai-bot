/**
 * 执行 ID 形态 · 同窗 `standards/naming-standard.md` §1 · `identity-schemas.yaml` `ExecutionId`
 */
export const EXECUTION_ID_MIN_LEN = 10;
export const EXECUTION_ID_MAX_LEN = 19;

/** 仅 ASCII 数字；不含字母、连字符、空格 */
export const EXECUTION_ID_PATTERN = /^[0-9]{10,19}$/;

export function isExecutionId(value: string): boolean {
  const t = value.trim();
  return t.length >= EXECUTION_ID_MIN_LEN && t.length <= EXECUTION_ID_MAX_LEN && EXECUTION_ID_PATTERN.test(t);
}
