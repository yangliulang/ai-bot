import { ArrowRightOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { Button, Card, Typography } from "antd";
import { useNavigate } from "react-router-dom";

const { Paragraph } = Typography;

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="coolbit-home-layout">
      <header className="coolbit-home-hero coolbit-home-hero--centered">
        <span className="coolbit-home-badge">体验版</span>
        <div className="coolbit-home-hero-icon" aria-hidden>
          <ThunderboltOutlined />
        </div>
        <h1 className="coolbit-page-title coolbit-home-title">Coolbit Agent</h1>
        <Paragraph className="coolbit-home-lead">
          通过 Telegram 与 AI 助手对话，完成<strong>交易所侧账户范围内</strong>的交易与查询；消耗按<strong>订阅档位与 Capability 配额</strong>核销，可在账单页查看流水。
        </Paragraph>
      </header>

      <Card bordered={false} className="coolbit-home-card coolbit-home-card__cta">
        <p className="coolbit-home-steps-hint">
          <span className="coolbit-home-steps-hint__emph">本页粘贴 API</span>
          <span className="coolbit-home-steps-hint__sep">→</span>
          <span>保存校验</span>
          <span className="coolbit-home-steps-hint__sep">→</span>
          <span>回 Telegram 使用</span>
        </p>
        <Button
          type="primary"
          size="large"
          block
          icon={<ArrowRightOutlined />}
          iconPosition="end"
          className="coolbit-home-primary-btn"
          onClick={() => navigate("/onboarding")}
        >
          开启助手
        </Button>
      </Card>
    </div>
  );
}
