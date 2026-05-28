import { useEffect, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
import {
  App,
  Button,
  Card,
  Divider,
  Form,
  Input,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import { ArrowLeftOutlined, LinkOutlined, ThunderboltOutlined } from "@ant-design/icons";
import { ProductPageShell } from "../../components/product";
import {
  MOCK_AGENT_CHANNELS,
  channelStatusTagColor,
  type AgentChannelListRow,
} from "../../data/agentChannelsMock";

const { Text, Paragraph } = Typography;

type WebhookHealth = "ok" | "degraded" | "unknown";

function TelegramChannelDetail() {
  const { message } = App.useApp();
  const [botForm] = Form.useForm();
  const [webhookForm] = Form.useForm();
  const [uxForm] = Form.useForm();
  const [webhookHealth, setWebhookHealth] = useState<WebhookHealth>("ok");
  const [voiceOk, setVoiceOk] = useState(false);
  const [fileOk, setFileOk] = useState(true);
  const [tradeOk, setTradeOk] = useState(true);
  const [autoExec, setAutoExec] = useState(false);

  const webhookStatusTag =
    webhookHealth === "ok" ? (
      <Tag color="success">回调可达 · 最近探测成功（演示）</Tag>
    ) : webhookHealth === "degraded" ? (
      <Tag color="warning">待确认 · 上次探测失败或未登记（演示）</Tag>
    ) : (
      <Tag>未探测</Tag>
    );

  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <Link to="/system/channels">
        <Button type="link" icon={<ArrowLeftOutlined />} style={{ paddingLeft: 0 }}>
          返回渠道列表
        </Button>
      </Link>

      <Card size="small" className="admin-panel-card" title="1. Bot 基础配置">
        <Paragraph type="secondary" style={{ marginTop: 0, fontSize: 12 }}>
          当前为 <Text strong>单一交易 Agent Runtime</Text>：全渠道共用同一编排与 Agent，渠道层仅负责 Telegram Bot 接入与渠道能力闸，不做 Agent / Prompt 路由。
        </Paragraph>
        <Form
          form={botForm}
          layout="vertical"
          initialValues={{
            botToken: "",
            botUsername: "coobit_agent_demo",
          }}
          onFinish={() => message.success("Bot 基础配置已保存（演示）")}
        >
          <Form.Item
            name="botToken"
            label="Bot Token"
            rules={[{ required: true, message: "请填写由 BotFather 签发的 Token" }]}
            extra="生产环境应由密钥托管回灌；此处为演示表单。"
          >
            <Input.Password placeholder="123456789:AAF…" autoComplete="off" />
          </Form.Item>
          <Form.Item
            name="botUsername"
            label="Bot Username"
            rules={[
              { required: true, message: "请填写 @handle（不含 @ 可自动补全）" },
            ]}
            normalize={(v: string) => (v?.startsWith("@") ? v.slice(1) : v)}
          >
            <Input addonBefore="@" placeholder="your_bot" />
          </Form.Item>
          <Button type="primary" htmlType="submit">
            保存 Bot 配置
          </Button>
        </Form>
      </Card>

      <Card size="small" className="admin-panel-card" title="2. Webhook">
        <Space direction="vertical" style={{ width: "100%" }} size={12}>
          <div>
            <Text type="secondary" style={{ fontSize: 12 }}>
              回调状态
            </Text>
            <div style={{ marginTop: 4 }}>{webhookStatusTag}</div>
          </div>
          <Form
            form={webhookForm}
            layout="vertical"
            initialValues={{
              webhookUrl: "https://api.example.com/v1/telegram/webhook/main",
              webhookSecret: "",
            }}
            onFinish={() => message.success("Webhook 参数已保存（演示）")}
          >
            <Form.Item
              name="webhookUrl"
              label="Webhook URL"
              rules={[{ required: true, message: "请填写 HTTPS 回调地址" }]}
            >
              <Input prefix={<LinkOutlined />} placeholder="https://…" />
            </Form.Item>
            <Form.Item
              name="webhookSecret"
              label="Webhook Secret"
              extra="用于校验 Telegram 请求头；与 Runtime 网关约定一致。"
            >
              <Input.Password placeholder="可选 · 旋转后需重新登记 Webhook" autoComplete="off" />
            </Form.Item>
            <Space wrap>
              <Button type="primary" htmlType="submit">
                保存 Webhook 参数
              </Button>
              <Button
                icon={<ThunderboltOutlined />}
                onClick={() => {
                  setWebhookHealth("ok");
                  message.success("测试连接成功（演示）");
                }}
              >
                测试连接
              </Button>
            </Space>
          </Form>
        </Space>
      </Card>

      <Card size="small" className="admin-panel-card" title="3. 渠道能力">
        <Space direction="vertical" style={{ width: "100%" }}>
          <Space align="center" wrap>
            <Text>允许交易</Text>
            <Switch checked={tradeOk} onChange={setTradeOk} />
          </Space>
          <Space align="center" wrap>
            <Text>自动执行</Text>
            <Switch checked={autoExec} onChange={setAutoExec} />
            <Text type="secondary" style={{ fontSize: 12 }}>
              与人工确认规则、运行场景协同
            </Text>
          </Space>
          <Space align="center" wrap>
            <Text>语音输入</Text>
            <Switch checked={voiceOk} onChange={setVoiceOk} />
          </Space>
          <Space align="center" wrap>
            <Text>文件上传</Text>
            <Switch checked={fileOk} onChange={setFileOk} />
          </Space>
          <Divider style={{ margin: "8px 0" }} />
          <Button
            type="primary"
            onClick={() => message.success("渠道能力已保存（演示）")}
          >
            保存能力开关
          </Button>
        </Space>
      </Card>

      <Card size="small" className="admin-panel-card" title="4. 用户体验">
        <Form
          form={uxForm}
          layout="vertical"
          initialValues={{
            defaultLocale: "zh-CN",
            commandMenuSummary: "已同步 BotFather：/start /help /portfolio（演示）",
            deepLinkTemplate: "https://h5.example.com/app/help?locale={locale}",
          }}
          onFinish={() => message.success("用户体验配置已保存（演示）")}
        >
          <Form.Item name="defaultLocale" label="默认语言">
            <Select
              options={[
                { value: "zh-CN", label: "中文（简体）" },
                { value: "en-US", label: "English (US)" },
              ]}
            />
          </Form.Item>
          <Form.Item name="commandMenuSummary" label="菜单">
            <Input.TextArea rows={2} placeholder="与 BotFather 菜单对齐的摘要或说明" />
          </Form.Item>
          <Form.Item
            name="deepLinkTemplate"
            label="DeepLink"
            extra="占位符如 {locale}；勿在链接中携带长期明文 Token。"
          >
            <Input placeholder="https://…" />
          </Form.Item>
          <Button type="primary" htmlType="submit">
            保存体验配置
          </Button>
        </Form>
      </Card>

      <Paragraph type="secondary" style={{ fontSize: 12, marginBottom: 0 }}>
        执行异常协查见 <Link to="/observability">执行链路协查</Link>。
      </Paragraph>
    </Space>
  );
}

function PlaceholderChannelDetail({ name }: { name: string }) {
  const { message } = App.useApp();
  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <Link to="/system/channels">
        <Button type="link" icon={<ArrowLeftOutlined />} style={{ paddingLeft: 0 }}>
          返回渠道列表
        </Button>
      </Link>
      <Card size="small" className="admin-panel-card">
        <Text>{name} 接入向导尚未在 Demo 中开放。</Text>
        <div style={{ marginTop: 12 }}>
          <Button type="primary" onClick={() => message.info("接入流程待产品冻结后接入")}>
            接入（演示）
          </Button>
        </div>
      </Card>
    </Space>
  );
}

export function ChannelConfigPage() {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const { channelId } = useParams<{ channelId?: string }>();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const legacy = searchParams.get("channel");
    if (legacy === "telegram") {
      navigate("/system/channels/telegram", { replace: true });
    }
  }, [searchParams, navigate]);

  const listColumns: ColumnsType<AgentChannelListRow> = [
    { title: "渠道", dataIndex: "name", width: 140, render: (n: string) => <Text strong>{n}</Text> },
    { title: "类型", dataIndex: "kindLabel", width: 120 },
    {
      title: "状态",
      dataIndex: "status",
      width: 120,
      render: (_: unknown, row) => (
        <Tag color={channelStatusTagColor(row.status)}>{row.statusLabel}</Tag>
      ),
    },
    { title: "用户规模（演示）", dataIndex: "userScaleLabel", width: 140 },
    {
      title: "操作",
      key: "op",
      width: 100,
      render: (_, row) => (
        <Button
          type="link"
          size="small"
          style={{ padding: 0 }}
          onClick={() => {
            if (row.action === "onboard") {
              message.info(`${row.name} 接入流程待开放（演示）`);
              return;
            }
            navigate(`/system/channels/${row.id}`);
          }}
        >
          {row.actionLabel}
        </Button>
      ),
    },
  ];

  if (channelId === "telegram") {
    return (
      <ProductPageShell
        pageId="sys.channels"
        showPageId={false}
        title="Telegram · Bot 接入控制台"
        description="单一 Runtime Agent 下的 Telegram 接入：Bot、Webhook、渠道能力闸与体验配置（不与 Prompt 治理叠床架屋）。"
        tags={<Tag color="blue">Bot 接入</Tag>}
      >
        <TelegramChannelDetail />
      </ProductPageShell>
    );
  }

  if (channelId === "discord") {
    return (
      <ProductPageShell
        pageId="sys.channels"
        showPageId={false}
        title="Discord · 渠道详情"
        description="多渠道接入中心预留位。"
        tags={<Tag>未接入</Tag>}
      >
        <PlaceholderChannelDetail name="Discord" />
      </ProductPageShell>
    );
  }

  if (channelId === "whatsapp") {
    return (
      <ProductPageShell
        pageId="sys.channels"
        showPageId={false}
        title="WhatsApp · 渠道详情"
        description="多渠道接入中心预留位。"
        tags={<Tag>未接入</Tag>}
      >
        <PlaceholderChannelDetail name="WhatsApp" />
      </ProductPageShell>
    );
  }

  if (channelId) {
    return <NavigateMissingChannel />;
  }

  return (
    <ProductPageShell
      pageId="sys.channels"
      showPageId={false}
      title="渠道管理"
      description="用户从哪些入口与 Agent 交互（Interaction Layer）。列表为运营视图；具体 Runtime 执行见运行场景与执行链路。"
      tags={<Tag>Agent Interaction Channel</Tag>}
    >
      <Card size="small" className="admin-panel-card" title="渠道列表">
        <Table
          rowKey="id"
          size="middle"
          columns={listColumns}
          dataSource={MOCK_AGENT_CHANNELS}
          pagination={false}
        />
      </Card>
      <Paragraph type="secondary" style={{ fontSize: 12, marginTop: 16, marginBottom: 0 }}>
        <Link to="/observability">执行链路协查</Link>
      </Paragraph>
    </ProductPageShell>
  );
}

function NavigateMissingChannel() {
  return (
    <ProductPageShell pageId="sys.channels" showPageId={false} title="渠道管理">
      <Text type="secondary">未找到该渠道。</Text>
      <div style={{ marginTop: 12 }}>
        <Link to="/system/channels">返回列表</Link>
      </div>
    </ProductPageShell>
  );
}
