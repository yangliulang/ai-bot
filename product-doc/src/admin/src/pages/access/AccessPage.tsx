import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  App,
  Button,
  Card,
  DatePicker,
  Form,
  Input,
  Modal,
  Popconfirm,
  Select,
  Space,
  Switch,
  Table,
  Tabs,
  Tag,
  Typography,
} from "antd";
import { PlusOutlined, ReloadOutlined } from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import type { Dayjs } from "dayjs";
import { ProductPageShell, AdminFilterSurface } from "../../components/product";
import { allConfigKeyRows, mockAccessWhitelist, mockUserBans, mockMembershipVipLevels } from "../../data/mock";
import type { MockUserBan, MockWhitelistEntry } from "../../data/types";
import { readDemoAgentMinVipTier, writeDemoAgentMinVipTier, clearDemoAgentMinVipTier, VIP_TIER_MAX } from "../../demo/accessDemoStorage";
import { isValidWhitelistListId } from "../../access/whitelistListId";
import {
  BAN_REASON_OPTIONS,
  BAN_SCOPE_AGENT_PRODUCT,
  BAN_SCOPE_AGENT_PRODUCT_ZH,
  banReasonZh,
} from "../../access/banLabels";

const { Text } = Typography;

type AccessTab = "whitelist" | "bans" | "vip";

const TAB_KEYS: AccessTab[] = ["whitelist", "bans", "vip"];

const VIP_CONFIG_KEY = "AGENT_MIN_VIP_TIER";

function parsePlatformDefaultTier(vipFallbackDemoValue: string): number {
  const raw = String(vipFallbackDemoValue).replace(/（.*）/, "").trim();
  const n = Number.parseInt(raw, 10);
  const v = Number.isFinite(n) ? n : 2;
  return Math.min(VIP_TIER_MAX, Math.max(0, v));
}

/** 将门槛值约束在 Mock 等级列表内（接口返回列表后仍用同一逻辑） */
function normalizeVipTierToMockOption(tierStr: string, platformDefaultTier: number): string {
  const allowed = new Set(mockMembershipVipLevels.map((l) => String(l.tier)));
  if (allowed.has(tierStr)) return tierStr;
  const fb = String(platformDefaultTier);
  if (allowed.has(fb)) return fb;
  return String(mockMembershipVipLevels[0]?.tier ?? 0);
}

function fmtIso(iso: string): string {
  try {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleString("zh-CN", { hour12: false });
  } catch {
    return iso;
  }
}

export function AccessPage() {
  const { message } = App.useApp();
  const [searchParams, setSearchParams] = useSearchParams();

  const tabFromUrl = searchParams.get("tab");
  const initialTab: AccessTab =
    tabFromUrl && TAB_KEYS.includes(tabFromUrl as AccessTab) ? (tabFromUrl as AccessTab) : "whitelist";
  const [tab, setTab] = useState<AccessTab>(initialTab);

  useEffect(() => {
    const t = searchParams.get("tab");
    if (t && TAB_KEYS.includes(t as AccessTab)) {
      setTab(t as AccessTab);
    }
  }, [searchParams]);

  const onTabChange = (k: string) => {
    const next = k as AccessTab;
    setTab(next);
    setSearchParams((prev) => {
      const p = new URLSearchParams(prev);
      p.set("tab", next);
      return p;
    });
  };

  const vipFallback =
    allConfigKeyRows.find((k) => k.configKey === VIP_CONFIG_KEY)?.demoValue ?? "2";

  const platformDefaultTier = useMemo(() => parsePlatformDefaultTier(vipFallback), [vipFallback]);

  const [vipTier, setVipTier] = useState(() => {
    const stored = readDemoAgentMinVipTier(vipFallback.replace(/（.*）/, "").trim());
    return normalizeVipTierToMockOption(stored, parsePlatformDefaultTier(vipFallback));
  });

  const [whitelist, setWhitelist] = useState<MockWhitelistEntry[]>(() => mockAccessWhitelist.map((w) => ({ ...w })));
  const [wlSearch, setWlSearch] = useState("");
  const [wlAddOpen, setWlAddOpen] = useState(false);
  const [wlForm] = Form.useForm<{ listId: string; userIdMasked: string; note?: string }>();

  const [bans, setBans] = useState<MockUserBan[]>(() => mockUserBans.map((b) => ({ ...b })));
  const [banSearch, setBanSearch] = useState("");
  const [banAddOpen, setBanAddOpen] = useState(false);
  const [banForm] = Form.useForm<{
    userUid: string;
    reasonCode: string;
    expiresAt?: Dayjs;
    linkedPause: boolean;
  }>();

  const filteredWhitelist = useMemo(() => {
    const q = wlSearch.trim().toLowerCase();
    if (!q) return whitelist;
    return whitelist.filter(
      (w) =>
        w.listId.toLowerCase().includes(q) ||
        w.userIdMasked.toLowerCase().includes(q) ||
        (w.note ?? "").toLowerCase().includes(q),
    );
  }, [whitelist, wlSearch]);

  const filteredBans = useMemo(() => {
    const q = banSearch.trim().toLowerCase();
    if (!q) return bans;
    return bans.filter((b) => {
      const reasonZh = banReasonZh(b.reasonCode);
      return (
        b.banId.toLowerCase().includes(q) ||
        b.userUid.toLowerCase().includes(q) ||
        b.reasonCode.toLowerCase().includes(q) ||
        reasonZh.toLowerCase().includes(q)
      );
    });
  }, [bans, banSearch]);

  const resetVipToDefault = () => {
    clearDemoAgentMinVipTier();
    const v = readDemoAgentMinVipTier(String(platformDefaultTier));
    setVipTier(normalizeVipTierToMockOption(v, platformDefaultTier));
    message.success("已恢复默认");
  };

  const persistVip = () => {
    writeDemoAgentMinVipTier(vipTier);
    const saved = readDemoAgentMinVipTier(String(platformDefaultTier));
    setVipTier(normalizeVipTierToMockOption(saved, platformDefaultTier));
    message.success(`已保存：VIP ${saved}`);
  };

  const reloadVipFromStorage = () => {
    const v = readDemoAgentMinVipTier(String(platformDefaultTier));
    setVipTier(normalizeVipTierToMockOption(v, platformDefaultTier));
    message.success("已刷新");
  };
  const handleWlAdd = async () => {
    const v = await wlForm.validateFields();
    const row: MockWhitelistEntry = {
      listId: v.listId.trim(),
      userIdMasked: v.userIdMasked.trim(),
      note: (v.note ?? "").trim() || "手工添加",
      addedAt: new Date().toISOString(),
      addedBy: "console.demo",
    };
    setWhitelist((prev) => [row, ...prev]);
    setWlAddOpen(false);
    wlForm.resetFields();
    message.success("已加入白名单");
  };

  const removeWhitelistRow = (row: MockWhitelistEntry) => {
    setWhitelist((prev) =>
      prev.filter((w) => !(w.listId === row.listId && w.userIdMasked === row.userIdMasked && w.addedAt === row.addedAt)),
    );
    message.success("已移除");
  };

  const handleBanCreate = async () => {
    const v = await banForm.validateFields();
    const banId = `ban-${Date.now()}`;
    const createdAt = new Date().toISOString();
    const expiresAt = v.expiresAt ? v.expiresAt.toISOString() : null;
    const row: MockUserBan = {
      banId,
      userUid: v.userUid.trim(),
      reasonCode: v.reasonCode,
      scope: BAN_SCOPE_AGENT_PRODUCT,
      expiresAt,
      createdAt,
      linkedPause: v.linkedPause,
      createdBy: "console.demo",
    };
    setBans((prev) => [row, ...prev]);
    setBanAddOpen(false);
    banForm.resetFields();
    message.success("已创建封禁");
  };

  const revokeBan = (banId: string) => {
    setBans((prev) => prev.filter((b) => b.banId !== banId));
    message.success("已撤销封禁");
  };

  const wlCols: ColumnsType<MockWhitelistEntry> = [
    { title: "名单ID", dataIndex: "listId", key: "l" },
    { title: "用户 UID", dataIndex: "userIdMasked", key: "u" },
    { title: "备注", dataIndex: "note", key: "n", ellipsis: true },
    { title: "加入时间", dataIndex: "addedAt", key: "a", render: (iso: string) => fmtIso(iso) },
    { title: "操作人", dataIndex: "addedBy", key: "b", render: (v?: string) => v ?? "—" },
    {
      title: "操作",
      key: "act",
      width: 96,
      render: (_, row) => (
        <Popconfirm title="确认从白名单移除该条？" onConfirm={() => removeWhitelistRow(row)}>
          <Button type="link" size="small" danger>
            移除
          </Button>
        </Popconfirm>
      ),
    },
  ];

  const banCols: ColumnsType<MockUserBan> = [
    { title: "ID", dataIndex: "banId", key: "id", ellipsis: true, render: (s: string) => <Text copyable={{ text: s }}>{s}</Text> },
    { title: "用户 UID", dataIndex: "userUid", key: "u", ellipsis: true, render: (s: string) => <Text copyable={{ text: s }}>{s}</Text> },
    { title: "原因", dataIndex: "reasonCode", key: "r", render: (code: string) => banReasonZh(code) },
    { title: "范围", dataIndex: "scope", key: "s", render: () => BAN_SCOPE_AGENT_PRODUCT_ZH },
    {
      title: "到期时间",
      dataIndex: "expiresAt",
      key: "e",
      render: (v: string | null) => (v ? fmtIso(v) : "永久 / 未设"),
    },
    { title: "暂停联动", dataIndex: "linkedPause", key: "p", render: (v: boolean) => (v ? "是" : "否") },
    { title: "创建时间", dataIndex: "createdAt", key: "c", render: (iso: string) => fmtIso(iso) },
    { title: "创建人", dataIndex: "createdBy", key: "cb", render: (v?: string) => v ?? "—" },
    {
      title: "操作",
      key: "act",
      width: 96,
      render: (_, row) => (
        <Popconfirm title="确认撤销该封禁？" onConfirm={() => revokeBan(row.banId)}>
          <Button type="link" size="small" danger>
            撤销
          </Button>
        </Popconfirm>
      ),
    },
  ];

  const tabsItems = [
    {
      key: "whitelist",
      label: "白名单",
      children: (
        <Card size="small" className="admin-panel-card" styles={{ body: { paddingTop: 16 } }}>
          <AdminFilterSurface
            title="查询条件"
            extra={
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setWlAddOpen(true)}>
                添加条目
              </Button>
            }
            style={{ marginBottom: 16 }}
          >
            <Input.Search
              allowClear
              size="middle"
              placeholder="搜索名单 ID、用户 UID 掩码、备注…"
              style={{ maxWidth: 480 }}
              value={wlSearch}
              onChange={(e) => setWlSearch(e.target.value)}
            />
          </AdminFilterSurface>
          <Table
            rowKey={(w) => `${w.listId}|${w.userIdMasked}|${w.addedAt}`}
            columns={wlCols}
            dataSource={filteredWhitelist}
            pagination={{ pageSize: 10 }}
            size="middle"
          />
        </Card>
      ),
    },
    {
      key: "bans",
      label: "用户封禁",
      children: (
        <Card size="small" className="admin-panel-card" styles={{ body: { paddingTop: 16 } }}>
          <AdminFilterSurface
            title="查询条件"
            extra={
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setBanAddOpen(true)}>
                新建封禁
              </Button>
            }
            style={{ marginBottom: 16 }}
          >
            <Input.Search
              allowClear
              size="middle"
              placeholder="搜索封禁 ID、用户 UID、原因…"
              style={{ maxWidth: 480 }}
              value={banSearch}
              onChange={(e) => setBanSearch(e.target.value)}
            />
          </AdminFilterSurface>
          <Table
            rowKey="banId"
            columns={banCols}
            dataSource={filteredBans}
            pagination={{ pageSize: 10 }}
            size="middle"
          />
        </Card>
      ),
    },
    {
      key: "vip",
      label: "VIP 门槛",
      children: (
        <Card
          size="small"
          className="admin-panel-card"
          title="VIP 门槛"
        >
          <Space direction="vertical" size="middle" style={{ maxWidth: 520 }}>
            <Text type="secondary">
              <Text code>{VIP_CONFIG_KEY}</Text>
              <span> · 平台默认 VIP {platformDefaultTier} · 等级数据为 Mock（正式由接口下发）</span>
            </Text>
            <Text type="secondary" style={{ display: "block", marginBottom: 4 }}>
              准入最低 VIP
            </Text>
            <Select
              style={{ width: "100%", maxWidth: 360 }}
              value={vipTier}
              placeholder="请选择会员 VIP 等级"
              options={mockMembershipVipLevels.map((l) => ({
                value: String(l.tier),
                label: l.label,
              }))}
              onChange={setVipTier}
            />
            <Space wrap>
              <Button type="primary" onClick={persistVip}>
                保存
              </Button>
              <Button onClick={resetVipToDefault}>恢复默认</Button>
            </Space>
          </Space>
        </Card>
      ),
    },
  ];

  return (
    <ProductPageShell
      pageId="access.overview"
      showPageId={false}
      title="准入管理"
      description="白名单、用户封禁、VIP 门槛维护。"
      tags={<Tag color="blue">风控运营</Tag>}
      extra={
        <Button icon={<ReloadOutlined />} onClick={reloadVipFromStorage}>
          刷新
        </Button>
      }
    >
      <Tabs activeKey={tab} onChange={onTabChange} items={tabsItems} />

      <Modal
        title="添加白名单条目"
        open={wlAddOpen}
        onOk={handleWlAdd}
        onCancel={() => {
          setWlAddOpen(false);
          wlForm.resetFields();
        }}
        destroyOnClose
      >
        <Form form={wlForm} layout="vertical">
          <Form.Item
            name="listId"
            label="名单ID"
            rules={[
              { required: true, message: "请输入名单ID" },
              {
                validator: (_, v) => {
                  const s = v != null ? String(v).trim() : "";
                  if (!s) return Promise.resolve();
                  return isValidWhitelistListId(s) ? Promise.resolve() : Promise.reject(new Error("名单ID格式不正确"));
                },
              },
            ]}
          >
            <Input placeholder="例如 20260507000001" maxLength={16} inputMode="numeric" autoComplete="off" />
          </Form.Item>
          <Form.Item
            name="userIdMasked"
            label="用户 UID（脱敏）"
            rules={[{ required: true, message: "请输入用户 UID 或脱敏掩码" }]}
          >
            <Input placeholder="例如 u-9****" />
          </Form.Item>
          <Form.Item name="note" label="备注">
            <Input.TextArea rows={2} placeholder="可选" />
          </Form.Item>
        </Form>
      </Modal>

      <Modal
        title="新建封禁"
        open={banAddOpen}
        onOk={handleBanCreate}
        onCancel={() => {
          setBanAddOpen(false);
          banForm.resetFields();
        }}
        destroyOnClose
        width={560}
      >
        <Form form={banForm} layout="vertical" initialValues={{ reasonCode: "AGENT_USER_BLOCKED", linkedPause: false }}>
          <Form.Item
            name="userUid"
            label="用户 UID"
            rules={[
              { required: true, message: "请输入用户 UID" },
              { pattern: /^\S+$/, message: "UID 不应包含空格" },
            ]}
          >
            <Input placeholder="用户 UID" autoComplete="off" />
          </Form.Item>
          <Form.Item name="reasonCode" label="封禁原因" rules={[{ required: true, message: "请选择封禁原因" }]}>
            <Select options={BAN_REASON_OPTIONS} placeholder="请选择" optionFilterProp="label" />
          </Form.Item>
          <Form.Item name="expiresAt" label="到期时间">
            <DatePicker showTime style={{ width: "100%" }} format="YYYY-MM-DD HH:mm" placeholder="可选" />
          </Form.Item>
          <Form.Item name="linkedPause" label="联动暂停实例" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </ProductPageShell>
  );
}

