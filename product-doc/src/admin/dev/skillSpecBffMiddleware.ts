import type { IncomingMessage, ServerResponse } from "node:http";
import type { Connect } from "vite";
import { createSkillSpecBffStore, SkillPublishError } from "./skillSpecBffStore";
import type { SkillSpecPublishRequest } from "../src/api/types/skillOperationSpec";

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

function sendProblem(res: ServerResponse, err: SkillPublishError): void {
  sendJson(res, err.status, {
    type: `urn:coobit:skill-publish:${err.code}`,
    title: err.code,
    detail: err.message,
    code: err.code,
  });
}

function decodePathSegment(seg: string): string {
  try {
    return decodeURIComponent(seg);
  } catch {
    return seg;
  }
}

/**
 * Vite dev · OpenAPI skill-specs + internal/skills/effective
 */
export function createSkillSpecBffMiddleware(repoRoot: string): Connect.NextHandleFunction {
  const api = createSkillSpecBffStore(repoRoot);

  return (req, res, next) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    const path = url.pathname;

    if (!path.startsWith("/api/v1/")) {
      next();
      return;
    }

    const run = async () => {
      try {
        if (req.method === "GET" && path === "/api/v1/admin/skill-specs") {
          sendJson(res, 200, api.list());
          return;
        }

        const adminSkill = path.match(
          /^\/api\/v1\/admin\/skill-specs\/([^/]+)(?:\/(versions|publish)(?:\/([^/]+))?)?$/,
        );
        if (adminSkill) {
          const skillId = decodePathSegment(adminSkill[1]!);
          const segment = adminSkill[2];
          const versionSeg = adminSkill[3] ? decodePathSegment(adminSkill[3]) : undefined;

          if (req.method === "GET" && !segment) {
            sendJson(res, 200, api.getSummary(skillId));
            return;
          }
          if (req.method === "GET" && segment === "versions" && !versionSeg) {
            sendJson(res, 200, api.getVersions(skillId));
            return;
          }
          if (req.method === "GET" && segment === "versions" && versionSeg) {
            sendJson(res, 200, api.getVersionBody(skillId, versionSeg));
            return;
          }
          if (req.method === "POST" && segment === "publish") {
            const body = (await readJsonBody(req)) as SkillSpecPublishRequest;
            sendJson(res, 200, api.publish(skillId, body));
            return;
          }
        }

        if (req.method === "GET" && path === "/api/v1/internal/skills/effective") {
          const skillId = url.searchParams.get("skillId");
          const skillSpecVersion = url.searchParams.get("skillSpecVersion");
          if (!skillId || !skillSpecVersion) {
            sendJson(res, 400, { title: "skillId and skillSpecVersion required" });
            return;
          }
          const effective = api.getEffective(skillId, skillSpecVersion);
          const ifNoneMatch = req.headers["if-none-match"];
          if (ifNoneMatch && ifNoneMatch === effective.etag) {
            res.statusCode = 304;
            res.end();
            return;
          }
          if (effective.etag) res.setHeader("ETag", effective.etag);
          sendJson(res, 200, effective);
          return;
        }

        next();
      } catch (e) {
        if (e instanceof SkillPublishError) {
          sendProblem(res, e);
          return;
        }
        sendJson(res, 500, { title: "Internal Error", detail: String(e) });
      }
    };

    void run();
  };
}
