import { Descriptions, Space, Tag, Typography, theme } from "antd";
import type { MockPromptPack } from "../../data/types";
import { zhPromptPackKind, zhPromptPackLockState } from "../../copy/zhLabels";
import { getPromptPackVersionHistory } from "../../data/mock";
import { PROMPT_DETAIL } from "./promptManagementUiCopy";

const { Text } = Typography;

function formatAt(iso?: string): string {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 16);
}

function showEffectiveBadge(p: MockPromptPack): boolean {
  return p.currentVersion != null && (p.lockState === "LOCKED" || p.lockState === "PUBLISHED");
}

export function PromptPackDetailPanel({ pack }: { pack: MockPromptPack }) {
  const { token } = theme.useToken();
  const versions = getPromptPackVersionHistory(pack.promptPackId).slice(0, 5);
  const effective = showEffectiveBadge(pack);

  return (
    <>
      <Space wrap size={8} style={{ marginBottom: 12 }}>
        {effective ? <Tag color="success">生效 · v{pack.currentVersion}</Tag> : null}
        {pack.hasDraft ? <Tag color="processing">有草稿</Tag> : null}
        <Tag>{zhPromptPackLockState(pack.lockState)}</Tag>
        <Tag>{zhPromptPackKind(pack.kind)}</Tag>
      </Space>

      <Descriptions column={1} size="small" labelStyle={{ width: 100, color: token.colorTextSecondary }}>
        <Descriptions.Item label="说明">{pack.description ?? "—"}</Descriptions.Item>
        <Descriptions.Item label={PROMPT_DETAIL.labelScenarioId}>
          {pack.scenarioId ?? "—"}
        </Descriptions.Item>
        <Descriptions.Item label={PROMPT_DETAIL.labelSkillScope}>
          {pack.skillSpecRef?.trim() ? (
            <Typography.Text code copyable={{ text: pack.skillSpecRef }}>
              {pack.skillSpecRef}
            </Typography.Text>
          ) : (
            PROMPT_DETAIL.skillScopeEmpty
          )}
        </Descriptions.Item>
        <Descriptions.Item label="当前版本">{pack.currentVersion != null ? `v${pack.currentVersion}` : "—"}</Descriptions.Item>
        <Descriptions.Item label="发布时间">{formatAt(pack.publishedAt)}</Descriptions.Item>
        <Descriptions.Item label="更新时间">{formatAt(pack.updatedAt)}</Descriptions.Item>
      </Descriptions>

      {versions.length > 0 ? (
        <div style={{ marginTop: 16 }}>
          <Text strong style={{ fontSize: 13, display: "block", marginBottom: 8 }}>
            最近版本记录
          </Text>
          <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13, color: token.colorTextSecondary }}>
            {versions.map((v) => (
              <li key={`${v.promptPackVersion}-${v.publishedAt}`}>
                v{v.promptPackVersion} · {v.event === "PUBLISH" ? "发布" : "回滚"} · {formatAt(v.publishedAt)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <Text strong style={{ fontSize: 13, display: "block", margin: "14px 0 8px" }}>
        正文预览
      </Text>
      <Typography.Paragraph
        type="secondary"
        style={{
          fontSize: 13,
          marginBottom: 0,
          padding: "10px 12px",
          background: token.colorFillTertiary,
          borderRadius: token.borderRadius,
          border: `1px solid ${token.colorBorderSecondary}`,
          whiteSpace: "pre-wrap",
          maxHeight: 180,
          overflow: "auto",
        }}
      >
        {pack.effectiveBodyPreview ?? "（暂无预览）"}
      </Typography.Paragraph>
    </>
  );
}
