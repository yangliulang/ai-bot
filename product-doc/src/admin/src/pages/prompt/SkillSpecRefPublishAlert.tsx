import { useEffect, useState } from "react";
import { Alert, Spin, Typography } from "antd";
import type { MockPromptPack } from "../../data/types";
import { formatSkillSpecRef, parseSkillSpecRef } from "../../skillPublish/parseSkillSpecRef";
import { validateSkillSpecRefForPublish } from "../../skillPublish/validateSkillSpecRefForPublish";
import { PROMPT_PUBLISH_GATE } from "./promptManagementUiCopy";

const { Text } = Typography;

type Props = {
  pack: MockPromptPack;
  scenarioId: string;
};

export function SkillSpecRefPublishAlert({ pack, scenarioId }: Props) {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [ok, setOk] = useState<boolean | null>(null);

  useEffect(() => {
    if (pack.kind !== "TRADING") {
      setOk(null);
      setMessage(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    void validateSkillSpecRefForPublish({
      promptPackKind: pack.kind,
      skillSpecRef: pack.skillSpecRef,
      scenarioId,
    }).then((r) => {
      if (cancelled) return;
      setOk(r.ok);
      if (r.ok && r.resolved) {
        setMessage(
          `${PROMPT_PUBLISH_GATE.okResolved}：${formatSkillSpecRef(r.resolved)}${
            r.resolved.source === "legacy" ? PROMPT_PUBLISH_GATE.legacyHint : ""
          }`,
        );
      } else {
        setMessage(r.reason ?? "校验未通过");
      }
      setLoading(false);
    });
    return () => {
      cancelled = true;
    };
  }, [pack.kind, pack.skillSpecRef, scenarioId]);

  if (pack.kind !== "TRADING") return null;

  const parsed = parseSkillSpecRef(pack.skillSpecRef, scenarioId);
  const alertType = ok === true ? "success" : ok === false ? "error" : "info";
  const title =
    loading
      ? PROMPT_PUBLISH_GATE.checking
      : ok === true
        ? PROMPT_PUBLISH_GATE.titleOk
        : ok === false
          ? PROMPT_PUBLISH_GATE.titleFail
          : PROMPT_PUBLISH_GATE.titlePending;

  return (
    <Alert
      type={alertType}
      showIcon
      banner
      style={{ marginBottom: 12 }}
      message={
        <span>
          {title}
          {loading ? <Spin size="small" style={{ marginLeft: 8 }} /> : null}
        </span>
      }
      description={
        <div style={{ fontSize: 13 }}>
          <Text type="secondary" style={{ fontSize: 12, display: "block" }}>
            {PROMPT_PUBLISH_GATE.labelScenario}：{scenarioId || "—"} · {PROMPT_PUBLISH_GATE.labelSkillRef}：
            {pack.skillSpecRef?.trim() || "—"}
          </Text>
          {parsed ? (
            <Text type="secondary" style={{ fontSize: 12, display: "block", marginTop: 4 }}>
              {PROMPT_PUBLISH_GATE.parsePrefix}：{formatSkillSpecRef(parsed)}
            </Text>
          ) : null}
          {message ? <div style={{ marginTop: 6 }}>{message}</div> : null}
        </div>
      }
    />
  );
}
