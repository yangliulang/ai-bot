import { Checkbox, Input, Modal, Space, Typography } from "antd";
import { useEffect, useState } from "react";
import { BILLING_DUAL_SIGN } from "../../copy/opsPanelHints";

const { Text } = Typography;

type Props = {
  open: boolean;
  title?: string;
  body?: string;
  ifMatchLabel?: string;
  confirmLoading?: boolean;
  onCancel: () => void;
  onConfirm: (ids: { operatorId: string; approverId: string }) => void | Promise<void>;
};

/** FR-MC502 / FR-MC509 同窗双签确认（演示 · 无真实 IAM） */
export function BillingDualSignModal({
  open,
  title = BILLING_DUAL_SIGN.title,
  body = BILLING_DUAL_SIGN.body,
  ifMatchLabel,
  confirmLoading,
  onCancel,
  onConfirm,
}: Props) {
  const [operatorAck, setOperatorAck] = useState(false);
  const [approverAck, setApproverAck] = useState(false);
  const [operatorId, setOperatorId] = useState("");
  const [approverId, setApproverId] = useState("");

  useEffect(() => {
    if (open) {
      setOperatorAck(false);
      setApproverAck(false);
      setOperatorId("");
      setApproverId("");
    }
  }, [open]);

  const handleOk = () => {
    if (!operatorAck || !approverAck) return;
    void onConfirm({ operatorId: operatorId.trim(), approverId: approverId.trim() });
  };

  const canSubmit =
    operatorAck &&
    approverAck &&
    operatorId.trim().length > 0 &&
    approverId.trim().length > 0 &&
    operatorId.trim() !== approverId.trim();

  return (
    <Modal
      title={title}
      open={open}
      onCancel={onCancel}
      onOk={handleOk}
      okButtonProps={{ disabled: !canSubmit }}
      confirmLoading={confirmLoading}
      okText={BILLING_DUAL_SIGN.confirm}
    >
      <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 12 }}>
        {body}
      </Text>
      <Space direction="vertical" style={{ width: "100%" }}>
        <Input
          placeholder={BILLING_DUAL_SIGN.operatorPlaceholder}
          value={operatorId}
          onChange={(e) => setOperatorId(e.target.value)}
        />
        <Checkbox checked={operatorAck} onChange={(e) => setOperatorAck(e.target.checked)}>
          {BILLING_DUAL_SIGN.operatorAck}
        </Checkbox>
        <Input
          placeholder={BILLING_DUAL_SIGN.approverPlaceholder}
          value={approverId}
          onChange={(e) => setApproverId(e.target.value)}
        />
        <Checkbox checked={approverAck} onChange={(e) => setApproverAck(e.target.checked)}>
          {BILLING_DUAL_SIGN.approverAck}
        </Checkbox>
        {ifMatchLabel ? (
          <Text type="secondary" style={{ fontSize: 11 }}>
            If-Match: <Text code>{ifMatchLabel}</Text>
          </Text>
        ) : null}
      </Space>
    </Modal>
  );
}

export function validateBillingDualSignIds(operatorId: string, approverId: string): string | null {
  if (!operatorId || !approverId) return BILLING_DUAL_SIGN.idsRequired;
  if (operatorId === approverId) return BILLING_DUAL_SIGN.distinct;
  return null;
}
