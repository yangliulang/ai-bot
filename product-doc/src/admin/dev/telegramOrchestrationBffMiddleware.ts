import type { IncomingMessage, ServerResponse } from "node:http";
import type { Connect } from "vite";
import {
  inferDemoRoutingClarifyFromUtterance,
  inferDemoSymbolLabelFromUtterance,
  runClarifyOrchestrationPipeline,
} from "../src/productionRuntime/clarifyOrchestrationPipeline";

function readJsonBody(req: IncomingMessage): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (c) => chunks.push(c));
    req.on("end", () => {
      const raw = Buffer.concat(chunks).toString("utf8");
      if (!raw.trim()) {
        resolve({});
        return;
      }
      try {
        resolve(JSON.parse(raw));
      } catch (e) {
        reject(e);
      }
    });
    req.on("error", reject);
  });
}

function sendJson(res: ServerResponse, status: number, body: unknown): void {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(body));
}

type DemoWebhookBody = {
  chat_id?: number;
  text?: string;
  mode?: "flash_convert" | "limit_order";
  slots?: Record<string, string | null>;
};

/**
 * Vite dev · Telegram 入站 Demo（非生产 Bot）
 *
 * POST /api/v1/demo/telegram/inbound
 * POST /api/v1/internal/agent/orchestration/trade-resolver（同窗 OpenAPI + pipeline）
 */
export function createTelegramOrchestrationBffMiddleware(): Connect.NextHandleFunction {
  return (req, res, next) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    const path = url.pathname;

    if (
      req.method === "POST" &&
      path === "/api/v1/internal/agent/orchestration/trade-resolver"
    ) {
      void readJsonBody(req)
        .then((body) => {
          const result = runClarifyOrchestrationPipeline(
            body as Parameters<typeof runClarifyOrchestrationPipeline>[0],
          );
          sendJson(res, 200, result);
        })
        .catch(() => sendJson(res, 400, { error: "invalid_json" }));
      return;
    }

    if (req.method === "POST" && path === "/api/v1/demo/telegram/inbound") {
      void readJsonBody(req)
        .then((body) => {
          const b = body as DemoWebhookBody;
          const text = b.text ?? "";
          const routingClarify = inferDemoRoutingClarifyFromUtterance(text);
          const symbolLabel = inferDemoSymbolLabelFromUtterance(text);
          const side = /卖|sell/i.test(text) ? "SELL" : "BUY";
          const symbol =
            symbolLabel != null ? `${symbolLabel}USDT` : (b.slots?.symbol ?? null);

          const pipeline = runClarifyOrchestrationPipeline({
            mode: b.mode ?? "flash_convert",
            slots: {
              symbol,
              side,
              type: b.mode === "limit_order" ? "LIMIT" : "MARKET",
              ...b.slots,
            },
            userUtterance: text,
            routingClarify,
            resolvedSymbolLabel: symbolLabel,
            effectiveLocale: "zh-Hans",
          });

          const outbound = pipeline.telegramOutbound;
          sendJson(res, 200, {
            chat_id: b.chat_id ?? 0,
            demo: true,
            /** 生产 BFF 须调 Telegram sendChatAction(typing) */
            telegramActions: [
              ...(pipeline.initialTyping?.sendTyping
                ? [{ method: "sendChatAction", action: "typing" as const }]
                : []),
            ],
            reply: {
              text:
                outbound?.progressHint ??
                outbound?.userVisibleHint ??
                (pipeline.output.missing.length === 0
                  ? "（Demo）参数齐备，可进入类型 A 确认卡。"
                  : "（Demo）仍缺参数，请继续澄清。"),
              reply_markup: outbound?.clarifyInlineKeyboard
                ? {
                    inline_keyboard: outbound.clarifyInlineKeyboard.rows,
                  }
                : undefined,
            },
            resolver: {
              missing: pipeline.output.missing,
              skillId: pipeline.output.skillId,
              appliedReadBalanceFill: pipeline.appliedReadBalanceFill ?? false,
              orchestrationNextSteps: pipeline.orchestrationNextSteps,
            },
          });
        })
        .catch(() => sendJson(res, 400, { error: "invalid_json" }));
      return;
    }

    next();
  };
}
