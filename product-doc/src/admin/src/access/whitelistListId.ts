/**
 * 准入白名单 · 名单ID（listId）展示与校验规则（Demo 管理台）
 * 与 OpenAPI 字段名 listId 对应；采用纯数字主键式 ID，避免 wl-、beta 等字母缩写直接作为主展示键。
 */

/** 12～16 位十进制，首位非 0（总长度与数值型清单主键字符串对齐） */
export const WHITELIST_LIST_ID_PATTERN = /^[1-9]\d{11,15}$/;

/** 人类可读说明（用于表单、提示文案等） */
export const WHITELIST_LIST_ID_RULE_HINT =
  "名单ID须为 12～16 位纯数字，首位不可为 0，不含字母与符号；建议：yyyymmdd + 当日流水（例：20260507000001）。";

export function isValidWhitelistListId(raw: string): boolean {
  return WHITELIST_LIST_ID_PATTERN.test(raw.trim());
}
