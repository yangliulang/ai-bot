import { Card, Tag, Typography } from "antd";
import type { ReactNode } from "react";
import { PageWorkflowTip, ProductPageShell } from "./product";
import { SpecFooter } from "./SpecFooter";

const { Paragraph, Text } = Typography;

export function ConsolePlaceholderPage({
  title,
  pageId,
  description,
  tags,
  children,
  specPaths,
  workflowSteps,
  /** 面向运营：弱化规格路径、演示路由说明与研发术语 */
  opsMode = false,
}: {
  title: string;
  pageId: string;
  description?: ReactNode;
  tags?: ReactNode;
  children?: React.ReactNode;
  specPaths: string[];
  workflowSteps?: string[];
  opsMode?: boolean;
}) {
  const defaultDesc = opsMode ? (
    <Paragraph style={{ marginBottom: 0 }}>用于日常运营查看与配置，具体能力以实际上线为准。</Paragraph>
  ) : (
    <Paragraph style={{ marginBottom: 0 }}>
      当前为<strong>低保真占位</strong>，用于评审流程与布局；正式上线后将接入表单、审批流与实时数据。
    </Paragraph>
  );

  const defaultTags = opsMode ? (
    <Tag color="blue">运营配置</Tag>
  ) : (
    <>
      <Tag color="processing">建设中</Tag>
      <Tag>后续接真实接口</Tag>
    </>
  );

  return (
    <ProductPageShell
      pageId={pageId}
      showPageId={!opsMode}
      title={title}
      description={description ?? defaultDesc}
      tags={tags ?? defaultTags}
    >
      {workflowSteps?.length ? <PageWorkflowTip steps={workflowSteps} /> : null}
      {children}
      {!opsMode ? (
        <Card size="small" className="admin-panel-card" style={{ marginTop: 16 }}>
          <Text type="secondary" style={{ fontSize: 13 }}>
            路由与页面标识对照（研发）：<Text code>规格要求/admin-console/demo-routing.md</Text>
          </Text>
        </Card>
      ) : null}
      {!opsMode && specPaths.length > 0 ? <SpecFooter paths={specPaths} /> : null}
      {opsMode ? (
        <Paragraph type="secondary" style={{ marginTop: 24, marginBottom: 0, fontSize: 12 }}>
          完整规则与审批流程以公司内部文档为准；需研发支持请通过工单或产研渠道反馈。
        </Paragraph>
      ) : null}
    </ProductPageShell>
  );
}
