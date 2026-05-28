import type { Plugin } from "vite";
import { createMeCommerceBffMiddleware } from "./meCommerceBffMiddleware";

export function meCommerceBffPlugin(): Plugin {
  return {
    name: "coolbit-me-commerce-bff-mock",
    configureServer(server) {
      server.middlewares.use(createMeCommerceBffMiddleware());
      server.httpServer?.once("listening", () => {
        // eslint-disable-next-line no-console
        console.log(
          "[me-commerce-bff] mock · commerce (summary/consumptions)",
        );
      });
    },
  };
}
