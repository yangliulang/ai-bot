/** 正文 UTF-8 · SHA-256 hex（同窗 `agent.skill.spec_read.specDigest`） */

function normalizeBodyForDigest(body: string): string {
  return body.replace(/\r\n/g, "\n");
}

export async function computeSpecDigest(bodyMarkdown: string): Promise<string> {
  const normalized = normalizeBodyForDigest(bodyMarkdown);
  const bytes = new TextEncoder().encode(normalized);
  const subtle = globalThis.crypto?.subtle;
  if (!subtle?.digest) {
    throw new Error("crypto.subtle.digest 不可用（须在 HTTPS 或 Node 20+ 环境）");
  }
  const buf = await subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(buf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

export function etagFromDigest(specDigest: string, skillSpecVersion: string): string {
  return `"${specDigest.slice(0, 16)}-${skillSpecVersion}"`;
}
