import { Card, Typography } from "antd";
import type { MockPromptPack } from "../../data/types";
import { buildDemoPromptAssemblyTrace, PROMPT_EDITOR } from "./promptManagementUiCopy";
import { PromptAssemblyTraceTable } from "./PromptAssemblyTraceTable";

const { Text } = Typography;

export function PromptAssemblyTraceCard({ pack }: { pack: MockPromptPack }) {
  const rows = buildDemoPromptAssemblyTrace(pack);

  return (
    <Card size="small" className="admin-panel-card" title={PROMPT_EDITOR.assemblyTraceTitle}>
      <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 8 }}>
        {PROMPT_EDITOR.assemblyTraceHint}
      </Text>
      <PromptAssemblyTraceTable rows={rows} />
    </Card>
  );
}
