import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { App, Spin, Tag, Typography, theme } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { useNavigate, useSearchParams } from "react-router-dom";
import { PagePrimaryButton, ProductPageShell } from "../../components/product";
import { getPromptPack, mockPromptPacks } from "../../data/mock";
import type { MockPromptPack } from "../../data/types";
import { PromptPackDetailDrawer } from "./PromptPackDetailDrawer";
import { isPromptApiEnabled } from "../../api/http";
import { loadAllPromptPacks, loadEditorBootstrap, loadPackForDrawer } from "./promptRemote";
import { PromptStrategyFilterPanel } from "./PromptStrategyFilterPanel";
import { PromptStrategyListSection } from "./PromptStrategyListSection";
import type { GovernanceKindFilter } from "./governanceKind";
import { parseGovernanceKind } from "./governanceKind";
import { packMatchesLifecycleFilter, parsePromptLifecycleListFilter, type PromptLifecycleListFilter } from "./promptLifecycle";
import { PromptCreateDraftModal } from "./PromptCreateDraftModal";
import { cloneToEphemeralBootstrap, persistEphemeralBootstrap } from "./promptEphemeral";
import { promptPackEditorPath } from "./promptPaths";
import { PromptGovernanceIntro } from "./PromptGovernanceIntro";
import { PROMPT_LIST_SOURCE } from "../../copy/opsPanelHints";

const { Text } = Typography;

/** 列表关键字：`q` 优先；兼容旧书签 `id` / `title`。 */
function keywordFromRouteSearchParams(sp: URLSearchParams): string {
  const q = (sp.get("q") ?? "").trim();
  if (q !== "") return q;
  const id = (sp.get("id") ?? "").trim();
  const title = (sp.get("title") ?? "").trim();
  if (id !== "") return id;
  if (title !== "") return title;
  return "";
}

export function PromptStrategyPage() {
  const { token } = theme.useToken();
  const navigate = useNavigate();
  const { message } = App.useApp();
  const [searchParams, setSearchParams] = useSearchParams();
  const packId = searchParams.get("pack") ?? "";

  const [listRows, setListRows] = useState<MockPromptPack[] | null>(null);
  const [listSource, setListSource] = useState<string>("mock");
  const [listError, setListError] = useState<string | undefined>();
  const [drawerPack, setDrawerPack] = useState<MockPromptPack | undefined>();
  const [forkModalOpen, setForkModalOpen] = useState(false);

  const reloadList = useCallback(() => {
    setListRows(null);
    loadAllPromptPacks()
      .then(({ rows, source, error, supplementedFromMock }) => {
        setListRows(rows);
        setListSource(source);
        if (error) {
          setListError(error);
        } else if (supplementedFromMock?.length) {
          setListError(PROMPT_LIST_SOURCE.mergeHint(supplementedFromMock.length));
        } else {
          setListError(undefined);
        }
      })
      .catch((e) => {
        setListRows(mockPromptPacks);
        setListSource("mock");
        setListError(undefined);
        message.error(String(e));
      });
  }, [message]);

  useEffect(() => {
    reloadList();
  }, [reloadList]);

  useEffect(() => {
    if (!packId) {
      setDrawerPack(undefined);
      return;
    }
    setDrawerPack(getPromptPack(packId));
    let cancelled = false;
    loadPackForDrawer(packId).then((p) => {
      if (!cancelled && p) setDrawerPack(p);
      if (!cancelled && !p && !getPromptPack(packId)) {
        setSearchParams(
          (prev) => {
            const n = new URLSearchParams(prev);
            n.delete("pack");
            return n;
          },
          { replace: true },
        );
      }
    });
    return () => {
      cancelled = true;
    };
  }, [packId, setSearchParams]);

  useEffect(() => {
    const filter = searchParams.get("filter");
    const tab = searchParams.get("tab");
    if (!filter && !tab) return;
    setSearchParams(
      (prev) => {
        const n = new URLSearchParams(prev);
        n.delete("filter");
        n.delete("tab");
        return n;
      },
      { replace: true },
    );
  }, [searchParams, setSearchParams]);

  useEffect(() => {
    if (!packId || listRows === null) return;
    const inList = listRows.some((p) => p.promptPackId === packId);
    const inMock = !!getPromptPack(packId);
    if (!inList && !inMock && !isPromptApiEnabled()) {
      setSearchParams(
        (prev) => {
          const n = new URLSearchParams(prev);
          n.delete("pack");
          return n;
        },
        { replace: true },
      );
    }
  }, [packId, listRows, setSearchParams]);

  const openPack = useCallback(
    (p: MockPromptPack) => {
      setSearchParams((prev) => {
        const n = new URLSearchParams(prev);
        n.set("pack", p.promptPackId);
        return n;
      });
    },
    [setSearchParams],
  );

  const closePack = useCallback(() => {
    setSearchParams((prev) => {
      const n = new URLSearchParams(prev);
      n.delete("pack");
      return n;
    });
  }, [setSearchParams]);

  const nonSafetyRows = useMemo(() => (listRows ?? []).filter((p) => p.kind !== "SAFETY"), [listRows]);

  const packsForFork = useMemo(() => {
    const base = nonSafetyRows;
    return base.length ? base : mockPromptPacks.filter((p) => p.kind !== "SAFETY");
  }, [nonSafetyRows]);

  const governanceKind = parseGovernanceKind(searchParams.get("kind"));

  const setGovernanceKind = useCallback(
    (k: GovernanceKindFilter) => {
      setSearchParams(
        (prev) => {
          const n = new URLSearchParams(prev);
          if (k === "all") n.delete("kind");
          else n.set("kind", k);
          return n;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  const lifecycleFilter = parsePromptLifecycleListFilter(searchParams.get("life"));

  const setLifecycleFilter = useCallback(
    (k: PromptLifecycleListFilter) => {
      setSearchParams(
        (prev) => {
          const n = new URLSearchParams(prev);
          if (k === "all") n.delete("life");
          else n.set("life", k);
          return n;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  const keywordFromUrl = useMemo(() => keywordFromRouteSearchParams(searchParams), [searchParams]);

  const [promptKeyword, setPromptKeyword] = useState(keywordFromUrl);

  useEffect(() => {
    setPromptKeyword(keywordFromUrl);
  }, [keywordFromUrl]);

  const queryFilteredRows = useMemo(() => {
    const kq = promptKeyword.trim().toLowerCase();
    let rows = nonSafetyRows;
    if (governanceKind !== "all") rows = rows.filter((p) => p.kind === governanceKind);
    rows = rows.filter((p) => packMatchesLifecycleFilter(p, lifecycleFilter));
    if (kq) {
      rows = rows.filter(
        (p) =>
          p.promptPackId.toLowerCase().includes(kq) ||
          (p.title ?? "").toLowerCase().includes(kq),
      );
    }
    return rows;
  }, [nonSafetyRows, governanceKind, lifecycleFilter, promptKeyword]);

  const syncQueryToUrl = useCallback(() => {
    setSearchParams((prev) => {
      const n = new URLSearchParams(prev);
      const trim = promptKeyword.trim();
      n.delete("id");
      n.delete("title");
      if (trim) n.set("q", trim);
      else n.delete("q");
      return n;
    });
  }, [promptKeyword, setSearchParams]);

  const syncQueryRef = useRef(syncQueryToUrl);
  syncQueryRef.current = syncQueryToUrl;

  useEffect(() => {
    const t = window.setTimeout(() => syncQueryRef.current(), 420);
    return () => window.clearTimeout(t);
  }, [promptKeyword]);

  const onResetQuery = useCallback(() => {
    setPromptKeyword("");
    setSearchParams((prev) => {
      const n = new URLSearchParams(prev);
      n.delete("q");
      n.delete("id");
      n.delete("title");
      n.delete("kind");
      n.delete("life");
      return n;
    });
  }, [setSearchParams]);

  const openForkModal = useCallback(() => {
    setForkModalOpen(true);
  }, []);

  const loadingList = listRows === null;

  return (
    <ProductPageShell
      pageId="ai.prompt-strategy"
      showPageId={false}
      title="提示词治理"
      description={
        <Text type="secondary" style={{ fontSize: 13 }}>
          分层管理：基础、场景、分析与体验（含安全防护）；业务能力在「技能与工具」登记册配置。
        </Text>
      }
      tags={
        listSource === "remote" ? (
          <Tag color="green">{PROMPT_LIST_SOURCE.tagRemote}</Tag>
        ) : listSource === "remote+mock-ssot" ? (
          <Tag color="blue">{PROMPT_LIST_SOURCE.tagRemoteMerged}</Tag>
        ) : listSource === "remote+fallback" ? (
          <Tag color="orange">{PROMPT_LIST_SOURCE.tagRemoteFallback}</Tag>
        ) : (
          <Tag color="purple">{PROMPT_LIST_SOURCE.tagMock}</Tag>
        )
      }
      extra={
        <PagePrimaryButton icon={<PlusOutlined />} onClick={openForkModal}>
          新建草稿
        </PagePrimaryButton>
      }
    >
      {listError ? (
        <div
          style={{
            marginBottom: 16,
            padding: "10px 14px",
            borderRadius: token.borderRadiusLG,
            borderLeft: `3px solid ${token.colorWarning}`,
            background: token.colorWarningBg,
          }}
        >
          <Text style={{ fontSize: 13 }}>{listError}</Text>
        </div>
      ) : null}

      <PromptGovernanceIntro />

      <Spin spinning={loadingList}>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <PromptStrategyFilterPanel
            promptKeyword={promptKeyword}
            governanceKind={governanceKind}
            lifecycleFilter={lifecycleFilter}
            onPromptKeywordChange={setPromptKeyword}
            onGovernanceKindChange={setGovernanceKind}
            onLifecycleFilterChange={setLifecycleFilter}
          />

          <PromptStrategyListSection
            loadingList={loadingList}
            nonSafetyRowsTotal={nonSafetyRows.length}
            querySig={`${promptKeyword}\t${governanceKind}\t${lifecycleFilter}`}
            queryFilteredRows={queryFilteredRows}
            onResetQuery={onResetQuery}
            onNewDraft={openForkModal}
            onOpenPack={openPack}
            showLifecycleColumn
          />
        </div>
      </Spin>

      <PromptPackDetailDrawer open={!!packId && !!drawerPack} pack={drawerPack ?? null} onClose={closePack} />

      <PromptCreateDraftModal
        open={forkModalOpen}
        onClose={() => setForkModalOpen(false)}
        templateRows={packsForFork}
        onBlankCreate={(b) => {
          persistEphemeralBootstrap(b);
          setForkModalOpen(false);
          navigate(promptPackEditorPath(b.pack.promptPackId));
          message.success("已创建本地草稿并打开编辑器");
        }}
        onCloneFromTemplate={async (templateId) => {
          const src = await loadEditorBootstrap(templateId);
          const next = cloneToEphemeralBootstrap(src);
          persistEphemeralBootstrap(next);
          setForkModalOpen(false);
          navigate(promptPackEditorPath(next.pack.promptPackId));
          message.success("已从模板复制为新的本地草稿");
        }}
      />
    </ProductPageShell>
  );
}
