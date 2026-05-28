/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-16
 * 修改功能: listId 与后端 **`WhitelistCreateRequest`** 对齐（1–64 · 字母数字 `._-`，支持 **`rollout`** 等 slug）
 * 作者: 杨永的Agent
 * 日期: 2026-05-12
 * 修改功能: 准入白名单 listId 校验（与 product-doc / 原型对齐）
 */
export const WHITELIST_LIST_ID_MAX_LEN = 64

/** 与 OpenAPI / 服务端一致：首字符须为字母或数字 */
export const WHITELIST_LIST_ID_PATTERN = /^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$/

export const WHITELIST_LIST_ID_RULE_HINT =
  '名单 ID（listId）须为 1～64 字符，仅字母、数字、`.`、`_`、`-`；可与 rollout 等策略键一致，或为数字主键（例：20260507000001）。'

export function isValidWhitelistListId(raw: string): boolean {
  const s = raw.trim()
  return s.length >= 1 && s.length <= WHITELIST_LIST_ID_MAX_LEN && WHITELIST_LIST_ID_PATTERN.test(s)
}
