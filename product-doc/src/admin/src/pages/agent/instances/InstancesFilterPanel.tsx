import { Divider, Flex, Form, Input, Select, Space, Tag, Tooltip, Typography, theme } from "antd";
import { FilterOutlined, SearchOutlined } from "@ant-design/icons";
import {
  ADMIN_FILTER_CONTROL_SIZE,
  ADMIN_PAGE_FILTER_FORM_PROPS,
  AdminFilterSurface,
  PageSecondaryButton,
} from "../../../components/product";
import { AGENT_INSTANCES } from "../../../copy/opsPanelHints";
import { zhAgentState, zhRuntimeState } from "../../../copy/zhLabels";

const { Text } = Typography;

export type InstancesFilterPanelProps = {
  /** 当前筛选结果数量 */
  resultCount: number;
  totalCount: number;
  keywordInput: string;
  gateDraft: string;
  rtDraft: string;
  onKeywordChange: (v: string) => void;
  onGateDraftChange: (v: string) => void;
  onRtDraftChange: (v: string) => void;
  onResetFilters: () => void;
  onExportListDemo?: () => void;
  /** 用户 UID（模糊） */
  userIdDraft: string;
  onUserIdDraftChange: (v: string) => void;
  /** `YYYY-MM-DD`，空串表示不限制 */
  lastActiveFromDay: string;
  lastActiveToDay: string;
  onLastActiveFromChange: (v: string) => void;
  onLastActiveToChange: (v: string) => void;
};

export function InstancesFilterPanel({
  resultCount,
  totalCount,
  keywordInput,
  gateDraft,
  rtDraft,
  onKeywordChange,
  onGateDraftChange,
  onRtDraftChange,
  onResetFilters,
  onExportListDemo,
  userIdDraft,
  onUserIdDraftChange,
  lastActiveFromDay,
  lastActiveToDay,
  onLastActiveFromChange,
  onLastActiveToChange,
}: InstancesFilterPanelProps) {
  const { token } = theme.useToken();

  return (
    <AdminFilterSurface className="admin-instances-query-surface" style={{ padding: "12px 16px", marginBottom: 12 }}>
      <Flex vertical gap={0}>
        <Flex
          wrap="wrap"
          gap="middle"
          align="center"
          justify="space-between"
          style={{ marginBottom: 12 }}
        >
          <Space size={10} wrap align="center">
            <Space size={8} align="center">
              <FilterOutlined style={{ color: token.colorTextSecondary, fontSize: 15 }} aria-hidden />
              <Text strong style={{ fontSize: 15, color: token.colorText }}>
                查询条件
              </Text>
            </Space>
            <Tag color="processing" style={{ margin: 0 }}>
              命中 {resultCount} / {totalCount}
            </Tag>
          </Space>
          <Space wrap size={10}>
            {onExportListDemo ? (
              <PageSecondaryButton onClick={onExportListDemo}>{AGENT_INSTANCES.exportList}</PageSecondaryButton>
            ) : null}
            <Tooltip title="清空条件并移除地址栏参数">
              <PageSecondaryButton onClick={onResetFilters}>重置</PageSecondaryButton>
            </Tooltip>
          </Space>
        </Flex>

        <Divider style={{ margin: "0 0 12px" }} />

        <Form
          {...ADMIN_PAGE_FILTER_FORM_PROPS}
          className="admin-instances-filter-form admin-instances-filter-form--compact"
          style={{ marginBottom: 0 }}
        >
          <div className="admin-filter-query-grid admin-instances-query-gridFields admin-instances-filter-grid-tight">
            <div className="admin-filter-span-4">
              <Form.Item label="关键字" style={{ marginBottom: 0, width: "100%" }}>
                <Input
                  allowClear
                  size={ADMIN_FILTER_CONTROL_SIZE}
                  placeholder="实例 ID、用户 UID 或子账户 UID（模糊匹配）"
                  prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
                  value={keywordInput}
                  onChange={(e) => onKeywordChange(e.target.value)}
                />
              </Form.Item>
              <Text type="secondary" style={{ fontSize: 11, display: "block", marginTop: 4 }}>
                实例 ID、用户 UID、子账户 UID；输入即筛选列表。
              </Text>
            </div>
            <div className="admin-filter-span-4">
              <Form.Item label="运行状态" style={{ marginBottom: 0, width: "100%" }}>
                <Select
                  value={gateDraft}
                  onChange={onGateDraftChange}
                  size={ADMIN_FILTER_CONTROL_SIZE}
                  style={{ width: "100%" }}
                  popupMatchSelectWidth={false}
                  options={[
                    { value: "all", label: "全部" },
                    { value: "NORMAL", label: zhAgentState("NORMAL") },
                    { value: "BILLING_BLOCKED", label: zhAgentState("BILLING_BLOCKED") },
                    { value: "GLOBAL_OFF", label: zhAgentState("GLOBAL_OFF") },
                    { value: "OPS_SUSPENDED", label: zhAgentState("OPS_SUSPENDED") },
                    { value: "MEMBERSHIP_BLOCKED", label: zhAgentState("MEMBERSHIP_BLOCKED") },
                    { value: "AGENT_SUBACCOUNT_BLOCKED", label: zhAgentState("AGENT_SUBACCOUNT_BLOCKED") },
                  ]}
                />
              </Form.Item>
            </div>
            <div className="admin-filter-span-4">
              <Form.Item label="实例状态" style={{ marginBottom: 0, width: "100%" }}>
                <Select
                  value={rtDraft}
                  onChange={onRtDraftChange}
                  size={ADMIN_FILTER_CONTROL_SIZE}
                  style={{ width: "100%" }}
                  popupMatchSelectWidth={false}
                  options={[
                    { value: "all", label: "全部" },
                    { value: "RUNNING", label: zhRuntimeState("RUNNING") },
                    { value: "PAUSED", label: zhRuntimeState("PAUSED") },
                    { value: "STOPPED", label: zhRuntimeState("STOPPED") },
                    { value: "STARTING", label: zhRuntimeState("STARTING") },
                    { value: "ERROR", label: zhRuntimeState("ERROR") },
                  ]}
                />
              </Form.Item>
            </div>
          </div>

          <div
            className="admin-filter-query-grid admin-instances-query-gridFields admin-instances-filter-grid-tight"
            style={{ marginTop: 12 }}
          >
            <div className="admin-filter-span-4">
              <Form.Item label="用户 UID" style={{ marginBottom: 0, width: "100%" }}>
                <Input
                  allowClear
                  size={ADMIN_FILTER_CONTROL_SIZE}
                  placeholder="用户 UID 片段"
                  value={userIdDraft}
                  onChange={(e) => onUserIdDraftChange(e.target.value)}
                />
              </Form.Item>
            </div>
            <div className="admin-filter-span-8">
              <Form.Item label="最近活跃（UTC 日期）" style={{ marginBottom: 0, width: "100%" }}>
                <Space.Compact style={{ width: "100%" }}>
                  <Input
                    type="date"
                    size={ADMIN_FILTER_CONTROL_SIZE}
                    style={{ width: "50%" }}
                    value={lastActiveFromDay}
                    onChange={(e) => onLastActiveFromChange(e.target.value)}
                  />
                  <Input
                    type="date"
                    size={ADMIN_FILTER_CONTROL_SIZE}
                    style={{ width: "50%" }}
                    value={lastActiveToDay}
                    onChange={(e) => onLastActiveToChange(e.target.value)}
                  />
                </Space.Compact>
              </Form.Item>
            </div>
          </div>
        </Form>

        <Text type="secondary" style={{ fontSize: 12, marginTop: 10, marginBottom: 0, display: "block", lineHeight: 1.5 }}>
          {AGENT_INSTANCES.filterInstantHint}
        </Text>
      </Flex>
    </AdminFilterSurface>
  );
}
