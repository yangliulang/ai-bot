import { Table } from "antd";
import type { TableProps } from "antd/es/table";
import { ADMIN_PRIMARY_TABLE_PROPS } from "./presets";
import { useAdminTablePagination } from "./useAdminTablePagination";

type AdminPrimaryListTableProps<R extends object> = Omit<TableProps<R>, "size" | "pagination"> &
  Partial<Pick<TableProps<R>, "size" | "pagination">> & {
    /** 默认 true；与分析页等小表可自行关闭 */
    bordered?: boolean;
    /** 筛选变化时重置分页（与 URL / 关键词同步） */
    paginationResetKey?: string;
  };

/**
 * 整页主列表表格：分页文案、默认 middle 档位与 antd Table 全局 token 对齐。
 */
export function AdminPrimaryListTable<R extends object>({
  bordered = true,
  size = ADMIN_PRIMARY_TABLE_PROPS.size,
  pagination,
  paginationResetKey,
  dataSource,
  ...rest
}: AdminPrimaryListTableProps<R>) {
  const rows = (Array.isArray(dataSource) ? dataSource : []) as R[];
  const disabled = pagination === false;
  const extraPagination =
    pagination === false || pagination === undefined
      ? undefined
      : (pagination as Exclude<typeof pagination, false | undefined>);

  const { pagination: clientPagination, slice } = useAdminTablePagination(rows.length, {
    resetKey: paginationResetKey,
    ...extraPagination,
  });

  const mergedPagination = disabled ? false : clientPagination;
  const displayRows = disabled ? rows : slice(rows);

  return (
    <Table<R>
      bordered={bordered}
      size={size}
      pagination={mergedPagination}
      dataSource={displayRows}
      {...rest}
    />
  );
}
