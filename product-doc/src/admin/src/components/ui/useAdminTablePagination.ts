import { useCallback, useEffect, useMemo, useState } from "react";
import type { TablePaginationConfig } from "antd/es/table/interface";
import { ADMIN_LIST_PAGE_SIZE, adminListPagination } from "./presets";
import { sliceTablePage } from "./tablePageSlice";

export type UseAdminTablePaginationOptions = {
  /** 筛选条件变化时重置到第 1 页 */
  resetKey?: string;
  pageSize?: number;
} & Partial<Omit<TablePaginationConfig, "current" | "pageSize" | "total" | "onChange">>;

/**
 * 主列表客户端分页：显式 slice dataSource，避免 Table 内部分页未生效时一次渲染全部行。
 */
export function useAdminTablePagination(total: number, options?: UseAdminTablePaginationOptions) {
  const { resetKey, pageSize: initialPageSize, ...paginationExtra } = options ?? {};
  const [current, setCurrent] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize ?? ADMIN_LIST_PAGE_SIZE);

  useEffect(() => {
    setCurrent(1);
  }, [resetKey]);

  useEffect(() => {
    const maxPage = Math.max(1, Math.ceil(total / pageSize) || 1);
    if (current > maxPage) setCurrent(maxPage);
  }, [total, pageSize, current]);

  const onChange = useCallback((page: number, size?: number) => {
    setCurrent(page);
    if (size != null && size !== pageSize) {
      setPageSize(size);
      setCurrent(1);
    }
  }, [pageSize]);

  const pagination = useMemo(
    () =>
      adminListPagination({
        current,
        pageSize,
        total,
        onChange,
        ...paginationExtra,
      }),
    // paginationExtra 由调用方传入稳定字段（pageSizeOptions / showTotal 等）
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [current, pageSize, total, onChange, resetKey],
  );

  const slice = useCallback(
    <T,>(rows: readonly T[]): T[] => sliceTablePage(rows, current, pageSize),
    [current, pageSize],
  );

  return { pagination, slice, current, pageSize };
}
