import { ReloadOutlined } from "@ant-design/icons";
import { App, Collapse, Tag } from "antd";
import { PageSecondaryButton, ProductPageShell } from "../../components/product";
import { SpecFooter } from "../../components/SpecFooter";
import { ConfirmationRulesPanel } from "./confirmation/ConfirmationRulesPanel";

export function ConfirmationRulesPage() {
  const { message } = App.useApp();

  return (
    <ProductPageShell
      pageId="ai.confirmation-rules"
      title="人工确认规则"
      description="风控规则中心：集中管理高风险交易与资金动作的确认门槛（何时须用户点头、何时加码二次确认）。可与风险限制、工具授权一起核对，兼顾安全与体验。"
      tags={<Tag color="purple">风控治理</Tag>}
      extra={
        <PageSecondaryButton icon={<ReloadOutlined />} onClick={() => message.success("已刷新规则目录（演示）")}>
          刷新
        </PageSecondaryButton>
      }
    >
      <ConfirmationRulesPanel />

      <Collapse
        bordered={false}
        style={{ marginTop: 24 }}
        items={[
          {
            key: "spec-refs",
            label: "制度与规格索引（内部参考，默认折叠）",
            children: (
              <SpecFooter
                compact
                paths={[
                  "risk/hitl-and-automation-matrix.md",
                  "risk/user-confirmation.md",
                  "domains/agent/agent-orchestration/confirmation-flow.md",
                  "prompts/confirmation/high-risk-confirmation.md",
                ]}
              />
            ),
          },
        ]}
      />
    </ProductPageShell>
  );
}
