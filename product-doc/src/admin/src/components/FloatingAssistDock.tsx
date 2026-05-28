import { useState } from "react";
import { BulbOutlined, CloseOutlined, MessageOutlined } from "@ant-design/icons";
import { Button, Card, FloatButton } from "antd";

/** 视觉对齐现有后台右下角「灯泡 + 客服」占位（无真实 IM） */
export function FloatingAssistDock() {
  const [chatOpen, setChatOpen] = useState(false);

  return (
    <>
      <FloatButton
        icon={<BulbOutlined />}
        type="primary"
        style={{ right: 24, bottom: 96 }}
        tooltip="提示 / 演示"
      />

      {chatOpen ? (
        <Card
          size="small"
          title={
            <span>
              <MessageOutlined style={{ marginRight: 8 }} />
              客服会话（演示）
            </span>
          }
          extra={
            <Button type="text" size="small" icon={<CloseOutlined />} onClick={() => setChatOpen(false)} aria-label="关闭" />
          }
          style={{
            position: "fixed",
            right: 24,
            bottom: 24,
            width: 280,
            zIndex: 1000,
            boxShadow: "0 4px 16px rgba(0,0,0,0.12)",
          }}
        >
          演示占位客服窗口，与交易所后台组件形态一致。
        </Card>
      ) : (
        <Button
          type="primary"
          shape="round"
          icon={<MessageOutlined />}
          onClick={() => setChatOpen(true)}
          style={{
            position: "fixed",
            right: 24,
            bottom: 24,
            zIndex: 999,
            boxShadow: "0 2px 8px rgba(24,144,255,0.35)",
          }}
        >
          客服会话（演示）
        </Button>
      )}
    </>
  );
}
