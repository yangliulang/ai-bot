/**
 * CC-P1-02 / MR-A：C 类外网工具（`tool.web.*`）运行时选用与生产启用写闸。
 * 语义同窗 `specs/openapi/components/tool-management-schemas.yaml` · `ToolRegistryEntry`
 * 与 `trade-assistance` §8.4、ADR-003。
 */

export type DeployEnvironment = "development" | "staging" | "production";

export type ToolRegistryGateEntry = {
  toolId: string;
  domain?: string;
  enabledOperational?: boolean;
  externalToolCompliance?: {
    legalReviewTicketId?: string | null;
  } | null;
};

/** C 类外网工具：与 schema `domain` 标签、`toolId` 前缀同窗 */
export function isCClassExternalTool(entry: Pick<ToolRegistryGateEntry, "toolId" | "domain">): boolean {
  if (entry.toolId.startsWith("tool.web.")) return true;
  const d = entry.domain?.trim();
  if (d?.startsWith("tool.web.")) return true;
  return false;
}

/**
 * 运行时选用：C 类仅当运营启用态为真时可进入工具调用路径（未登记/停用的条目不会为 true）。
 */
export function cClassEligibleForRuntimeCall(entry: Pick<ToolRegistryGateEntry, "toolId" | "domain" | "enabledOperational">): boolean {
  if (!isCClassExternalTool(entry)) return false;
  return entry.enabledOperational === true;
}

export type EnableWriteValidation =
  | { ok: true }
  | { ok: false; code: "LEGAL_REVIEW_TICKET_REQUIRED"; message: string };

/**
 * 生产侧「将 C 类外网工具保持/置为运营启用」时：`legalReviewTicketId` 须非空（CC-P1-02 默认写闸）。
 * 停用（`enabledOperational=false`）时不校验工单号。
 */
export function validateProductionOperationalEnableForCClass(params: {
  entry: Pick<ToolRegistryGateEntry, "toolId" | "domain">;
  nextEnabledOperational: boolean;
  legalReviewTicketId: string | null | undefined;
  environment: DeployEnvironment;
}): EnableWriteValidation {
  const { entry, nextEnabledOperational, legalReviewTicketId, environment } = params;
  if (!isCClassExternalTool(entry)) return { ok: true };
  if (!nextEnabledOperational) return { ok: true };
  if (environment !== "production") return { ok: true };
  const ticket = (legalReviewTicketId ?? "").trim();
  if (!ticket) {
    return {
      ok: false,
      code: "LEGAL_REVIEW_TICKET_REQUIRED",
      message:
        "生产环境将 C 类外网工具置为运营启用时，须填写 externalToolCompliance.legalReviewTicketId（或登记 contract-closure §8 合规豁免）。",
    };
  }
  return { ok: true };
}
