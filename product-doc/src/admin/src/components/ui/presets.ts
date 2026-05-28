import type { FormProps } from "antd/es/form";
import type { GlobalToken } from "antd/es/theme/interface";
import type { TableProps } from "antd/es/table";
import type { CSSProperties } from "react";

/** 筛选条、页头操作区控件高度档位（对齐 exchangeAdminTheme controlHeight） */
export const ADMIN_FILTER_CONTROL_SIZE = "middle" as const;

/** 列表页「过滤器」表单：纵向标签 + 无必填红星 */
export const ADMIN_PAGE_FILTER_FORM_PROPS = {
  layout: "vertical" as const,
  requiredMark: false as const,
} satisfies Pick<FormProps, "layout" | "requiredMark">;

export const ADMIN_LIST_PAGE_SIZE = 10;

/** 列表页分页：单列可扫读总数，单列页弱化分页器噪声 */
export function adminListPagination(
  extra?: false | Partial<Exclude<TableProps["pagination"], false | undefined>>,
): TableProps["pagination"] {
  if (extra === false) return false;
  return {
    pageSize: ADMIN_LIST_PAGE_SIZE,
    showSizeChanger: true,
    pageSizeOptions: [10, 15, 20, 50],
    hideOnSinglePage: false,
    showTotal: (total, range) => `${range[0]}-${range[1]} / 共 ${total} 条`,
    ...extra,
  };
}

/** 高密度内嵌表格（抽屉、编辑器内）默认值，可按页面覆盖 pagination */
export const ADMIN_EMBEDDED_TABLE_PROPS = {
  size: "small" as const,
};

/** 主列表表格（整页）：与主题 Table token 对齐 */
export const ADMIN_PRIMARY_TABLE_PROPS = {
  size: "middle" as const,
};

/** 预览块 / Drawer 摘要条：与筛选条同系视觉层级 */
export function adminPeekPanelShellStyle(token: GlobalToken): CSSProperties {
  return {
    marginBottom: 16,
    padding: "12px 14px",
    borderRadius: token.borderRadiusLG,
    background: token.colorFillAlter,
    border: `1px solid ${token.colorBorderSecondary}`,
  };
}
