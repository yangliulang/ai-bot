import type { CSSProperties } from "react";
import { Typography } from "antd";

/** Prompt 业务 ID（非 code 胶囊样式，可复制） */
export function PromptPackIdText({
  promptPackId,
  type,
  style,
}: {
  promptPackId: string;
  type?: "secondary";
  style?: CSSProperties;
}) {
  return (
    <Typography.Text
      copyable={{ text: promptPackId }}
      type={type}
      style={{ wordBreak: "break-all", fontSize: 13, ...(style ?? {}) }}
    >
      {promptPackId}
    </Typography.Text>
  );
}
