import { InfoCircleOutlined } from "@ant-design/icons";
import { Alert, Steps, theme } from "antd";

/** 弱工程化、强化「怎么做」的轻量流程提示 */
export function PageWorkflowTip({
  title = "建议操作流程",
  steps,
}: {
  title?: string;
  steps: string[];
}) {
  const { token } = theme.useToken();
  return (
    <Alert
      type="info"
      showIcon
      icon={<InfoCircleOutlined />}
      message={title}
      style={{ marginBottom: 20, borderRadius: token.borderRadiusLG }}
      description={
        <Steps
          direction="vertical"
          size="small"
          current={-1}
          items={steps.map((s) => ({ title: s }))}
          style={{ marginTop: 8 }}
        />
      }
    />
  );
}
