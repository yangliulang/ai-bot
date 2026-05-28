import { Alert, Form, Input, Select, Space, Tag, Tooltip, Typography, theme } from "antd";
import { FilterOutlined, SearchOutlined } from "@ant-design/icons";
import {
  ADMIN_FILTER_CONTROL_SIZE,
  ADMIN_PAGE_FILTER_FORM_PROPS,
  AdminFilterSurface,
  PageSecondaryButton,
} from "../../components/product";
import type { ExecutionStatusFilter } from "./executionListTypes";

const { Text } = Typography;

export function ExecutionListFilters({
  qCorrelation,
  qIntent,
  statusFilter,
  dateFrom,
  dateTo,
  statusOptions,
  /** 全量数据集条数（与命中数对照） */
  totalCount,
  resultCount,
  dateRangeInvalid,
  onQCorrelation,
  onQIntent,
  onStatusFilter,
  onDateFrom,
  onDateTo,
  onReset,
}: {
  /** 合并检索：执行 ID、用户 UID、场景 ID（OR 匹配） */
  qCorrelation: string;
  qIntent: string;
  statusFilter: ExecutionStatusFilter;
  dateFrom: string;
  dateTo: string;
  statusOptions: { value: ExecutionStatusFilter; label: string }[];
  /** 全量条数；省略时（如 API 仅返回一页）只展示本页命中 */
  totalCount?: number;
  resultCount: number;
  /** 结束日早于起始日时为 true（上游会忽略日期筛） */
  dateRangeInvalid: boolean;
  onQCorrelation: (v: string) => void;
  onQIntent: (v: string) => void;
  onStatusFilter: (v: ExecutionStatusFilter) => void;
  onDateFrom: (v: string) => void;
  onDateTo: (v: string) => void;
  onReset: () => void;
}) {
  const { token } = theme.useToken();

  return (
    <AdminFilterSurface
      className="admin-runtime-execution-query-surface"
      style={{ padding: "12px 16px", marginBottom: 12 }}
      title={
        <Space align="center" size={8} wrap>
          <FilterOutlined style={{ color: token.colorTextSecondary, fontSize: 15 }} aria-hidden />
          <Text strong style={{ fontSize: 15, color: token.colorText }}>
            筛选条件
          </Text>
        </Space>
      }
      extra={
        <Space wrap size={8} align="center">
          <Tag color="processing" style={{ margin: 0 }}>
            {totalCount !== undefined ? `命中 ${resultCount} / ${totalCount}` : `本页 ${resultCount} 条`}
          </Tag>
          <Tooltip title="清空条件并同步地址栏">
            <PageSecondaryButton onClick={onReset}>重置</PageSecondaryButton>
          </Tooltip>
        </Space>
      }
    >
      <Form {...ADMIN_PAGE_FILTER_FORM_PROPS} layout="vertical" requiredMark={false} style={{ marginBottom: 0 }}>
        {dateRangeInvalid ? (
          <Alert
            type="warning"
            showIcon
            message="日期范围无效：已忽略日期筛选"
            style={{ marginBottom: 12 }}
          />
        ) : null}
        <div className="admin-filter-query-grid admin-runtime-execution-filter-grid">
          <div className="admin-filter-span-6">
            <Form.Item
              label="执行 / 用户 UID / 场景"
              style={{ marginBottom: 0 }}
              className="admin-runtime-execution-correlation-item"
            >
              <Input
                allowClear
                size={ADMIN_FILTER_CONTROL_SIZE}
                placeholder="执行 ID、用户 UID 或场景 ID · 任一串即匹配"
                prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
                value={qCorrelation}
                onChange={(e) => onQCorrelation(e.target.value)}
              />
            </Form.Item>
          </div>
          <div className="admin-filter-span-3">
            <Form.Item label="意图" style={{ marginBottom: 0 }}>
              <Input
                allowClear
                size={ADMIN_FILTER_CONTROL_SIZE}
                placeholder="关键词"
                prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
                value={qIntent}
                onChange={(e) => onQIntent(e.target.value)}
              />
            </Form.Item>
          </div>

          <div className="admin-filter-span-3">
            <Form.Item label="运行状态" style={{ marginBottom: 0 }}>
              <Select<ExecutionStatusFilter>
                size={ADMIN_FILTER_CONTROL_SIZE}
                style={{ width: "100%" }}
                value={statusFilter}
                onChange={onStatusFilter}
                options={statusOptions}
                popupMatchSelectWidth={false}
              />
            </Form.Item>
          </div>

          <div className="admin-filter-span-6">
            <Form.Item label="创建起始日" style={{ marginBottom: 0 }}>
              <Input type="date" size={ADMIN_FILTER_CONTROL_SIZE} value={dateFrom} onChange={(e) => onDateFrom(e.target.value)} />
            </Form.Item>
          </div>

          <div className="admin-filter-span-6">
            <Form.Item label="创建结束日" style={{ marginBottom: 0 }}>
              <Input type="date" size={ADMIN_FILTER_CONTROL_SIZE} value={dateTo} onChange={(e) => onDateTo(e.target.value)} />
            </Form.Item>
          </div>
        </div>
      </Form>
    </AdminFilterSurface>
  );
}
