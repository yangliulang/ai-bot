import { useEffect, useMemo, useState } from "react";
import { CopyOutlined } from "@ant-design/icons";
import {
  App,
  Button,
  Collapse,
  Drawer,
  Empty,
  Segmented,
  Space,
  Spin,
  Tabs,
  Typography,
} from "antd";
import { getSkillMarkdown, getSkillRegistryEntry } from "./skillRegistryCatalog";
import { getCachedSkillOperationView, warmSkillOperationCache } from "./skillOperationCache";
import { SKILL_DRAWER, type SkillSpecSectionKey } from "./skillRegistryUiCopy";
import { SkillOperationOverview } from "./SkillOperationOverview";
import { SKILL_SPEC_SECTIONS, SkillSpecSectionContent } from "./skillSpecSections";

const { Text } = Typography;

export type SkillOperationDrawerProps = {
  skillId: string | null;
  onClose: () => void;
};

export function SkillOperationDrawer({ skillId, onClose }: SkillOperationDrawerProps) {
  const { message } = App.useApp();
  const [mainTab, setMainTab] = useState<"overview" | "spec">("overview");
  const [specSection, setSpecSection] = useState<SkillSpecSectionKey>("params");

  const entry = skillId ? getSkillRegistryEntry(skillId) : undefined;
  const view = skillId ? getCachedSkillOperationView(skillId) : null;
  const rawMd = entry?.specPath ? getSkillMarkdown(entry.specPath) : undefined;
  const specLoading = Boolean(entry?.specPath && !view);

  useEffect(() => {
    if (!skillId) return;
    warmSkillOperationCache();
    setMainTab("overview");
    setSpecSection("params");
  }, [skillId]);

  const segmentedOptions = useMemo(() => {
    if (!view) return [];
    return SKILL_SPEC_SECTIONS.map((s) => {
      const n = s.count(view);
      return {
        label: (
          <span className="admin-skill-spec-segment-label">
            {s.label}
            {n > 0 ? (
              <span className="admin-skill-spec-segment-count">{n}</span>
            ) : null}
          </span>
        ),
        value: s.key,
        disabled: s.key === "api" && n === 0,
      };
    });
  }, [view]);

  const goToSpec = (section?: SkillSpecSectionKey) => {
    setMainTab("spec");
    if (section) setSpecSection(section);
  };

  const copySkillId = () => {
    if (!entry?.skillId) return;
    void navigator.clipboard.writeText(entry.skillId).then(
      () => message.success(SKILL_DRAWER.copySuccess),
      () => message.error(SKILL_DRAWER.copyFail),
    );
  };

  const drawerTitle = entry ? (
    <div className="admin-skill-drawer-title">
      <Text strong className="admin-skill-drawer-title__name">
        {entry.summary}
      </Text>
      <Text type="secondary" className="admin-skill-drawer-title__hint">
        {SKILL_DRAWER.switchHint}
      </Text>
    </div>
  ) : (
    SKILL_DRAWER.fallbackTitle
  );

  const drawerWidth =
    typeof window !== "undefined" ? Math.min(880, window.innerWidth - 40) : 880;

  return (
    <Drawer
      className="admin-skill-operation-drawer"
      title={drawerTitle}
      placement="right"
      width={drawerWidth}
      open={Boolean(skillId)}
      onClose={onClose}
      destroyOnClose
      styles={{ body: { paddingTop: 12 } }}
      footer={
        <div className="admin-skill-drawer-footer">
          <Text type="secondary" className="admin-skill-drawer-footer__id">
            {entry?.skillId ?? ""}
          </Text>
          <Space>
            {entry?.skillId ? (
              <Button icon={<CopyOutlined />} onClick={copySkillId}>
                {SKILL_DRAWER.copyId}
              </Button>
            ) : null}
            <Button type="primary" onClick={onClose}>
              {SKILL_DRAWER.close}
            </Button>
          </Space>
        </div>
      }
    >
      {entry ? (
        <div className="admin-skill-drawer-root">
          <Tabs
            className="admin-skill-drawer-tabs"
            activeKey={mainTab}
            onChange={(k) => setMainTab(k as "overview" | "spec")}
            items={[
              {
                key: "overview",
                label: SKILL_DRAWER.tabOverview,
                children: (
                  <SkillOperationOverview
                    entry={entry}
                    view={view}
                    onGoToSpec={goToSpec}
                  />
                ),
              },
              {
                key: "spec",
                label: SKILL_DRAWER.tabSpec,
                disabled: !view && !specLoading,
                children: (
                  <div className="admin-skill-drawer-tab-pane">
                    {specLoading ? (
                      <div className="admin-skill-drawer-loading">
                        <Spin tip={SKILL_DRAWER.loading} />
                      </div>
                    ) : view ? (
                      <>
                        <Segmented
                          className="admin-skill-spec-segmented"
                          block
                          options={segmentedOptions}
                          value={specSection}
                          onChange={(v) => setSpecSection(v as SkillSpecSectionKey)}
                        />
                        <div className="admin-skill-spec-section-body">
                          <SkillSpecSectionContent view={view} section={specSection} />
                        </div>
                        {rawMd ? (
                          <Collapse
                            className="admin-skill-drawer-raw"
                            style={{ marginTop: 16 }}
                            items={[
                              {
                                key: "raw",
                                label: SKILL_DRAWER.rawCollapse,
                                children: (
                                  <pre className="admin-skill-drawer-raw__pre">{rawMd}</pre>
                                ),
                              },
                            ]}
                          />
                        ) : null}
                      </>
                    ) : (
                      <Empty description={SKILL_DRAWER.emptyEntry} />
                    )}
                  </div>
                ),
              },
            ]}
          />
        </div>
      ) : (
        <Empty description={SKILL_DRAWER.emptyEntry} />
      )}
    </Drawer>
  );
}
