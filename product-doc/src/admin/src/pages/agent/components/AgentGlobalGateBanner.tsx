import { useState } from "react";
import { Link } from "react-router-dom";
import { Alert, Button, Space } from "antd";
import { AGENT_GLOBAL_GATE } from "../../../copy/opsPanelHints";
import { isDemoGlobalAgentSwitchOn } from "../../../utils/demoGlobalAgentSwitch";
import { dismissG01BannerForUtcToday, isG01BannerDismissedForUtcToday } from "../../../utils/g01BannerUtcDismiss";

/** 全局开关关闭时，实例列表 / 详情页顶提示。 */
export function AgentGlobalGateBanner() {
  const [hidden, setHidden] = useState(() => isG01BannerDismissedForUtcToday());

  if (hidden || isDemoGlobalAgentSwitchOn()) return null;

  return (
    <Alert
      type="warning"
      showIcon
      banner
      style={{ marginBottom: 16 }}
      message={
        <Space wrap size="middle" align="center">
          <span>{AGENT_GLOBAL_GATE.message}</span>
          <Link to="/access">{AGENT_GLOBAL_GATE.configLink}</Link>
          <Button
            type="link"
            size="small"
            style={{ padding: 0, height: "auto" }}
            onClick={() => {
              dismissG01BannerForUtcToday();
              setHidden(true);
            }}
          >
            {AGENT_GLOBAL_GATE.dismissToday}
          </Button>
        </Space>
      }
      description={AGENT_GLOBAL_GATE.description}
    />
  );
}
