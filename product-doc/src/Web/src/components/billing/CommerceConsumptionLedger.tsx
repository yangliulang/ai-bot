import { DownloadOutlined } from "@ant-design/icons";
import { Button, Card, message, Space, Table, Tag, Typography } from "antd";
import type { ColumnsType } from "antd/es/table";
import type { TablePaginationConfig } from "antd/es/table/interface";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { labelCapabilitySku } from "@/data/meCommerceMock";
import type {
  ConsumptionDebitStatus,
  MeCommerceConsumptionRow,
} from "@/data/meCommerceConsumptionMock";
import { AGENT_BILLING_COPY } from "@/copy/agentBillingCopy";
import type { ConsumptionDataSource } from "@/hooks/useMeCommerceConsumptions";

const { Paragraph, Text } = Typography;

const MOBILE_PAGE_SIZE = 5;
const MOBILE_PRELOAD_MS = 320;

const DESKTOP_PAGINATION: TablePaginationConfig = {
  pageSize: 10,
  showSizeChanger: false,
  showLessItems: true,
  showTotal: (total, range) => `第 ${range[0]}–${range[1]} 条，共 ${total} 条`,
};

function escapeCsvCell(value: string): string {
  if (/[",\n\r]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`;
  }
  return value;
}

function buildCsv(rows: MeCommerceConsumptionRow[]): string {
  const headers = [
    "时间",
    "场景类型",
    "Capability",
    "核销状态",
    "扣减单位",
    "成本观测（Token）",
    "执行 ID",
    "billingTraceId",
  ];
  const lines = [
    headers.map(escapeCsvCell).join(","),
    ...rows.map((r) =>
      [
        r.time,
        r.sceneType,
        r.capabilitySkuId,
        r.debitStatus,
        r.consumedUnits != null ? String(r.consumedUnits) : "",
        r.tokens != null ? String(r.tokens) : "",
        r.executionId,
        r.billingTraceId,
      ]
        .map(escapeCsvCell)
        .join(","),
    ),
  ];
  return `\uFEFF${lines.join("\r\n")}`;
}

function debitTag(status: ConsumptionDebitStatus) {
  if (status === "SUCCESS") return <Tag color="success">已核销</Tag>;
  if (status === "INSUFFICIENT") return <Tag color="error">额度不足</Tag>;
  if (status === "FAILED") return <Tag color="error">失败</Tag>;
  return <Tag color="processing">待终局</Tag>;
}

function exportFilename(): string {
  const d = new Date();
  const p = (n: number) => String(n).padStart(2, "0");
  return `agent-commerce-consumptions-${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}.csv`;
}

type ApiPagination = {
  hasMore: boolean;
  loadingMore: boolean;
  onLoadMore: () => void;
};

type Props = {
  rows: MeCommerceConsumptionRow[];
  source: ConsumptionDataSource;
  loading: boolean;
  compactLayout: boolean;
  apiPagination?: ApiPagination;
  /** 嵌入 Tab 面板时不套外层 Card */
  embedded?: boolean;
};

function sourceTag(source: ConsumptionDataSource) {
  if (source === "remote") return <Tag color="processing">已接 API</Tag>;
  if (source === "remote+fallback") return <Tag color="warning">回退演示</Tag>;
  return <Tag bordered={false}>演示</Tag>;
}

export function CommerceConsumptionLedger({
  rows,
  source,
  loading,
  compactLayout,
  apiPagination,
  embedded = false,
}: Props) {
  const useRemotePager = !!apiPagination?.hasMore;
  const [mobileVisible, setMobileVisible] = useState(MOBILE_PAGE_SIZE);
  const [mobilePrefetched, setMobilePrefetched] = useState<MeCommerceConsumptionRow[] | null>(null);
  const compactWasAppliedRef = useRef<boolean | undefined>(undefined);

  useEffect(() => {
    const prev = compactWasAppliedRef.current;
    compactWasAppliedRef.current = compactLayout;
    if (prev === undefined) return;
    if (compactLayout && !prev) {
      setMobileVisible(MOBILE_PAGE_SIZE);
      setMobilePrefetched(null);
    }
  }, [compactLayout]);

  useEffect(() => {
    if (useRemotePager) return;
    if (!compactLayout) return;
    if (mobileVisible >= rows.length) return;
    if (mobilePrefetched !== null) return;

    let cancelled = false;
    const timer = window.setTimeout(() => {
      if (cancelled) return;
      const chunk = rows.slice(mobileVisible, mobileVisible + MOBILE_PAGE_SIZE);
      setMobilePrefetched(chunk.length > 0 ? chunk : null);
    }, MOBILE_PRELOAD_MS);

    return () => {
      cancelled = true;
      window.clearTimeout(timer);
    };
  }, [compactLayout, rows, mobileVisible, mobilePrefetched, useRemotePager]);

  const mobileDisplayed = useMemo(() => rows.slice(0, mobileVisible), [rows, mobileVisible]);

  const appendMobile = useCallback(() => {
    if (!mobilePrefetched?.length) return;
    setMobileVisible((n) => n + mobilePrefetched.length);
    setMobilePrefetched(null);
  }, [mobilePrefetched]);

  const exportLedger = useCallback(() => {
    if (rows.length === 0) {
      message.warning("暂无流水可导出");
      return;
    }
    try {
      const blob = new Blob([buildCsv(rows)], { type: "text/csv;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = exportFilename();
      a.rel = "noopener";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.setTimeout(() => URL.revokeObjectURL(url), 2_000);
      message.success("已开始下载 CSV");
    } catch {
      message.error("导出失败，请稍后重试");
    }
  }, [rows]);

  const columns: ColumnsType<MeCommerceConsumptionRow> = [
    { title: "时间", dataIndex: "time", key: "time", width: 160 },
    { title: "场景", dataIndex: "sceneType", key: "sceneType", width: 88 },
    {
      title: "Capability",
      dataIndex: "capabilitySkuId",
      key: "capabilitySkuId",
      width: 120,
      render: (sku: string) => labelCapabilitySku(sku),
    },
    {
      title: "核销",
      dataIndex: "debitStatus",
      key: "debitStatus",
      width: 96,
      render: (s: ConsumptionDebitStatus) => debitTag(s),
    },
    {
      title: "扣减",
      dataIndex: "consumedUnits",
      key: "consumedUnits",
      align: "right",
      width: 64,
      render: (v: number | undefined) => (v != null ? v : "—"),
    },
    {
      title: "成本观测",
      dataIndex: "tokens",
      key: "tokens",
      align: "right",
      width: 72,
      render: (v: number | undefined) => (v != null ? v.toLocaleString("zh-CN") : "—"),
    },
    { title: "执行 ID", dataIndex: "executionId", key: "executionId", ellipsis: true, width: 148 },
  ];

  const hint = (
    <Paragraph type="secondary" className="coolbit-billing-tab-hint">
      每次可计费执行扣减 Capability 额度；Token 仅成本观测。 {AGENT_BILLING_COPY.ledgerDebitInsufficientHint}
      {useRemotePager ? " 支持分页加载。" : compactLayout ? " 窄屏可点「加载更多」。" : null}
    </Paragraph>
  );

  const tableBlock = (
    <div className="coolbit-billing-table-shell">
      <Table
        size={compactLayout ? "small" : "middle"}
        rowKey="key"
        loading={loading}
        pagination={compactLayout ? false : DESKTOP_PAGINATION}
        columns={columns}
        dataSource={compactLayout && !useRemotePager ? mobileDisplayed : rows}
        scroll={{ x: "max-content" }}
        locale={{ emptyText: "暂无核销记录" }}
      />
      {useRemotePager ? (
        <div className="coolbit-billing-ledger-mobile-more">
          <Text type="secondary" className="coolbit-billing-ledger-mobile-more__meta">
            已展示 {rows.length} 条
          </Text>
          <Button
            type="primary"
            block={compactLayout}
            className="coolbit-billing-ledger-mobile-more__btn"
            loading={apiPagination!.loadingMore}
            onClick={() => void apiPagination!.onLoadMore()}
          >
            加载更多
          </Button>
        </div>
      ) : null}
      {!useRemotePager && compactLayout && mobileVisible < rows.length ? (
        <div className="coolbit-billing-ledger-mobile-more">
          <Text type="secondary" className="coolbit-billing-ledger-mobile-more__meta">
            {mobileDisplayed.length} / {rows.length}
            {mobilePrefetched ? " · 可加载" : " · 预加载中…"}
          </Text>
          <Button
            type="primary"
            block
            className="coolbit-billing-ledger-mobile-more__btn"
            loading={!mobilePrefetched}
            disabled={!mobilePrefetched}
            onClick={appendMobile}
          >
            加载更多
          </Button>
        </div>
      ) : null}
    </div>
  );

  if (embedded) {
    return (
      <div className="coolbit-billing-tab-panel">
        <div className="coolbit-billing-tab-toolbar">
          <Space wrap size={8}>
            {sourceTag(source)}
          </Space>
          <Button type="default" icon={<DownloadOutlined />} onClick={exportLedger}>
            导出 CSV
          </Button>
        </div>
        {hint}
        {tableBlock}
      </div>
    );
  }

  return (
    <Card
      bordered={false}
      className="coolbit-billing-card"
      title="Capability 核销流水"
      loading={loading}
      extra={
        <Space wrap>
          {sourceTag(source)}
          <Button icon={<DownloadOutlined />} onClick={exportLedger}>
            导出
          </Button>
        </Space>
      }
    >
      {hint}
      {tableBlock}
    </Card>
  );
}
