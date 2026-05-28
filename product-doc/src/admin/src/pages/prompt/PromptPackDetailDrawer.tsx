import { Button, Drawer, Typography } from "antd";
import { Link } from "react-router-dom";
import { EditOutlined } from "@ant-design/icons";
import { promptPackEditorPath } from "./promptPaths";
import type { MockPromptPack } from "../../data/types";
import { PromptPackDetailPanel } from "./PromptPackDetailPanel";
import { PromptPackIdText } from "./promptIdDisplay";

export function PromptPackDetailDrawer({
  open,
  pack,
  onClose,
}: {
  open: boolean;
  pack: MockPromptPack | null;
  onClose: () => void;
}) {
  if (!pack) return null;

  const editorTo = promptPackEditorPath(pack.promptPackId);

  return (
    <Drawer
      title={
        <div style={{ paddingRight: 8 }}>
          <Typography.Text strong style={{ fontSize: 15, display: "block" }}>
            {pack.title}
          </Typography.Text>
          <div style={{ marginTop: 4 }}>
            <PromptPackIdText promptPackId={pack.promptPackId} type="secondary" />
          </div>
        </div>
      }
      placement="right"
      width={480}
      open={open}
      onClose={onClose}
      destroyOnClose
      maskClosable
      keyboard
      extra={
        <Link to={editorTo} onClick={onClose}>
          <Button type="primary" size="small" icon={<EditOutlined />}>
            编辑
          </Button>
        </Link>
      }
      styles={{ body: { paddingBottom: 16 } }}
      footer={<Button onClick={onClose}>关闭</Button>}
    >
      <PromptPackDetailPanel pack={pack} />
    </Drawer>
  );
}
