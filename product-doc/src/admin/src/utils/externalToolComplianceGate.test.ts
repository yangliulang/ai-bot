import { describe, expect, it } from "vitest";
import {
  cClassEligibleForRuntimeCall,
  isCClassExternalTool,
  validateProductionOperationalEnableForCClass,
} from "./externalToolComplianceGate";

describe("isCClassExternalTool", () => {
  it("识别 toolId 前缀 tool.web.", () => {
    expect(isCClassExternalTool({ toolId: "tool.web.social_sentiment" })).toBe(true);
    expect(isCClassExternalTool({ toolId: "tool.exchange.spot.order" })).toBe(false);
  });

  it("识别 domain 标签 tool.web.*", () => {
    expect(isCClassExternalTool({ toolId: "custom.vendor.xyz", domain: "tool.web.search" })).toBe(true);
  });
});

describe("cClassEligibleForRuntimeCall", () => {
  it("仅 enabledOperational=true 的 C 类为可调用", () => {
    expect(
      cClassEligibleForRuntimeCall({
        toolId: "tool.web.social_sentiment",
        enabledOperational: true,
      }),
    ).toBe(true);
    expect(
      cClassEligibleForRuntimeCall({
        toolId: "tool.web.social_sentiment",
        enabledOperational: false,
      }),
    ).toBe(false);
    expect(
      cClassEligibleForRuntimeCall({
        toolId: "tool.exchange.spot.order",
        enabledOperational: true,
      }),
    ).toBe(false);
  });
});

describe("validateProductionOperationalEnableForCClass", () => {
  const cEntry = { toolId: "tool.web.social_sentiment" as const };

  it("非生产环境不要求工单号", () => {
    expect(
      validateProductionOperationalEnableForCClass({
        entry: cEntry,
        nextEnabledOperational: true,
        legalReviewTicketId: "",
        environment: "development",
      }),
    ).toEqual({ ok: true });
  });

  it("生产启用 C 类且工单号为空 → 拒绝", () => {
    const r = validateProductionOperationalEnableForCClass({
      entry: cEntry,
      nextEnabledOperational: true,
      legalReviewTicketId: "  ",
      environment: "production",
    });
    expect(r.ok).toBe(false);
    if (!r.ok) expect(r.code).toBe("LEGAL_REVIEW_TICKET_REQUIRED");
  });

  it("生产启用 C 类且工单号非空 → 通过", () => {
    expect(
      validateProductionOperationalEnableForCClass({
        entry: cEntry,
        nextEnabledOperational: true,
        legalReviewTicketId: "LEGAL-2026-8899",
        environment: "production",
      }),
    ).toEqual({ ok: true });
  });

  it("生产停用不要求工单号", () => {
    expect(
      validateProductionOperationalEnableForCClass({
        entry: cEntry,
        nextEnabledOperational: false,
        legalReviewTicketId: "",
        environment: "production",
      }),
    ).toEqual({ ok: true });
  });

  it("非 C 类不触发写闸", () => {
    expect(
      validateProductionOperationalEnableForCClass({
        entry: { toolId: "tool.exchange.spot.order" },
        nextEnabledOperational: true,
        legalReviewTicketId: "",
        environment: "production",
      }),
    ).toEqual({ ok: true });
  });
});
