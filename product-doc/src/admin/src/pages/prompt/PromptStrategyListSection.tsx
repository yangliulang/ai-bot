import { Empty, Space } from "antd";
import { AdminTablePanel, PagePrimaryButton, PageSecondaryButton } from "../../components/product";
import type { MockPromptPack } from "../../data/types";
import { PromptPacksTable } from "./PromptPacksTable";

export type PromptStrategyListSectionProps = {
  loadingList: boolean;
  nonSafetyRowsTotal: number;
  /** 筛选关键词变化时用于重置表格分页 */
  querySig: string;
  queryFilteredRows: MockPromptPack[];
  onResetQuery: () => void;
  onNewDraft: () => void;
  onOpenPack: (p: MockPromptPack) => void;
  /** 展示生命周期阶段列 */
  showLifecycleColumn?: boolean;
};

export function PromptStrategyListSection({
  loadingList,
  nonSafetyRowsTotal,
  querySig,
  queryFilteredRows,
  onResetQuery,
  onNewDraft,
  onOpenPack,
  showLifecycleColumn = false,
}: PromptStrategyListSectionProps) {

  if (loadingList) {
    return null;
  }

  return (
    <>
      <AdminTablePanel>
        {queryFilteredRows.length === 0 ? (
          <div style={{ padding: "48px 24px" }}>
            {nonSafetyRowsTotal === 0 ? (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="暂无业务侧 Prompt（不含安全防护 / SAFETY）">
                <PagePrimaryButton onClick={onNewDraft}>新建草稿</PagePrimaryButton>
              </Empty>
            ) : (
              <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="没有符合当前关键词的条目">
                <Space>
                  <PagePrimaryButton onClick={onResetQuery}>清空筛选</PagePrimaryButton>
                  <PageSecondaryButton onClick={onNewDraft}>新建草稿</PageSecondaryButton>
                </Space>
              </Empty>
            )}
          </div>
        ) : (
          <PromptPacksTable
            data={queryFilteredRows}
            onView={onOpenPack}
            bordered
            listPagination
            paginationResetKey={querySig}
            showLifecycleColumn={showLifecycleColumn}
          />
        )}
      </AdminTablePanel>
    </>
  );
}
