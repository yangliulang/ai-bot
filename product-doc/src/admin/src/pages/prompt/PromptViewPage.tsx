import { useCallback, useEffect, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { Button, Space, Spin } from "antd";
import { ArrowLeftOutlined, EditOutlined } from "@ant-design/icons";
import { ProductPageShell } from "../../components/product";
import { getPromptPack } from "../../data/mock";
import type { MockPromptPack } from "../../data/types";
import { isPromptApiEnabled } from "../../api/http";
import { loadPackForDrawer } from "./promptRemote";
import { promptPackEditorPath, promptPackListHref } from "./promptPaths";
import { PromptPackDetailPanel } from "./PromptPackDetailPanel";
import { PromptPackIdText } from "./promptIdDisplay";

export function PromptViewPage() {
  const { promptPackId = "" } = useParams();
  const [pack, setPack] = useState<MockPromptPack | undefined>();
  const [loading, setLoading] = useState(true);

  const reload = useCallback(async () => {
    if (!promptPackId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setPack(getPromptPack(promptPackId));
    try {
      const p = await loadPackForDrawer(promptPackId);
      if (p) setPack(p);
      if (!p && !getPromptPack(promptPackId) && !isPromptApiEnabled()) {
        setPack(undefined);
      }
    } finally {
      setLoading(false);
    }
  }, [promptPackId]);

  useEffect(() => {
    void reload();
  }, [reload]);

  if (!promptPackId) {
    return <Navigate to="/prompts/strategy" replace />;
  }

  if (loading) {
    return (
      <ProductPageShell pageId="ai.prompt-view" showPageId={false} title="加载中…" extra={null}>
        <div style={{ padding: 80, textAlign: "center" }}>
          <Spin size="large" />
        </div>
      </ProductPageShell>
    );
  }

  if (!pack) {
    return <Navigate to="/prompts/strategy" replace />;
  }

  const listBack = promptPackListHref(pack);
  const editorTo = promptPackEditorPath(pack.promptPackId);

  return (
    <ProductPageShell
      pageId="ai.prompt-view"
      showPageId={false}
      title={pack.title}
      description={
        <span>
          Prompt ID：<PromptPackIdText promptPackId={pack.promptPackId} />
        </span>
      }
      extra={
        <Space wrap>
          <Link to={listBack}>
            <Button icon={<ArrowLeftOutlined />}>返回列表</Button>
          </Link>
          <Link to={editorTo}>
            <Button type="primary" icon={<EditOutlined />}>
              编辑
            </Button>
          </Link>
        </Space>
      }
    >
      <PromptPackDetailPanel pack={pack} />
    </ProductPageShell>
  );
}
