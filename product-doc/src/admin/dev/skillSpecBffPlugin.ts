import path from "node:path";
import { fileURLToPath } from "node:url";
import type { Plugin } from "vite";
import { createBillingCommerceBffMiddleware } from "./billingCommerceBffMiddleware";
import { createBillingLedgerBffMiddleware } from "./billingLedgerBffMiddleware";
import { createInternalBillingEntitlementsBffMiddleware } from "./internalBillingEntitlementsBffMiddleware";
import { createSkillSpecBffMiddleware } from "./skillSpecBffMiddleware";
import { createTelegramOrchestrationBffMiddleware } from "./telegramOrchestrationBffMiddleware";

const devDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(devDir, "../../..");

/** 本地 Dev：实现 OpenAPI `admin/skill-specs/*` + `internal/skills/effective` */
export function skillSpecBffPlugin(): Plugin {
  return {
    name: "coobit-skill-spec-bff-mock",
    configureServer(server) {
      server.middlewares.use(createSkillSpecBffMiddleware(repoRoot));
      server.middlewares.use(createBillingCommerceBffMiddleware());
      server.middlewares.use(createBillingLedgerBffMiddleware());
      server.middlewares.use(createInternalBillingEntitlementsBffMiddleware());
      server.middlewares.use(createTelegramOrchestrationBffMiddleware());
      server.httpServer?.once("listening", () => {
        // eslint-disable-next-line no-console
        console.log(
          "[admin-bff-mock] skill-specs · commerce · ledger · entitlements · telegram/clarify-demo",
        );
      });
    },
  };
}
