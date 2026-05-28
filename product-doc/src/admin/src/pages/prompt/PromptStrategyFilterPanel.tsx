import { Form, Input, Select, theme } from "antd";
import { SearchOutlined } from "@ant-design/icons";
import {
  ADMIN_FILTER_CONTROL_SIZE,
  ADMIN_PAGE_FILTER_FORM_PROPS,
  AdminFilterSurface,
} from "../../components/product";
import type { GovernanceKindFilter } from "./governanceKind";
import type { PromptLifecycleListFilter } from "./promptLifecycle";
import { zhPromptPackKind } from "../../copy/zhLabels";
import { PROMPT_GOVERNANCE_LIST_KINDS } from "./promptPackKinds";

const KIND_OPTIONS: { value: GovernanceKindFilter; label: string }[] = [
  { value: "all", label: "全部类型" },
  ...PROMPT_GOVERNANCE_LIST_KINDS.map((k) => ({
    value: k,
    label: zhPromptPackKind(k),
  })),
];

const LIFE_OPTIONS: { value: PromptLifecycleListFilter; label: string }[] = [
  { value: "all", label: "全部阶段" },
  { value: "draft", label: "草稿线（DRAFT）" },
  { value: "published", label: "已发布（PUBLISHED）" },
  { value: "locked", label: "已锁定（LOCKED）" },
  { value: "iterate", label: "生效包·有未发草稿" },
  { value: "deprecated", label: "下线标记" },
];

export type PromptStrategyFilterPanelProps = {
  promptKeyword: string;
  governanceKind: GovernanceKindFilter;
  lifecycleFilter: PromptLifecycleListFilter;
  onPromptKeywordChange: (v: string) => void;
  onGovernanceKindChange: (v: GovernanceKindFilter) => void;
  onLifecycleFilterChange: (v: PromptLifecycleListFilter) => void;
};

export function PromptStrategyFilterPanel({
  promptKeyword,
  governanceKind,
  lifecycleFilter,
  onPromptKeywordChange,
  onGovernanceKindChange,
  onLifecycleFilterChange,
}: PromptStrategyFilterPanelProps) {
  const { token } = theme.useToken();

  return (
    <AdminFilterSurface
      className="admin-prompt-strategy-query-surface"
      style={{ padding: "10px 14px", marginBottom: 10 }}
      title="查询条件"
    >
      <Form {...ADMIN_PAGE_FILTER_FORM_PROPS} style={{ marginBottom: 0 }}>
        <div className="admin-filter-query-grid admin-prompt-strategy-filter-grid">
          <div className="admin-filter-span-6">
            <Form.Item label="Prompt ID / 名称" style={{ marginBottom: 0 }}>
              <Input
                allowClear
                size={ADMIN_FILTER_CONTROL_SIZE}
                placeholder="任一匹配 Prompt ID 或名称（模糊）"
                prefix={<SearchOutlined style={{ color: token.colorTextQuaternary }} />}
                value={promptKeyword}
                onChange={(e) => onPromptKeywordChange(e.target.value)}
              />
            </Form.Item>
          </div>
          <div className="admin-filter-span-6">
            <Form.Item label="类型" style={{ marginBottom: 0 }} tooltip="拼装槽位大类：系统 / 交易 / 分析 / 安全防护。">
              <Select<GovernanceKindFilter>
                size={ADMIN_FILTER_CONTROL_SIZE}
                style={{ width: "100%" }}
                value={governanceKind}
                onChange={onGovernanceKindChange}
                options={KIND_OPTIONS}
                popupMatchSelectWidth={false}
              />
            </Form.Item>
          </div>
        </div>
        <div className="admin-filter-query-grid admin-prompt-strategy-filter-grid" style={{ marginTop: 8 }}>
          <div className="admin-filter-span-6">
            <Form.Item label="生命周期阶段" style={{ marginBottom: 0 }}>
              <Select<PromptLifecycleListFilter>
                size={ADMIN_FILTER_CONTROL_SIZE}
                style={{ width: "100%" }}
                value={lifecycleFilter}
                onChange={onLifecycleFilterChange}
                options={LIFE_OPTIONS}
                popupMatchSelectWidth={false}
              />
            </Form.Item>
          </div>
        </div>
      </Form>
    </AdminFilterSurface>
  );
}
