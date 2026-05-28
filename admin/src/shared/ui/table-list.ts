/** 宽表无数据、仅 loading 骨架时不横向滚动 */
export function adminTableHostOverflowClass(allowHorizontalScroll: boolean): string {
  return allowHorizontalScroll ? 'overflow-x-auto' : 'overflow-x-hidden'
}
