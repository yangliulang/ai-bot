import { type ComponentProps, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  App,
  Alert,
  Button,
  Card,
  Col,
  Divider,
  Dropdown,
  Input,
  Row,
  Space,
  Spin,
  Tag,
  Typography,
} from "antd";
import type { MenuProps } from "antd";
import { Link, Navigate, useParams } from "react-router-dom";
import { SaveOutlined } from "@ant-design/icons";
import { ProductPageShell } from "../../components/product";
import { ApiError } from "../../api/http";
import type { MockFewShotRow, MockPromptPackDraft } from "../../data/types";
import { zhPromptPackKind, zhPromptPackLockState } from "../../copy/zhLabels";
import { promptPackListHref, promptPackViewPath } from "./promptPaths";
import { PromptMarkdownLiteField } from "./PromptMarkdownLiteField";
import { PromptPackIdText } from "./promptIdDisplay";
import { runPromptPublishGate, type PromptPublishGateTrace } from "./promptPublishGate";
import { PromptAssemblyTraceCard } from "./PromptAssemblyTraceCard";
import {
  PromptPublishRejectTrace,
  PromptPublishRejectTraceTable,
} from "./PromptPublishRejectTracePanel";
import { SkillSpecRefPublishAlert } from "./SkillSpecRefPublishAlert";
import { PromptUnifiedAnalysisMeta } from "./PromptUnifiedAnalysisMeta";
import { isUnifiedAnalysisPromptPack } from "../../data/mockPromptData";
import { PROMPT_EDITOR_EXTRA, PROMPT_PUBLISH_MODAL } from "../../copy/opsPanelHints";
import { PROMPT_EDITOR } from "./promptManagementUiCopy";
import { isLocalDraftPromptPackId, persistEphemeralBootstrap } from "./promptEphemeral";
import {
  type EditorBootstrap,
  remotePublish,
  remoteRollback,
  remoteSaveDraft,
  resolveEditorBootstrap,
} from "./promptRemote";

const { Text } = Typography;

const SESSION_PREFIX = "prompt-editor-cache:";

/** Token 粗略估计（非精确 tokenizer）；与字数一并展示便于治理侧体感体量 */
function approximateTokensFromUtf8(text: string): number {
  const t = text.trim();
  if (!t.length) return 0;
  return Math.max(1, Math.ceil(Array.from(text).length / 3.2));
}

function extractPlaceholderKeys(markdown: string): string[] {
  const keys = new Set<string>();
  const re = /\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}/g;
  let m: RegExpExecArray | null;
  while ((m = re.exec(markdown))) {
    keys.add(m[1]);
  }
  return [...keys].sort((a, b) => a.localeCompare(b));
}

function formatAt(iso?: string): string {
  if (!iso) return "—";
  return iso.replace("T", " ").slice(0, 16);
}

function cloneFew(rows: MockFewShotRow[]): MockFewShotRow[] {
  return rows.map((r) => ({ ...r }));
}

/** 草稿 / 已发布（治理可读口径）；与后端 lockState 近似对齐 */
function promptGovernancePublicationLabel(lockState: string): { zh: string; color: ComponentProps<typeof Tag>["color"] } {
  const u = (lockState || "").toUpperCase();
  if (u === "DRAFT") return { zh: "草稿", color: "blue" };
  if (u === "PUBLISHED") return { zh: "已发布", color: "green" };
  if (u === "LOCKED") return { zh: "已发布（冻结）", color: "cyan" };
  if (u === "DISABLED") return { zh: "已停用", color: "default" };
  return { zh: zhPromptPackLockState(lockState), color: "default" };
}

function loadSessionDraft(id: string): Partial<MockPromptPackDraft> | null {
  try {
    const raw = sessionStorage.getItem(SESSION_PREFIX + id);
    if (!raw) return null;
    return JSON.parse(raw) as Partial<MockPromptPackDraft>;
  } catch {
    return null;
  }
}

function saveSessionDraft(id: string, partial: Partial<MockPromptPackDraft>) {
  try {
    const prev = loadSessionDraft(id) ?? {};
    sessionStorage.setItem(SESSION_PREFIX + id, JSON.stringify({ ...prev, ...partial }));
  } catch {
    /* ignore quota */
  }
}

function serializeWorkbench(snapshot: {
  packTitle: string;
  scenarioId: string;
  skillRef: string;
  body: string;
}): string {
  return JSON.stringify(snapshot);
}

function PromptPackEditorInner({ bootstrap }: { bootstrap: EditorBootstrap }) {
  const { message, modal } = App.useApp();
  const pack = bootstrap.pack;
  const remote = bootstrap.remote;
  const versions = bootstrap.versionHistory;
  const locked = pack.lockState === "LOCKED";
  const [draftUnlocked, setDraftUnlocked] = useState(false);
  const canEditBody = !locked || draftUnlocked;
  const localDraft = isLocalDraftPromptPackId(pack.promptPackId);
  const unifiedAnalysis = isUnifiedAnalysisPromptPack(pack);

  const boundScenarioId = pack.scenarioId?.trim() ?? "";
  const boundSkillSpecRef = pack.skillSpecRef?.trim() ?? "";

  const preservedFewShotsRef = useRef(cloneFew(bootstrap.draft.fewShots));
  const preservedVariableSchemaJsonRef = useRef(bootstrap.draft.variableSchemaJson);
  const preservedSandboxFixtureJsonRef = useRef(bootstrap.draft.sandboxFixtureJson);

  const [etag, setEtag] = useState(bootstrap.etag);
  const [packTitle, setPackTitle] = useState(pack.title);
  const [baseline, setBaseline] = useState("");
  const [body, setBody] = useState(bootstrap.draft.bodyMarkdown);

  const [publishTrace, setPublishTrace] = useState<PromptPublishGateTrace | null>(null);
  const [publishPreflightLoading, setPublishPreflightLoading] = useState(false);
  const publishPreflightGen = useRef(0);

  const runPublishPreflight = useCallback(async () => {
    const gen = ++publishPreflightGen.current;
    setPublishPreflightLoading(true);
    try {
      const trace = await runPromptPublishGate(pack, boundScenarioId, body);
      if (publishPreflightGen.current === gen) setPublishTrace(trace);
    } finally {
      if (publishPreflightGen.current === gen) setPublishPreflightLoading(false);
    }
  }, [pack, boundScenarioId, body]);

  useEffect(() => {
    const p = bootstrap.pack;
    const d = bootstrap.draft;
    const sess = loadSessionDraft(p.promptPackId);
    const mergedBody = sess?.bodyMarkdown ?? d.bodyMarkdown;

    preservedFewShotsRef.current = cloneFew(d.fewShots);
    preservedVariableSchemaJsonRef.current = d.variableSchemaJson;
    preservedSandboxFixtureJsonRef.current = d.sandboxFixtureJson;

    setPackTitle(p.title);
    setBody(mergedBody);
    setEtag(bootstrap.etag);
    setDraftUnlocked(false);
    setBaseline(
      serializeWorkbench({
        packTitle: p.title,
        scenarioId: p.scenarioId ?? "",
        skillRef: p.skillSpecRef ?? "",
        body: mergedBody,
      }),
    );
  }, [bootstrap]);

  const workbenchSig = useMemo(
    () =>
      serializeWorkbench({
        packTitle,
        scenarioId: boundScenarioId,
        skillRef: boundSkillSpecRef,
        body,
      }),
    [packTitle, boundScenarioId, boundSkillSpecRef, body],
  );

  const dirty = baseline.length > 0 && workbenchSig !== baseline;

  const tokenApprox = useMemo(() => approximateTokensFromUtf8(body), [body]);
  const placeholderKeys = useMemo(() => extractPlaceholderKeys(body), [body]);
  const pubLabel = useMemo(() => promptGovernancePublicationLabel(pack.lockState), [pack.lockState]);

  useEffect(() => {
    if (!dirty) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [dirty]);

  const listBack = promptPackListHref(pack);

  const bumpBaseline = useCallback(() => {
    setBaseline(
      serializeWorkbench({
        packTitle,
        scenarioId: boundScenarioId,
        skillRef: boundSkillSpecRef,
        body,
      }),
    );
  }, [packTitle, boundScenarioId, boundSkillSpecRef, body]);

  const onSaveDraft = useCallback(async () => {
    const fewShots = preservedFewShotsRef.current;
    const variableSchemaJson = preservedVariableSchemaJsonRef.current;
    const sandboxFixtureJson = preservedSandboxFixtureJsonRef.current;

    saveSessionDraft(pack.promptPackId, {
      bodyMarkdown: body,
    });

    if (remote) {
      let variableSchema: unknown;
      try {
        variableSchema = variableSchemaJson.trim() ? JSON.parse(variableSchemaJson) : {};
      } catch {
        message.error("草稿中的变量结构与正文不同步（JSON），请刷新后重试或联系研发修复数据");
        return;
      }
      try {
        const patch: Record<string, unknown> = {
          bodyMarkdown: body,
          body,
          scenarioId: boundScenarioId,
          skillSpecRef: boundSkillSpecRef,
          variableSchema,
          fewShots,
        };
        if (packTitle.trim()) patch.title = packTitle.trim();

        const { etag: next } = await remoteSaveDraft(pack.promptPackId, etag, patch);
        setEtag(next);
        message.success("草稿已保存");
        bumpBaseline();
      } catch (e) {
        if (e instanceof ApiError && e.status === 409) {
          message.error("版本冲突：请刷新页面后再编辑");
        } else {
          message.error(String(e));
        }
      }
    } else {
      message.success(localDraft ? PROMPT_EDITOR.savedLocal : PROMPT_EDITOR.savedPreview);
      if (localDraft) {
        persistEphemeralBootstrap({
          ...bootstrap,
          etag,
          pack: {
            ...pack,
            title: packTitle.trim() || pack.title,
            updatedAt: new Date().toISOString(),
          },
          draft: {
            promptPackId: pack.promptPackId,
            etag,
            bodyMarkdown: body,
            fewShots,
            variableSchemaJson,
            sandboxFixtureJson,
          },
        });
      }
      bumpBaseline();
    }
  }, [
    body,
    bootstrap,
    bumpBaseline,
    etag,
    localDraft,
    message,
    pack,
    pack.promptPackId,
    packTitle,
    remote,
    boundScenarioId,
    boundSkillSpecRef,
  ]);

  useEffect(() => {
    const t = window.setTimeout(() => {
      void runPublishPreflight();
    }, 480);
    return () => window.clearTimeout(t);
  }, [runPublishPreflight]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!(e.ctrlKey || e.metaKey) || e.key !== "s") return;
      e.preventDefault();
      if (canEditBody) void onSaveDraft();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [canEditBody, onSaveDraft]);

  const onPublish = useCallback(() => {
    void (async () => {
      const trace = await runPromptPublishGate(pack, boundScenarioId, body);
      setPublishTrace(trace);
      if (!trace.ok) {
        modal.error({
          title: "暂不可发布",
          width: 720,
          content: (
            <div style={{ marginTop: 8 }}>
              <PromptPublishRejectTraceTable rejections={trace.rejections} />
            </div>
          ),
        });
        return;
      }
      modal.confirm({
        title: "发布当前草稿？",
        content: remote ? (
          <p>{PROMPT_PUBLISH_MODAL.remoteConfirm}</p>
        ) : (
          <p>{PROMPT_PUBLISH_MODAL.localConfirm}</p>
        ),
        onOk: async () => {
          if (remote) {
            try {
              await remotePublish(pack.promptPackId);
              message.success("发布已提交");
            } catch (e) {
              message.error(String(e));
            }
          } else {
            message.success(PROMPT_PUBLISH_MODAL.localSuccess);
          }
        },
      });
    })();
  }, [body, boundScenarioId, message, modal, pack, remote, setPublishTrace]);

  const onRollback = useCallback(
    (ver: number) => {
      modal.confirm({
        title: `回滚到 v${ver}？`,
        content: remote ? "未保存的正文可能被覆盖，请先按需保存草稿。" : PROMPT_PUBLISH_MODAL.rollbackLocalHint,
        onOk: async () => {
          if (remote) {
            try {
              await remoteRollback(pack.promptPackId, ver);
              message.success("回滚请求已提交");
            } catch (e) {
              message.error(String(e));
            }
          } else {
            message.success(`已模拟回滚到 v${ver}`);
          }
        },
      });
    },
    [message, modal, pack.promptPackId, remote],
  );

  const rollbackMenuProps: MenuProps = useMemo(
    () =>
      ({
        items:
          versions.length === 0
            ? [{ key: "__none__", disabled: true, label: "暂无版本记录" }]
            : versions.slice(0, 20).map((v) => ({
                key: String(v.promptPackVersion),
                label: `v${v.promptPackVersion} · ${formatAt(v.publishedAt)}`,
              })),
        onClick: ({ key }: { key: string }) => {
          if (key === "__none__") return;
          onRollback(Number(key));
        },
      }) satisfies MenuProps,
    [versions, onRollback],
  );

  const titleSuffix = localDraft ? packTitle.trim() || pack.title : pack.title;

  return (
    <ProductPageShell
      pageId="ai.prompt-editor"
      showPageId={false}
      title={`Prompt · ${titleSuffix}`}
      description={<Text type="secondary">{PROMPT_EDITOR.pageDescription}</Text>}
      tags={
        <Space wrap size={6}>
          {dirty ? (
            <Tag color="orange" style={{ marginInlineEnd: 0 }}>
              未保存
            </Tag>
          ) : null}
          {localDraft ? (
            <Tag color="processing" style={{ marginInlineEnd: 0 }}>
              仅本机草稿
            </Tag>
          ) : null}
        </Space>
      }
      extra={
        <Space wrap size={[8, 8]}>
          <Link to={listBack}>
            <Button>返回列表</Button>
          </Link>
          {localDraft ? null : (
            <Link to={promptPackViewPath(pack.promptPackId)}>
              <Button type="link">详情</Button>
            </Link>
          )}
        </Space>
      }
    >
      {localDraft ? (
        <Alert
          type="warning"
          showIcon
          banner
          style={{ marginBottom: 12 }}
          message={PROMPT_EDITOR.localDraftBanner}
        />
      ) : null}

      {unifiedAnalysis ? <PromptUnifiedAnalysisMeta /> : null}
      {!unifiedAnalysis ? <SkillSpecRefPublishAlert pack={pack} scenarioId={boundScenarioId} /> : null}

      {locked && !draftUnlocked ? (
        <Alert
          type="warning"
          showIcon
          style={{ marginBottom: 12 }}
          message={PROMPT_EDITOR.lockedVersionMessage}
          description={PROMPT_EDITOR.lockedVersionDescription}
          action={
            <Button size="small" type="primary" ghost onClick={() => setDraftUnlocked(true)}>
              复制草稿
            </Button>
          }
        />
      ) : locked && draftUnlocked ? (
        <Alert type="success" showIcon style={{ marginBottom: 12 }} message={PROMPT_EDITOR.draftReadyMessage} />
      ) : null}

      <Row gutter={[16, 16]} align="top">
        <Col xs={24} lg={16} xl={17}>
          <Space direction="vertical" size={12} style={{ width: "100%" }}>
            <Card size="small" className="admin-panel-card" title="基础信息">
              <Space direction="vertical" size={10} style={{ width: "100%" }}>
                <div>
                  <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                    Prompt 名称
                  </Text>
                  <Input
                    value={packTitle}
                    onChange={(e) => setPackTitle(e.target.value)}
                    placeholder="列表与标题展示名"
                    disabled={locked && !draftUnlocked}
                  />
                  {locked && !draftUnlocked ? (
                    <Text type="secondary" style={{ fontSize: 11, display: "block", marginTop: 4 }}>
                      解冻前不可改标题；复制草稿后可改。
                    </Text>
                  ) : null}
                </div>
                <Row gutter={[12, 8]}>
                  <Col span={24}>
                    <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                      {PROMPT_EDITOR.labelPackId}
                    </Text>
                    <PromptPackIdText promptPackId={pack.promptPackId} />
                  </Col>
                  <Col xs={24} sm={12}>
                    <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                      Prompt 类型
                    </Text>
                    <Tag>{zhPromptPackKind(pack.kind)}</Tag>
                  </Col>
                  <Col xs={24} sm={12}>
                    <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                      状态
                    </Text>
                    <Tag color={pubLabel.color === "default" || !pubLabel.color ? undefined : pubLabel.color}>{pubLabel.zh}</Tag>
                    {pack.hasDraft === true ? (
                      <Tag color="purple" style={{ marginLeft: 4 }}>
                        有未发布草稿
                      </Tag>
                    ) : null}
                  </Col>
                  {pack.kind === "TRADING" && (
                    <>
                      <Col xs={24} sm={12}>
                        <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                          {PROMPT_EDITOR.labelScenarioId}
                        </Text>
                        <Text code copyable={boundScenarioId ? { text: boundScenarioId } : undefined}>
                          {boundScenarioId || "—"}
                        </Text>
                      </Col>
                      <Col xs={24} sm={12}>
                        <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                          {PROMPT_EDITOR.labelSkillScope}
                        </Text>
                        <Text code copyable={boundSkillSpecRef ? { text: boundSkillSpecRef } : undefined}>
                          {boundSkillSpecRef || PROMPT_EDITOR_EXTRA.skillScopeEmptyInferred}
                        </Text>
                        <Text type="secondary" style={{ fontSize: 11, display: "block", marginTop: 4 }}>
                          {PROMPT_EDITOR.skillScopeHint}
                        </Text>
                      </Col>
                    </>
                  )}
                </Row>
              </Space>
            </Card>

            <Card size="small" className="admin-panel-card" title="Prompt 内容">
              <Space direction="vertical" size={8} style={{ width: "100%" }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {PROMPT_EDITOR.contentHint}
                </Text>
                <PromptMarkdownLiteField value={body} onChange={setBody} disabled={!canEditBody} minEditorHeightPx={380} />
                {placeholderKeys.length > 0 ? (
                  <div>
                    <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 6 }}>
                      正文中占位符一览（语法高亮的轻量视图）
                    </Text>
                    <Space wrap size={[4, 4]}>
                      {placeholderKeys.map((k) => (
                        <Tag key={k} color="processing">
                          {`{{${k}}}`}
                        </Tag>
                      ))}
                    </Space>
                  </div>
                ) : (
                  <Text type="secondary" style={{ fontSize: 11 }}>
                    未检测到 <Text code>{"{{name}}"}</Text> 形占位符
                  </Text>
                )}
              </Space>
            </Card>
          </Space>
        </Col>

        <Col xs={24} lg={8} xl={7}>
          <Space direction="vertical" size={12} style={{ width: "100%", position: "sticky", top: 8 }}>
          <Card size="small" className="admin-panel-card" title="版本与发布">
            <Space direction="vertical" size={14} style={{ width: "100%" }}>
              <div>
                <Text type="secondary" style={{ fontSize: 12, display: "block" }}>
                  Token（粗估）
                </Text>
                <Text strong style={{ fontSize: 20 }}>
                  {tokenApprox}
                </Text>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  字数 {body.length.toLocaleString()}
                </Text>
              </div>

              <Divider style={{ margin: "4px 0" }} />

              <div>
                <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                  当前生效版本
                </Text>
                <Text>{pack.currentVersion != null ? `v${pack.currentVersion}` : "—（尚未发布）"}</Text>
              </div>
              <div>
                <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                  最近发布时间
                </Text>
                <Text>{formatAt(pack.publishedAt)}</Text>
              </div>
              <div>
                <Text type="secondary" style={{ fontSize: 12, display: "block", marginBottom: 4 }}>
                  发布人
                </Text>
                <Text>{pack.publisher ?? "—"}</Text>
              </div>

              <Divider style={{ margin: "4px 0" }} />

              <div>
                <Text strong style={{ fontSize: 12, display: "block", marginBottom: 8 }}>
                  版本历史（最近）
                </Text>
                <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12, color: "#666", maxHeight: 200, overflow: "auto" }}>
                  {versions.length === 0 ? (
                    <li>暂无记录</li>
                  ) : (
                    versions.slice(0, 12).map((v) => (
                      <li key={`${v.promptPackVersion}-${v.publishedAt}`}>
                        v{v.promptPackVersion} · {formatAt(v.publishedAt)}
                      </li>
                    ))
                  )}
                </ul>
              </div>

              <PromptPublishRejectTrace
                trace={publishTrace}
                loading={publishPreflightLoading && !publishTrace}
                compact
                title={PROMPT_EDITOR.publishRejectTraceTitle}
              />

              <Space direction="vertical" style={{ width: "100%" }} size={8}>
                <Button block loading={publishPreflightLoading} onClick={() => void runPublishPreflight()}>
                  {PROMPT_EDITOR.publishPreflightButton}
                </Button>
                <Button block icon={<SaveOutlined />} type="primary" ghost onClick={() => void onSaveDraft()} disabled={!canEditBody}>
                  保存草稿（⌘S）
                </Button>
                <Dropdown disabled={versions.length === 0} menu={rollbackMenuProps}>
                  <Button block disabled={versions.length === 0}>
                    从历史版本恢复
                  </Button>
                </Dropdown>
                <Button block type="primary" onClick={onPublish} disabled={!canEditBody}>
                  发布
                </Button>
              </Space>

              {!remote ? (
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {localDraft ? PROMPT_EDITOR.localDraftVersionHint : PROMPT_EDITOR.demoSaveHint}
                </Text>
              ) : (
                <Text type="secondary" style={{ fontSize: 11 }}>
                  {PROMPT_EDITOR.publishFooterRemote}
                </Text>
              )}
            </Space>
          </Card>

          {pack.kind === "TRADING" && <PromptAssemblyTraceCard pack={pack} />}
          </Space>
        </Col>
      </Row>
    </ProductPageShell>
  );
}

export function PromptPackEditorPage() {
  const { promptPackId = "" } = useParams();
  const [bootstrap, setBootstrap] = useState<EditorBootstrap | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!promptPackId) {
      setBootstrap(null);
      setLoading(false);
      return;
    }
    let cancelled = false;
    setLoading(true);
    resolveEditorBootstrap(promptPackId)
      .then((b) => {
        if (!cancelled) setBootstrap(b);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [promptPackId]);

  if (!promptPackId) {
    return <Navigate to="/prompts/strategy" replace />;
  }

  if (loading) {
    return (
      <ProductPageShell pageId="ai.prompt-editor" showPageId={false} title="加载中…" extra={null}>
        <div style={{ padding: 80, textAlign: "center" }}>
          <Spin size="large" />
        </div>
      </ProductPageShell>
    );
  }

  if (!bootstrap) {
    return <Navigate to="/prompts/strategy" replace />;
  }

  return <PromptPackEditorInner key={bootstrap.pack.promptPackId} bootstrap={bootstrap} />;
}