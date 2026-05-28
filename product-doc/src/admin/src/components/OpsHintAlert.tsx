import type { ReactNode } from "react";
import { Alert, type AlertProps, Typography } from "antd";

const { Text } = Typography;

export type OpsHintAlertProps = Omit<AlertProps, "description"> & {
  description?: ReactNode;
  /** 契约字段 / 事件名等；默认以次要字号展示在描述下方 */
  technicalDetail?: ReactNode;
};

/**
 * 运营向信息提示：主文案可读，技术对照可选展示。
 */
export function OpsHintAlert({
  description,
  technicalDetail,
  ...rest
}: OpsHintAlertProps) {
  const hasBody = description != null || technicalDetail != null;

  return (
    <Alert
      {...rest}
      description={
        hasBody ? (
          <>
            {description}
            {technicalDetail != null ? (
              <Text type="secondary" style={{ fontSize: 11, display: "block", marginTop: description ? 6 : 0 }}>
                技术对照：{technicalDetail}
              </Text>
            ) : null}
          </>
        ) : undefined
      }
    />
  );
}
