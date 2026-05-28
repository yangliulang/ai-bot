import { Typography } from "antd";
import { ANALYSIS_CAPABILITY_REGISTRY } from "../../data/mockPromptData";
import { PROMPT_EDITOR } from "./promptManagementUiCopy";

const { Text } = Typography;

const DOMAIN_LABEL: Record<string, string> = {
  market: "行情",
  research: "研究/舆情",
  portfolio: "账户/订单",
  wealth: "理财（只读）",
  monitoring: "监控条件",
};

export function PromptUnifiedAnalysisMeta() {
  const byDomain = new Map<string, string[]>();
  for (const row of ANALYSIS_CAPABILITY_REGISTRY) {
    const label = DOMAIN_LABEL[row.domain] ?? row.domain;
    const list = byDomain.get(label) ?? [];
    list.push(row.title);
    byDomain.set(label, list);
  }

  return (
    <div style={{ marginBottom: 12 }}>
      <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 8 }}>
        {PROMPT_EDITOR.unifiedAnalysisBanner}
      </Text>
      <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 6 }}>
        {PROMPT_EDITOR.labelAnalysisCapabilities}
      </Text>
      <ul style={{ margin: "0 0 8px", paddingLeft: 18, fontSize: 12, color: "rgba(0,0,0,0.65)" }}>
        {[...byDomain.entries()].map(([domain, titles]) => (
          <li key={domain}>
            <Text strong style={{ fontSize: 12 }}>
              {domain}
            </Text>
            ：{titles.join("、")}
          </li>
        ))}
      </ul>
      <Text type="secondary" style={{ fontSize: 11 }}>
        {PROMPT_EDITOR.analysisCapabilitiesHint}
      </Text>
    </div>
  );
}
