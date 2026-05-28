/** 客户端表格分页 · 当前页数据切片（与 useAdminTablePagination 共用） */
export function sliceTablePage<T>(rows: readonly T[], current: number, pageSize: number): T[] {
  const start = (current - 1) * pageSize;
  return rows.slice(start, start + pageSize);
}
