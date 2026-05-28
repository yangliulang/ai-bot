import { Typography } from "antd";
import { PROMPT_GOVERNANCE_INTRO } from "./promptManagementUiCopy";

const { Paragraph } = Typography;

/** 列表页顶说明（非 Alert 卡片，避免占用首屏） */
export function PromptGovernanceIntro({ compact = false }: { compact?: boolean }) {
  return (
    <Paragraph
      type="secondary"
      style={{ marginBottom: compact ? 8 : 12, fontSize: 13, lineHeight: 1.55 }}
    >
      {PROMPT_GOVERNANCE_INTRO.description}
    </Paragraph>
  );
}
