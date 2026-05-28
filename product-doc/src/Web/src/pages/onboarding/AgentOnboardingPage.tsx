import { CheckCircleFilled, LinkOutlined, SafetyCertificateOutlined } from "@ant-design/icons";
import { Alert, Button, Checkbox, Descriptions, Divider, Form, Input, Tag, Typography } from "antd";
import { useCallback, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { OnboardingPanel } from "@/components/onboarding/OnboardingPanel";
import { getAgentApiBase, postTradingApiBinding } from "@/api/meAgent";

const { Paragraph, Text } = Typography;

const panelSubtitle = (
  <>
    无须登录交易所网页。核对 Telegram 后填写 <strong>subUid</strong> 与子账户 <strong>API Key / Secret</strong>，保存即服务端校验。
  </>
);

const FALLBACK_TELEGRAM_BOT_URL = "https://t.me/CoolbitTradingAgentBot";

function telegramBotOpenUrlFromEnv(searchParams: URLSearchParams): string {
  const fromQuery = searchParams.get("tg_bot")?.trim();
  if (fromQuery && /^https:\/\/t\.me\//i.test(fromQuery)) return fromQuery;
  const envUrl = import.meta.env.VITE_TELEGRAM_BOT_URL?.trim();
  if (envUrl) return envUrl;
  return FALLBACK_TELEGRAM_BOT_URL;
}

function normalizeTelegramUsername(raw: string): string {
  const t = raw.trim();
  if (!t) return "";
  const handle = t.startsWith("@") ? t.slice(1) : t;
  if (!handle) return "";
  return `@${handle}`;
}

function pickDeeplinkToken(searchParams: URLSearchParams): string | undefined {
  const keys = ["deeplink_token", "bind_token", "token", "confirm_token"] as const;
  for (const k of keys) {
    const v = searchParams.get(k)?.trim();
    if (v) return v;
  }
  return undefined;
}

function pickSubaccountUidFromQuery(searchParams: URLSearchParams): string {
  const keys = ["agent_sub_account_uid", "subaccount_uid", "sub_uid", "subUid"] as const;
  for (const k of keys) {
    const v = searchParams.get(k)?.trim();
    if (v) return v;
  }
  return "";
}

function newIdempotencyKey(): string {
  try {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return crypto.randomUUID();
    }
  } catch {
    /* fallback */
  }
  return `idem-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`;
}

type BindFormValues = {
  agentSubAccountUid: string;
  apiKey: string;
  apiSecret: string;
  agree: boolean;
};

/** Telegram + subUid + Key/Secret → 保存校验（FR-WEB / initialization-flow §1.2） */
export default function AgentOnboardingPage() {
  const [searchParams] = useSearchParams();
  const [form] = Form.useForm<BindFormValues>();
  const telegramBotOpenUrl = useMemo(() => telegramBotOpenUrlFromEnv(searchParams), [searchParams]);
  const deeplinkToken = useMemo(() => pickDeeplinkToken(searchParams), [searchParams]);
  const subaccountUidFromQuery = useMemo(() => pickSubaccountUidFromQuery(searchParams), [searchParams]);

  const telegramParsed = useMemo(() => {
    const fromQuery =
      searchParams.get("tg_username")?.trim() ??
      searchParams.get("telegram_username")?.trim() ??
      searchParams.get("tg_user")?.trim();
    return {
      username: fromQuery ? normalizeTelegramUsername(fromQuery) : "",
      fromLink: Boolean(fromQuery),
    };
  }, [searchParams]);

  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [bindResult, setBindResult] = useState<{
    agentSubAccountId?: string;
    declaredSubaccountUid?: string;
  } | null>(null);

  const apiBase = useMemo(() => getAgentApiBase(), []);

  const onFinish = useCallback(
    async (values: BindFormValues) => {
      setErrorMsg(null);
      const agentSubAccountUid = values.agentSubAccountUid.trim();
      const apiKey = values.apiKey.trim();
      const apiSecret = values.apiSecret.trim();
      if (!agentSubAccountUid || !apiKey || !apiSecret) {
        setErrorMsg("请填写 subUid、API Key 与 Secret。");
        return;
      }

      setLoading(true);
      try {
        if (!apiBase) {
          await new Promise((r) => setTimeout(r, 700));
          setBindResult({ declaredSubaccountUid: agentSubAccountUid });
          setDone(true);
          return;
        }

        const result = await postTradingApiBinding({
          idempotencyKey: newIdempotencyKey(),
          agentSubAccountUid,
          apiKey,
          apiSecret,
          deeplinkToken,
        });
        setBindResult({
          agentSubAccountId: result.agentSubAccountId,
          declaredSubaccountUid: agentSubAccountUid,
        });
        setDone(true);
      } catch (e) {
        const msg = e instanceof Error ? e.message : "绑定失败，请稍后重试。";
        setErrorMsg(msg);
      } finally {
        setLoading(false);
      }
    },
    [apiBase, deeplinkToken],
  );

  const rowStyles = {
    label: { width: 112, color: "#666666", fontSize: 13 },
    content: { fontSize: 13 },
  } as const;

  const boundSubaccountId =
    bindResult?.agentSubAccountId?.trim() ||
    (!apiBase && done ? "—（演示模式）" : undefined);

  const resetFlow = useCallback(() => {
    setDone(false);
    setBindResult(null);
    setErrorMsg(null);
    form.resetFields();
  }, [form]);

  if (done) {
    return (
      <div className="coolbit-main__narrow">
        <OnboardingPanel title="绑定完成" tone="success" closeTo={false} className="coolbit-onboarding-panel--standalone">
          <div className="coolbit-onboarding-result">
            <div className="coolbit-success-icon-wrap" aria-hidden>
              <CheckCircleFilled />
            </div>
            <Paragraph className="coolbit-onboarding-result__title">绑定成功</Paragraph>
            <Text type="secondary" className="coolbit-onboarding-result__lead">
              请在该子账户<strong>现货 USDT</strong>预留扣费余额，然后返回 Telegram 继续使用 Bot。
            </Text>
          </div>

          {bindResult?.declaredSubaccountUid || boundSubaccountId ? (
            <div className="coolbit-description-wrap coolbit-onboarding-result__summary">
              <Descriptions
                column={1}
                bordered
                size="small"
                styles={rowStyles}
                items={[
                  {
                    key: "tg",
                    label: "Telegram",
                    children: (
                      <Text
                        className="coolbit-onboarding-mono"
                        copyable={telegramParsed.username ? { text: telegramParsed.username.replace(/^@/, "") } : false}
                      >
                        {telegramParsed.username || "—"}
                      </Text>
                    ),
                  },
                  ...(bindResult?.declaredSubaccountUid
                    ? [
                        {
                          key: "uid",
                          label: "subUid",
                          children: (
                            <Text className="coolbit-onboarding-mono" copyable={{ text: bindResult.declaredSubaccountUid }}>
                              {bindResult.declaredSubaccountUid}
                            </Text>
                          ),
                        },
                      ]
                    : []),
                  ...(boundSubaccountId
                    ? [
                        {
                          key: "sub",
                          label: "内部绑定 ID",
                          children: boundSubaccountId.startsWith("—") ? (
                            <span className="coolbit-onboarding-mono">{boundSubaccountId}</span>
                          ) : (
                            <Text className="coolbit-onboarding-mono" copyable={{ text: boundSubaccountId }}>
                              {boundSubaccountId}
                            </Text>
                          ),
                        },
                      ]
                    : []),
                ]}
              />
            </div>
          ) : null}

          <div className="coolbit-success-steps coolbit-success-steps--compact">
            <Text type="secondary" className="coolbit-onboarding-result__next">
              首次打开 Bot 请先点「Start」，再对话或下单。
            </Text>
          </div>

          <Button
            type="primary"
            size="large"
            block
            href={telegramBotOpenUrl}
            target="_blank"
            rel="noreferrer"
            icon={<LinkOutlined />}
            className="coolbit-onboarding-submit-btn"
          >
            返回 Telegram 对话
          </Button>
          <div className="coolbit-onboarding-result__secondary">
            <Button type="link" size="small" onClick={resetFlow}>
              重新配置
            </Button>
          </div>
        </OnboardingPanel>
      </div>
    );
  }

  return (
    <div className="coolbit-main__narrow">
      <OnboardingPanel title="绑定交易助手" subtitle={panelSubtitle} closeTo={false} className="coolbit-onboarding-panel--standalone">
        <section className="coolbit-onboarding-block" aria-labelledby="onboarding-tg-heading">
          <h3 id="onboarding-tg-heading" className="coolbit-onboarding-section-title">
            Telegram
          </h3>
          <div className="coolbit-onboarding-tg-card">
            <div className="coolbit-onboarding-tg-card__icon" aria-hidden>
              <SafetyCertificateOutlined />
            </div>
            <div className="coolbit-onboarding-tg-card__body">
              <div className="coolbit-onboarding-tg-card__label">账号</div>
              {telegramParsed.username ? (
                <div className="coolbit-onboarding-tg-card__value coolbit-onboarding-mono">{telegramParsed.username}</div>
              ) : (
                <div className="coolbit-onboarding-tg-card__value coolbit-onboarding-tg-card__value--muted">
                  未识别（请从 Bot 链接进入）
                </div>
              )}
              {(deeplinkToken || telegramParsed.fromLink) && (
                <div className="coolbit-onboarding-tg-card__meta">
                  {deeplinkToken ? (
                    <Tag bordered={false} color="success">
                      链接令牌已携带
                    </Tag>
                  ) : (
                    <Tag bordered={false}>已从链接打开</Tag>
                  )}
                </div>
              )}
            </div>
          </div>
          {!telegramParsed.fromLink ? (
            <p className="coolbit-onboarding-footnote">
              调试可加 <span className="coolbit-onboarding-mono">?tg_username=demo</span>
            </p>
          ) : null}
        </section>

        <Divider className="coolbit-onboarding-divider" />

        <section className="coolbit-onboarding-block" aria-labelledby="onboarding-api-heading">
          <h3 id="onboarding-api-heading" className="coolbit-onboarding-section-title">
            交易所凭证
          </h3>
          <p className="coolbit-onboarding-bind-hint" role="note">
            <strong>安全：</strong>
            仅在本页填写；勿在聊天中发送 Secret。subUid 与 Key 须属<strong>同一子账户</strong>。
          </p>

          <Form
            form={form}
            layout="vertical"
            requiredMark
            colon={false}
            initialValues={{ agree: false, agentSubAccountUid: subaccountUidFromQuery }}
            onFinish={onFinish}
            scrollToFirstError={{ behavior: "smooth", block: "center" }}
          >
            <Form.Item
              label="子账户 UID（subUid）"
              name="agentSubAccountUid"
              rules={[{ required: true, message: "请填写 subUid" }]}
              extra="与交易所列表一致，且与下方 Key 同户。"
              normalize={(v) => (typeof v === "string" ? v.trim() : v)}
            >
              <Input
                size="large"
                autoComplete="off"
                spellCheck={false}
                autoCapitalize="off"
                autoCorrect="off"
                placeholder="subUid"
              />
            </Form.Item>
            <Form.Item
              label="API Key"
              name="apiKey"
              rules={[{ required: true, message: "请填写 API Key" }]}
              normalize={(v) => (typeof v === "string" ? v.trim() : v)}
            >
              <Input
                size="large"
                autoComplete="off"
                spellCheck={false}
                autoCapitalize="off"
                autoCorrect="off"
                placeholder="子账户 API Key"
              />
            </Form.Item>
            <Form.Item
              label="Secret Key"
              name="apiSecret"
              rules={[{ required: true, message: "请填写 Secret Key" }]}
              normalize={(v) => (typeof v === "string" ? v.trim() : v)}
            >
              <Input.Password
                size="large"
                autoComplete="new-password"
                spellCheck={false}
                autoCapitalize="off"
                autoCorrect="off"
                placeholder="私密，勿泄露"
                aria-label="Secret Key，请勿泄露"
              />
            </Form.Item>

            {errorMsg ? (
              <Alert type="error" showIcon role="alert" className="coolbit-onboarding-alert" message={errorMsg} />
            ) : null}

            <Form.Item
              name="agree"
              valuePropName="checked"
              className="coolbit-consent-row coolbit-consent-row--form-item"
              rules={[
                {
                  validator: (_, v) =>
                    v ? Promise.resolve() : Promise.reject(new Error("请先阅读并勾选确认")),
                },
              ]}
            >
              <Checkbox>
                <span className="coolbit-onboarding-consent-text">
                  授权用于查询与交易；<strong>不提币</strong>、不改安全设置；风险自担。
                </span>
              </Checkbox>
            </Form.Item>

            <Form.Item className="coolbit-onboarding-submit-wrap">
              <Button
                type="primary"
                htmlType="submit"
                size="large"
                block
                loading={loading}
                className="coolbit-onboarding-submit-btn"
              >
                保存
              </Button>
            </Form.Item>
          </Form>
        </section>
      </OnboardingPanel>
    </div>
  );
}
