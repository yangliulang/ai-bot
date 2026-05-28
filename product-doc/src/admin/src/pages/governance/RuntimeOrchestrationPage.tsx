import { useCallback } from "react";
import { useSearchParams } from "react-router-dom";
import { App, Tabs, Tag } from "antd";
import { ReloadOutlined } from "@ant-design/icons";
import { PageSecondaryButton, ProductPageShell } from "../../components/product";
import { ExecutionPolicyTab } from "./orchestration/ExecutionPolicyTab";
import { ScenarioRoutingTab } from "./orchestration/ScenarioRoutingTab";

type OrchestrationTab = "routing" | "policy";

function isOrchestrationTab(s: string | null): s is OrchestrationTab {
  return s === "routing" || s === "policy";
}

export function RuntimeOrchestrationPage() {
  const { message } = App.useApp();
  const [searchParams, setSearchParams] = useSearchParams();
  const tabRaw = searchParams.get("tab");
  const activeTab: OrchestrationTab = isOrchestrationTab(tabRaw) ? tabRaw : "routing";
  const scenarioFromUrl = searchParams.get("scenario") ?? "";

  const onTabChange = useCallback(
    (key: string) => {
      const next = new URLSearchParams(searchParams);
      if (key === "routing") {
        next.delete("tab");
      } else {
        next.set("tab", key);
      }
      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  const clearScenarioFromUrl = useCallback(() => {
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        next.delete("scenario");
        return next;
      },
      { replace: true },
    );
  }, [setSearchParams]);

  return (
    <ProductPageShell
      pageId="ai.runtime-orchestration"
      title="运行场景"
      description="按业务类型浏览智能体运行场景；执行边界在「执行策略」。内部标识与规格路径见各场景详情。"
      tags={
        <Tag color="geekblue">AI 治理</Tag>
      }
      extra={
        <PageSecondaryButton icon={<ReloadOutlined />} onClick={() => message.success("已刷新")}>
          刷新
        </PageSecondaryButton>
      }
    >
      <Tabs
        activeKey={activeTab}
        onChange={onTabChange}
        style={{ marginTop: 0 }}
        items={[
          {
            key: "routing",
            label: "场景目录",
            children: (
              <ScenarioRoutingTab initialScenarioSearch={scenarioFromUrl} onClearScenarioParam={clearScenarioFromUrl} />
            ),
          },
          {
            key: "policy",
            label: "执行策略",
            children: <ExecutionPolicyTab />,
          },
        ]}
      />

    </ProductPageShell>
  );
}
