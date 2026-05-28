import { useCallback, useEffect, useMemo, useState } from "react";
import {
  App,
  Button,
  Card,
  Divider,
  Dropdown,
  Empty,
  Form,
  Input,
  Select,
  Space,
  Table,
  Tabs,
  Tag,
  Tooltip,
  Typography,
} from "antd";
import { DownOutlined, HistoryOutlined, ReloadOutlined, SearchOutlined } from "@ant-design/icons";
import type { ColumnsType } from "antd/es/table";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { ProductPageShell, AdminFilterSurface, ADMIN_FILTER_CONTROL_SIZE, ADMIN_PAGE_FILTER_FORM_PROPS } from "../../components/product";
import { OpsHintAlert } from "../../components/OpsHintAlert";
import { zhCapabilitySku } from "../../copy/billingLabels";
import { BILLING_LEDGER } from "../../copy/opsPanelHints";
import { buildObservabilitySearch, buildObservabilitySearchFromCorrelateHint } from "../../utils/observabilityDeepLink";
import type { MockBillingLedgerRow } from "../../data/types";
import { useBillingLedgerRows } from "../../hooks/useBillingLedgerRows";
import {
  billingTraceExpandedRowRender,
  runtimeBillingTraceColumns,
} from "./ledgerTable";

const { Text } = Typography;

const LEDGER_TAB_KEYS = ["ledger", "correlate"] as const;
type LedgerTabKey = (typeof LEDGER_TAB_KEYS)[number];

function isLedgerTab(k: string): k is LedgerTabKey {
  return (LEDGER_TAB_KEYS as readonly string[]).includes(k);
}

function parseDayStart(isoDate: string): number {
  const d = new Date(`${isoDate.trim()}T00:00:00`);
  return d.getTime();
}

function parseDayEnd(isoDate: string): number {
  const d = new Date(`${isoDate.trim()}T23:59:59.999`);
  return d.getTime();
}

function filterRuntimeBillingRows(
  rows: MockBillingLedgerRow[],
  p: {
    debitStatus: string;
    capabilitySkuId: string;
    userKeyword: string;
    intentType: string;
    executionStatus: string;
    execOrTraceKeyword: string;
    dateFrom: string;
    dateTo: string;
  },
): MockBillingLedgerRow[] {
  let out = rows;
  if (p.debitStatus) {
    out = out.filter((r) => r.debitStatus === p.debitStatus);
  }
  if (p.capabilitySkuId) {
    out = out.filter((r) => r.capabilitySkuId === p.capabilitySkuId);
  }
  const u = p.userKeyword.trim().toLowerCase();
  if (u) {
    out = out.filter((r) => r.userIdMasked.toLowerCase().includes(u));
  }
  if (p.intentType) {
    out = out.filter((r) => r.intentType === p.intentType);
  }
  if (p.executionStatus) {
    out = out.filter((r) => r.executionStatus.toUpperCase() === p.executionStatus.toUpperCase());
  }
  const et = p.execOrTraceKeyword.trim().toLowerCase();
  if (et) {
    out = out.filter(
      (r) =>
        r.executionId.toLowerCase().includes(et) || r.billingTraceId.toLowerCase().includes(et),
    );
  }
  if (p.dateFrom.trim()) {
    const t0 = parseDayStart(p.dateFrom);
    if (!Number.isNaN(t0)) {
      out = out.filter((r) => new Date(r.recordedAt).getTime() >= t0);
    }
  }
  if (p.dateTo.trim()) {
    const t1 = parseDayEnd(p.dateTo);
    if (!Number.isNaN(t1)) {
      out = out.filter((r) => new Date(r.recordedAt).getTime() <= t1);
    }
  }
  return out;
}

const sharedExpandable = {
  expandRowByClick: false,
  expandedRowRender: (row: MockBillingLedgerRow) => billingTraceExpandedRowRender(row),
};

export function BillingLedgerPage() {
  const { message } = App.useApp();
  const navigate = useNavigate();
  const { rows: ledgerRows, source: ledgerSource, loading: ledgerLoading, reload, searchCorrelate } =
    useBillingLedgerRows();

  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    const t = searchParams.get("tab");
    if (t === "finance" || searchParams.has("trace")) {
      const p = new URLSearchParams(searchParams);
      p.delete("tab");
      p.delete("trace");
      setSearchParams(p, { replace: true });
    }
  }, [searchParams, setSearchParams]);

  const rawTab = searchParams.get("tab") ?? "ledger";
  const activeTab: LedgerTabKey =
    rawTab === "finance" ? "ledger" : isLedgerTab(rawTab) ? rawTab : "ledger";
  const urlQ = searchParams.get("q") ?? "";
  const [lookup, setLookup] = useState(urlQ);

  const [filterDebitStatus, setFilterDebitStatus] = useState<string>("");
  const [filterCapability, setFilterCapability] = useState<string>("");
  const [filterUser, setFilterUser] = useState("");
  const [filterIntentType, setFilterIntentType] = useState<string>("");
  const [filterExecutionStatus, setFilterExecutionStatus] = useState<string>("");
  const [filterExecOrTrace, setFilterExecOrTrace] = useState("");
  const [filterDateFrom, setFilterDateFrom] = useState("");
  const [filterDateTo, setFilterDateTo] = useState("");

  useEffect(() => {
    setLookup(urlQ);
  }, [urlQ]);

  useEffect(() => {
    const uid = searchParams.get("userId");
    if (uid) setFilterUser(uid);
    const q = searchParams.get("q");
    if (q) setLookup(q);
  }, [searchParams]);

  const [correlateHits, setCorrelateHits] = useState<MockBillingLedgerRow[]>([]);
  const [correlateLoading, setCorrelateLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setCorrelateLoading(true);
    void searchCorrelate(lookup)
      .then((h) => {
        if (!cancelled) setCorrelateHits(h);
      })
      .finally(() => {
        if (!cancelled) setCorrelateLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [lookup, searchCorrelate]);

  const filteredLedger = useMemo(
    () =>
      filterRuntimeBillingRows(ledgerRows, {
        debitStatus: filterDebitStatus,
        capabilitySkuId: filterCapability,
        userKeyword: filterUser,
        intentType: filterIntentType,
        executionStatus: filterExecutionStatus,
        execOrTraceKeyword: filterExecOrTrace,
        dateFrom: filterDateFrom,
        dateTo: filterDateTo,
      }),
    [
      filterDebitStatus,
      filterCapability,
      filterUser,
      filterIntentType,
      filterExecutionStatus,
      filterExecOrTrace,
      filterDateFrom,
      filterDateTo,
      ledgerRows,
    ],
  );

  const ledgerColumns: ColumnsType<MockBillingLedgerRow> = useMemo(
    () => [
      ...runtimeBillingTraceColumns,
      {
        title: "操作",
        key: "next",
        width: 96,
        align: "center" as const,
        fixed: "right" as const,
        render: (_: unknown, row: MockBillingLedgerRow) => {
          const obsHref = `/observability${buildObservabilitySearch({
            executionId: row.executionId,
            traceId: row.billingTraceId,
            tab: "billing",
          })}`;
          return (
            <Dropdown
              trigger={["click"]}
              menu={{
                items: [
                  {
                    key: "exec",
                    label: "查看执行",
                    onClick: () => navigate(`/runtime/executions/${row.executionId}`),
                  },
                  {
                    key: "log",
                    label: "查看日志",
                    onClick: () => navigate(obsHref),
                  },
                  { type: "divider" },
                  {
                    key: "retry",
                    label: "重试扣费",
                    disabled: true,
                    icon: <ReloadOutlined />,
                  },
                ],
              }}
            >
              <Button type="link" size="small" style={{ padding: "0 4px" }}>
                操作 <DownOutlined style={{ fontSize: 10 }} />
              </Button>
            </Dropdown>
          );
        },
      },
    ],
    [navigate],
  );

  const onTabChange = useCallback(
    (k: string) => {
      const next = k === "finance" ? "ledger" : isLedgerTab(k) ? k : "ledger";
      const p = new URLSearchParams(searchParams);
      if (next === "ledger") p.delete("tab");
      else p.set("tab", next);
      setSearchParams(p, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  const applyCorrelateQuery = useCallback(() => {
    const p = new URLSearchParams(searchParams);
    p.set("tab", "correlate");
    if (lookup.trim()) p.set("q", lookup.trim());
    else p.delete("q");
    setSearchParams(p, { replace: true });
  }, [lookup, searchParams, setSearchParams]);

  const observabilityFallbackHref = `/observability${buildObservabilitySearchFromCorrelateHint(lookup)}`;

  const capabilityFilterOptions = useMemo(
    () =>
      Array.from(new Set(ledgerRows.map((r) => r.capabilitySkuId))).map((sku) => ({
        value: sku,
        label: zhCapabilitySku(sku),
      })),
    [ledgerRows],
  );

  const resetLedgerFilters = useCallback(() => {
    setFilterDebitStatus("");
    setFilterCapability("");
    setFilterUser("");
    setFilterIntentType("");
    setFilterExecutionStatus("");
    setFilterExecOrTrace("");
    setFilterDateFrom("");
    setFilterDateTo("");
    message.success("已重置筛选条件");
  }, [message]);

  const tabBarExtra = (
    <Space size="middle" wrap={false} style={{ maxWidth: "100%" }}>
      <Tooltip
        title={
          ledgerSource === "remote"
            ? BILLING_LEDGER.tagApiConnected
            : ledgerSource === "remote+fallback"
              ? BILLING_LEDGER.tagApiFallback
              : BILLING_LEDGER.demoDataTooltip
        }
      >
        <Tag
          style={{ margin: 0 }}
          color={ledgerSource === "remote" ? "processing" : ledgerSource === "remote+fallback" ? "warning" : undefined}
        >
          {ledgerSource === "remote"
            ? BILLING_LEDGER.tagApiConnected
            : ledgerSource === "remote+fallback"
              ? BILLING_LEDGER.tagApiFallback
              : BILLING_LEDGER.tagLocalPreview}
        </Tag>
      </Tooltip>
      <Button icon={<ReloadOutlined />} size="small" loading={ledgerLoading} onClick={() => void reload()}>
        刷新
      </Button>
    </Space>
  );

  return (
    <ProductPageShell
      pageId="billing.ledger"
      showPageId={false}
      title="执行核销追踪"
      description={BILLING_LEDGER.description}
      tags={
        <>
          <Tag color="processing">权益核销</Tag>
          <Tag>计费与账务</Tag>
        </>
      }
    >
      <Tabs
        activeKey={activeTab}
        onChange={onTabChange}
        tabBarExtraContent={tabBarExtra}
        destroyInactiveTabPane={false}
        style={{ overflow: "hidden" }}
        items={[
          {
            key: "ledger",
            label: (
              <span>
                <HistoryOutlined /> {BILLING_LEDGER.tabLedger}
              </span>
            ),
            children: (
              <Card size="small" bordered={false} styles={{ body: { padding: 0 } }}>
                <div style={{ padding: "16px 16px 0" }}>
                  <AdminFilterSurface
                    title="查询条件"
                    extra={
                      <Text type="secondary" style={{ fontSize: 13 }}>
                        命中 <Text strong>{filteredLedger.length}</Text> 条
                      </Text>
                    }
                    footer={
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        executionId、billingTraceId、用户与各状态下为<strong>交集</strong>；时间按账单记录日（零点）闭区间过滤。
                      </Text>
                    }
                  >
                    <Form {...ADMIN_PAGE_FILTER_FORM_PROPS} style={{ marginBottom: 0 }}>
                      <div className="admin-filter-query-grid">
                        <div className="admin-filter-span-6">
                          <Form.Item label="执行 ID / 计费链路" style={{ marginBottom: 0 }}>
                            <Input
                              allowClear
                              placeholder="executionId、billingTraceId 包含匹配"
                              value={filterExecOrTrace}
                              onChange={(e) => setFilterExecOrTrace(e.target.value)}
                              size={ADMIN_FILTER_CONTROL_SIZE}
                            />
                          </Form.Item>
                        </div>
                        <div className="admin-filter-span-6">
                          <Form.Item label="用户 UID" style={{ marginBottom: 0 }}>
                            <Input
                              allowClear
                              placeholder="用户 UID（掩码）"
                              value={filterUser}
                              onChange={(e) => setFilterUser(e.target.value)}
                              size={ADMIN_FILTER_CONTROL_SIZE}
                            />
                          </Form.Item>
                        </div>
                        <div className="admin-filter-span-4">
                          <Form.Item label="意图类型" style={{ marginBottom: 0 }}>
                            <Select
                              allowClear
                              placeholder="全部"
                              value={filterIntentType || undefined}
                              onChange={(v) => setFilterIntentType(v ?? "")}
                              style={{ width: "100%" }}
                              size={ADMIN_FILTER_CONTROL_SIZE}
                              options={[
                                { value: "分析", label: "分析" },
                                { value: "交易", label: "交易" },
                                { value: "Monitoring", label: "Monitoring" },
                              ]}
                            />
                          </Form.Item>
                        </div>
                        <div className="admin-filter-span-4">
                          <Form.Item label="执行状态" style={{ marginBottom: 0 }}>
                            <Select
                              allowClear
                              placeholder="全部"
                              value={filterExecutionStatus || undefined}
                              onChange={(v) => setFilterExecutionStatus(v ?? "")}
                              style={{ width: "100%" }}
                              size={ADMIN_FILTER_CONTROL_SIZE}
                              options={[
                                { value: "COMPLETED", label: "已完成" },
                                { value: "UNKNOWN", label: "UNKNOWN" },
                                { value: "RUNNING", label: "运行中" },
                                { value: "FAILED", label: "失败" },
                              ]}
                            />
                          </Form.Item>
                        </div>
                        <div className="admin-filter-span-4">
                          <Form.Item label="核销状态" style={{ marginBottom: 0 }}>
                            <Select
                              allowClear
                              placeholder="全部"
                              value={filterDebitStatus || undefined}
                              onChange={(v) => setFilterDebitStatus(v ?? "")}
                              style={{ width: "100%" }}
                              size={ADMIN_FILTER_CONTROL_SIZE}
                              options={[
                                { value: "SUCCESS", label: "核销成功" },
                                { value: "INSUFFICIENT", label: "额度不足" },
                                { value: "FAILED", label: "核销失败" },
                                { value: "AWAITING_FINAL", label: "待终局" },
                              ]}
                            />
                          </Form.Item>
                        </div>
                        <div className="admin-filter-span-4">
                          <Form.Item label="Capability" style={{ marginBottom: 0 }}>
                            <Select
                              allowClear
                              placeholder="全部"
                              value={filterCapability || undefined}
                              onChange={(v) => setFilterCapability(v ?? "")}
                              style={{ width: "100%" }}
                              size={ADMIN_FILTER_CONTROL_SIZE}
                              options={capabilityFilterOptions}
                            />
                          </Form.Item>
                        </div>
                        <div className="admin-filter-span-4">
                          <Form.Item label="入账起始日" style={{ marginBottom: 0 }}>
                            <Input type="date" value={filterDateFrom} onChange={(e) => setFilterDateFrom(e.target.value)} size={ADMIN_FILTER_CONTROL_SIZE} />
                          </Form.Item>
                        </div>
                        <div className="admin-filter-span-4">
                          <Form.Item label="入账结束日" style={{ marginBottom: 0 }}>
                            <Input type="date" value={filterDateTo} onChange={(e) => setFilterDateTo(e.target.value)} size={ADMIN_FILTER_CONTROL_SIZE} />
                          </Form.Item>
                        </div>
                        <div className="admin-filter-span-12">
                          <div style={{ display: "flex", flexWrap: "wrap", justifyContent: "flex-end", gap: 12, paddingTop: 2 }}>
                            <Button
                              type="primary"
                              icon={<SearchOutlined />}
                              size={ADMIN_FILTER_CONTROL_SIZE}
                              onClick={() => message.success(`当前命中 ${filteredLedger.length} 条（演示）`)}
                            >
                              查询
                            </Button>
                            <Button size={ADMIN_FILTER_CONTROL_SIZE} onClick={resetLedgerFilters}>
                              重置
                            </Button>
                          </div>
                        </div>
                      </div>
                    </Form>
                  </AdminFilterSurface>

                  <OpsHintAlert
                    type="info"
                    showIcon
                    style={{ marginBottom: 12 }}
                    message={BILLING_LEDGER.listExpandHint}
                  />
                </div>
                <div style={{ padding: "8px 12px 16px" }}>
                  <Table
                    rowKey="billingTraceId"
                    loading={ledgerLoading}
                    columns={ledgerColumns}
                    dataSource={filteredLedger}
                    tableLayout="fixed"
                    pagination={{
                      pageSize: 10,
                      showSizeChanger: true,
                      showTotal: (t) => `共 ${t} 条`,
                      pageSizeOptions: ["10", "20", "50"],
                    }}
                    size="middle"
                    scroll={{ x: 1180 }}
                    locale={{
                      emptyText: <Empty description="当前条件下无记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />,
                    }}
                    expandable={sharedExpandable}
                  />
                </div>
              </Card>
            ),
          },
          {
            key: "correlate",
            label: (
              <span>
                <SearchOutlined /> {BILLING_LEDGER.tabCorrelate}
              </span>
            ),
            children: (
              <Card size="small" bordered={false} styles={{ body: { padding: 0 } }}>
                <div style={{ padding: "16px 20px 12px" }}>
                  <Space.Compact style={{ maxWidth: 680, width: "100%" }}>
                    <Input
                      size="large"
                      placeholder="executionId · billingTraceId · userId · requestId · 失败原因码…"
                      value={lookup}
                      onChange={(e) => setLookup(e.target.value)}
                      allowClear
                      onPressEnter={applyCorrelateQuery}
                    />
                    <Button type="primary" size="large" icon={<SearchOutlined />} onClick={applyCorrelateQuery}>
                      追踪
                    </Button>
                  </Space.Compact>
                  <Text type="secondary" style={{ fontSize: 12, display: "block", marginTop: 8 }}>
                    示例：<Text code>20260501001001</Text> · <Text code>bt-7f2a-001</Text> · <Text code>req-7f2a-001</Text>
                  </Text>
                </div>
                <Divider style={{ margin: 0 }} />
                <div style={{ padding: "16px 20px 24px", minHeight: 280 }}>
                  {!lookup.trim() ? (
                    <Empty
                      image={Empty.PRESENTED_IMAGE_SIMPLE}
                      description="输入线索后在前端账单中匹配"
                      styles={{ image: { height: 48 } }}
                    />
                  ) : correlateHits.length === 0 ? (
                    <Empty description="无匹配；可带线索跳转观测「计费」扩大检索">
                      <Link to={observabilityFallbackHref}>
                        <Button type="primary">去观测（预填）</Button>
                      </Link>
                    </Empty>
                  ) : (
                    <>
                      <Text type="secondary" style={{ display: "block", marginBottom: 12 }}>
                        共 <Text strong>{correlateHits.length}</Text> {BILLING_LEDGER.correlateHitCount}
                      </Text>
                      <Table
                        rowKey="billingTraceId"
                        columns={ledgerColumns}
                        loading={correlateLoading}
                        dataSource={correlateHits}
                        tableLayout="fixed"
                        pagination={false}
                        size="small"
                        scroll={{ x: 1180 }}
                        expandable={sharedExpandable}
                      />
                    </>
                  )}
                </div>
              </Card>
            ),
          },
        ]}
      />
    </ProductPageShell>
  );
}
